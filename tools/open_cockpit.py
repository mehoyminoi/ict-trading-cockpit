"""Open an existing retained Study workspace through the ordinary application."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ict_cockpit.main import main

if __name__ == '__main__':
    raise SystemExit(main(require_workspace=True))
