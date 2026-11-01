"""Resolve copied workspace media without modifying historical receipts."""
import json
import os
from pathlib import Path


def manifest_roots(data):
    """Read explicit relocation roots; unknown formats fail closed."""
    if not isinstance(data, dict):
        raise ValueError('Invalid workspace origin manifest')
    version = data.get('version')
    if type(version) is not int or version not in (1, 2):
        raise ValueError('Unsupported workspace origin manifest version')
    values = [data.get('original_root')] if version == 1 else data.get('reference_roots')
    if not isinstance(values, list) or not values:
        raise ValueError('Invalid workspace origin roots')
    roots = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise ValueError('Invalid workspace origin root')
        root = Path(value)
        if not root.is_absolute() or '..' in root.parts or root == Path(root.anchor):
            raise ValueError('Invalid workspace origin root')
        if root in roots:
            raise ValueError('Duplicate workspace origin root')
        roots.append(root)
    if (not isinstance(data.get('original_root'), str)
            or Path(data['original_root']) != roots[0]):
        raise ValueError('Invalid original workspace root')
    return roots


def reference_relative(reference, roots):
    """Require one unambiguous relative path across all declared roots."""
    path = Path(reference)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('Invalid image reference')
    matches = set()
    for root in roots:
        try:
            matches.add(path.relative_to(root))
        except ValueError:
            pass
    if len(matches) != 1:
        raise ValueError('External or ambiguous image reference')
    return matches.pop()


def resolve_study_image(reference):
    path = Path(reference)
    xdg = os.environ.get('XDG_DATA_HOME')
    if not xdg:
        return str(path)
    workspace = Path(xdg).parent
    manifest = workspace / 'study-workspace-origin.json'
    if not manifest.exists():
        return str(path)
    # Invalid provenance must not fall back to an original temporary file.
    try:
        data = json.loads(manifest.read_text())
        roots = manifest_roots(data)
        relative = reference_relative(path, roots + [workspace])
        resolved = (workspace / relative).resolve()
        resolved.relative_to(workspace.resolve())
        return str(resolved)
    except (ValueError, KeyError, TypeError, OSError):
        return ''
