from PySide6.QtWidgets import QApplication

from ict_cockpit.gui.study_find_widget import StudyFindWidget


def test_study_find_widget_can_be_constructed() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    assert widget is not None

def test_study_find_widget_builds_study_find() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    widget.instrument_input.setText("mnq")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("London low raid")
    widget.observation_input.setPlainText(
        "Bullish displacement followed the sweep."
    )
    widget.available_move_input.setValue(74.5)
    widget.notes_input.setPlainText("Clean example.")

    study_find = widget.build_study_find()

    assert study_find.instrument == "MNQ"
    assert study_find.session == "NYAM"
    assert study_find.pattern_name == "London low raid"
    assert study_find.observation == (
        "Bullish displacement followed the sweep."
    )
    assert study_find.available_move_handles == 74.5
    assert study_find.notes == "Clean example."

def test_study_find_widget_generates_summary() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("London low raid")
    widget.observation_input.setPlainText(
        "Bullish displacement followed the sweep."
    )
    widget.available_move_input.setValue(74.5)

    rendered = widget.generate_summary()

    assert "Asset: MNQ" in rendered
    assert "Session: NYAM" in rendered
    assert "Pattern: London low raid" in rendered
    assert "74.50 handles" in rendered

def test_study_find_widget_includes_image_path() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("London low raid")
    widget.observation_input.setPlainText(
        "Bullish displacement followed the sweep."
    )

    widget.image_paths = [
    "/tmp/chart.png",
    ]

    study_find = widget.build_study_find()

    assert study_find.image_path == "/tmp/chart.png"

def test_study_find_widget_reuses_same_id() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    widget.instrument_input.setText("MNQ")
    widget.session_input.setText("NYAM")
    widget.pattern_input.setText("Pattern")
    widget.observation_input.setPlainText(
        "Observation"
    )

    first = widget.build_study_find()
    second = widget.build_study_find()

    assert first.id == second.id

def test_study_find_widget_tracks_multiple_image_paths() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    widget.image_paths = [
        "/tmp/chart-1.png",
        "/tmp/chart-2.png",
    ]

    widget.image_list.addItems(
        widget.image_paths
    )

    assert widget.image_list.count() == 2
    assert widget.image_paths == [
        "/tmp/chart-1.png",
        "/tmp/chart-2.png",
    ]

def test_study_find_widget_removes_selected_image() -> None:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    widget = StudyFindWidget()

    widget.image_paths = [
        "/tmp/chart-1.png",
        "/tmp/chart-2.png",
    ]

    widget.image_list.addItems(
        widget.image_paths
    )

    widget.image_list.setCurrentRow(0)

    widget.remove_selected_image()

    assert widget.image_paths == [
        "/tmp/chart-2.png"
    ]

    assert widget.image_list.count() == 1