from collections import Counter
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.database.competency_evidence_repository import (
    CompetencyEvidenceRepository,
)
from ict_cockpit.trade_plan import TradePlanDefinition


class CompetencyEvidenceReviewWidget(QWidget):
    """Read-only Review / Development view over accumulated competency evidence."""

    study_competency_requested = Signal(str)

    def __init__(
        self,
        trade_plan: TradePlanDefinition,
        repository: CompetencyEvidenceRepository,
    ) -> None:
        super().__init__()
        self.trade_plan = trade_plan
        self.repository = repository
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
        self.evidence_list.setMaximumHeight(220)
        self.evidence_list.currentItemChanged.connect(
            lambda _current, _previous: self._render_selected()
        )

        self.detail_label = QLabel()
        self.detail_label.setWordWrap(True)
        self.detail_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.detail_label.setContentsMargins(8, 6, 8, 6)

        self.study_this_button = QPushButton("Study this competency")
        self.study_this_button.setEnabled(False)
        self.study_this_button.clicked.connect(self._request_targeted_study)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(heading)
        layout.addWidget(help_text)
        layout.addWidget(self.competency_combo)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.evidence_list)
        layout.addWidget(self.detail_label)
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
            label = (
                self.competency_combo.currentText()
                if competency_id
                else "the current Trade Plan"
            )
            self.summary_label.setText(
                f"No reviewed competency evidence recorded for {label}."
            )
            self.evidence_list.addItem("No evidence yet")
            self.evidence_list.item(0).setData(256, "")
            self.detail_label.setText(
                "Complete a focused Study, Rehearsal, or Validation review to "
                "create evidence. No proficiency conclusion is inferred here."
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

    def _selected_competency_id(self) -> str:
        selected = self.evidence_list.currentItem()
        evidence_id = selected.data(256) if selected is not None else ""
        item = self._evidence_by_id.get(str(evidence_id or ""))
        if item is not None:
            return item.competency_id
        return str(self.competency_combo.currentData() or "")

    def _request_targeted_study(self) -> None:
        competency_id = self._selected_competency_id()
        if competency_id:
            self.study_competency_requested.emit(competency_id)

    def _render_selected(self) -> None:
        selected = self.evidence_list.currentItem()
        evidence_id = selected.data(256) if selected is not None else ""
        item = self._evidence_by_id.get(str(evidence_id or ""))
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
