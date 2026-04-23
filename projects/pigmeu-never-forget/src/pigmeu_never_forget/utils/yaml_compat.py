"""YAML compatibility wrapper with optional PyYAML and local fallback."""

from __future__ import annotations

from typing import Any

try:
    import yaml as _pyyaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    _pyyaml = None


def safe_dump(data: Any, sort_keys: bool = False) -> str:
    """Dump YAML using PyYAML when available, otherwise fallback serializer."""
    if _pyyaml is not None:
        return str(_pyyaml.safe_dump(data, sort_keys=sort_keys))
    return _fallback_safe_dump(data, sort_keys=sort_keys)


def safe_load(text: str) -> Any:
    """Load YAML using PyYAML when available, otherwise fallback parser."""
    if _pyyaml is not None:
        return _pyyaml.safe_load(text)
    return _fallback_safe_load(text)


def _fallback_safe_dump(data: Any, sort_keys: bool = False) -> str:
    return _dump_value(data, indent=0, sort_keys=sort_keys).rstrip() + "\n"


def _fallback_safe_load(text: str) -> Any:
    lines = [line.rstrip("\n") for line in text.splitlines()]
    filtered = [line for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not filtered:
        return None
    value, next_index = _parse_block(filtered, index=0, indent=0)
    if next_index != len(filtered):
        raise ValueError("Unable to parse full YAML payload.")
    return value


def _dump_value(value: Any, indent: int, sort_keys: bool) -> str:
    prefix = " " * indent
    if isinstance(value, dict):
        items = value.items()
        if sort_keys:
            items = sorted(items)
        lines: list[str] = []
        for key, nested_value in items:
            if isinstance(nested_value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_dump_value(nested_value, indent + 2, sort_keys))
            else:
                lines.append(f"{prefix}{key}: {_format_scalar(nested_value)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                rendered = _dump_value(item, indent + 2, sort_keys).splitlines()
                first = rendered[0] if rendered else ""
                lines.append(f"{prefix}- {first.strip()}")
                lines.extend(f"{' ' * (indent + 2)}{line}" for line in rendered[1:])
            else:
                lines.append(f"{prefix}- {_format_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{_format_scalar(value)}"


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if text == "" or any(char in text for char in [":", "#", "\n"]) or text.strip() != text:
        return f'"{text}"'
    return text


def _parse_block(lines: list[str], index: int, indent: int) -> tuple[Any, int]:
    if lines[index].startswith(" " * indent + "- "):
        return _parse_list(lines, index, indent)
    return _parse_dict(lines, index, indent)


def _parse_dict(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(f"Unexpected indentation at line: {line}")
        stripped = line.strip()
        if stripped.startswith("- "):
            break
        key, separator, remainder = stripped.partition(":")
        if separator == "":
            raise ValueError(f"Invalid mapping line: {line}")
        if remainder.strip() == "":
            if index + 1 >= len(lines) or _indent_of(lines[index + 1]) <= indent:
                result[key] = {}
                index += 1
                continue
            nested, index = _parse_block(lines, index + 1, indent + 2)
            result[key] = nested
            continue
        result[key] = _parse_scalar(remainder.strip())
        index += 1
    return result, index


def _parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        line = lines[index]
        current_indent = _indent_of(line)
        if current_indent < indent:
            break
        if current_indent != indent:
            raise ValueError(f"Unexpected indentation at line: {line}")
        stripped = line.strip()
        if not stripped.startswith("- "):
            break
        item_content = stripped[2:].strip()
        if item_content == "":
            nested, index = _parse_block(lines, index + 1, indent + 2)
            result.append(nested)
            continue
        if ":" in item_content and not item_content.startswith('"') and not item_content.startswith("'"):
            item, index = _parse_inline_mapping_item(lines, index, indent, item_content)
            result.append(item)
            continue
        result.append(_parse_scalar(item_content))
        index += 1
    return result, index


def _parse_inline_mapping_item(
    lines: list[str],
    index: int,
    indent: int,
    item_content: str,
) -> tuple[dict[str, Any], int]:
    key, _, remainder = item_content.partition(":")
    item: dict[str, Any] = {}
    if remainder.strip():
        item[key] = _parse_scalar(remainder.strip())
        index += 1
    else:
        nested, index = _parse_block(lines, index + 1, indent + 2)
        item[key] = nested
    while index < len(lines):
        line = lines[index]
        current_indent = _indent_of(line)
        if current_indent < indent + 2:
            break
        if current_indent != indent + 2:
            raise ValueError(f"Unexpected indentation at line: {line}")
        stripped = line.strip()
        key, separator, remainder = stripped.partition(":")
        if separator == "":
            raise ValueError(f"Invalid mapping line: {line}")
        if remainder.strip() == "":
            nested, index = _parse_block(lines, index + 1, indent + 4)
            item[key] = nested
        else:
            item[key] = _parse_scalar(remainder.strip())
            index += 1
    return item, index


def _parse_scalar(value: str) -> Any:
    if value in {"null", "Null", "NULL"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))
