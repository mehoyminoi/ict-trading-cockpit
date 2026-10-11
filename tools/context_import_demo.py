"""E6 manual acceptance sandbox: synthetic exports and a separate local DB."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import QDate, QDateTime
from PySide6.QtWidgets import QApplication
from ict_cockpit.database.connection import create_connection
from ict_cockpit.database.schema import initialize_schema
from ict_cockpit.database.tda_repository import TDARepository
from ict_cockpit.database.study_find_repository import StudyFindRepository
from ict_cockpit.gui.main_window import MainWindow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, help="Reuse a previous E6 sandbox to check restart")
    args = parser.parse_args()
    directory = args.data_dir or Path(tempfile.mkdtemp(prefix="ict-e6-"))
    directory.mkdir(parents=True, exist_ok=True)
    rows = [
        {"title": "Fixture release", "country": "USD", "date": "2026-10-06T08:30:00-04:00",
         "impact": "High", "forecast": "2%", "previous": "1%"},
        {"title": "Fixture bank holiday", "country": "AUD", "date": "2026-10-04T16:00:00-04:00",
         "impact": "Holiday", "forecast": "", "previous": ""},
        {"title": "Fixture release", "country": "USD", "date": "2026-10-06T08:31:00-04:00",
         "impact": "High", "forecast": "2%", "previous": "1.5%"},
    ]
    for name, contents in (("fixture.json", rows), ("revised.json", [{**x, "previous": "revised"} for x in rows]),
                           ("wrong-week.json", [{**rows[0], "date": "2026-10-13T08:30:00-04:00"}]),
                           ("malformed.json", [{"title": "Fixture incomplete"}])):
        path = directory / name
        if not path.exists():
            path.write_text(json.dumps(contents), encoding="utf-8")
    print(f"E6 sandbox: {directory.resolve()}", flush=True)
    print(f"Restart: python tools/context_import_demo.py --data-dir {directory.resolve()}", flush=True)
    app = QApplication(sys.argv[:1])
    conn = create_connection(directory / "demo.db")
    initialize_schema(conn)
    window = MainWindow(TDARepository(conn), StudyFindRepository(conn))
    plan = window.trade_plan_widget
    plan.section_list.setCurrentRow(plan._section_ids.index("process"))
    plan.process_tabs.setCurrentWidget(plan.context_import_widget)
    plan.context_import_widget.week_start.setDate(QDate(2026, 10, 4))
    plan.process_run_launcher_widget.market_time_edit.setDateTime(QDateTime.fromString("2026-10-06T10:15:00", "yyyy-MM-ddTHH:mm:ss"))
    window.setWindowTitle("E6 acceptance sandbox — synthetic records / separate database")
    window.show()
    result = app.exec()
    conn.close()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
