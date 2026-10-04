from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QApplication
)



from ict_cockpit.gui.context_step import ContextStep
from ict_cockpit.gui.bias_step import BiasStep
from ict_cockpit.gui.draw_thesis_step import DrawThesisStep
from ict_cockpit.analysis.tda import TDARecord

class TDAWorkflowWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.current_step = 0

        self.step_titles = [
            "Context",
            "Bias",
            "Draw / Thesis",
        ]

        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.step_stack = QStackedWidget()

        self.context_step = ContextStep()
        self.bias_step = BiasStep()
        self.draw_thesis_step = DrawThesisStep()

        self.context_step.next_requested.connect(self.go_next)
        self.context_step.back_requested.connect(self.go_back)
        
        self.bias_step.next_requested.connect(self.go_next)
        self.bias_step.back_requested.connect(self.go_back)

        self.draw_thesis_step.next_requested.connect(self.go_next)
        self.draw_thesis_step.back_requested.connect(self.go_back)

        self.step_stack.addWidget(self.context_step)
        self.step_stack.addWidget(self.bias_step)
        self.step_stack.addWidget(self.draw_thesis_step)


        self.back_button = QPushButton("← Back")
        self.next_button = QPushButton("Next →")

        self.back_button.clicked.connect(self.go_back)
        self.next_button.clicked.connect(self.go_next)


        navigation_layout = QHBoxLayout()
        navigation_layout.addWidget(self.back_button)
        navigation_layout.addStretch()
        navigation_layout.addWidget(self.next_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.step_stack, 1)
        main_layout.addLayout(navigation_layout)

        self.setLayout(main_layout)

        self._update_view()

        app = QApplication.instance()

        if app is not None:
            app.installEventFilter(self)

    def _create_placeholder_step(self, title: str) -> QWidget:
        page = QWidget()

        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

        page.setLayout(layout)

        return page

    def go_next(self) -> None:
        if self.current_step < len(self.step_titles) - 1:
            self.current_step += 1
            self._update_view()

    def go_back(self) -> None:
        if self.current_step > 0:
            self.current_step -= 1
            self._update_view()

    def _update_view(self) -> None:
        self.step_stack.setCurrentIndex(self.current_step)

        step_number = self.current_step + 1
        total_steps = len(self.step_titles)
        current_title = self.step_titles[self.current_step]

        self.progress_label.setText(
            f"Step {step_number} of {total_steps} — {current_title}"
        )

        self.back_button.setEnabled(self.current_step > 0)

        if self.current_step == total_steps - 1:
            self.next_button.setText("Complete")
            self.next_button.setEnabled(False)
        else:
            self.next_button.setText("Next →")
            self.next_button.setEnabled(True)
    def eventFilter(self, watched, event) -> bool:
        if isinstance(watched, QWidget):
            belongs_to_workflow = (
                watched is self
                or self.isAncestorOf(watched)
            )

            if belongs_to_workflow:
                if event.type() == QEvent.Type.MouseButtonRelease:
                    if event.button() == Qt.MouseButton.BackButton:
                        self.go_back()
                        return True

                    if event.button() == Qt.MouseButton.ForwardButton:
                        self.go_next()
                        return True

                if event.type() == QEvent.Type.Wheel:
                    delta = event.angleDelta()

                    if abs(delta.x()) > abs(delta.y()) and delta.x() != 0:
                        if delta.x() < 0:
                            self.go_next()
                        else:
                            self.go_back()

                        return True

        return super().eventFilter(watched, event)
    
    def build_tda_record(self) -> TDARecord:
        weekly_bias = self.bias_step.weekly_bias()
        daily_bias = self.bias_step.daily_bias()

        if weekly_bias is None:
            raise ValueError("Weekly bias must be selected")

        if daily_bias is None:
            raise ValueError("Daily bias must be selected")

        return TDARecord(
            analysis_date=self.context_step.analysis_date(),
            instrument=self.context_step.instrument(),
            weekly_bias=weekly_bias,
            daily_bias=daily_bias,
            primary_draw=self.draw_thesis_step.primary_draw(),
            secondary_draw=self.draw_thesis_step.secondary_draw(),
            narrative=self.draw_thesis_step.narrative(),
        )