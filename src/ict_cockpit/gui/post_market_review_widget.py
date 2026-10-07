from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.quarter_theory import (
    qt_context_summary,
    raw_quarter_contextual_summary,
    raw_quarter_stack_relevance_summary,
    raw_quarter_stack_summary,
)
from ict_cockpit.analysis.tda_station_session import TDAStationSession
from ict_cockpit.analysis.trading_session_run import (
    InterpretationOutcome,
    ProcessAdherence,
    RunEvidenceKind,
    StudyOutcome,
    TradingRun,
)
from ict_cockpit.process_blueprint import ProcessBlueprint


class PostMarketReviewWidget(QWidget):
    """Review market interpretation first, then process on a separate stage."""

    interpretation_changed = Signal(str)
    review_changed = Signal(str, str, bool)
    study_review_changed = Signal(str, str)

    def __init__(self, blueprint: ProcessBlueprint) -> None:
        super().__init__()
        self._loading = False
        self._station_names = {
            station.id: station.name
            for mode in blueprint.modes
            for deck in mode.decks
            for station in deck.stations
        }

        heading = QLabel("Post-Market Review")
        heading.setStyleSheet("font-size: 16px; font-weight: 600;")
        purpose = QLabel(
            "Review what changed in the market first. Judge process separately afterward."
        )
        purpose.setWordWrap(True)

        self.stage_label = QLabel()
        self.stage_label.setStyleSheet("font-weight: 600;")

        self.stage_stack = QStackedWidget()
        self.market_review_page = self._build_market_review_page()
        self.process_review_page = self._build_process_review_page()
        self.stage_stack.addWidget(self.market_review_page)
        self.stage_stack.addWidget(self.process_review_page)

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(purpose)
        layout.addWidget(self.stage_label)
        layout.addWidget(self.stage_stack, 1)

        self.show_market_review()

    def _build_market_review_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        self.run_summary_label = QLabel("No Trading Run loaded")
        self.run_summary_label.setWordWrap(True)
        self.run_summary_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.run_summary_label.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(self.run_summary_label)

        compare_layout = QHBoxLayout()

        tda_frame = QFrame()
        tda_frame.setFrameShape(QFrame.Shape.StyledPanel)
        tda_layout = QVBoxLayout(tda_frame)
        tda_heading = QLabel("TDA — what I expected")
        tda_heading.setStyleSheet("font-weight: 600;")
        tda_note = QLabel("Saved analysis carried into the Trading Run")
        tda_note.setWordWrap(True)
        self.tda_snapshot_list = QListWidget()
        self.tda_snapshot_list.setMaximumHeight(240)
        tda_layout.addWidget(tda_heading)
        tda_layout.addWidget(tda_note)
        tda_layout.addWidget(self.tda_snapshot_list)

        live_frame = QFrame()
        live_frame.setFrameShape(QFrame.Shape.StyledPanel)
        live_layout = QVBoxLayout(live_frame)
        live_heading = QLabel("Live Watch — what changed")
        live_heading.setStyleSheet("font-weight: 600;")
        live_note = QLabel("Only observations and thesis changes are surfaced here")
        live_note.setWordWrap(True)
        self.live_changes_list = QListWidget()
        self.live_changes_list.setMaximumHeight(240)
        live_layout.addWidget(live_heading)
        live_layout.addWidget(live_note)
        live_layout.addWidget(self.live_changes_list)

        compare_layout.addWidget(tda_frame, 1)
        compare_layout.addWidget(live_frame, 1)
        layout.addLayout(compare_layout)

        interpretation_frame = QFrame()
        interpretation_frame.setFrameShape(QFrame.Shape.StyledPanel)
        interpretation_layout = QVBoxLayout(interpretation_frame)
        interpretation_layout.setContentsMargins(10, 8, 10, 8)
        interpretation_heading = QLabel("Did the initial interpretation materially hold?")
        interpretation_heading.setStyleSheet("font-weight: 600;")
        interpretation_help = QLabel(
            "Classify the market interpretation itself. This is separate from process adherence and P&L."
        )
        interpretation_help.setWordWrap(True)
        interpretation_layout.addWidget(interpretation_heading)
        interpretation_layout.addWidget(interpretation_help)

        self.interpretation_group = QButtonGroup(self)
        self.interpretation_group.setExclusive(True)
        self.interpretation_buttons: dict[InterpretationOutcome, QPushButton] = {}
        interpretation_buttons_layout = QHBoxLayout()
        labels = {
            InterpretationOutcome.MATERIALLY_ACCURATE: "Materially Accurate",
            InterpretationOutcome.MISSED_CRITICAL_INFORMATION: "Changed · Missed Critical Info",
            InterpretationOutcome.UNEXPLAINED_STUDY_NEEDED: "Changed · Unexplained / Study Needed",
            InterpretationOutcome.EXOGENOUS_EVENT: "Changed · External / Exogenous",
        }
        for state, label in labels.items():
            button = QPushButton(label)
            button.setCheckable(True)
            if state is InterpretationOutcome.UNEXPLAINED_STUDY_NEEDED:
                button.setToolTip(
                    "The cause is unknown at my current level of price-action understanding; this is a study signal, not a claim of randomness."
                )
            self.interpretation_group.addButton(button)
            self.interpretation_buttons[state] = button
            interpretation_buttons_layout.addWidget(button)
        interpretation_layout.addLayout(interpretation_buttons_layout)
        self.interpretation_group.buttonClicked.connect(self._emit_interpretation)
        layout.addWidget(interpretation_frame)

        navigation = QHBoxLayout()
        navigation.addStretch()
        self.to_process_review_button = QPushButton("Continue to Process Review →")
        self.to_process_review_button.clicked.connect(self.show_process_review)
        navigation.addWidget(self.to_process_review_button)
        layout.addLayout(navigation)
        layout.addStretch()
        return page

    def _build_process_review_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        intro = QLabel(
            "Now judge the process independently of whether the thesis or trade outcome was correct."
        )
        intro.setWordWrap(True)
        intro.setFrameShape(QFrame.Shape.StyledPanel)
        intro.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(intro)

        adherence_heading = QLabel("Process adherence")
        adherence_heading.setStyleSheet("font-weight: 600;")
        layout.addWidget(adherence_heading)

        self.adherence_group = QButtonGroup(self)
        self.adherence_group.setExclusive(True)
        self.adherence_buttons: dict[ProcessAdherence, QPushButton] = {}
        adherence_layout = QHBoxLayout()
        for state in (
            ProcessAdherence.FOLLOWED,
            ProcessAdherence.MIXED,
            ProcessAdherence.DEVIATION,
        ):
            button = QPushButton(state.value)
            button.setCheckable(True)
            self.adherence_group.addButton(button)
            self.adherence_buttons[state] = button
            adherence_layout.addWidget(button)
        adherence_layout.addStretch()
        self.adherence_group.buttonClicked.connect(self._emit_review)
        layout.addLayout(adherence_layout)

        self.takeaway_input = QLineEdit()
        self.takeaway_input.setPlaceholderText(
            "Optional takeaway — what is worth carrying forward?"
        )
        self.takeaway_input.editingFinished.connect(self._emit_review)
        layout.addWidget(self.takeaway_input)

        self.film_night_checkbox = QCheckBox("Take this Trading Run to Film Night / Lab")
        self.film_night_checkbox.toggled.connect(self._emit_review)
        layout.addWidget(self.film_night_checkbox)

        self.study_review_frame = QFrame()
        self.study_review_frame.setFrameShape(QFrame.Shape.StyledPanel)
        study_layout = QVBoxLayout(self.study_review_frame)
        study_layout.setContentsMargins(10, 8, 10, 8)
        study_layout.setSpacing(4)

        study_heading = QLabel("Study Review")
        study_heading.setStyleSheet("font-weight: 600;")
        self.study_question_label = QLabel()
        self.study_question_label.setWordWrap(True)
        self.study_hypothesis_label = QLabel()
        self.study_hypothesis_label.setWordWrap(True)
        self.study_scope_label = QLabel()
        self.study_scope_label.setWordWrap(True)
        self.study_competency_label = QLabel()
        self.study_competency_label.setWordWrap(True)

        outcome_row = QHBoxLayout()
        outcome_row.addWidget(QLabel("Study outcome"))
        self.study_outcome_combo = QComboBox()
        self.study_outcome_combo.addItems(
            [item.value for item in StudyOutcome]
        )
        self.study_outcome_combo.currentTextChanged.connect(
            self._emit_study_review
        )
        outcome_row.addWidget(self.study_outcome_combo, 1)

        self.study_outcome_note_input = QLineEdit()
        self.study_outcome_note_input.setPlaceholderText(
            "What did this run teach you? (optional)"
        )
        self.study_outcome_note_input.editingFinished.connect(
            self._emit_study_review
        )

        study_layout.addWidget(study_heading)
        study_layout.addWidget(self.study_question_label)
        study_layout.addWidget(self.study_hypothesis_label)
        study_layout.addWidget(self.study_scope_label)
        study_layout.addWidget(self.study_competency_label)
        study_layout.addLayout(outcome_row)
        study_layout.addWidget(self.study_outcome_note_input)
        layout.addWidget(self.study_review_frame)
        self.study_review_frame.hide()

        navigation = QHBoxLayout()
        self.back_to_market_button = QPushButton("← Back to Market Review")
        self.back_to_market_button.clicked.connect(self.show_market_review)
        navigation.addWidget(self.back_to_market_button)
        navigation.addStretch()
        layout.addLayout(navigation)
        layout.addStretch()
        return page

    def show_market_review(self) -> None:
        self.stage_stack.setCurrentWidget(self.market_review_page)
        self.stage_label.setText("1 of 2 · Market Review")

    def show_process_review(self) -> None:
        self.stage_stack.setCurrentWidget(self.process_review_page)
        self.stage_label.setText("2 of 2 · Process Review")

    def load_state(
        self,
        trading_run: TradingRun,
        tda_session: TDAStationSession,
    ) -> None:
        self._loading = True
        try:
            outcome = trading_run.outcome or "In review"
            self.run_summary_label.setText(
                f"{trading_run.run_label} · Outcome: {outcome} · "
                f"Current thesis: {trading_run.current_thesis_state.value}"
            )

            self.tda_snapshot_list.clear()
            populated_tda = 0
            qt_summary = qt_context_summary(trading_run.qt_context)
            raw_stack = raw_quarter_stack_summary(
                trading_run.market_time_context
            )
            if (
                qt_summary != "No QT / AMDX interpretation recorded"
                or raw_stack != "Not available"
            ):
                detail = "QT / AMDX Stack"
                if qt_summary != "No QT / AMDX interpretation recorded":
                    detail += "\n" + qt_summary
                if raw_stack != "Not available":
                    detail += "\nRaw stack · " + raw_stack
                    raw_detail = raw_quarter_contextual_summary(
                        trading_run.market_time_context
                    )
                    if raw_detail != "Not available":
                        detail += "\n" + raw_detail
                    detail += (
                        "\nStack watch · "
                        + raw_quarter_stack_relevance_summary(
                            trading_run.market_time_context
                        )
                    )
                self.tda_snapshot_list.addItem(detail)
                populated_tda += 1
            for item in tda_session.observations:
                if not item.observation:
                    continue
                name = self._station_names.get(item.station_id, item.station_id)
                self.tda_snapshot_list.addItem(f"{name}\n{item.observation}")
                populated_tda += 1
            if populated_tda == 0:
                self.tda_snapshot_list.addItem("No written TDA observations were recorded.")

            self.live_changes_list.clear()
            if not trading_run.evidence:
                self.live_changes_list.addItem("No Live Watch observations or thesis changes were recorded.")
            for item in trading_run.evidence:
                if item.kind is RunEvidenceKind.THESIS_STATE:
                    text = f"Thesis → {item.thesis_state.value}"
                    if item.note:
                        text += f"\n{item.note}"
                else:
                    text = f"Observation\n{item.note}"
                self.live_changes_list.addItem(text)

            for state, button in self.interpretation_buttons.items():
                button.setChecked(trading_run.review_interpretation_outcome is state)
            for state, button in self.adherence_buttons.items():
                button.setChecked(trading_run.review_process_adherence is state)
            self.takeaway_input.setText(trading_run.review_takeaway)
            self.film_night_checkbox.setChecked(trading_run.review_film_night)

            study = trading_run.study_context
            self.study_review_frame.setVisible(study is not None)
            if study is not None:
                self.study_question_label.setText(
                    "Question · " + study.question
                )
                self.study_hypothesis_label.setText(
                    "Hypothesis · "
                    + (study.hypothesis or "Not specified")
                )
                self.study_scope_label.setText(
                    "Scope · " + (study.scope or "Not specified")
                )
                competency_names = [
                    str(item.get("name", item.get("id", ""))).strip()
                    for item in study.competency_focus
                    if str(item.get("name", item.get("id", ""))).strip()
                ]
                self.study_competency_label.setText(
                    "Competency focus · "
                    + (
                        ", ".join(competency_names)
                        if competency_names
                        else "Not specified"
                    )
                )
                self.study_outcome_combo.setCurrentText(
                    study.outcome.value
                )
                self.study_outcome_note_input.setText(
                    study.outcome_note
                )
        finally:
            self._loading = False

    def clear_state(self) -> None:
        self._loading = True
        try:
            self.run_summary_label.setText("No Trading Run loaded")
            self.tda_snapshot_list.clear()
            self.live_changes_list.clear()
            self.interpretation_group.setExclusive(False)
            for button in self.interpretation_buttons.values():
                button.setChecked(False)
            self.interpretation_group.setExclusive(True)
            self.adherence_group.setExclusive(False)
            for button in self.adherence_buttons.values():
                button.setChecked(False)
            self.adherence_group.setExclusive(True)
            self.takeaway_input.clear()
            self.film_night_checkbox.setChecked(False)
            self.study_review_frame.hide()
            self.study_question_label.clear()
            self.study_hypothesis_label.clear()
            self.study_scope_label.clear()
            self.study_competency_label.clear()
            self.study_outcome_combo.setCurrentText(
                StudyOutcome.NOT_REVIEWED.value
            )
            self.study_outcome_note_input.clear()
            self.show_market_review()
        finally:
            self._loading = False

    def _selected_interpretation(self) -> InterpretationOutcome:
        for state, button in self.interpretation_buttons.items():
            if button.isChecked():
                return state
        return InterpretationOutcome.NOT_REVIEWED

    def _selected_adherence(self) -> ProcessAdherence:
        for state, button in self.adherence_buttons.items():
            if button.isChecked():
                return state
        return ProcessAdherence.NOT_REVIEWED

    def _emit_interpretation(self, *_args) -> None:
        if self._loading:
            return
        self.interpretation_changed.emit(self._selected_interpretation().value)

    def _emit_review(self, *_args) -> None:
        if self._loading:
            return
        self.review_changed.emit(
            self._selected_adherence().value,
            self.takeaway_input.text().strip(),
            self.film_night_checkbox.isChecked(),
        )


    def _emit_study_review(self, *_args) -> None:
        if self._loading or self.study_review_frame.isHidden():
            return
        self.study_review_changed.emit(
            self.study_outcome_combo.currentText(),
            self.study_outcome_note_input.text().strip(),
        )
