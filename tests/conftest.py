import gc
import os

import pytest
from PySide6.QtWidgets import QApplication


# Keep a strong session-lifetime reference to the Qt application. Individual
# GUI tests historically call QApplication.instance() as needed, but relying on
# temporary Python references becomes fragile as the suite creates and destroys
# hundreds of PySide widgets/event filters.
_TEST_QAPP: QApplication | None = None


@pytest.fixture(scope="session", autouse=True)
def qt_application() -> QApplication:
    global _TEST_QAPP

    # Use Qt's headless platform when the caller has not selected a platform.
    # This still allows local developers to override QT_QPA_PLATFORM explicitly.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    _TEST_QAPP = app

    yield app

    # Tear Qt down while Python classes/slots are still alive. Leaving the
    # QApplication until interpreter shutdown can produce misleading slot
    # lookup diagnostics after pytest has already reported success.
    app.closeAllWindows()
    app.processEvents()
    app.quit()
    app.processEvents()
    _TEST_QAPP = None
    gc.collect()
