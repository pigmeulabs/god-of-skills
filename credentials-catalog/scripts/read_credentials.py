#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required", file=sys.stderr)
    raise

DEFAULT_PATH = Path('/home/chico/projects/.globals/credentials.yaml')
LOOKUP_FIELDS = ('user', 'email', 'url', 'port', 'type')


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


def normalize(text):
    return ' '.join(str(text).strip().lower().split())


def score_service(service, query):
    query_n = normalize(query)
    name = service.get('name', '')
    name_n = normalize(name)
    if name == query:
        return 100
    if name_n == query_n:
        return 90
    account = service.get('account', {}) or {}
    for field in LOOKUP_FIELDS:
        value = account.get(field)
        if value is None:
            continue
        if str(value) == query:
            return 80
    if query_n in name_n:
        return 60
    return 0


def main():
    parser = argparse.ArgumentParser(description='Read and search the credentials catalog')
    parser.add_argument('--path', default=str(DEFAULT_PATH))
    parser.add_argument('--service', help='Service name or lookup term')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    path = Path(args.path)
    data = load_catalog(path)
    services = data.get('services', [])

    result = services
    if args.service:
        ranked = []
        for svc in services:
            score = score_service(svc, args.service)
            if score > 0:
                ranked.append((score, svc))
        ranked.sort(key=lambda item: (-item[0], item[1].get('name', '')))
        result = [svc for _, svc in ranked]

    payload = {
        'path': str(path),
        'count': len(result),
        'services': result,
    }
    if args.pretty:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(payload, ensure_ascii=False))


if __name__ == '__main__':
    main()
