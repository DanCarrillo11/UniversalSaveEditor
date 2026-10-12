"""Original box art; attribution in assets/covers/sources.json."""
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPixmap, QPainterPath
from PySide6.QtWidgets import QWidget

class Artwork(QWidget):
    _cache = {}
    _platform_crop = {'bbs':0.065}
    def __init__(self, game, parent=None, height=230, crop=False):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.crop=crop;self.game_id=game.id
        self._highlight=0.0
        self.hover_animation=QPropertyAnimation(self,b'hoverHighlight',self)
        self.hover_animation.setDuration(140)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.top_crop_ratio=self._platform_crop.get(game.id,0)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAccessibleName('Cover art for '+game.title)
        if game.id not in self._cache:
            folder=Path(__file__).resolve().parent/'assets/covers'
            extension = '.svg' if game.id in ('ddd','kh3') else '.jpg' if game.id in ('webfishing','maxpayne','ror2','alice','re4_2005') else '.png'
            path=folder/(game.id+extension)
            self._cache[game.id]=QPixmap(str(path))
        self.pixmap=self._cache[game.id]
    def get_highlight(self):return self._highlight
    def set_highlight(self,value):
        self._highlight=value;self.update()
    hoverHighlight=Property(float,get_highlight,set_highlight)
    def set_hovered(self,hovered,animated=True):
        self.hover_animation.stop()
        target=0.08 if hovered else 0.0
        if not animated:self.set_highlight(target);return
        self.hover_animation.setStartValue(self._highlight)
        self.hover_animation.setEndValue(target)
        self.hover_animation.start()
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        outline=QPainterPath();outline.addRoundedRect(QRectF(self.rect()),8,8);painter.setClipPath(outline)
        painter.fillRect(self.rect(),QColor('#10151e'))
        if not self.pixmap.isNull():
            crop_y=self.pixmap.height()*self.top_crop_ratio
            source=QRectF(0,crop_y,self.pixmap.width(),self.pixmap.height()-crop_y)
            mode=Qt.AspectRatioMode.KeepAspectRatioByExpanding if self.crop else Qt.AspectRatioMode.KeepAspectRatio
            size=source.size().toSize().scaled(self.size(),mode)
            target=QRectF((self.width()-size.width())/2,(self.height()-size.height())/2,size.width(),size.height())
            painter.drawPixmap(target,self.pixmap,source)
        if self._highlight:painter.fillRect(self.rect(),QColor(255,255,255,round(255*self._highlight)))
        painter.end()
