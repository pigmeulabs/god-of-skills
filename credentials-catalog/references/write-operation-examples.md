# Write Operation Examples

## Add example
Proposed entry:

```yaml
- name: "API Service"
  account:
    user: "api_user"
    key: "api_key"
    url: "https://api.example.com"
    type: "REST"
```

Confirmation wording:
Apply this new service entry to `/home/chico/projects/.globals/credentials.yaml`?

## Update example
Current match:

```yaml
- name: "Email Service"
  account:
    user: "email_user"
    password: "old_password"
    url: "smtp.example.com"
    port: 587
    type: "SMTP"
```

Proposed update:
- `password`: `old_password` -> `new_password`

Confirmation wording:
Confirm that I should update the fields above in `/home/chico/projects/.globals/credentials.yaml`.

## Remove example
Target entry:

```yaml
- name: "Legacy Redis"
  account:
    url: "localhost"
    port: 6379
    type: "Redis"
```

Confirmation wording:
Confirm that I should remove this service entry from `/home/chico/projects/.globals/credentials.yaml`.
