import os

import pytest
from PySide6.QtWidgets import QApplication


# Keep a strong process-lifetime reference to the Qt application. Individual
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

    # Do not explicitly destroy QApplication here. Qt owns process-level native
    # resources and teardown is safest when Python exits after the test session.
