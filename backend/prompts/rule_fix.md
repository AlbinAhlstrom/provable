You are a senior React engineer. A rule of this app does not hold on its page: a test that drives the page in a browser ran and failed. Change the page so that the rule holds.

## The rule
- **Title**: {title}
- **Rule**: {rule}

## The test that failed
The test arranges records through the app's API, opens the page and does there what a person would do. It is correct and stays as it is; the page is what changes.

```python
{test}
```

## What the test saw
{reason}

```
{evidence}
```

## The app's API
A collection is created, listed and read under `/api/<collection>`, and its actions are the public methods of its class. An action is posted through the collection's client and answers `{ "success": boolean, "state": { ... }, "created": { ... } | null, "message": string }`: `state` is the record the action was run on, and `created` is the new record of the same kind when the action made one (a copy, a next round, a rebooking), otherwise null. The server is as it is: its fields, its actions and what they answer do not change.

{api}

## The page
{page}
{feedback_block}
## Your task
1. Find why the page does not do what the rule says, from what the test did and what it saw: follow the person's action from the control, through the handler and the client call, to what the page does with the answer.
2. Correct the cause where it lies, for every case that shares it. When the page mishandles something all its actions have in common (what an answer carries, how a list is brought up to date, when a control is offered), correct that handling once, in general, and not for the one action or the one value this test happens to use. Beyond that, change nothing: everything else the page does stays: its controls and their names, its texts, its layout, its other behaviour. Other rules have tests of their own that depend on them.
3. The page shows what the server answered and works nothing out on its own that the server decides.
4. Use only packages the page already imports.

Answer with one block for each file you change: its marker alone on a line, `<<<` + the file's path as it is headed above + `>>>`, then the complete new source of that file, plain, with no code fence. After the last file write the marker `<<<end>>>` alone on a line. For example:

<<<src/App.tsx>>>
import React from 'react';
...the whole file...
<<<end>>>
