from collections import Counter
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.competency import (
    CompetencyDevelopmentDirection,
    DevelopmentDirection,
)
from ict_cockpit.database.competency_development_direction_repository import (
    CompetencyDevelopmentDirectionRepository,
)
from ict_cockpit.database.competency_evidence_repository import (
    CompetencyEvidenceRepository,
)
from ict_cockpit.trade_plan import TradePlanDefinition


class CompetencyEvidenceReviewWidget(QWidget):
    """Review / Development view over evidence and human synthesis."""

    study_competency_requested = Signal(str)

    def __init__(
        self,
        trade_plan: TradePlanDefinition,
        repository: CompetencyEvidenceRepository,
        development_direction_repository:
            CompetencyDevelopmentDirectionRepository | None = None,
    ) -> None:
        super().__init__()
        self.trade_plan = trade_plan
        self.repository = repository
        self.development_direction_repository = (
            development_direction_repository
        )
        self._evidence_by_id = {}

        heading = QLabel("Competency Evidence")
        heading.setStyleSheet("font-weight: 600;")

        help_text = QLabel(
            "Inspect accumulated evidence without converting it into a score or "
            "automatic proficiency decision."
        )
        help_text.setWordWrap(True)

        self.competency_combo = QComboBox()
        self.competency_combo.addItem("All competencies", "")
        for competency in trade_plan.competencies:
            self.competency_combo.addItem(
                f"{competency.name} · {competency.category}",
                competency.id,
            )
        self.competency_combo.currentIndexChanged.connect(self.refresh)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.summary_label.setContentsMargins(8, 6, 8, 6)

        self.evidence_list = QListWidget()
        self.evidence_list.setMaximumHeight(150)
        self.evidence_list.currentItemChanged.connect(
            lambda _current, _previous: self._selection_changed()
        )

        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        self.detail_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.detail_label.setContentsMargins(8, 6, 8, 6)

        self.study_this_button = QPushButton("Study this competency")
        self.study_this_button.setEnabled(False)
        self.study_this_button.clicked.connect(self._request_targeted_study)

        self.development_frame = QFrame()
        self.development_frame.setFrameShape(QFrame.Shape.StyledPanel)
        development_layout = QVBoxLayout(self.development_frame)
        development_layout.setContentsMargins(8, 6, 8, 6)
        development_layout.setSpacing(4)

        development_heading = QLabel("Development Direction")
        development_heading.setStyleSheet("font-weight: 600;")
        development_layout.addWidget(development_heading)

        development_note = QLabel(
            "Human-reviewed synthesis of what deliberate work should happen "
            "next. This does not change competency state, Evidence Maturity, "
            "or eligibility."
        )
        development_note.setWordWrap(True)
        development_layout.addWidget(development_note)

        self.current_direction_label = QLabel("No Development Direction recorded.")
        self.current_direction_label.setWordWrap(True)
        development_layout.addWidget(self.current_direction_label)

        self.direction_combo = QComboBox()
        for direction in DevelopmentDirection:
            self.direction_combo.addItem(direction.value, direction.value)
        development_layout.addWidget(self.direction_combo)

        self.direction_note_input = QLineEdit()
        self.direction_note_input.setPlaceholderText(
            "Optional synthesis note — what pattern or development need do you see?"
        )
        development_layout.addWidget(self.direction_note_input)

        self.link_selected_evidence_checkbox = QCheckBox(
            "Link the selected evidence record as supporting evidence"
        )
        self.link_selected_evidence_checkbox.setChecked(False)
        development_layout.addWidget(self.link_selected_evidence_checkbox)

        self.selected_evidence_link_label = QLabel(
            "Selected evidence link · no evidence selected"
        )
        self.selected_evidence_link_label.setWordWrap(True)
        development_layout.addWidget(self.selected_evidence_link_label)

        self.save_direction_button = QPushButton("Save Development Direction")
        self.save_direction_button.clicked.connect(
            self._save_development_direction
        )
        development_layout.addWidget(self.save_direction_button)

        self.development_status_label = QLabel()
        self.development_status_label.setWordWrap(True)
        development_layout.addWidget(self.development_status_label)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(heading)
        layout.addWidget(help_text)
        layout.addWidget(self.competency_combo)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.evidence_list)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.development_frame)
        layout.addWidget(self.study_this_button)

        self.refresh()

    def refresh(self, *_args) -> None:
        competency_id = str(self.competency_combo.currentData() or "")
        if competency_id:
            evidence = self.repository.list_for_competency(
                self.trade_plan.id,
                competency_id,
            )
            evidence = list(reversed(evidence))
        else:
            evidence = self.repository.list_for_plan(self.trade_plan.id)

        self._evidence_by_id = {item.id: item for item in evidence}
        self.evidence_list.clear()

        if not evidence:
            self.study_this_button.setEnabled(bool(competency_id))
            self._render_synthesis_summary([], competency_id)
            self.evidence_list.addItem("No evidence yet")
            self.evidence_list.item(0).setData(256, "")
            self.detail_label.setText(
                "Complete a focused Study, Rehearsal, or Validation review to "
                "create evidence. No proficiency conclusion is inferred here."
            )
            self._refresh_development_editor()
            return

        self._render_synthesis_summary(evidence, competency_id)

        for item in evidence:
            recorded = self._format_recorded_at(item.recorded_at)
            row = (
                f"{recorded} · {item.competency_name} · "
                f"{item.run_purpose} · {item.study_outcome}"
            )
            self.evidence_list.addItem(row)
            self.evidence_list.item(self.evidence_list.count() - 1).setData(
                256,
                item.id,
            )

        self.evidence_list.setCurrentRow(0)
        self.study_this_button.setEnabled(True)
        self._refresh_development_editor()

    def _render_synthesis_summary(
        self,
        evidence,
        competency_id: str,
    ) -> None:
        if not competency_id:
            if not evidence:
                self.summary_label.setText(
                    "No reviewed competency evidence recorded for the current Trade Plan."
                )
                return
            outcomes = Counter(item.study_outcome for item in evidence)
            environments = Counter(item.run_purpose for item in evidence)
            outcome_text = " · ".join(
                f"{name}: {count}" for name, count in sorted(outcomes.items())
            )
            environment_text = " · ".join(
                f"{name}: {count}" for name, count in sorted(environments.items())
            )
            self.summary_label.setText(
                f"{len(evidence)} evidence record(s) · {environment_text}\n"
                f"Reviewed outcomes · {outcome_text}"
            )
            return

        competency = next(
            (
                item
                for item in self.trade_plan.competencies
                if item.id == competency_id
            ),
            None,
        )
        competency_name = competency.name if competency is not None else competency_id
        competency_category = competency.category if competency is not None else ""

        current_direction = None
        if self.development_direction_repository is not None:
            current_direction = self.development_direction_repository.get(
                self.trade_plan.id,
                competency_id,
            )

        direction_text = (
            current_direction.direction.value
            if current_direction is not None
            else "Not recorded"
        )
        linked_count = (
            len(current_direction.supporting_evidence_ids)
            if current_direction is not None
            else 0
        )

        if not evidence:
            self.summary_label.setText(
                f"Competency Synthesis · {competency_name}"
                + (f" · {competency_category}" if competency_category else "")
                + f" · Trade Plan {self.trade_plan.revision}\n"
                f"Development Direction · {direction_text} · "
                f"supporting evidence: {linked_count}\n"
                "Evidence coverage · no reviewed evidence recorded\n"
                "Descriptive coverage only · no proficiency, Evidence Maturity, "
                "or eligibility conclusion is inferred."
            )
            return

        outcomes = Counter(item.study_outcome for item in evidence)
        purposes = Counter(item.run_purpose for item in evidence)
        purpose_text = " · ".join(
            f"{name}: {count}" for name, count in sorted(purposes.items())
        )
        outcome_text = " · ".join(
            f"{name}: {count}" for name, count in sorted(outcomes.items())
        )

        parsed_times = []
        for item in evidence:
            try:
                parsed_times.append(datetime.fromisoformat(item.recorded_at))
            except (TypeError, ValueError):
                continue
        if parsed_times:
            oldest = min(parsed_times).strftime("%Y-%m-%d")
            newest = max(parsed_times).strftime("%Y-%m-%d")
            range_text = f"{oldest} -> {newest}"
        else:
            range_text = "Unknown"

        self.summary_label.setText(
            f"Competency Synthesis · {competency_name}"
            + (f" · {competency_category}" if competency_category else "")
            + f" · Trade Plan {self.trade_plan.revision}\n"
            f"Development Direction · {direction_text} · "
            f"supporting evidence: {linked_count}\n"
            f"Evidence coverage · {len(evidence)} reviewed · {purpose_text}\n"
            f"Reviewed outcomes · {outcome_text}\n"
            f"Evidence range · {range_text}\n"
            "Descriptive coverage only · no proficiency, Evidence Maturity, "
            "or eligibility conclusion is inferred."
        )

    def _selection_changed(self) -> None:
        self._render_selected()
        self._refresh_development_editor()

    def _selected_evidence(self):
        selected = self.evidence_list.currentItem()
        evidence_id = selected.data(256) if selected is not None else ""
        return self._evidence_by_id.get(str(evidence_id or ""))

    def _selected_competency_id(self) -> str:
        item = self._selected_evidence()
        if item is not None:
            return item.competency_id
        return str(self.competency_combo.currentData() or "")

    def _request_targeted_study(self) -> None:
        competency_id = self._selected_competency_id()
        if competency_id:
            self.study_competency_requested.emit(competency_id)

    def _refresh_development_editor(self) -> None:
        competency_id = self._selected_competency_id()
        enabled = (
            bool(competency_id)
            and self.development_direction_repository is not None
        )
        self.direction_combo.setEnabled(enabled)
        self.direction_note_input.setEnabled(enabled)
        self.save_direction_button.setEnabled(enabled)

        selected_evidence = self._selected_evidence()
        self.link_selected_evidence_checkbox.setEnabled(
            enabled and selected_evidence is not None
        )
        if not enabled:
            self.link_selected_evidence_checkbox.setChecked(False)
            self.selected_evidence_link_label.setText(
                "Selected evidence link · no competency/evidence selected"
            )
            self.current_direction_label.setText(
                "Select a competency or evidence record to review its "
                "Development Direction."
            )
            self.direction_note_input.clear()
            self.development_status_label.clear()
            return

        current = self.development_direction_repository.get(
            self.trade_plan.id,
            competency_id,
        )
        if current is None:
            self.current_direction_label.setText(
                "No Development Direction recorded."
            )
            self.direction_combo.setCurrentText(
                DevelopmentDirection.NO_ACTIVE_FOCUS.value
            )
            self.direction_note_input.clear()
            self.link_selected_evidence_checkbox.setChecked(False)
            self.selected_evidence_link_label.setText(
                "Selected evidence link · not linked"
                if selected_evidence is not None
                else "Selected evidence link · no evidence selected"
            )
        else:
            linked_count = len(current.supporting_evidence_ids)
            link_text = (
                f" · supporting evidence: {linked_count}"
                if linked_count
                else " · no supporting evidence linked"
            )
            self.current_direction_label.setText(
                f"Current · {current.direction.value}"
                + (
                    f" · {current.note}"
                    if current.note
                    else ""
                )
                + link_text
            )
            self.direction_combo.setCurrentText(current.direction.value)
            self.direction_note_input.setText(current.note)
            selected_is_linked = (
                selected_evidence is not None
                and selected_evidence.id in current.supporting_evidence_ids
            )
            self.link_selected_evidence_checkbox.setChecked(selected_is_linked)
            self.selected_evidence_link_label.setText(
                "Selected evidence link · linked"
                if selected_is_linked
                else (
                    "Selected evidence link · not linked"
                    if selected_evidence is not None
                    else "Selected evidence link · no evidence selected"
                )
            )
        self.development_status_label.setText(
            "The checkbox reflects whether the currently selected evidence "
            "record is linked to the saved Development Direction."
        )

    def _save_development_direction(self) -> None:
        if self.development_direction_repository is None:
            return

        competency_id = self._selected_competency_id()
        if not competency_id:
            self.development_status_label.setText(
                "Select a competency before saving a Development Direction."
            )
            return

        selected_evidence = self._selected_evidence()
        current = self.development_direction_repository.get(
            self.trade_plan.id,
            competency_id,
        )
        supporting_evidence_ids = list(
            current.supporting_evidence_ids
            if current is not None
            else []
        )
        if selected_evidence is not None:
            if self.link_selected_evidence_checkbox.isChecked():
                if selected_evidence.id not in supporting_evidence_ids:
                    supporting_evidence_ids.append(selected_evidence.id)
            else:
                supporting_evidence_ids = [
                    evidence_id
                    for evidence_id in supporting_evidence_ids
                    if evidence_id != selected_evidence.id
                ]

        item = CompetencyDevelopmentDirection(
            trade_plan_id=self.trade_plan.id,
            trade_plan_revision=self.trade_plan.revision,
            competency_id=competency_id,
            direction=DevelopmentDirection(
                self.direction_combo.currentData()
            ),
            note=self.direction_note_input.text(),
            supporting_evidence_ids=supporting_evidence_ids,
        )
        self.development_direction_repository.save(item)
        competency_id_for_summary = self._selected_competency_id()
        if competency_id_for_summary:
            self._render_synthesis_summary(
                list(self._evidence_by_id.values()),
                competency_id_for_summary,
            )
        linked_count = len(item.supporting_evidence_ids)
        self.current_direction_label.setText(
            f"Current · {item.direction.value}"
            + (f" · {item.note}" if item.note else "")
            + (
                f" · supporting evidence: {linked_count}"
                if linked_count
                else " · no supporting evidence linked"
            )
        )
        if selected_evidence is not None:
            selected_state = (
                "linked"
                if selected_evidence.id in item.supporting_evidence_ids
                else "not linked"
            )
            evidence_text = f" · selected evidence is {selected_state}"
        else:
            evidence_text = (
                f" · supporting evidence: {linked_count}"
                if linked_count
                else " · no supporting evidence linked"
            )
        if selected_evidence is not None:
            self.selected_evidence_link_label.setText(
                "Selected evidence link · linked"
                if selected_evidence.id in item.supporting_evidence_ids
                else "Selected evidence link · not linked"
            )
        else:
            self.selected_evidence_link_label.setText(
                "Selected evidence link · no evidence selected"
            )
        self.development_status_label.setText(
            f"Development Direction saved{evidence_text}. "
            "No competency state or eligibility change was made."
        )

    def _render_selected(self) -> None:
        item = self._selected_evidence()
        if item is None:
            return

        lines = [
            f"{item.competency_name} · {item.competency_category}",
            (
                f"{item.run_environment} / {item.run_purpose} · "
                f"{item.study_outcome}"
            ),
            f"Trade Plan · {item.trade_plan_revision}",
        ]
        if item.study_question:
            lines.append(f"Question · {item.study_question}")
        if item.study_hypothesis:
            lines.append(f"Hypothesis · {item.study_hypothesis}")
        if item.study_scope:
            lines.append(f"Scope · {item.study_scope}")
        if item.note:
            lines.append(f"Review · {item.note}")
        lines.append(f"Run · {item.trading_run_id}")
        self.detail_label.setText("\n".join(lines))

    @staticmethod
    def _format_recorded_at(value: str) -> str:
        try:
            parsed = datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return value or "Unknown time"
        return parsed.strftime("%Y-%m-%d %H:%M")
