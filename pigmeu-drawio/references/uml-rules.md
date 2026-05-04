# UML Rules

## Use case diagrams

- Use stick-figure actors outside the system boundary.
- Use ellipses for use cases inside the boundary.
- Use simple association lines between actors and use cases.
- Use dashed arrows for `include` and `extend` relationships.
- Label system boundary with the product or subsystem name.

## Class diagrams

- Use class boxes with compartments: class name, attributes, methods.
- Use open triangle arrowheads for inheritance/generalization.
- Use diamond markers for aggregation/composition when semantically correct.
- Use multiplicities near association endpoints.
- Avoid implementation detail unless explicitly requested.

## Sequence diagrams

- Time flows top to bottom.
- Participants/lifelines are ordered left to right by responsibility.
- Use activation bars for processing intervals.
- Use solid arrows for calls and dashed arrows for returns.
- Keep message labels as verb phrases.

## Activity diagrams

- Use rounded rectangles for actions.
- Use diamonds for decisions/merges.
- Use bars for fork/join when parallelism matters.
- Label branches clearly.

## State machine diagrams

- Include initial and final states when applicable.
- Label transitions as `event [guard] / action` when useful.
- Group nested states only if the model benefits from hierarchy.
