"""Accessible, scale-independent cover favorite button. SPDX-License-Identifier: GPL-3.0-or-later."""
import math
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QPushButton


class FavoriteButton(QPushButton):
    def __init__(self, title, checked=False, parent=None):
        super().__init__(parent)
        self.title=title
        self.setObjectName('favoriteButton')
        self.setFixedSize(32,32)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggled.connect(self.update_label)
        self.update_label()

    def update_label(self):
        action='Remove from favorites' if self.isChecked() else 'Add to favorites'
        self.setToolTip(action)
        self.setAccessibleName(action+': '+self.title)
        self.update()

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor('#93C5FF'),1.5) if self.hasFocus() else Qt.PenStyle.NoPen)
        painter.setBrush(QColor(23,23,25,235 if self.underMouse() else 205))
        painter.drawRoundedRect(QRectF(1,1,30,30),10,10)
        star=QPainterPath()
        for index in range(10):
            angle=-math.pi/2+index*math.pi/5
            radius=9 if index%2==0 else 4.2
            x,y=16+math.cos(angle)*radius,16+math.sin(angle)*radius
            if index==0:star.moveTo(x,y)
            else:star.lineTo(x,y)
        star.closeSubpath()
        color=QColor('#93C5FF' if self.isChecked() else '#FFFFFF')
        painter.setPen(QPen(color,1.5))
        painter.setBrush(color if self.isChecked() else Qt.BrushStyle.NoBrush)
        painter.drawPath(star)
        painter.end()
