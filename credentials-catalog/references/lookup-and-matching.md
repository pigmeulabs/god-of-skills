# Lookup And Matching Rules

## Matching priority
1. exact `name`
2. case-insensitive normalized `name`
3. exact match on `user`, `email`, `url`, `port`, or `type`
4. partial contains match on `name`

## Disambiguation
If more than one service matches:
- list the candidate service names;
- include one distinguishing field such as `url`, `type`, or `user`;
- ask which one should be used.

## Read output policy
Return only the fields needed for the current task when possible.
Examples:
- database login task: `user`, `password`, `url`, `port`, `type`
- api call task: `key`, `url`, `type`
- smtp task: `user`, `password`, `url`, `port`, `type`

If a needed field is absent, state that the field is missing from the catalog.
