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
from ror2_unlocks import UNLOCK_IDS

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

def value_text(field,value):
    if field.fmt == 'xml-unlock':
        return 'Unlocked' if int(value) else 'Locked'
    try:return number_text(value)
    except (TypeError,ValueError):return str(value)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UniversalSaveEditor — your save library')
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
        nav.addWidget(label('YOUR NEXT SAVE POINT','small',True))
        nav.addSpacing(30)
        nav.addWidget(label('PERSONAL SPACE','eyebrow'))
        self.library_nav=button('Save library',self.show_library,'nav');self.library_nav.setCheckable(True)
        self.editor_nav=button('Save editor',self.show_editor,'nav');self.editor_nav.setCheckable(True);self.editor_nav.setEnabled(False)
        nav.addWidget(self.library_nav);nav.addWidget(self.editor_nav)
        nav.addSpacing(24)
        nav.addWidget(label('COLLECTIONS','eyebrow'))
        for name in ('WEBFISHING','RISK OF RAIN','KINGDOM HEARTS','MAX PAYNE'):
            nav.addWidget(button(name.title(),lambda checked=False,n=name:self.collection(n),'nav'))
        nav.addStretch()
        nav.addWidget(label('YOUR SAVES, PROTECTED','eyebrow'))
        nav.addWidget(label('Local. No accounts.\nYour original is always preserved.','muted',True))
        nav.addSpacing(8)
        nav.addWidget(button('User guide',self.open_guide))
        nav.addWidget(label('v0.5  /  IN DEVELOPMENT','small'))
        shell.addWidget(side)
        self.stack=QStackedWidget();shell.addWidget(self.stack,1)
        self.build_library();self.build_editor()
        self.statusBar().showMessage('Ready · Local processing')
        QShortcut(QKeySequence('Ctrl+O'),self,activated=self.open_file)
        QShortcut(QKeySequence('Ctrl+Return'),self,activated=self.review)
        QShortcut(QKeySequence('Ctrl+F'),self,activated=lambda:(self.show_library(),self.search.setFocus()))
        self.scan();self.show_library()

    def build_library(self):
        page=QWidget();box=layout(page,True,30,18)
        top=QHBoxLayout()
        titlebox=QVBoxLayout();titlebox.addWidget(label('YOUR SAVE SPACE','eyebrow'));titlebox.addWidget(label('Save library','title'))
        top.addLayout(titlebox);top.addStretch()
        top.addWidget(button('Refresh',self.scan))
        top.addWidget(button('+  Open save',self.open_file,'primary'))
        box.addLayout(top)
        box.addWidget(label('Adjust your progress and return to your favorite worlds.','muted'))
        strip=QFrame();strip.setObjectName('panel');stats=layout(strip,False,18,24)
        self.available=label(f'{sum(game.editable for game in GAMES):02d}  EDITORS AVAILABLE','success')
        self.detected=label('00  FILES DETECTED','muted')
        stats.addWidget(self.available);stats.addWidget(self.detected);stats.addStretch();stats.addWidget(label('BACKUPS BEFORE CHANGES','small'))
        box.addWidget(strip)
        tools=QHBoxLayout()
        self.search=QLineEdit();self.search.setPlaceholderText('Search games…');self.search.setAccessibleName('Search games');self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.render_cards)
        tools.addWidget(self.search,1)
        self.filter_buttons=[]
        for key,text in [('all','All'),('ready','Available'),('pending','Coming soon')]:
            b=button(text,lambda checked=False,k=key:self.set_filter(k),'filter');b.setCheckable(True);b.setChecked(key=='all')
            self.filter_buttons.append((key,b));tools.addWidget(b)
        box.addLayout(tools)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        content=QWidget();self.grid=QGridLayout(content);self.grid.setContentsMargins(0,0,8,0);self.grid.setSpacing(18)
        scroll.setWidget(content);box.addWidget(scroll,1)
        box.addWidget(label('Available means editing is implemented. In-game validation is still in progress.','small',True))
        self.stack.addWidget(page)

    def build_editor(self):
        page=QWidget();outer=layout(page,True,28,14)
        top=QHBoxLayout();titles=QVBoxLayout()
        self.editor_eyebrow=label('SAVE EDITOR','eyebrow');self.editor_title=label('Your save','title')
        titles.addWidget(self.editor_eyebrow);titles.addWidget(self.editor_title);top.addLayout(titles);top.addStretch()
        top.addWidget(button('Open another…',self.open_file));outer.addLayout(top)
        self.editor_subtitle=label('','muted',True);outer.addWidget(self.editor_subtitle)
        self.file_combo=QComboBox();self.file_combo.setAccessibleName('Save file');self.file_combo.activated.connect(self.select_file)
        outer.addWidget(self.file_combo)
        self.slot_combo=QComboBox();self.slot_combo.setAccessibleName('Save slot');self.slot_combo.activated.connect(self.change_slot)
        outer.addWidget(self.slot_combo)
        self.warning=label('','warning',True);outer.addWidget(self.warning)
        self.repair=QCheckBox('Repair the integrity check when exporting the copy')
        self.repair.toggled.connect(self.update_summary);outer.addWidget(self.repair)
        body=QHBoxLayout();body.setSpacing(22)
        self.tabs=QTabWidget();self.tabs.setUsesScrollButtons(True);body.addWidget(self.tabs,1)
        side=QFrame();side.setObjectName('panel');side.setFixedWidth(275);summary=layout(side,True,18,12)
        summary.addWidget(label('BEFORE SAVING','eyebrow'))
        self.change_count=label('No changes','section');summary.addWidget(self.change_count)
        summary.addWidget(label('Compare your edits with the file you opened.','muted',True))
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        self.summary_content=QWidget();self.summary_box=layout(self.summary_content,True,0,10)
        scroll.setWidget(self.summary_content);summary.addWidget(scroll,1)
        summary.addWidget(label('01  Review values\n02  Choose another file\n03  Keep your backup','small',True))
        self.review_button=button('Review and export  →',self.review,'primary');summary.addWidget(self.review_button)
        self.reset_button=button('Reset changes',self.reset);summary.addWidget(self.reset_button)
        body.addWidget(side);outer.addLayout(body,1)
        self.install_note=label('','small',True);outer.addWidget(self.install_note)
        self.stack.addWidget(page)

    def scan(self):
        try:self.files=discover()
        except OSError as error:
            QMessageBox.warning(self,'Search failed',str(error));return
        self.detected.setText(f'{len(self.files):02d}  FILES DETECTED')
        self.render_cards()
        self.statusBar().showMessage(f'{len(self.files)} files found in the usual folders · Drag a file here to open it')

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
            row=QHBoxLayout();row.addWidget(label('EDITOR AVAILABLE' if game.editable else 'IN DEVELOPMENT','badge' if game.editable else 'pending'));row.addStretch();box.addLayout(row)
            box.addWidget(label(game.title,'section',True));box.addWidget(label(game.subtitle,'muted',True))
            features=label(game.description,'cardDescription',True)
            features.setAccessibleName('Editor features for '+game.title)
            box.addWidget(features)
            count=sum(g==game.id for g,p in self.files)
            box.addWidget(label(f'{count} file'+('s' if count!=1 else '')+' detected' if count else 'No saves detected','small'))
            box.addWidget(button('Open editor  →' if game.editable else 'View compatibility',lambda checked=False,g=game:self.select_game(g)))
            self.grid.addWidget(card,index//3,index%3)
        if not games:
            empty=label('No games matched your search.\nTry another name or change the filter.','muted',True)
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
            QMessageBox.information(self,game.title,'Compatibility pending\n\n'+game.description+'\n\nEditing is not available for this game yet.');return
        if self.save and self.save.game==game.id:self.show_editor();return
        files=[p for g,p in self.files if g==game.id]
        if files:self.load(game.id,files[0])
        else:self.open_file(game.id)

    def open_file(self,game=None):
        if not isinstance(game,str):game=None
        filename,_=QFileDialog.getOpenFileName(self,'Open a save','', 'Save files (*.sav *.png *.xml);;All files (*)')
        if filename:self.open_path(Path(filename),game)

    def open_path(self,path,game=None):
        if game is None:
            name=path.name.lower()
            if name.startswith(('khrecom','kh2','khbbs')):
                QMessageBox.information(self,'Format pending','This game does not have an editor yet.');return
            game={'.sav':'webfishing','.xml':'ror2'}.get(path.suffix.lower(),'kh1')
        self.load(game,path)

    def state_signature(self):
        return (tuple(sorted(self.edits.items())),self.repair.isChecked())

    def may_discard(self):
        if not self.edits and not self.repair.isChecked():return True
        if self.state_signature()==self.exported_state:return True
        return QMessageBox.question(self,'Unsaved changes','Discard the changes made to this save?',QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)==QMessageBox.StandardButton.Discard

    def load(self,game,path):
        if not self.may_discard():return False
        try:save=Save(read_limited(path),game)
        except (ValueError,OSError) as error:
            QMessageBox.warning(self,'Could not open the save',str(error));return False
        self.save=save;self.path=Path(path);self.edits={};self.inputs={};self.exported_state=None;self.slot_index=0
        gameinfo=BY_ID[game];self.selected_game=game
        self.editor_title.setText(gameinfo.title)
        self.editor_eyebrow.setText('EDITOR / '+gameinfo.subtitle.upper())
        self.editor_subtitle.setText(gameinfo.description)
        if game in ('webfishing','ror2'):
            self.review_button.setText('Review and apply  →')
            self.install_note.setText('Apply replaces the active file after preserving an exact backup beside it.')
        else:
            self.review_button.setText('Review and export  →')
            self.install_note.setText('Export creates an edited save and an original backup. It does not install the copy in the game.')
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
        self.statusBar().showMessage(f'{self.path.name} · Original preserved · Editing in memory')
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
            if self.save.game=='webfishing':group='Bait' if field.key.startswith('bait:') else 'Economy'
            else:group={'0':'Sora','1':'Donald','2':'Goofy'}.get(field.key.split(':')[0],'Economy')
            group=field.group or group
            groups.setdefault(group,[]).append(field)
        preferred=['Characters','Skills','Skins and recolors','Artifacts','Items and equipment','Logs','Newt Altars','Economy','Progress','Combat']
        ordered=sorted(groups,key=lambda name:(preferred.index(name) if name in preferred else len(preferred),name))
        for name in ordered:
            fields=groups[name]
            scroll=QScrollArea();scroll.setWidgetResizable(True)
            content=QWidget();box=layout(content,True,4,12)
            box.addWidget(label(name,'section'))
            box.addWidget(label('Only fields you change will be modified.','muted',True))
            unlock_fields=[field for field in fields if field.fmt == 'xml-unlock']
            if unlock_fields:
                actions=QHBoxLayout()
                actions.addWidget(button('Unlock category',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,1),'primary'))
                actions.addWidget(button('Restore category',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,None)))
                actions.addStretch();box.addLayout(actions)
                field_filter=QLineEdit();field_filter.setPlaceholderText('Search this category…')
                field_filter.setClearButtonEnabled(True);box.addWidget(field_filter)
            rows=[]
            for field in fields:
                row=QFrame();row.setObjectName('field');line=layout(row,False,8,16)
                caption=QVBoxLayout();caption.addWidget(label(field.label))
                if field.fmt == 'xml-unlock':
                    caption.addWidget(label(f'Original: {value_text(field,field.value)}  ·  {field.key.removeprefix("unlock:")}','small',True))
                else:
                    caption.addWidget(label(f'Original: {number_text(field.value)}  ·  Range: {field.minimum:,}–{field.maximum:,}','small',True))
                line.addLayout(caption,1)
                key=(self.slot_index,field.key)
                if field.fmt == 'xml-unlock':
                    entry=QCheckBox('Unlocked')
                    entry.setChecked(bool(int(self.edits.get(key,field.value))))
                    entry.toggled.connect(lambda checked,k=key,f=field,e=entry:self.unlock_changed(k,f,e,checked))
                    self.mark_unlock(entry,field,entry.isChecked())
                else:
                    entry=QLineEdit(self.edits.get(key,number_text(field.value)))
                    entry.setFixedWidth(130);entry.setAlignment(Qt.AlignmentFlag.AlignRight)
                    entry.textChanged.connect(lambda text,k=key,f=field,e=entry:self.edit_changed(k,f,e,text))
                    self.mark_entry(entry,field,entry.text())
                entry.setAccessibleName(field.label)
                self.inputs[key]=entry;line.addWidget(entry)
                box.addWidget(row);rows.append((field.label.casefold()+' '+field.key.casefold(),row))
            if unlock_fields:
                field_filter.textChanged.connect(lambda text,rs=rows:[row.setVisible(text.casefold().strip() in searchable) for searchable,row in rs])
            box.addStretch();scroll.setWidget(content);self.tabs.addTab(scroll,name)
        self.update_summary()

    def set_unlock_fields(self,fields,value):
        for field in fields:
            key=(self.slot_index,field.key)
            checkbox=self.inputs.get(key)
            if isinstance(checkbox,QCheckBox):
                checkbox.setChecked(bool(field.value if value is None else value))

    def mark_unlock(self,entry,field,checked):
        changed=int(checked) != field.value
        entry.setProperty('changed',changed)
        entry.style().unpolish(entry);entry.style().polish(entry)

    def unlock_changed(self,key,field,entry,checked):
        if int(checked) == field.value:self.edits.pop(key,None)
        else:self.edits[key]=str(int(checked))
        self.mark_unlock(entry,field,checked);self.update_summary()

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
            if not field.minimum<=value<=field.maximum:raise ValueError(f'{field.label}: use a value between {field.minimum} and {field.maximum}.')
            changes[(index,key)]=value
        return changes

    def update_summary(self):
        if not hasattr(self,'summary_box'):return
        clear(self.summary_box)
        count=len(self.edits)
        self.change_count.setText(f'{count:02d} change'+('s' if count!=1 else '') if count else 'No changes')
        visible_edits=list(self.edits.items())
        for (index,key),text in visible_edits[:80]:
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            item=label(f'{field.label}\n{value_text(field,field.value)}  →  {value_text(field,text) if text else "…"}','',True)
            self.summary_box.addWidget(item)
            if len(self.save.slots)>1:self.summary_box.addWidget(label(self.save.slots[index].name,'small',True))
        if len(visible_edits)>80:
            self.summary_box.addWidget(label(f'+ {len(visible_edits)-80} more changes','muted',True))
        if not count:self.summary_box.addWidget(label('Your edits will appear here.','muted',True))
        if self.repair.isChecked():self.summary_box.addWidget(label('The CRC will be repaired in the copy.','success',True))
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
            QMessageBox.warning(self,'Review your edits',str(error));return
        direct=self.save.game in ('webfishing','ror2')
        dialog=QDialog(self);dialog.setWindowTitle('Review and apply' if direct else 'Review and export');dialog.resize(650,550)
        box=layout(dialog,True,24,16)
        box.addWidget(label('ONE LAST LOOK','eyebrow'));box.addWidget(label('Your edited save','title'))
        box.addWidget(label('The active save will be replaced after an exact backup is created.' if direct else 'A separate edited file and an exact original backup will be created.','muted',True))
        text=QTextEdit();text.setReadOnly(True)
        lines=[]
        for (index,key),value in self.validated_changes().items():
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            lines.append(f'{self.save.slots[index].name}\n{field.label}: {value_text(field,field.value)} → {value_text(field,value)}')
        if self.repair.isChecked():lines.append('Repair the save block CRC in the copy.')
        text.setPlainText('\n\n'.join(lines));box.addWidget(text,1)
        box.addWidget(label('Loading edited copies in each game still requires validation.','small',True))
        actions=QHBoxLayout();actions.addWidget(button('Back',dialog.reject));actions.addStretch()
        def write():
            if direct:
                try:backup=replace_current(self.path,self.save.raw,output)
                except (ValueError,OSError) as error:
                    QMessageBox.warning(dialog,'Could not apply changes',str(error));return
                self.exported_state=self.state_signature();dialog.accept()
                QMessageBox.information(self,'Changes applied',f'Active save replaced:\n{self.path}\n\nOriginal backup:\n{backup}')
                self.load(self.save.game,self.path)
                self.statusBar().showMessage(f'Changes applied to {BY_ID[self.save.game].title} · Original backup preserved')
                return
            filename,_=QFileDialog.getSaveFileName(dialog,'Export copy',str(self.path.parent/(self.path.stem+'.edited'+self.path.suffix)),f'Save file (*{self.path.suffix})')
            if not filename:return
            try:backup=export_copy(self.path,self.save.raw,output,filename)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'Could not export',str(error));return
            self.exported_state=self.state_signature();dialog.accept()
            self.statusBar().showMessage('Copy exported and verified · Original unchanged')
            QMessageBox.information(self,'Copy ready',f'Edited save:\n{filename}\n\nOriginal backup:\n{backup}\n\nSee the guide before loading it in the game.')
        actions.addWidget(button('Apply to active save' if direct else 'Choose destination and export',write,'primary'));box.addLayout(actions)
        dialog.exec()

    def open_guide(self):
        dialog=QDialog(self);dialog.setWindowTitle('UniversalSaveEditor guide');dialog.resize(760,650)
        box=layout(dialog,True,24,16);box.addWidget(label('Before returning to the game','title'))
        text=QTextEdit();text.setReadOnly(True);text.setMarkdown((ROOT/'README.md').read_text(encoding='utf-8'))
        box.addWidget(text,1);box.addWidget(button('Got it',dialog.accept));dialog.exec()

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
                    'ror2Unlocks':len(UNLOCK_IDS),
                    'frozen':bool(getattr(sys,'frozen',False))}
            destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
            window.grab().save(str(destination.with_suffix('.png')))
            app.exit(0 if all(covers.values()) else 1)
        QTimer.singleShot(1000,check_startup)
    sys.exit(app.exec())

if __name__=='__main__':main()
