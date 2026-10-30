"""Resolve copied workspace media without modifying historical receipts."""
import json
import os
from pathlib import Path


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
        origin = Path(data['original_root'])
        if data['version'] != 1 or not origin.is_absolute() or '..' in path.parts:
            return ''
        try:
            relative = path.relative_to(origin)
        except ValueError:
            relative = path.relative_to(workspace)
        resolved = (workspace / relative).resolve()
        resolved.relative_to(workspace.resolve())
        return str(resolved)
    except (ValueError, KeyError, TypeError, OSError):
        return ''
