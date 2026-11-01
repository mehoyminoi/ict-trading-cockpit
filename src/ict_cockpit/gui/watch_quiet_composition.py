"""Quiet native Watch composition over existing runtime and AMDX owners."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ict_cockpit.analysis.amdx import Role, XSubtype
from ict_cockpit.analysis.attention_cues import build_attention_cue
from ict_cockpit.analysis.trading_session_run import (
    AuthorizationGateState,
    AuthorizationStatus,
)
from ict_cockpit.gui.amdx_context_widget import role_text


DISPLAY_PROFILES = ("tv-left", "tv-below")


def _market_clock(context: dict) -> str:
    captured = str(context.get("captured_at", ""))
    return captured[11:16] if len(captured) >= 16 else (captured or "Unknown")


class WatchOrientationRail(QFrame):
    """Peripheral reacquisition cues and the two accepted support launchers."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("watchOrientationRail")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.profile = "tv-left"

        self.heading = QLabel("CHART-FACING EDGE")
        self.heading.setObjectName("watchOrientationHeading")
        self.position_label = QLabel("Position\nWatch")
        self.market_time_label = QLabel("Market time\nUnknown")
        self.interval_label = QLabel("Active interval\nUnavailable")
        self.safety_label = QLabel("Safety\nBroker facts unavailable")
        self.next_label = QLabel("Next\nObserve")
        self.next_label.setObjectName("watchNextCue")
        for label in (
            self.position_label,
            self.market_time_label,
            self.interval_label,
            self.safety_label,
            self.next_label,
        ):
            label.setWordWrap(True)
            label.setFrameShape(QFrame.Shape.StyledPanel)
            label.setContentsMargins(7, 5, 7, 5)

        self.plan_reference_button = QPushButton("Plan reference")
        self.plan_reference_button.setToolTip(
            "Open the active Trade Plan reference and legal AMDX choices (P)"
        )
        self.study_find_button = QPushButton("Capture Study Find")
        self.study_find_button.setToolTip(
            "Open contextual Study Find capture (Ctrl+Shift+F)"
        )
        self.chart_hint_label = QLabel("TradingView is immediately left")
        self.chart_hint_label.setWordWrap(True)

        self.box = QBoxLayout(QBoxLayout.Direction.TopToBottom, self)
        self.box.setContentsMargins(7, 7, 7, 7)
        self.box.setSpacing(5)
        for widget in (
            self.heading,
            self.position_label,
            self.market_time_label,
            self.interval_label,
            self.safety_label,
            self.plan_reference_button,
            self.study_find_button,
            self.next_label,
            self.chart_hint_label,
        ):
            self.box.addWidget(widget)
        self.box.setStretchFactor(self.next_label, 1)
        self.setMaximumWidth(170)

    def set_profile(self, profile: str) -> None:
        if profile not in DISPLAY_PROFILES:
            raise ValueError(f"unknown workspace display profile: {profile}")
        self.profile = profile
        below = profile == "tv-below"
        self.box.setDirection(
            QBoxLayout.Direction.LeftToRight
            if below
            else QBoxLayout.Direction.TopToBottom
        )
        self.setMaximumWidth(16777215 if below else 170)
        self.setMaximumHeight(104 if below else 16777215)
        self.chart_hint_label.setText(
            "TradingView is below this edge"
            if below
            else "TradingView is immediately left"
        )

    def load_context(self, run, projection, safety_text: str) -> None:
        context = dict(run.market_time_context or {}) if run is not None else {}
        session = str(context.get("session", "Closed"))
        self.position_label.setText(f"Position\nWatch · {session}")
        self.market_time_label.setText(f"Market time\n{_market_clock(context)} ET")
        self.interval_label.setText(
            "Active interval\n"
            + (projection.target_label.replace("Working AMDX · ", "") if projection else "Unavailable")
        )
        self.safety_label.setText(f"Safety\n{safety_text}")
        cue = build_attention_cue(run) if run is not None else None
        self.next_label.setText(
            "Next\n" + (cue.headline if cue is not None else "No active run")
        )
        self.next_label.setProperty(
            "attentionLevel",
            cue.style_key if cue is not None else "quiet",
        )


