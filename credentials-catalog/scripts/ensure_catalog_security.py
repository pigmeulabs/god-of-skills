#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import pwd
import stat

try:
    import yaml
except ImportError:
    raise

DEFAULT_PATH = Path('/home/chico/projects/.globals/credentials.yaml')
DEFAULT_GITIGNORE = Path('/home/chico/projects/.gitignore')
IGNORE_LINE = '/home/chico/projects/.globals/credentials.yaml'


def ensure_catalog(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    created = False
    if not path.exists():
        path.write_text(yaml.safe_dump({'services': []}, sort_keys=False), encoding='utf-8')
        created = True
    path.chmod(0o600)
    return created


def ensure_gitignore(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(line + '\n', encoding='utf-8')
        return True, True
    content = path.read_text(encoding='utf-8').splitlines()
    if line in content:
        return False, True
    with path.open('a', encoding='utf-8') as handle:
        if content and content[-1] != '':
            handle.write('\n')
        handle.write(line + '\n')
    return True, True


def owner_name(path: Path):
    uid = path.stat().st_uid
    return pwd.getpwuid(uid).pw_name


def main():
    parser = argparse.ArgumentParser(description='Ensure catalog file exists, has mode 600, and is ignored by git')
    parser.add_argument('--path', default=str(DEFAULT_PATH))
    parser.add_argument('--gitignore', default=str(DEFAULT_GITIGNORE))
    args = parser.parse_args()

    catalog_path = Path(args.path)
    gitignore_path = Path(args.gitignore)
    created = ensure_catalog(catalog_path)
    gitignore_updated, gitignore_exists = ensure_gitignore(gitignore_path, IGNORE_LINE)
    mode = stat.S_IMODE(catalog_path.stat().st_mode)
    owner = owner_name(catalog_path)
    payload = {
        'catalog_path': str(catalog_path),
        'catalog_created': created,
        'mode': oct(mode),
        'owner': owner,
        'owner_ok': owner in {'chico', 'root'},
        'gitignore_path': str(gitignore_path),
        'gitignore_updated': gitignore_updated,
        'gitignore_exists': gitignore_exists,
    }
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == '__main__':
    main()
