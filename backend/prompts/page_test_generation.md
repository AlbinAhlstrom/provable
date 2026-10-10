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
Find controls the way a person does, by role and by the name read out for them: `page.get_by_role("button", name="Send order")`, `page.get_by_label("Email")`, `page.get_by_text("Sold out")`. Two things below show which roles, names and texts exist. "The page as it opens" lists what a browser read out from the opened page, each line a role and the name it carries: take a name from there as it is written. The page's source shows the rest: what is behind a menu or in a dialog that was closed, how a name is built from a record's values, and which record the page shows when it opens (the newest one, a chosen one, a list of all). A name built from values (`"Row 2, column 3, empty"`, `"Table 4, free"`) is matched with the values your Given produces. A name you give matches every control whose name contains it, so give the whole name with `exact=True`; leave it out only when you mean to match a part. Use a CSS selector only for something that has no role, name or text.

## The app's API
A collection is created, listed and read under `/api/<collection>`, and its actions are the public methods of its class; `app` calls them for you. Field names, their defaults and the actions' parameters:

{api}

## The page as it opens
What a browser read out when the page opened on an app holding only the records it starts with. A long run of like controls is shown by its first few and a line that counts the rest and gives the forms their names take.

```
{rendered}
```

## The page's source
{page}

## Rules for the test
1. Write ONE pytest module that proves the rule below: arrange (Given), act on the page (When), assert (Then).
2. Prove the rule in the simplest situation that shows it, in which nothing but this rule decides the outcome. A When that also finishes the whole (the last free place is taken, the last open item is dealt with, an order's only line is removed) brings the rules about finishing into play, so arrange enough that the whole is still unfinished afterwards, unless finishing is what the rule is about. Assert what the rule's Then states and stop there: a field, a counter or a log the rule does not name belongs to another rule. Above each assertion, write a short comment that says why the expected result follows from the records you arranged. Where it follows by counting or calculating (how many items are left, which positions touch another, a sum, a limit worked out from two sizes), have the test work it out from those records in code and use the result, in the names it looks for as well as in what it expects.
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