class WatchAMDXNowWidget(QFrame):
    """Compact Watch projection of the maintained AMDX source and command."""

    def __init__(self, source) -> None:
        super().__init__()
        self.source = source
        self._decision_error = ""
        self.projection = source.decision_projection()
        self.setObjectName("watchAMDXNow")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(360)
        self.setMaximumWidth(500)

        heading = QLabel("AMDX now · nested current state")
        heading.setStyleSheet("font-weight: 600;")
        self.higher_label = QLabel("Higher context unavailable")
        self.higher_label.setWordWrap(True)
        self.target_label = QLabel("No active AMDX target")
        self.target_label.setWordWrap(True)
        self.target_label.setStyleSheet("font-weight: 600;")

        self.table = QTableWidget(2, 5)
        self.table.setHorizontalHeaderLabels(["Q1", "Q2", "Q3", "Q4", "Profile"])
        self.table.setVerticalHeaderLabels(["Day", "90m"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(39)
        self.table.setFixedHeight(106)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.cellClicked.connect(self._select_quarter)

        actions = QGridLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(4)
        self.role_buttons = {}
        for column, role in enumerate((Role.A, Role.M, Role.D)):
            button = QPushButton(role.value)
            button.clicked.connect(
                lambda _checked=False, selected=role: self._choose(selected)
            )
            self.role_buttons[role] = button
            actions.addWidget(button, 0, column)
        self.x_buttons = {}
        for column, (label, subtype) in enumerate(
            (("X(?)", None), ("X(C)", XSubtype.CONTINUATION), ("X(R)", XSubtype.REVERSAL))
        ):
            button = QPushButton(label)
            button.clicked.connect(
                lambda _checked=False, selected=subtype: self._choose(Role.X, selected)
            )
            self.x_buttons[subtype] = button
            actions.addWidget(button, 1, column)

        self.status_label = QLabel("Current only · no Watch history/comparison")
        self.status_label.setWordWrap(True)
        self.full_stack_button = QPushButton("Open full AMDX lens")
        self.full_stack_button.clicked.connect(self.source.full_stack_button.click)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(5)
        layout.addWidget(heading)
        layout.addWidget(self.higher_label)
        layout.addWidget(self.target_label)
        layout.addWidget(self.table)
        layout.addLayout(actions)
        layout.addWidget(self.status_label)
        layout.addWidget(self.full_stack_button)
        layout.addStretch()

        source.decision_projection_changed.connect(self.refresh_projection)
        source.recorded.connect(lambda _claim: self.refresh_projection(source.decision_projection()))
        self.refresh_projection(self.projection)

    def _select_quarter(self, row: int, column: int) -> None:
        if column >= 4:
            return
        self._decision_error = ""
        self.source.select_quarter(row, column)
        self.refresh_projection(self.source.decision_projection())

    def _choose(self, role: Role, subtype: XSubtype | None = None) -> None:
        projection = self.projection
        if projection is None:
            return
        if self.source.choose_decision(projection.token, role, subtype):
            self._decision_error = ""
        else:
            self._decision_error = self.source.status_label.text() or "Not recorded · review the AMDX target and choose again"
        self.refresh_projection(self.source.decision_projection())

    def refresh_projection(self, projection) -> None:
        self.projection = projection
        self.target_label.setText(projection.target_label)
        self.higher_label.setText(
            self.source.higher_label.text().replace("Higher QT · ", "Context · ")
            or "Higher context unavailable"
        )
        source_table = self.source.table
        self.table.setRowCount(source_table.rowCount())
        self.table.setVerticalHeaderLabels(
            [
                source_table.verticalHeaderItem(row).text()
                if source_table.verticalHeaderItem(row) is not None
                else ""
                for row in range(source_table.rowCount())
            ]
        )
        for row in range(source_table.rowCount()):
            for column in range(source_table.columnCount()):
                source_item = source_table.item(row, column)
                item = QTableWidgetItem(source_item.text() if source_item else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setToolTip(source_item.toolTip() if source_item else "")
                self.table.setItem(row, column, item)
        current = (
            role_text(projection.current_role, projection.current_subtype)
            if projection.current_role
            else "Unresolved"
        )
        status = f"Current {current} · quartet {projection.profile} · no Watch history/comparison"
        if not projection.available:
            status = projection.unavailable_reason or "AMDX recording unavailable"
        self.status_label.setText(self._decision_error or status)
        for role, button in self.role_buttons.items():
            legal = role in projection.legal_roles
            button.setVisible(legal)
            button.setEnabled(projection.available and legal)
        for subtype, button in self.x_buttons.items():
            legal = Role.X in projection.legal_roles and (
                subtype is None or subtype in projection.legal_x_subtypes
            )
            button.setVisible(legal)
            button.setEnabled(projection.available and legal)
        self.full_stack_button.setEnabled(
            self.source.binding is not None and not self.source._read_error
        )


class WatchProcessSafetyStrip(QFrame):
    """Always-visible truthful projection of current process and broker limits."""

    def __init__(self, risk_summary: str = "") -> None:
        super().__init__()
        self.risk_summary = risk_summary.strip()
        self.setObjectName("watchProcessSafety")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self.heading = QLabel("Broker & process safety")
        self.heading.setStyleSheet("font-weight: 600;")
        self.summary_label = QLabel("No active run")
        self.no_pnl_label = QLabel("P&L intentionally absent")
        header = QGridLayout()
        header.addWidget(self.heading, 0, 0)
        header.addWidget(self.summary_label, 0, 1)
        header.addWidget(self.no_pnl_label, 0, 2)
        header.setColumnStretch(1, 1)

        self.cells = {}
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(5)
        for column, key in enumerate(
            ("environment", "authorization", "broker", "risk", "position", "orders")
        ):
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            cell_layout = QVBoxLayout(frame)
            cell_layout.setContentsMargins(6, 4, 6, 4)
            title = QLabel(key.replace("_", " ").title())
            title.setObjectName("watchSafetyCellTitle")
            value = QLabel("Unavailable")
            value.setWordWrap(True)
            detail = QLabel()
            detail.setWordWrap(True)
            frame.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            value.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            detail.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            cell_layout.addWidget(title)
            cell_layout.addWidget(value)
            cell_layout.addWidget(detail)
            grid.addWidget(frame, 0, column)
            grid.setColumnStretch(column, 1)
            self.cells[key] = (frame, value, detail)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 5, 7, 5)
        layout.setSpacing(4)
        layout.addLayout(header)
        layout.addLayout(grid)

    def _set_cell(self, key: str, value: str, detail: str, state: str = "quiet") -> None:
        frame, value_label, detail_label = self.cells[key]
        value_label.setText(value)
        detail_label.setText(detail)
        frame.setProperty("safetyState", state)

    def load_run(self, run) -> str:
        if run is None:
            self.summary_label.setText("No active run")
            return "No active run"

        self._set_cell(
            "environment",
            f"{run.environment.value} · {run.purpose.value}",
            "Account identity unavailable",
        )

        candidates = [
            item
            for item in run.setup_candidates
            if item.source_type == "Playbook"
        ]
        results = [run.candidate_authorization(item.id) for item in candidates]
        if any(item.status is AuthorizationStatus.AUTHORIZED for item in results):
            authorization = "Candidate authorized"
            authorization_detail = "Plan gates and configured threshold clear"
            authorization_state = "clear"
        elif any(item.status is AuthorizationStatus.BLOCKED for item in results):
            blocked = next(
                item
                for item in results
                if item.status is AuthorizationStatus.BLOCKED
            )
            authorization = "Candidate blocked"
            authorization_detail = blocked.blockers[0] if blocked.blockers else blocked.detail
            authorization_state = "attention"
        elif results:
            authorization = "Not configured"
            authorization_detail = results[0].detail
            authorization_state = "unavailable"
        else:
            run_gates = [
                run.authorization_gate_states.get(
                    str(item.get("id", "")), AuthorizationGateState.PENDING
                )
                for item in run.authorization_policy_snapshot
                if str(item.get("scope", "Run")) == "Run"
            ]
            blocked_count = sum(item is AuthorizationGateState.BLOCKED for item in run_gates)
            pending_count = sum(item is AuthorizationGateState.PENDING for item in run_gates)
            authorization = "No candidate active"
            authorization_detail = (
                f"{blocked_count} run gate(s) blocked"
                if blocked_count
                else f"{pending_count} run gate(s) pending"
                if pending_count
                else "Await setup criteria"
            )
            authorization_state = "attention" if blocked_count else "quiet"
        self._set_cell(
            "authorization",
            authorization,
            authorization_detail,
            authorization_state,
        )

        self._set_cell(
            "broker",
            "Adapter not connected",
            "Unavailable is not treated as safe",
            "unavailable",
        )
        self._set_cell(
            "risk",
            "Plan rules only",
            self.risk_summary or "No numeric account envelope is connected",
            "unavailable",
        )
        self._set_cell(
            "position",
            "Unavailable",
            "No broker position/order facts in Alpha 0.7",
            "unavailable",
        )
        self._set_cell(
            "orders",
            "Nothing staged by Cockpit",
            "Order submission is not implemented",
        )
        summary = authorization
        if authorization_state == "attention":
            summary += " · attention required"
        else:
            summary += " · broker facts unavailable"
        self.summary_label.setText(summary)
        self.setProperty("safetyState", authorization_state)
        return summary


class WatchQuietCompositionWidget(QWidget):
    """Four-region quiet Watch composition without duplicating state ownership."""

    def __init__(self, live_watch_widget, amdx_source, *, profile="tv-left") -> None:
        super().__init__()
        self.live_watch_widget = live_watch_widget
        self.amdx_source = amdx_source
        self.orientation = WatchOrientationRail()
        self.amdx_now = WatchAMDXNowWidget(amdx_source)
        self.safety = WatchProcessSafetyStrip(live_watch_widget.base_policy.risk_summary)

        self.operating_scroll = QScrollArea()
        self.operating_scroll.setObjectName("watchOperatingCanvas")
        self.operating_scroll.setWidgetResizable(True)
        self.operating_scroll.setFrameShape(QFrame.Shape.StyledPanel)
        self.operating_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.operating_scroll.setWidget(live_watch_widget)
        self.operating_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        if hasattr(live_watch_widget, "set_quiet_composition"):
            live_watch_widget.set_quiet_composition(True)

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(7)
        self.profile = ""
        self.set_profile(profile)

        self.setStyleSheet(
            "#watchOrientationRail, #watchAMDXNow, #watchProcessSafety, "
            "#watchOperatingCanvas { border: 1px solid palette(mid); border-radius: 5px; }"
            "#watchOrientationHeading, #watchSafetyCellTitle { color: palette(mid); "
            "font-size: 10px; font-weight: 600; }"
            "#watchNextCue { border-left: 3px solid palette(highlight); }"
        )

        amdx_source.decision_projection_changed.connect(self._projection_changed)

    @property
    def plan_reference_button(self):
        return self.orientation.plan_reference_button

    @property
    def study_find_button(self):
        return self.orientation.study_find_button

    def set_profile(self, profile: str) -> None:
        if profile not in DISPLAY_PROFILES:
            raise ValueError(f"unknown workspace display profile: {profile}")
        for widget in (
            self.orientation,
            self.operating_scroll,
            self.amdx_now,
            self.safety,
        ):
            self.grid.removeWidget(widget)
        self.profile = profile
        self.orientation.set_profile(profile)
        if profile == "tv-below":
            self.grid.addWidget(self.operating_scroll, 0, 0)
            self.grid.addWidget(self.amdx_now, 0, 1)
            self.grid.addWidget(self.safety, 1, 0, 1, 2)
            self.grid.addWidget(self.orientation, 2, 0, 1, 2)
            self.grid.setColumnStretch(0, 3)
            self.grid.setColumnStretch(1, 2)
            self.grid.setColumnStretch(2, 0)
            self.grid.setRowStretch(0, 1)
        else:
            self.grid.addWidget(self.orientation, 0, 0, 2, 1)
            self.grid.addWidget(self.operating_scroll, 0, 1)
            self.grid.addWidget(self.amdx_now, 0, 2)
            self.grid.addWidget(self.safety, 1, 1, 1, 2)
            self.grid.setColumnStretch(0, 0)
            self.grid.setColumnStretch(1, 3)
            self.grid.setColumnStretch(2, 2)
            self.grid.setRowStretch(0, 1)

    def load_context(self, run) -> None:
        safety_text = self.safety.load_run(run)
        self.amdx_now.refresh_projection(self.amdx_source.decision_projection())
        self.orientation.load_context(
            run,
            self.amdx_source.decision_projection(),
            safety_text,
        )

    def _projection_changed(self, projection) -> None:
        self.amdx_now.refresh_projection(projection)
        run = self.amdx_source.run
        self.orientation.load_context(run, projection, self.safety.summary_label.text())
