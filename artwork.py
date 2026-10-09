"""Original vector artwork, drawn locally without game assets."""
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPolygonF, QPen, QLinearGradient, QPainterPath
from PySide6.QtWidgets import QWidget

class Artwork(QWidget):
    def __init__(self,game,parent=None):
        super().__init__(parent)
        self.game=game
        self.setMinimumHeight(124)
        self.setMaximumHeight(152)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(self.width()/400,self.height()/160)
        accent=QColor(self.game.accent)
        gradient=QLinearGradient(0,0,400,160)
        gradient.setColorAt(0,QColor('#273345'))
        gradient.setColorAt(1,QColor('#151c29'))
        p.fillRect(QRectF(0,0,400,160),gradient)
        def poly(points,color):
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor(color))
            p.drawPolygon(QPolygonF([QPointF(x,y) for x,y in points]))
        if self.game.id=='webfishing':
            p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor('#d9dbad'));p.drawEllipse(QPointF(295,39),22,22)
            poly([(0,98),(70,28),(140,99),(218,49),(319,107),(400,70),(400,160),(0,160)],'#455c55')
            poly([(0,114),(96,62),(165,122),(272,90),(400,119),(400,160),(0,160)],'#2b4342')
            poly([(0,122),(125,105),(210,120),(400,113),(400,160),(0,160)],'#557881')
            poly([(0,125),(123,134),(86,160),(0,160)],'#293c39')
            for x,y in [(35,73),(65,89),(362,84)]:
                poly([(x,y-32),(x-17,y+16),(x+17,y+16)],'#243e36')
            p.setPen(QPen(QColor('#cde1c9'),2));p.drawLine(QPointF(86,126),QPointF(144,81));p.drawLine(QPointF(144,81),QPointF(194,143))
            p.setPen(QPen(QColor('#91b5ba'),1))
            for x,y,w in [(228,132,42),(151,152,31),(311,147,52)]:p.drawLine(QPointF(x,y),QPointF(x+w,y))
        elif self.game.id=='maxpayne':
            for i,h in enumerate([61,89,55,106,71,83,113,48,76,95]):
                x=i*43;poly([(x,160),(x,160-h),(x+32,160-h),(x+32,160)],'#303442')
                p.setPen(QPen(QColor('#96716c'),2))
                for y in range(168-h,142,13):p.drawLine(QPointF(x+10,y),QPointF(x+17,y))
            p.setPen(QPen(QColor('#667080'),1))
            for x in range(5,420,27):p.drawLine(QPointF(x,0),QPointF(x-55,160))
            poly([(170,160),(182,99),(177,83),(182,65),(199,65),(205,83),(198,101),(219,160)],'#0c121d')
        else:
            p.setPen(QPen(QColor('#485375'),1))
            for x in range(-160,500,42):p.drawLine(QPointF(x,160),QPointF(200+(x-200)*.3,96))
            for y in [103,118,137,157]:p.drawLine(QPointF(0,y),QPointF(400,y))
            p.setPen(QPen(accent,2));p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(204,71),45,45);p.drawEllipse(QPointF(204,71),52,52)
            heart=QPainterPath(QPointF(204,95))
            heart.cubicTo(130,47,184,30,204,58);heart.cubicTo(225,30,276,47,204,95)
            p.setBrush(accent);p.setPen(Qt.PenStyle.NoPen);p.drawPath(heart)
            p.setPen(QPen(QColor('#e0daf7'),4));p.drawLine(QPointF(240,91),QPointF(290,129));p.drawLine(QPointF(278,119),QPointF(284,110));p.drawLine(QPointF(287,126),QPointF(293,117))
            p.setPen(QPen(accent,1))
            for x,y in [(59,33),(124,52),(329,41),(296,20)]:
                p.drawLine(QPointF(x-3,y),QPointF(x+3,y));p.drawLine(QPointF(x,y-3),QPointF(x,y+3))
        p.setPen(QPen(QColor(255,255,255,9),1))
        for y in range(0,160,4):p.drawLine(QPointF(0,y),QPointF(400,y))
        p.end()
