"""Original box art; attribution in assets/covers/sources.json."""
from pathlib import Path
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

class Artwork(QWidget):
    _cache = {}
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.setFixedHeight(230)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAccessibleName('Portada de '+game.title)
        if game.id not in self._cache:
            folder=Path(__file__).resolve().parent/'assets/covers'
            path=folder/(game.id+('.jpg' if game.id in ('webfishing','maxpayne','ror2') else '.png'))
            self._cache[game.id]=QPixmap(str(path))
        self.pixmap=self._cache[game.id]
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(),QColor('#10151e'))
        if not self.pixmap.isNull():
            size=self.pixmap.size().scaled(self.size(),Qt.AspectRatioMode.KeepAspectRatio)
            target=QRectF((self.width()-size.width())/2,(self.height()-size.height())/2,size.width(),size.height())
            painter.drawPixmap(target,self.pixmap,QRectF(self.pixmap.rect()))
        painter.end()
