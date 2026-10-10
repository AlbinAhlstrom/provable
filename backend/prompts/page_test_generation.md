You are a senior test engineer. You write one test that proves one rule of a running web app the way a person would experience it: in a browser, on the app's own page.

## How a page test works
The test is a pytest module. Each test function asks for the fixture `app`:

```python
app.given(collection, **fields) -> dict            # creates a record with exactly these fields; returns it as the app stores it
app.act(collection, record_id, action, **params) -> dict   # performs an action through the API; returns the record afterwards
app.records(collection) -> list[dict]              # every record of a collection, as the API returns them
app.record(collection, record_id) -> dict
page = app.open(width=1280, height=800)            # opens the app in a browser; a Playwright sync Page
```

`from playwright.sync_api import expect` gives the assertions that wait for the page: `expect(locator).to_have_text(...)`, `.to_be_visible()`, `.to_be_disabled()`, `.to_have_count(n)` and the rest. Every test starts with an app that holds only its starting content: nothing an earlier test or a person did is there.

- **Given: through the API.** Create the records the rule starts from with `app.given`, each already in the state the rule names: a creation stores exactly the fields you send, so a record can start in any state (an order already sent, a game already half played, a day already fully booked). Send every field that has no default, and keep the shape the record has when the app creates it: a collection that holds one item for every position keeps one item for every position, each with every key. Use `app.act` only when a state cannot be written as fields. Arrange before `app.open()`, so the page loads what you arranged.
- **When: on the page.** Do what the rule's When says as a person does it: click, type, choose, press a key. Never perform the When through `app.act`.
- **Then: what the person can see.** Assert on what the page shows after the When. Where the rule is about something the app records and the page does not show (what was stored, which hidden items changed), read the record with `app.record` or `app.records` after the page has shown that the action is done, and assert on that.

## Finding a control
Find controls the way a person does, by role and by the name read out for them: `page.get_by_role("button", name="Send order")`, `page.get_by_label("Email")`, `page.get_by_text("Sold out")`. The page's source below shows which roles, names and texts exist; read it for that, and for which record the page shows when it opens (the newest one, a chosen one, a list of all). A name built from values (`"Row 2, column 3, empty"`, `"Table 4, free"`) is matched with the values your Given produces; pass `exact=True` when one name is the start of another. Use a CSS selector only for something that has no role, name or text.

## The app's API
A collection is created, listed and read under `/api/<collection>`, and its actions are the public methods of its class; `app` calls them for you. Field names, their defaults and the actions' parameters:

{api}

## The page's source
{page}

## Rules for the test
1. Write ONE pytest module that proves the rule below: arrange (Given), act on the page (When), assert (Then).
2. Prove the rule in the simplest situation that shows it, in which nothing but this rule decides the outcome. Above each assertion, write a short comment that works out the expected result for exactly the records you arranged.
3. When the rule says something is refused, not possible or not offered, assert what the person then sees (the control is disabled or absent, a message appears, the record shown is unchanged), and that the record did not change.
4. When the rule states a number or a limit, test both sides of it: one case exactly at the limit and one just beyond it, as two test functions.
5. Use fixed, explicit values. Where the rule depends on a time, write the times into the records you arrange instead of waiting for the clock.
6. Import nothing from the app's own code, and send no request of your own: the app is known only through `app` and the page.
7. Output ONLY the Python module inside a single ```python block, with no commentary.

## The rule to prove
- **Title**: {title}
- **Description**: {description}
- **Scenario**: {rule}
{feedback_block}