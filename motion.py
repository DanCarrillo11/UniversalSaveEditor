"""Short, interruptible interface transitions. SPDX-License-Identifier: GPL-3.0-or-later."""
from PySide6.QtCore import QObject, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsOpacityEffect


class ViewTransition(QObject):
    """Fade one incoming view without delaying navigation or rebuilding widgets."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.enabled=True
        self.widget=None
        self.animation=None

    def stop(self):
        if self.animation is not None:
            self.animation.stop()
            self.animation.deleteLater()
            self.animation=None
        if self.widget is not None:
            self.widget.setGraphicsEffect(None)
            self.widget=None

    def fade(self, widget):
        self.stop()
        if not self.enabled or not widget.isVisible():return
        self.widget=widget
        effect=QGraphicsOpacityEffect(widget)
        effect.setOpacity(0.35)
        widget.setGraphicsEffect(effect)
        animation=QPropertyAnimation(effect,b'opacity',self)
        animation.setDuration(160)
        animation.setStartValue(0.35);animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(self.stop)
        self.animation=animation
        animation.start()
