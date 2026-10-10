import gc
import os

import pytest
from PySide6.QtCore import QCoreApplication, QEvent, QTimer
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
    # Dispose test-owned windows before draining events. Otherwise timers on
    # hundreds of still-live widgets can run against already-closed test DBs
    # or continuously replenish the event queue during session teardown.
    for widget in app.topLevelWidgets():
        for timer in widget.findChildren(QTimer):
            timer.stop()
        widget.close()
        widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
    app.quit()
    app.processEvents()
    _TEST_QAPP = None
    gc.collect()
