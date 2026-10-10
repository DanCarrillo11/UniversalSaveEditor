"""UniversalSaveEditor desktop interface. SPDX-License-Identifier: GPL-3.0-or-later."""
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QStackedWidget, QComboBox,
    QTabWidget, QCheckBox, QMessageBox, QFileDialog, QDialog, QTextEdit,
)
from core import Save, discover, read_limited, export_copy, replace_current
from catalog import GAMES, BY_ID
from artwork import Artwork

ROOT=Path(__file__).resolve().parent

def label(text,name='',wrap=False):
    item=QLabel(text)
    item.setTextFormat(Qt.TextFormat.PlainText)
    item.setObjectName(name)
    item.setWordWrap(wrap)
    return item

def button(text,callback,name=''):
    item=QPushButton(text)
    item.setObjectName(name)
    item.setCursor(Qt.CursorShape.PointingHandCursor)
    item.clicked.connect(callback)
    return item

def layout(widget,vertical=True,margins=0,spacing=12):
    result=QVBoxLayout(widget) if vertical else QHBoxLayout(widget)
    result.setContentsMargins(margins,margins,margins,margins)
    result.setSpacing(spacing)
    return result

def clear(box):
    while box.count():
        item=box.takeAt(0)
        if item.widget():
            item.widget().hide()
            item.widget().deleteLater()
        elif item.layout():clear(item.layout())

