#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required", file=sys.stderr)
    raise

DEFAULT_PATH = Path('/home/chico/projects/.globals/credentials.yaml')
ALLOWED_FIELDS = {'user', 'email', 'key', 'password', 'url', 'port', 'type'}


def load_catalog(path: Path):
    if not path.exists():
        return {'services': []}
    content = path.read_text(encoding='utf-8').strip()
    if not content:
        return {'services': []}
    data = yaml.safe_load(content) or {'services': []}
    if not isinstance(data, dict) or 'services' not in data or not isinstance(data['services'], list):
        raise ValueError('Catalog must be a YAML object with top-level key services as a list')
    return data


def save_catalog(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding='utf-8')


def normalize_service_name(name: str) -> str:
    return ' '.join(name.strip().lower().split())


def find_index(services, name: str):
    target = normalize_service_name(name)
    matches = [i for i, svc in enumerate(services) if normalize_service_name(svc.get('name', '')) == target]
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f'Multiple services match the name {name!r}')
    return matches[0]


def parse_account_args(values):
    account = {}
    for item in values or []:
        if '=' not in item:
            raise ValueError(f'Invalid account field {item!r}. Use key=value format.')
        key, value = item.split('=', 1)
        key = key.strip()
        if key not in ALLOWED_FIELDS:
            raise ValueError(f'Unsupported account field {key!r}')
        if key == 'port':
            try:
                account[key] = int(value)
            except ValueError as exc:
                raise ValueError('port must be an integer') from exc
        else:
            account[key] = value
    return account


def main():
    parser = argparse.ArgumentParser(description='Add, update, or remove credentials catalog entries')
    parser.add_argument('operation', choices=['add', 'update', 'remove'])
    parser.add_argument('--path', default=str(DEFAULT_PATH))
    parser.add_argument('--name', required=True)
    parser.add_argument('--field', action='append', help='account field in key=value format')
    args = parser.parse_args()

    path = Path(args.path)
    data = load_catalog(path)
    services = data['services']

    if args.operation == 'add':
        if find_index(services, args.name) is not None:
            raise ValueError(f'Service {args.name!r} already exists')
        account = parse_account_args(args.field)
        services.append({'name': args.name, 'account': account})
    elif args.operation == 'update':
        index = find_index(services, args.name)
        if index is None:
            raise ValueError(f'Service {args.name!r} was not found')
        account = services[index].setdefault('account', {})
        account.update(parse_account_args(args.field))
    elif args.operation == 'remove':
        index = find_index(services, args.name)
        if index is None:
            raise ValueError(f'Service {args.name!r} was not found')
        services.pop(index)

    save_catalog(path, data)
    print(f'{args.operation} succeeded for {args.name}')


if __name__ == '__main__':
    main()
