import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from ict_cockpit.analysis.amdx import Role
from tools.tda_watch_journey_demo import open_demo


def dispose(connection, window):
    for timer in window.findChildren(QTimer):
        timer.stop()
    window.close()
    window.deleteLater()
    QApplication.processEvents()
    connection.close()


def test_normal_handoff_return_capture_and_restart(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'outside'))
    path = tmp_path / 'journey'
    connection, window = open_demo(path)
    shell = window.trade_plan_widget.trading_day_shell_widget
    runtime = shell.runtime
    runner = runtime.tda_station_runner_widget
    run_id = shell.active_trading_run.id
    station_session_id = runner.session.id
    process_id = runtime.session.id
    try:
        assert runtime.current_mode.id == 'tda'
        assert runner.session.completed_count() == 0
        assert not runtime.apply_transition('finish-tda')
        for station in tuple(runner.session.station_ids):
            runner.select_station(station)
            runner.observation_input.setPlainText('Synthetic primary draw' if station == 'tda-primary-draw'
                else 'Synthetic thesis: wait for a retracement' if station == 'tda-thesis'
                else 'Synthetic context reviewed')
            if station == 'tda-thesis':
                editor = runtime.tda_watch_point_widget
                editor.if_input.setText('Price returns to the marked area')
                editor.then_input.setText('Observe displacement; no automatic entry')
                editor.add_button.click()
            runner.complete_and_continue()
        point = runner.session.watch_points[0]
        runtime.transition_buttons['finish-tda'].click()
        assert runtime.current_mode.id == 'live-watch'
        assert shell.active_trading_run.id == run_id
        watch = runtime.live_watch_widget
        lines = '\n'.join(watch.watch_points_list.item(i).text() for i in range(watch.watch_points_list.count()))
        assert 'Synthetic primary draw' in lines and 'Synthetic thesis' in lines
        assert point.id in watch.watch_point_combos
        assert '8/8' in watch.tda_summary_label.text()
        assert runtime.watch_quiet_composition.safety.cells['broker'][1].text() == 'Adapter not connected'
        runtime.watch_quiet_composition.amdx_now.role_buttons[Role.D].click()
        assert '· D' in runtime.watch_quiet_composition.amdx_now.table.item(1, 2).text()
        shell.study_find_button.click()
        dock = window.contextual_study_find_dock
        dock.pattern_input.setText('Synthetic handoff example')
        dock.observation_input.setPlainText('Context visible without transcription')
        assert dock.save_and_return()
        assert runtime.current_mode.id == 'live-watch'
        assert shell.active_trading_run.id == run_id
        assert connection.execute('SELECT count(*) FROM study_find').fetchone()[0] == 1
        runtime.transition_buttons['live-return-analysis'].click()
        assert runtime.current_mode.id == 'tda'
        runner.select_station('tda-thesis')
        assert runner.observation_input.toPlainText() == 'Synthetic thesis: wait for a retracement'
        runner.observation_input.setPlainText('Revised synthetic thesis')
        runtime.transition_buttons['finish-tda'].click()
        assert runtime.current_mode.id == 'live-watch'
        assert any('Revised synthetic thesis' in watch.watch_points_list.item(i).text()
                   for i in range(watch.watch_points_list.count()))
    finally:
        dispose(connection, window)
    connection, window = open_demo(path)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        runtime = shell.runtime
        assert shell.active_trading_run.id == run_id
        assert runtime.session.id == process_id
        assert runtime.tda_station_runner_widget.session.id == station_session_id
        assert runtime.current_mode.id == 'live-watch'
        assert runtime.tda_station_runner_widget.session.observation_for('tda-thesis').observation == 'Revised synthetic thesis'
        assert runtime.tda_station_runner_widget.session.watch_points[0].id == point.id
        assert '· D' in runtime.watch_quiet_composition.amdx_now.table.item(1, 2).text()
        assert connection.execute('SELECT count(*) FROM trading_session_run').fetchone()[0] == 1
        assert connection.execute('SELECT count(*) FROM study_find').fetchone()[0] == 1
    finally:
        dispose(connection, window)


def test_tda_restart_does_not_complete_work_and_unrelated_directory_refused(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'outside'))
    path = tmp_path / 'journey'
    connection, window = open_demo(path)
    shell = window.trade_plan_widget.trading_day_shell_widget
    runner = shell.runtime.tda_station_runner_widget
    identity = shell.active_trading_run.id
    runner.open_mapped_slot(2)
    station = runner.current_station_id
    runner.observation_input.setPlainText('Still thinking')
    dispose(connection, window)
    connection, window = open_demo(path)
    try:
        shell = window.trade_plan_widget.trading_day_shell_widget
        runner = shell.runtime.tda_station_runner_widget
        assert shell.active_trading_run.id == identity
        assert shell.runtime.current_mode.id == 'tda'
        assert runner.current_station_id == station
        assert runner.observation_input.toPlainText() == 'Still thinking'
        assert runner.session.completed_count() == 0
    finally:
        dispose(connection, window)
    unrelated = tmp_path / 'keep'
    unrelated.mkdir()
    (unrelated / 'valuable.txt').write_text('keep')
    with pytest.raises(ValueError, match='empty trial directory'):
        open_demo(unrelated)
    assert (unrelated / 'valuable.txt').read_text() == 'keep'
