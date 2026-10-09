"""
QA form check: the audit uses the page as a visitor would.

Measuring a page says nothing about whether it works: a form whose every submission the API refuses still renders
perfectly. This check fills each form with values its fields accept, submits it and reads what the API answered.

- A request the API refused (4xx, 5xx) or that never arrived is a defect, quoted with the API's own answer so the one
  rework knows what to change.
- A form the check could not complete (a field it cannot satisfy, no submit control, nothing sent) is a warning: the
  check's limit, not the page's fault.
- A record the check created is removed again (DELETE on the created record).

Values are chosen from what a field declares about itself (type, min, max, minlength, maxlength, options, and the
example in its placeholder), never from its name or the domain.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from urllib.parse import urlsplit

from pipeline_trace import traced

SCRIPT_TIMEOUT_S = 15

_FORM_SCRIPT = r"""
var done = arguments[arguments.length - 1];
(async function () {
    var sleep = function (ms) { return new Promise(function (r) { setTimeout(r, ms); }); };

    // Every request that is not a read is recorded with the API's answer
    var calls = [];
    var idIn = function (text) { try { var id = JSON.parse(text).id; return id === undefined ? null : id; } catch (e) { return null; } };
    var realFetch = window.fetch.bind(window);
    window.fetch = async function (input, init) {
        var method = ((init && init.method) || (input && input.method) || 'GET').toUpperCase();
        if (method === 'GET') return realFetch(input, init);
        var call = {method: method, url: (typeof input === 'string') ? input : ((input && input.url) || String(input)),
                    status: null, body: '', error: ''};
        calls.push(call);
        try {
            var res = await realFetch(input, init);
            try { var text = await res.clone().text(); call.id = idIn(text); call.body = text.slice(0, 400); } catch (e) {}
            call.status = res.status;
            return res;
        } catch (err) { call.error = String(err); throw err; }
    };
    var realOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url) {
        if (String(method).toUpperCase() !== 'GET') {
            var call = {method: String(method).toUpperCase(), url: String(url), status: null, body: '', error: ''};
            calls.push(call);
            this.addEventListener('loadend', function () {
                if (this.status) {
                    var text = String(this.responseText || '');
                    call.id = idIn(text); call.body = text.slice(0, 400); call.status = this.status;
                }
                else call.error = 'the request did not complete';
            });
        }
        return realOpen.apply(this, arguments);
    };

    var visible = function (el) { var r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    var setValue = function (el, value) {
        var proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype
            : el instanceof HTMLSelectElement ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
        Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);  // a framework's own setter is bypassed
        el.dispatchEvent(new Event('input', {bubbles: true}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
    };
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var tomorrow = new Date(Date.now() + 24 * 3600 * 1000);
    var day = tomorrow.getFullYear() + '-' + pad(tomorrow.getMonth() + 1) + '-' + pad(tomorrow.getDate());
    var textFor = function (el) {
        // The field's own example of what it accepts ("e.g. 2, 5") is the best value there is for it
        var example = (el.getAttribute('placeholder') || '').replace(/^\s*(e\.?g\.?|ex\.?|example)[:,]?\s*/i, '').trim();
        var text = example || 'QA check';
        var min = el.minLength > 0 ? el.minLength : 0, max = el.maxLength > 0 ? el.maxLength : 0;
        while (text.length < min) text += ' QA check';
        return max ? text.slice(0, max) : text;
    };
    var valueFor = function (el) {
        switch ((el.getAttribute('type') || 'text').toLowerCase()) {
            case 'email': return 'qa.check@example.com';
            case 'tel': return '5550100';
            case 'url': return 'https://example.com';
            case 'number': case 'range': return el.min !== '' ? el.min : (el.max !== '' && Number(el.max) < 1 ? el.max : '1');
            case 'date': return el.min || day;
            case 'time': return el.min || '10:00';
            case 'datetime-local': return el.min || (day + 'T10:00');
            case 'month': return el.min || day.slice(0, 7);
            case 'password': return 'Qa-check-1234';
            case 'color': return '#336699';
            default: return textFor(el);
        }
    };
    var fill = function (form, filled) {
        var radios = {};
        Array.from(form.elements).forEach(function (el) {
            if (filled.has(el) || el.disabled || el.readOnly || !visible(el) && el.type !== 'radio' && el.type !== 'checkbox') return;
            var tag = el.tagName.toLowerCase(), type = (el.getAttribute('type') || '').toLowerCase();
            if (tag === 'button' || tag === 'fieldset' || ['submit', 'button', 'reset', 'file', 'hidden', 'image'].indexOf(type) >= 0) return;
            filled.add(el);
            if (tag === 'select') {
                var option = Array.from(el.options).find(function (o) { return o.value !== '' && !o.disabled; });
                if (option) setValue(el, option.value);
            } else if (type === 'checkbox') {
                if (el.required && !el.checked) el.click();
            } else if (type === 'radio') {
                if (!radios[el.name] && !form.querySelector('input[type=radio][name="' + el.name + '"]:checked')) el.click();
                radios[el.name] = true;
            } else {
                setValue(el, valueFor(el));
            }
        });
    };
    var labelOf = function (form, submit) {
        var text = submit ? (submit.innerText || submit.value || '') : '';
        return (text.trim() || form.getAttribute('aria-label') || form.id || 'form').slice(0, 60);
    };

    var outcomes = [];
    var forms = Array.from(document.querySelectorAll('form')).filter(visible).slice(0, 3);
    for (var f = 0; f < forms.length; f++) {
        var form = forms[f];
        if (!form.isConnected) continue;  // an earlier submission replaced it
        var filled = new WeakSet();
        fill(form, filled);
        await sleep(80);   // fields that appear once another has a value
        fill(form, filled);
        await sleep(80);
        var submit = form.querySelector('button[type=submit], input[type=submit], button:not([type])');
        var result = {label: labelOf(form, submit), outcome: 'submitted', calls: [], invalid: [], cleanup: ''};
        outcomes.push(result);
        if (!submit) { result.outcome = 'no_submit_control'; continue; }
        var invalid = Array.from(form.elements).filter(function (el) { return el.willValidate && !el.checkValidity(); });
        if (invalid.length) {
            result.outcome = 'not_filled';
            result.invalid = invalid.map(function (el) { return el.name || el.id || el.tagName.toLowerCase(); }).slice(0, 6);
            continue;
        }
        var before = calls.length;
        submit.click();
        // Until every request is answered and none has followed for a moment (a submission can be several calls)
        var quiet = 0, seen = 0;
        for (var waited = 0; waited < 5000 && quiet < 400; waited += 100) {
            await sleep(100);
            var mine = calls.slice(before);
            var settled = mine.length && mine.every(function (c) { return c.status !== null || c.error; });
            quiet = (settled && mine.length === seen) ? quiet + 100 : 0;
            seen = mine.length;
        }
        result.calls = calls.slice(before);
        if (!result.calls.length) { result.outcome = 'no_request'; continue; }
        // What this check created is removed again
        for (var c = 0; c < result.calls.length; c++) {
            var call = result.calls[c];
            if (call.method !== 'POST' || !(call.status >= 200 && call.status < 300)) continue;
            var id = call.id;
            if (id === null || id === undefined) continue;  // an answer without an id created no record to remove
            try {
                var removed = await realFetch(call.url.replace(/\/+$/, '') + '/' + encodeURIComponent(id), {method: 'DELETE'});
                if (removed.status === 404 && result.cleanup === 'removed') continue;  // a later call on the same record
                result.cleanup = removed.ok ? 'removed' : 'not_removed';
            } catch (e) { result.cleanup = 'not_removed'; }
        }
    }
    window.fetch = realFetch;
    XMLHttpRequest.prototype.open = realOpen;
    done(outcomes);
})().catch(function (err) { done({error: String(err)}); });
"""


@dataclass
class FormCheck:
    """What using the page's forms showed. Defects fail the audit; warnings are reported with the verdict."""
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    outcomes: List[Dict[str, Any]] = field(default_factory=list)


def _request(call: Dict[str, Any]) -> str:
    parts = urlsplit(str(call.get("url") or ""))
    return f"{call.get('method')} {parts.path or call.get('url')}"


def verdict_from_outcomes(device: str, outcomes: List[Dict[str, Any]]) -> FormCheck:
    """A request the API refused, or that never arrived, is a defect. A form the check could not complete, and a test
    record it could not remove, are warnings."""
    check = FormCheck(outcomes=outcomes)
    for outcome in outcomes:
        form = f'the form "{outcome.get("label")}"'
        kind = outcome.get("outcome")
        if kind == "no_submit_control":
            check.warnings.append(f"[{device}] {form} has no submit control, so it was not exercised")
        elif kind == "not_filled":
            check.warnings.append(f"[{device}] the form check could not fill {form} "
                                  f"(fields: {', '.join(outcome.get('invalid') or [])}), so it was not submitted")
        elif kind == "no_request":
            check.warnings.append(f"[{device}] submitting {form} sent no request")
        for call in outcome.get("calls") or []:
            status = call.get("status")
            if call.get("error") or status is None:
                check.defects.append(f"[{device}] Submitting {form} failed: {_request(call)} did not complete "
                                     f"({call.get('error') or 'no answer'})")
            elif status >= 400:
                check.defects.append(f"[{device}] Submitting {form} failed: {_request(call)} answered {status}: "
                                     f"{str(call.get('body') or '').strip()[:400]}")
        if outcome.get("cleanup") == "not_removed":
            check.warnings.append(f"[{device}] the record created by submitting {form} could not be removed again")
    return check


@traced("qa.form_check")
def exercise_forms(driver, device: str) -> FormCheck:
    """Fills and submits each form on the page the driver has open. A check that could not run is a warning."""
    try:
        driver.set_script_timeout(SCRIPT_TIMEOUT_S)
        outcomes = driver.execute_async_script(_FORM_SCRIPT)
    except Exception as err:
        return FormCheck(warnings=[f"[{device}] the form check could not run: {type(err).__name__}: {str(err)[:200]}"])
    if isinstance(outcomes, dict):
        return FormCheck(warnings=[f"[{device}] the form check could not run: {outcomes.get('error')}"])
    return verdict_from_outcomes(device, list(outcomes or []))
