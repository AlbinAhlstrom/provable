You wrote the plan below: what a product is, the actions it has and the rules it obeys. Before anything is built from it, the rules were checked against the plan itself, and some cannot hold as written. You write those rules again. Everything else of the plan stays as it is.

## The plan
What an action does is decided by its `does`, and that stays as written. Each entry of `situations` is `name = what it is in a person's words: the values it holds`, and a rule the records obey starts from one of them.

```json
{contract}
```

## The rules that cannot hold
Each was worked through: its situation was taken, what the plan says its action does was carried out on exactly those records, to the end, and the result was compared with the rule's Then.

{named_rules}

## Your task
For each rule above, find out which of these it is, and write it again so that it holds.

- **The situation is too small for what the rule is about.** The rule is about one step, and in its situation that step also finishes the whole (the last free place is taken, the last hidden item is opened, the only line is removed), so what `does` says of finishing happens too. Give the rule a situation of its own, large enough that the whole is still unfinished after the step, and state in `then` exactly what the step leaves there.
- **The rule is about what the step brings about.** Then its `then` states everything `does` says happens from that situation, the finishing included, each field and value.
- **The When does not fit the situation.** The rule needs something to have happened first (a finished whole, a record already taken). That is a situation's to hold: give the rule a situation in which it already has, and a `when` that is the action alone with the value of every parameter.
- **Two rules ask for different results from the same situation and action.** Keep the one that states what `does` says, and write the other again as above, or from a situation of its own in which its result is the true one.

A situation you add:
- has a new name in `snake_case`; the situations the plan has are other rules' to start from and stay as they are.
- is written whole, in the form of the plan's own: every field that differs from its starting value, and for a list of parts how many there are and, by position, which of them hold what. A value worked out from others (how many neighbours hold something, a total) is the number that follows from the rest. Nothing is left to chance or to the present moment.
- is as small as shows the rule.

Before you answer, go through each rule you wrote once more as it was checked: from its situation, carry out its action's `does` step by step to the end, count what a closing condition speaks of ("when every ... is ...", "once none is left"), and see that `then` states what you arrive at.

Answer with JSON:
- `situations`: the situations you add, each as `name = what it is in a person's words: the values it holds`. An empty list when the rules need none.
- `rules`: each rule above, written again, with its `title` exactly as it stands and `given`, `when`, `then`, `sees` and `plain` in the form the plan's rules have: `given` the name of a situation and after it only what differs; `when` the action with the value of every parameter (for a rule of the page alone, the gesture and the part it is done on); `then` the fields and values afterwards, or the refusal by name, or "nothing changes" (empty for a rule of the page alone); `sees` what the page then reads out, in the names of `read_out`; `plain` the rule as the person who uses the product would say it, as Given, When, Then.
