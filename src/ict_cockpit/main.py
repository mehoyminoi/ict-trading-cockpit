import sys

from PySide6.QtWidgets import QApplication

from ict_cockpit.database.bootstrap import open_default_application_database
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.gui.main_window import MainWindow
from ict_cockpit.database.study_find_repository import StudyFindRepository


def main() -> int:
    app = QApplication(sys.argv)

    connection = open_default_application_database()
    tda_repository = TDARepository(connection)

    tda_repository = TDARepository(connection)
    study_find_repository = StudyFindRepository(connection) 

    window = MainWindow(
        tda_repository,
        study_find_repository,
    )
    window.show()

    exit_code = app.exec()

    connection.close()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())