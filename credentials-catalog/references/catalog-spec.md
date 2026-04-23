# Credentials Catalog Specification

## Canonical path
- Catalog file: `/home/chico/projects/.globals/credentials.yaml`
- Gitignore target: `/home/chico/projects/.globals/credentials.yaml`

## Canonical structure

```yaml
services:
  - name: "Database Service"
    account:
      user: "db_user"
      password: "db_password"
      url: "localhost"
      port: 5432
      type: "PostgreSQL"
```

## Allowed fields
Each service entry must have:
- `name`
- `account`

Inside `account`, these fields may appear when applicable:
- `user`
- `email`
- `key`
- `password`
- `url`
- `port`
- `type`

Do not force fields that are not applicable.

## Empty file shape
When creating the file from scratch, initialize it as:

```yaml
services: []
```

## Normalization rules
- Preserve user-provided values exactly.
- Preserve service names exactly in storage.
- Use YAML safe serialization.
- Keep the file human-readable.