def number_text(value):
    return str(int(value)) if float(value).is_integer() else str(value)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UniversalSaveEditor — tu biblioteca de partidas')
        self.resize(1320,900)
        self.setMinimumSize(1060,740)
        self.setAcceptDrops(True)
        self.setStyleSheet((ROOT/'theme.qss').read_text(encoding='utf-8'))
        self.files=[];self.save=None;self.path=None;self.inputs={};self.edits={}
        self.exported_state=None;self.slot_index=0;self.filter='all';self.selected_game=None
        root=QWidget();self.setCentralWidget(root)
        shell=layout(root,False,0,0)
        side=QFrame();side.setObjectName('sidebar');side.setFixedWidth(218)
        nav=layout(side,True,20,12)
        nav.addSpacing(12)
        nav.addWidget(label('Universal\nSaveEditor','brand'))
        nav.addWidget(label('TU PRÓXIMO PUNTO DE GUARDADO','small',True))
        nav.addSpacing(30)
        nav.addWidget(label('ESPACIO PERSONAL','eyebrow'))
        self.library_nav=button('Biblioteca',self.show_library,'nav');self.library_nav.setCheckable(True)
        self.editor_nav=button('Editor de partida',self.show_editor,'nav');self.editor_nav.setCheckable(True);self.editor_nav.setEnabled(False)
        nav.addWidget(self.library_nav);nav.addWidget(self.editor_nav)
        nav.addSpacing(24)
        nav.addWidget(label('COLECCIONES','eyebrow'))
        for name in ('WEBFISHING','KINGDOM HEARTS','MAX PAYNE'):
            nav.addWidget(button(name.title(),lambda checked=False,n=name:self.collection(n),'nav'))
        nav.addStretch()
        nav.addWidget(label('TUS PARTIDAS, A SALVO','eyebrow'))
        nav.addWidget(label('Local. Sin cuentas.\nEl original siempre se conserva.','muted',True))
        nav.addSpacing(8)
        nav.addWidget(button('Guía de uso',self.open_guide))
        nav.addWidget(label('v0.3  /  EN DESARROLLO','small'))
        shell.addWidget(side)
        self.stack=QStackedWidget();shell.addWidget(self.stack,1)
        self.build_library();self.build_editor()
        self.statusBar().showMessage('Listo · Procesamiento local')
        QShortcut(QKeySequence('Ctrl+O'),self,activated=self.open_file)
        QShortcut(QKeySequence('Ctrl+Return'),self,activated=self.review)
        QShortcut(QKeySequence('Ctrl+F'),self,activated=lambda:(self.show_library(),self.search.setFocus()))
        self.scan();self.show_library()

    def build_library(self):
        page=QWidget();box=layout(page,True,30,18)
        top=QHBoxLayout()
        titlebox=QVBoxLayout();titlebox.addWidget(label('TU ESPACIO DE GUARDADO','eyebrow'));titlebox.addWidget(label('Biblioteca','title'))
        top.addLayout(titlebox);top.addStretch()
        top.addWidget(button('Actualizar',self.scan))
        top.addWidget(button('+  Abrir partida',self.open_file,'primary'))
        box.addLayout(top)
        box.addWidget(label('Un lugar para ajustar tu progreso y volver a tus mundos favoritos.','muted'))
        strip=QFrame();strip.setObjectName('panel');stats=layout(strip,False,18,24)
        self.available=label('02  EDITORES DISPONIBLES','success')
        self.detected=label('00  ARCHIVOS DETECTADOS','muted')
        stats.addWidget(self.available);stats.addWidget(self.detected);stats.addStretch();stats.addWidget(label('COPIAS ANTES QUE CAMBIOS','small'))
        box.addWidget(strip)
        tools=QHBoxLayout()
        self.search=QLineEdit();self.search.setPlaceholderText('Buscar un juego…');self.search.setAccessibleName('Buscar juegos');self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.render_cards)
        tools.addWidget(self.search,1)
        self.filter_buttons=[]
        for key,text in [('all','Todos'),('ready','Disponibles'),('pending','Próximamente')]:
            b=button(text,lambda checked=False,k=key:self.set_filter(k),'filter');b.setCheckable(True);b.setChecked(key=='all')
            self.filter_buttons.append((key,b));tools.addWidget(b)
        box.addLayout(tools)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        content=QWidget();self.grid=QGridLayout(content);self.grid.setContentsMargins(0,0,8,0);self.grid.setSpacing(18)
        scroll.setWidget(content);box.addWidget(scroll,1)
        box.addWidget(label('Disponible = edición implementada. La validación dentro de cada juego sigue en curso.','small',True))
        self.stack.addWidget(page)

    def build_editor(self):
        page=QWidget();outer=layout(page,True,28,14)
        top=QHBoxLayout();titles=QVBoxLayout()
        self.editor_eyebrow=label('EDITOR DE PARTIDA','eyebrow');self.editor_title=label('Tu partida','title')
        titles.addWidget(self.editor_eyebrow);titles.addWidget(self.editor_title);top.addLayout(titles);top.addStretch()
        top.addWidget(button('Abrir otra…',self.open_file));outer.addLayout(top)
        self.editor_subtitle=label('','muted',True);outer.addWidget(self.editor_subtitle)
        self.file_combo=QComboBox();self.file_combo.setAccessibleName('Archivo de partida');self.file_combo.activated.connect(self.select_file)
        outer.addWidget(self.file_combo)
        self.slot_combo=QComboBox();self.slot_combo.setAccessibleName('Registro dentro de la partida');self.slot_combo.activated.connect(self.change_slot)
        outer.addWidget(self.slot_combo)
        self.warning=label('','warning',True);outer.addWidget(self.warning)
        self.repair=QCheckBox('Reparar la comprobación de integridad al exportar la copia')
        self.repair.toggled.connect(self.update_summary);outer.addWidget(self.repair)
        body=QHBoxLayout();body.setSpacing(22)
        self.tabs=QTabWidget();self.tabs.setUsesScrollButtons(True);body.addWidget(self.tabs,1)
        side=QFrame();side.setObjectName('panel');side.setFixedWidth(275);summary=layout(side,True,18,12)
        summary.addWidget(label('ANTES DE GUARDAR','eyebrow'))
        self.change_count=label('Sin cambios','section');summary.addWidget(self.change_count)
        summary.addWidget(label('Compara los ajustes con el archivo que abriste.','muted',True))
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        self.summary_content=QWidget();self.summary_box=layout(self.summary_content,True,0,10)
        scroll.setWidget(self.summary_content);summary.addWidget(scroll,1)
        summary.addWidget(label('01  Revisa los valores\n02  Elige otro archivo\n03  Conserva tu respaldo','small',True))
        self.review_button=button('Revisar y exportar  →',self.review,'primary');summary.addWidget(self.review_button)
        self.reset_button=button('Restablecer cambios',self.reset);summary.addWidget(self.reset_button)
        body.addWidget(side);outer.addLayout(body,1)
        self.install_note=label('','small',True);outer.addWidget(self.install_note)
        self.stack.addWidget(page)

    def scan(self):
        try:self.files=discover()
        except OSError as error:
            QMessageBox.warning(self,'No se pudo buscar',str(error));return
        self.detected.setText(f'{len(self.files):02d}  ARCHIVOS DETECTADOS')
        self.render_cards()
        self.statusBar().showMessage(f'{len(self.files)} archivos encontrados en las carpetas habituales · Arrastra un archivo para abrirlo')

    def set_filter(self,key):
        self.filter=key
        for item,b in self.filter_buttons:b.setChecked(item==key)
        self.render_cards()

    def collection(self,name):
        self.set_filter('all');self.search.setText(name);self.show_library()

    def render_cards(self):
        if not hasattr(self,'grid'):return
        clear(self.grid)
        for row in range(self.grid.rowCount()):self.grid.setRowStretch(row,0)
        search=self.search.text().casefold().strip()
        games=[g for g in GAMES if search in (g.title+' '+g.subtitle+' '+g.family+' '+g.description).casefold() and (self.filter=='all' or g.editable==(self.filter=='ready'))]
        self.visible_games=[g.id for g in games]
        for index,game in enumerate(games):
            card=QFrame();card.setObjectName('card');card.setMinimumWidth(240)
            box=layout(card,True,14,9)
            box.addWidget(Artwork(game))
            row=QHBoxLayout();row.addWidget(label('EDITOR DISPONIBLE' if game.editable else 'EN DESARROLLO','badge' if game.editable else 'pending'));row.addStretch();box.addLayout(row)
            box.addWidget(label(game.title,'section',True));box.addWidget(label(game.subtitle,'muted',True))
            features=label(game.description,'cardDescription',True)
            features.setAccessibleName('Funciones del editor de '+game.title)
            box.addWidget(features)
            count=sum(g==game.id for g,p in self.files)
            box.addWidget(label(f'{count} archivo'+('s' if count!=1 else '')+' detectado'+('s' if count!=1 else '') if count else 'Sin partidas detectadas','small'))
            box.addWidget(button('Abrir editor  →' if game.editable else 'Ver compatibilidad',lambda checked=False,g=game:self.select_game(g)))
            self.grid.addWidget(card,index//3,index%3)
        if not games:
            empty=label('No encontramos ese juego.\nPrueba con otro nombre o cambia el filtro.','muted',True)
            self.grid.addWidget(empty,0,0,1,3)
        for col in range(3):self.grid.setColumnStretch(col,1)
        self.grid.setRowStretch((len(games)+2)//3,1)

    def show_library(self):
        self.stack.setCurrentIndex(0);self.library_nav.setChecked(True);self.editor_nav.setChecked(False)

    def show_editor(self):
        if self.save:
            self.stack.setCurrentIndex(1);self.library_nav.setChecked(False);self.editor_nav.setChecked(True)

    def select_game(self,game):
        if not game.editable:
            QMessageBox.information(self,game.title,'Compatibilidad pendiente\n\n'+game.description+'\n\nLa edición de este juego todavía no está disponible.');return
        if self.save and self.save.game==game.id:self.show_editor();return
        files=[p for g,p in self.files if g==game.id]
        if files:self.load(game.id,files[0])
        else:self.open_file(game.id)

    def open_file(self,game=None):
        if not isinstance(game,str):game=None
        filename,_=QFileDialog.getOpenFileName(self,'Abrir una partida','', 'Partidas (*.sav *.png *.xml);;Todos los archivos (*)')
        if filename:self.open_path(Path(filename),game)

    def open_path(self,path,game=None):
        if game is None:
            name=path.name.lower()
            if name.startswith(('khrecom','kh2','khbbs')):
                QMessageBox.information(self,'Formato pendiente','Ese juego todavía no tiene un editor disponible.');return
            game={'.sav':'webfishing','.xml':'ror2'}.get(path.suffix.lower(),'kh1')
        self.load(game,path)

    def state_signature(self):
        return (tuple(sorted(self.edits.items())),self.repair.isChecked())

    def may_discard(self):
        if not self.edits and not self.repair.isChecked():return True
        if self.state_signature()==self.exported_state:return True
        return QMessageBox.question(self,'Cambios sin exportar','¿Descartar los cambios de esta partida?',QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)==QMessageBox.StandardButton.Discard

    def load(self,game,path):
        if not self.may_discard():return False
        try:save=Save(read_limited(path),game)
        except (ValueError,OSError) as error:
            QMessageBox.warning(self,'No se pudo abrir la partida',str(error));return False
        self.save=save;self.path=Path(path);self.edits={};self.inputs={};self.exported_state=None;self.slot_index=0
        gameinfo=BY_ID[game];self.selected_game=game
        self.editor_title.setText(gameinfo.title)
        self.editor_eyebrow.setText('EDITOR / '+gameinfo.subtitle.upper())
        self.editor_subtitle.setText(gameinfo.description)
        if game in ('webfishing','ror2'):
            self.review_button.setText('Revisar y aplicar  →')
            self.install_note.setText('Aplicar reemplaza el archivo activo y conserva un respaldo exacto junto al original.')
        else:
            self.review_button.setText('Revisar y exportar  →')
            self.install_note.setText('Exportar crea una partida editada y un respaldo del original. No instala la copia en el juego.')
        self.file_combo.blockSignals(True);self.file_combo.clear()
        paths=[p for g,p in self.files if g==game]
        if self.path not in paths:paths.append(self.path)
        for p in paths:self.file_combo.addItem(p.name,p)
        self.file_combo.setCurrentIndex(paths.index(self.path));self.file_combo.setToolTip(str(self.path));self.file_combo.blockSignals(False)
        self.slot_combo.blockSignals(True);self.slot_combo.clear()
        self.slot_combo.addItems([s.name for s in save.slots]);self.slot_combo.blockSignals(False)
        self.warning.setText('\n'.join(save.warnings));self.warning.setVisible(bool(save.warnings))
        self.repair.blockSignals(True);self.repair.setChecked(False);self.repair.setVisible(bool(save.warnings));self.repair.blockSignals(False)
        self.editor_nav.setEnabled(True)
        self.render_fields();self.show_editor()
        self.statusBar().showMessage(f'{self.path.name} · Original conservado · Edición en memoria')
        return True

    def select_file(self,index):
        target=self.file_combo.itemData(index)
        if not self.load(self.save.game,target):
            self.file_combo.setCurrentIndex(self.file_combo.findData(self.path))

    def change_slot(self,index):
        if self.save and index>=0:self.slot_index=index;self.render_fields()

    def render_fields(self):
        self.inputs={}
        while self.tabs.count():
            widget=self.tabs.widget(0);self.tabs.removeTab(0);widget.deleteLater()
        groups={}
        for field in self.save.slots[self.slot_index].fields:
            if self.save.game=='webfishing':group='Cebos' if field.key.startswith('bait:') else 'Economía'
            else:group={'0':'Sora','1':'Donald','2':'Goofy'}.get(field.key.split(':')[0],'Economía')
            group=field.group or group
            groups.setdefault(group,[]).append(field)
        for name,fields in groups.items():
            scroll=QScrollArea();scroll.setWidgetResizable(True)
            content=QWidget();box=layout(content,True,4,12)
            box.addWidget(label(name,'section'))
            box.addWidget(label('Solo se modificarán los campos que cambies.','muted',True))
            for field in fields:
                row=QFrame();row.setObjectName('field');line=layout(row,False,8,16)
                caption=QVBoxLayout();caption.addWidget(label(field.label));caption.addWidget(label(f'Original: {number_text(field.value)}  ·  Rango: {field.minimum:,}–{field.maximum:,}','small',True))
                line.addLayout(caption,1)
                key=(self.slot_index,field.key)
                entry=QLineEdit(self.edits.get(key,number_text(field.value)))
                entry.setAccessibleName(field.label);entry.setFixedWidth(130);entry.setAlignment(Qt.AlignmentFlag.AlignRight)
                entry.textChanged.connect(lambda text,k=key,f=field,e=entry:self.edit_changed(k,f,e,text))
                self.inputs[key]=entry;line.addWidget(entry)
                box.addWidget(row);self.mark_entry(entry,field,entry.text())
            box.addStretch();scroll.setWidget(content);self.tabs.addTab(scroll,name)
        self.update_summary()

    def mark_entry(self,entry,field,text):
        changed=text.strip()!=number_text(field.value)
        try:value=field.parse(text);valid=True
        except ValueError:valid=False
        entry.setProperty('invalid',changed and not valid);entry.setProperty('changed',changed)
        entry.style().unpolish(entry);entry.style().polish(entry)

    def edit_changed(self,key,field,entry,text):
        if text.strip()==number_text(field.value):self.edits.pop(key,None)
        else:self.edits[key]=text
        self.mark_entry(entry,field,text);self.update_summary()

    def validated_changes(self):
        changes={}
        for (index,key),text in self.edits.items():
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            try:value=field.parse(text)
            except ValueError as error:raise ValueError(f'{field.label}: {error}')
            if not field.minimum<=value<=field.maximum:raise ValueError(f'{field.label}: usa un valor entre {field.minimum} y {field.maximum}.')
            changes[(index,key)]=value
        return changes

    def update_summary(self):
        if not hasattr(self,'summary_box'):return
        clear(self.summary_box)
        count=len(self.edits)
        self.change_count.setText(f'{count:02d} cambio'+('s' if count!=1 else '') if count else 'Sin cambios')
        for (index,key),text in self.edits.items():
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            item=label(f'{field.label}\n{number_text(field.value)}  →  {text or "…"}','',True)
            self.summary_box.addWidget(item)
            if len(self.save.slots)>1:self.summary_box.addWidget(label(self.save.slots[index].name,'small',True))
        if not count:self.summary_box.addWidget(label('Los ajustes que hagas aparecerán aquí.','muted',True))
        if self.repair.isChecked():self.summary_box.addWidget(label('Se reparará el CRC en la copia.','success',True))
        valid=True
        try:self.validated_changes()
        except ValueError as error:
            valid=False;self.summary_box.addWidget(label(str(error),'warning',True))
        self.summary_box.addStretch()
        has_work=bool(count or self.repair.isChecked())
        can_repair=not self.save or not self.save.warnings or self.repair.isChecked()
        self.review_button.setEnabled(bool(self.save and has_work and valid and can_repair))
        self.reset_button.setEnabled(has_work)

    def reset(self):
        if self.save and self.may_discard():
            self.edits={};self.exported_state=None;self.repair.setChecked(False);self.render_fields()

    def review(self):
        if not self.save or not self.review_button.isEnabled():return
        try:output=self.save.patched(self.validated_changes(),repair_crc=self.repair.isChecked())
        except ValueError as error:
            QMessageBox.warning(self,'Revisa los ajustes',str(error));return
        direct=self.save.game in ('webfishing','ror2')
        dialog=QDialog(self);dialog.setWindowTitle('Revisar y aplicar' if direct else 'Revisar y exportar');dialog.resize(650,550)
        box=layout(dialog,True,24,16)
        box.addWidget(label('UN ÚLTIMO VISTAZO','eyebrow'));box.addWidget(label('Tu nueva partida','title'))
        box.addWidget(label('Reemplazaremos el save slot actual y conservaremos un respaldo exacto del original.' if direct else 'Crearemos otro archivo y un respaldo exacto del original.','muted',True))
        text=QTextEdit();text.setReadOnly(True)
        lines=[]
        for (index,key),value in self.validated_changes().items():
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            lines.append(f'{self.save.slots[index].name}\n{field.label}: {number_text(field.value)} → {value}')
        if self.repair.isChecked():lines.append('Reparar el CRC del bloque de guardado en la copia.')
        text.setPlainText('\n\n'.join(lines));box.addWidget(text,1)
        box.addWidget(label('La carga dentro del juego aún necesita validación.','small',True))
        actions=QHBoxLayout();actions.addWidget(button('Volver',dialog.reject));actions.addStretch()
        def write():
            if direct:
                try:backup=replace_current(self.path,self.save.raw,output)
                except (ValueError,OSError) as error:
                    QMessageBox.warning(dialog,'No se pudo aplicar',str(error));return
                self.exported_state=self.state_signature();dialog.accept()
                QMessageBox.information(self,'Cambios aplicados',f'Partida activa reemplazada:\n{self.path}\n\nRespaldo original:\n{backup}')
                self.load(self.save.game,self.path)
                self.statusBar().showMessage('Cambios aplicados a WEBFISHING · Respaldo original conservado')
                return
            filename,_=QFileDialog.getSaveFileName(dialog,'Exportar copia',str(self.path.parent/(self.path.stem+'.edited'+self.path.suffix)),f'Partida (*{self.path.suffix})')
            if not filename:return
            try:backup=export_copy(self.path,self.save.raw,output,filename)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'No se pudo exportar',str(error));return
            self.exported_state=self.state_signature();dialog.accept()
            self.statusBar().showMessage('Copia exportada y verificada · Original intacto')
            QMessageBox.information(self,'Copia lista',f'Partida editada:\n{filename}\n\nRespaldo original:\n{backup}\n\nConsulta la guía para probarla dentro del juego.')
        actions.addWidget(button('Aplicar al save slot actual' if direct else 'Elegir destino y exportar',write,'primary'));box.addLayout(actions)
        dialog.exec()

    def open_guide(self):
        dialog=QDialog(self);dialog.setWindowTitle('Guía de UniversalSaveEditor');dialog.resize(760,650)
        box=layout(dialog,True,24,16);box.addWidget(label('Antes de volver al juego','title'))
        text=QTextEdit();text.setReadOnly(True);text.setMarkdown((ROOT/'README.md').read_text(encoding='utf-8'))
        box.addWidget(text,1);box.addWidget(button('Entendido',dialog.accept));dialog.exec()

    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls() and len(event.mimeData().urls())==1 and event.mimeData().urls()[0].isLocalFile():event.acceptProposedAction()

    def dropEvent(self,event):
        self.open_path(Path(event.mimeData().urls()[0].toLocalFile()));event.acceptProposedAction()

    def closeEvent(self,event):
        if self.may_discard():event.accept()
        else:event.ignore()

def main():
    app=QApplication(sys.argv)
    app.setApplicationName('UniversalSaveEditor');app.setOrganizationName('UniversalSaveEditor')
    app.setWindowIcon(QIcon(str(ROOT/'assets/memory-card-icon.png')))
    app.setStyle('Fusion')
    window=Window();window.show()
    if '--smoke-test' in sys.argv:
        # Used by release validation; exercises the packaged resources and Qt.
        import json
        destination=Path(sys.argv[sys.argv.index('--smoke-test')+1])
        def check_startup():
            covers={g.id:not Artwork._cache[g.id].isNull() for g in GAMES}
            report={'title':window.windowTitle(),'covers':covers,
                    'games':len(window.visible_games),'icon':not app.windowIcon().isNull(),
                    'frozen':bool(getattr(sys,'frozen',False))}
            destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
            window.grab().save(str(destination.with_suffix('.png')))
            app.exit(0 if all(covers.values()) else 1)
        QTimer.singleShot(1000,check_startup)
    sys.exit(app.exec())

if __name__=='__main__':main()
