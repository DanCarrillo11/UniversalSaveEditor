"""Original box art; attribution in assets/covers/sources.json."""
from pathlib import Path
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

class Artwork(QWidget):
    _cache = {}
    _platform_crop = {'bbs':0.065}
    def __init__(self, game, parent=None, height=230, crop=False):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.crop=crop;self.game_id=game.id
        self.top_crop_ratio=self._platform_crop.get(game.id,0)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAccessibleName('Cover art for '+game.title)
        if game.id not in self._cache:
            folder=Path(__file__).resolve().parent/'assets/covers'
            path=folder/(game.id+('.jpg' if game.id in ('webfishing','maxpayne','ror2','alice') else '.png'))
            self._cache[game.id]=QPixmap(str(path))
        self.pixmap=self._cache[game.id]
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(),QColor('#10151e'))
        if not self.pixmap.isNull():
            crop_y=self.pixmap.height()*self.top_crop_ratio
            source=QRectF(0,crop_y,self.pixmap.width(),self.pixmap.height()-crop_y)
            mode=Qt.AspectRatioMode.KeepAspectRatioByExpanding if self.crop else Qt.AspectRatioMode.KeepAspectRatio
            size=source.size().toSize().scaled(self.size(),mode)
            target=QRectF((self.width()-size.width())/2,(self.height()-size.height())/2,size.width(),size.height())
            painter.drawPixmap(target,self.pixmap,source)
        painter.end()
