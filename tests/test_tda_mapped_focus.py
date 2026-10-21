from dataclasses import replace
from PySide6.QtCore import QSettings, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from ict_cockpit.default_process import build_default_process_blueprint
from ict_cockpit.gui.tda_station_runner_widget import TDAStationRunnerWidget


def test_map_and_editor_share_state_without_navigation_completion():
    runner = TDAStationRunnerWidget(build_default_process_blueprint())
    first = runner.current_station_id
    runner.observation_input.setPlainText('Monthly draw overhead')
    assert 'Monthly draw overhead' in runner.mapped_buttons[first].text()
    second = runner._current_deck().stations[1].id
    runner.mapped_buttons[second].click()
    assert runner.current_station_id == second
    assert not runner.session.observation_for(first).completed
    runner.full_deck_button.click()
    runner.open_station_from_deck(first)
    assert runner.observation_input.toPlainText() == 'Monthly draw overhead'
    assert runner.view_tabs.currentWidget() is runner.focus_page
    assert 'Top left' in runner.tradingview_label.text()
    runner.close()


def test_slot_uses_position_not_definition_order_and_ignores_missing_slot():
    blueprint = build_default_process_blueprint()
    mode = next(m for m in blueprint.modes if m.id == 'tda')
    deck = mode.decks[0]
    first, second, *rest = deck.stations
    swapped = replace(deck, stations=(replace(first,layout_row=0,layout_column=1),
        replace(second,layout_row=0,layout_column=0),*rest))
    mode2 = replace(mode,decks=(swapped,*mode.decks[1:]))
    runner = TDAStationRunnerWidget(replace(blueprint,modes=tuple(mode2 if m.id=='tda' else m for m in blueprint.modes)))
    runner.open_mapped_slot(1)
    assert runner.current_station_id == second.id
    runner.open_mapped_slot(2)
    assert runner.current_station_id == first.id
    runner.open_mapped_slot(99)
    assert runner.current_station_id == first.id
    runner.close()


def test_numeric_typing_is_not_navigation_and_alt_slot_is_scoped():
    runner = TDAStationRunnerWidget(build_default_process_blueprint())
    runner.show()
    runner.activateWindow()
    runner.observation_input.setFocus()
    QApplication.processEvents()
    first = runner.current_station_id
    QTest.keyClicks(runner.observation_input,'1234')
    assert runner.current_station_id == first
    assert runner.observation_input.toPlainText() == '1234'
    QTest.keyClick(runner.observation_input,Qt.Key.Key_2,Qt.KeyboardModifier.AltModifier)
    assert runner.current_station_id == runner._current_deck().stations[1].id
    assert runner.session.observation_for(first).observation == '1234'
    assert not runner.session.observation_for(first).completed
    runner.close()


def test_splitter_restore_and_completion_moves_map_to_next_deck(tmp_path):
    settings = QSettings(str(tmp_path/'layout.ini'),QSettings.Format.IniFormat)
    runner = TDAStationRunnerWidget(build_default_process_blueprint())
    runner.configure_workspace_settings(settings)
    runner.resize(1200,800)
    runner.show()
    QApplication.processEvents()
    runner.focus_splitter.setSizes([450,650])
    runner._save_splitter()
    before = runner.focus_splitter.saveState()
    restored = TDAStationRunnerWidget(build_default_process_blueprint())
    restored.configure_workspace_settings(settings)
    assert restored.focus_splitter.saveState() == before
    first_deck = runner._tda_decks[0]
    runner.select_station(first_deck.stations[-1].id)
    runner.complete_and_continue()
    assert runner._current_deck().id == runner._tda_decks[1].id
    assert set(runner.mapped_buttons) == {s.id for s in runner._tda_decks[1].stations}
    assert runner.session.observation_for(first_deck.stations[-1].id).completed
    runner.close()
    restored.close()


def test_demo_restores_work_station_and_layout_without_run(tmp_path):
    import pytest
    from tools.tda_mapped_focus_demo import open_demo
    trial = tmp_path/'trial'
    connection,window = open_demo(trial)
    runner = window.runner
    runner.open_mapped_slot(2)
    station_id = runner.current_station_id
    runner.observation_input.setPlainText('Retained factual observation')
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()
    connection,window = open_demo(trial)
    try:
        assert window.runner.current_station_id == station_id
        assert window.runner.observation_input.toPlainText() == 'Retained factual observation'
        assert not window.runner.session.observation_for(station_id).completed
        assert connection.execute('SELECT count(*) FROM trading_session_run').fetchone()[0] == 0
    finally:
        window.close()
        window.deleteLater()
        QApplication.processEvents()
        connection.close()
    unrelated = tmp_path/'unrelated'
    unrelated.mkdir()
    (unrelated/'keep.txt').write_text('keep')
    with pytest.raises(ValueError,match='empty directory'):
        open_demo(unrelated)
