"""UniversalSaveEditor desktop interface. SPDX-License-Identifier: GPL-3.0-or-later."""
import sys
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt, QUrl, QTimer, Signal
from PySide6.QtGui import QDesktopServices, QIcon, QKeySequence, QShortcut, QPixmap, QFontDatabase
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QStackedWidget, QComboBox,
    QTabWidget, QCheckBox, QMessageBox, QFileDialog, QDialog, QTextEdit,
    QLayout,
)
from core import Save, discover, read_limited, export_copy, replace_current, identify_game, backup_files, restore_backup
from catalog import GAMES, BY_ID
from artwork import Artwork
from ror2_unlocks import UNLOCK_IDS
from version import VERSION

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
    if field.boolean:return 'Enabled' if int(value) else 'Disabled'
    if field.choices:
        try:return field.choices[int(value)]
        except (ValueError,IndexError):return str(value)
    try:return number_text(value)
    except (TypeError,ValueError):return str(value)

class GameCard(QFrame):
    clicked=Signal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):self.clicked.emit()
        super().mouseReleaseEvent(event)
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Space):self.clicked.emit();event.accept();return
        super().keyPressEvent(event)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('UniversalSaveEditor — your save library')
        self.resize(1536,960)
        self.setMinimumSize(1100,720)
        self.setAcceptDrops(True)
        self.setStyleSheet((ROOT/'theme.qss').read_text(encoding='utf-8'))
        self.files=[];self.save=None;self.path=None;self.inputs={};self.edits={}
        self.exported_state=None;self.slot_index=0;self.filter='all';self.selected_game='kh1'
        self.grid_columns=0;self.grid_available_width=0;self._reflow_pending=False
        root=QWidget();self.setCentralWidget(root)
        window=layout(root,True,0,0)
        header=QFrame();header.setObjectName('appHeader');header.setFixedHeight(82)
        head=layout(header,False,24,14)
        icon=QLabel();icon.setPixmap(QPixmap(str(ROOT/'assets/memory-card-icon.png')).scaled(42,42,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));icon.setFixedSize(48,48)
        head.addWidget(icon)
        brand=QVBoxLayout();brand.setSpacing(1);brand.addWidget(label('UniversalSaveEditor','brand'));brand.addWidget(label('Your games. Your progress. One editor.','muted'))
        head.addLayout(brand);head.addStretch();head.addWidget(label('LOCAL  •  PRIVATE  •  BACKED UP','headerStatus'))
        window.addWidget(header)
        shell=QHBoxLayout();shell.setContentsMargins(0,0,0,0);shell.setSpacing(0);window.addLayout(shell,1)
        side=QFrame();side.setObjectName('sidebar');side.setFixedWidth(208)
        nav=layout(side,True,14,8)
        nav.addSpacing(8)
        nav.addWidget(label('WORKSPACE','eyebrow'))
        self.library_nav=button('▦   Library',self.show_library,'nav');self.library_nav.setCheckable(True)
        self.editor_nav=button('✎   Save editor',self.show_editor,'nav');self.editor_nav.setCheckable(True);self.editor_nav.setEnabled(False)
        nav.addWidget(self.library_nav);nav.addWidget(self.editor_nav)
        nav.addSpacing(18)
        nav.addWidget(label('COLLECTIONS','eyebrow'))
        for name in dict.fromkeys(game.family for game in GAMES):
            nav.addWidget(button(name.title(),lambda checked=False,n=name:self.collection(n),'nav'))
        nav.addStretch()
        nav.addWidget(label('SAFE EDITING','eyebrow'))
        nav.addWidget(label('Changes stay local. A backup is created before applying them.','muted',True))
        nav.addSpacing(8)
        nav.addWidget(button('?   Guide and about',self.open_guide,'nav'))
        nav.addWidget(label('v'+VERSION+'  /  PRE-RELEASE','small'))
        shell.addWidget(side)
        self.stack=QStackedWidget();shell.addWidget(self.stack,1)
        self.build_library();self.build_editor()
        self.statusBar().showMessage('Ready · Local processing')
        QShortcut(QKeySequence('Ctrl+O'),self,activated=self.open_file)
        QShortcut(QKeySequence('Ctrl+Return'),self,activated=self.review)
        QShortcut(QKeySequence('Ctrl+F'),self,activated=self.focus_search)
        self.scan();self.show_library()

    def build_library(self):
        page=QWidget();box=layout(page,True,14,10)
        top=QHBoxLayout()
        self.search=QLineEdit();self.search.setPlaceholderText('Search games…');self.search.setAccessibleName('Search games');self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.render_cards);top.addWidget(self.search,1)
        self.platform_filter=QComboBox();self.platform_filter.addItem('Platform: All','all');self.platform_filter.addItem('Platform: Steam','steam');self.platform_filter.addItem('Platform: PC','pc')
        self.platform_filter.currentIndexChanged.connect(self.render_cards);top.addWidget(self.platform_filter)
        self.status_filter=QComboBox();self.status_filter.addItem('All games','all');self.status_filter.addItem('Editors available','ready');self.status_filter.addItem('Coming soon','pending')
        self.status_filter.currentIndexChanged.connect(lambda:self.set_filter(self.status_filter.currentData()));top.addWidget(self.status_filter)
        self.sort_filter=QComboBox();self.sort_filter.addItem('Sort: A–Z','az');self.sort_filter.addItem('Sort: Z–A','za');self.sort_filter.addItem('Sort: Ready first','ready')
        self.sort_filter.currentIndexChanged.connect(self.render_cards);top.addWidget(self.sort_filter)
        top.addWidget(button('↻',self.scan,'iconButton'))
        top.addWidget(button('+  Open save',self.open_file,'primary'));box.addLayout(top)
        content_row=QHBoxLayout();content_row.setSpacing(12)
        library=QFrame();library.setObjectName('libraryPanel');library_box=layout(library,True,12,10)
        heading=QHBoxLayout();heading.addWidget(label('GAME LIBRARY','eyebrow'));heading.addStretch();self.library_count=label('','small');heading.addWidget(self.library_count);library_box.addLayout(heading)
        scroll=QScrollArea();scroll.setWidgetResizable(True);self.library_scroll=scroll
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content=QWidget();self.grid=QGridLayout(content);self.grid.setContentsMargins(0,0,4,0);self.grid.setHorizontalSpacing(8);self.grid.setVerticalSpacing(14)
        self.grid.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        scroll.setWidget(content);library_box.addWidget(scroll,1);content_row.addWidget(library,1)
        self.detail=QFrame();self.detail.setObjectName('detailPanel');self.detail.setFixedWidth(350)
        self.detail_box=layout(self.detail,True,16,10);content_row.addWidget(self.detail)
        box.addLayout(content_row,1)
        footer=QHBoxLayout();self.available=label(f'{sum(game.editable for game in GAMES):02d} editors available','muted');self.detected=label('00 save files detected','muted')
        footer.addWidget(self.available);footer.addSpacing(18);footer.addWidget(self.detected);footer.addStretch();footer.addWidget(label('●  Ready','readyStatus'));footer.addWidget(label('v'+VERSION,'small'));box.addLayout(footer)
        self.stack.addWidget(page)

    def build_editor(self):
        page=QWidget();outer=layout(page,True,28,14)
        top=QHBoxLayout();titles=QVBoxLayout()
        self.editor_eyebrow=label('SAVE EDITOR','eyebrow');self.editor_title=label('Your save','title')
        titles.addWidget(self.editor_eyebrow);titles.addWidget(self.editor_title);top.addLayout(titles);top.addStretch()
        top.addWidget(button('Open another…',self.open_file));outer.addLayout(top)
        self.backup_button=button('Backups and restore',self.open_backups)
        top.addWidget(self.backup_button)
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
        self.save_steps=label('01  Review values\n02  Save your changes\n03  Keep your backup','small',True)
        summary.addWidget(self.save_steps)
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
        if hasattr(self,'status_filter') and self.status_filter.currentData()!=key:
            self.status_filter.blockSignals(True);self.status_filter.setCurrentIndex(self.status_filter.findData(key));self.status_filter.blockSignals(False)
        self.render_cards()

    def collection(self,name):
        self.set_filter('all');self.search.setText(name);self.show_library()

    def render_cards(self):
        if not hasattr(self,'grid'):return
        clear(self.grid)
        for row in range(self.grid.rowCount()):self.grid.setRowStretch(row,0)
        search=self.search.text().casefold().strip()
        platform=self.platform_filter.currentData() if hasattr(self,'platform_filter') else 'all'
        games=[g for g in GAMES if search in (g.title+' '+g.subtitle+' '+g.family+' '+g.description).casefold()
               and (self.filter=='all' or g.editable==(self.filter=='ready'))
               and (platform=='all' or platform in g.subtitle.casefold())]
        order=self.sort_filter.currentData() if hasattr(self,'sort_filter') else 'az'
        games.sort(key=lambda g:(not g.editable,g.title) if order=='ready' else g.title,reverse=order=='za')
        self.visible_games=[g.id for g in games]
        self.game_cards={}
        available=max(180,self.library_scroll.viewport().width())
        columns=max(1,(available+8)//188)
        card_width=max(1,(available-8*(columns-1)-8)//columns)
        for column in range(self.grid.columnCount()):
            self.grid.setColumnMinimumWidth(column,0);self.grid.setColumnStretch(column,0)
        self.grid_columns=columns;self.grid_available_width=available
        self.library_count.setText(f'{len(games)} game'+('s' if len(games)!=1 else ''))
        if games and (self.selected_game not in self.visible_games):self.selected_game=games[0].id
        for index,game in enumerate(games):
            card=GameCard();card.setObjectName('gameCard');card.setProperty('selected',game.id==self.selected_game);card.setFixedWidth(card_width);card.setAccessibleName(game.title)
            card.clicked.connect(lambda g=game:self.activate_game(g));self.game_cards[game.id]=card
            card_box=layout(card,True,6,4)
            cover=QFrame();cover.setObjectName('coverFrame');cover.setProperty('selected',game.id==self.selected_game)
            cover.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            cover_box=layout(cover,True,0,0);cover_box.addWidget(Artwork(game,height=int((card_width-18)*1.5)));card_box.addWidget(cover)
            title=label(game.title,'cardTitle',True);card_box.addWidget(title)
            features=label(game.description,'cardDescription',True);features.setAccessibleName('Editor features for '+game.title);features.hide();card_box.addWidget(features)
            count=sum(g==game.id for g,p in self.files)
            state=('◇  Experimental' if game.experimental else '●  Editor ready' if game.editable else '○  Coming soon')+(f'  ·  {count} save'+('s' if count!=1 else '') if count else '')
            card_box.addWidget(label(state,'cardMeta',True))
            self.grid.addWidget(card,index//columns,index%columns)
        if not games:
            empty=label('No games matched your search.\nTry another name or change the filter.','muted',True)
            self.grid.addWidget(empty,0,0,1,columns)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        self.grid.activate()
        content=self.library_scroll.widget()
        content.setMinimumSize(0,self.grid.minimumSize().height())
        content.resize(self.library_scroll.viewport().width(),max(content.minimumHeight(),self.library_scroll.viewport().height()))
        self.render_game_detail()

    def preview_game(self,game):
        self.selected_game=game.id
        for game_id,card in self.game_cards.items():
            card.setProperty('selected',game_id==game.id);card.style().unpolish(card);card.style().polish(card)
        self.render_game_detail()

    def activate_game(self,game):
        self.preview_game(game)
        if game.editable:self.select_game(game)

    def render_game_detail(self):
        clear(self.detail_box)
        if not self.visible_games or not self.selected_game or self.selected_game not in BY_ID:
            self.detail_box.addStretch();self.detail_box.addWidget(label('Select a game to see its save editor.','muted',True));self.detail_box.addStretch();return
        game=BY_ID[self.selected_game]
        files=[p for g,p in self.files if g==game.id]
        hero=QHBoxLayout();hero.setSpacing(14)
        art=Artwork(game,height=180);art.setFixedWidth(120);hero.addWidget(art)
        info=QVBoxLayout();info.setSpacing(6)
        row=QHBoxLayout();row.addWidget(label('EXPERIMENTAL' if game.experimental else 'AVAILABLE' if game.editable else 'COMING SOON','badge' if game.editable else 'pending'));row.addStretch();info.addLayout(row)
        info.addWidget(label(game.title,'detailTitle',True));info.addWidget(label(game.subtitle,'muted',True))
        info.addSpacing(4);info.addWidget(label(f'{len(files)} save file'+('s' if len(files)!=1 else '')+' detected','small',True))
        info.addStretch()
        open_button=button('Open editor',lambda:self.open_selected_game(),'primary');open_button.setEnabled(game.editable);info.addWidget(open_button)
        hero.addLayout(info,1);self.detail_box.addLayout(hero)
        line=QFrame();line.setObjectName('divider');line.setFixedHeight(1);self.detail_box.addWidget(line)
        self.detail_box.addWidget(label('EDITOR FEATURES','eyebrow'))
        features=label(game.description,'detailDescription',True);features.setAccessibleName('Editor features for '+game.title);self.detail_box.addWidget(features)
        line=QFrame();line.setObjectName('divider');line.setFixedHeight(1);self.detail_box.addWidget(line)
        self.detail_box.addWidget(label('SAVE FILES','eyebrow'))
        if files:
            for path in files[:3]:
                row=QFrame();row.setObjectName('saveRow');row_box=layout(row,False,10,8)
                details=QVBoxLayout();details.setSpacing(2);details.addWidget(label(path.name,'saveName',True))
                try:size=f'{path.stat().st_size/1024:.1f} KB'
                except OSError:size='Local save'
                details.addWidget(label(size+'  ·  '+str(path.parent),'small',True));row_box.addLayout(details,1)
                row_box.addWidget(button('•••',lambda checked=False,p=path:self.open_save_folder(p),'rowMenu'));row.setToolTip(str(path));self.detail_box.addWidget(row)
            if len(files)>3:self.detail_box.addWidget(label(f'+ {len(files)-3} more','small'))
        else:self.detail_box.addWidget(label('No save detected in the usual folders.','muted',True))
        self.detail_box.addStretch()
        self.detail_box.addWidget(label('ACTIONS','eyebrow'))
        choose=button('Choose save file…',lambda:self.open_file(game.id));choose.setEnabled(game.editable);self.detail_box.addWidget(choose)
        if files:self.detail_box.addWidget(button('Open save folder',lambda:self.open_save_folder(files[0])))
        if not game.editable:self.detail_box.addWidget(label('Support for this game will be added in a future update.','small',True))

    def open_selected_game(self):
        if self.selected_game:self.select_game(BY_ID[self.selected_game])

    def open_save_folder(self,path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent)))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if not hasattr(self,'library_scroll') or self._reflow_pending:return
        self._reflow_pending=True
        QTimer.singleShot(80,self.reflow_library)

    def reflow_library(self):
        self._reflow_pending=False
        if not hasattr(self,'library_scroll'):return
        available=max(180,self.library_scroll.viewport().width())
        columns=max(1,(available+8)//188)
        if columns!=self.grid_columns or abs(available-self.grid_available_width)>8:
            position=self.library_scroll.verticalScrollBar().value()
            self.render_cards()
            self.library_scroll.verticalScrollBar().setValue(position)

    def show_library(self):
        self.stack.setCurrentIndex(0);self.library_nav.setChecked(True);self.editor_nav.setChecked(False)

    def show_editor(self):
        if self.save:
            self.stack.setCurrentIndex(1);self.library_nav.setChecked(False);self.editor_nav.setChecked(True)

    def focus_search(self):
        if self.stack.currentIndex()==1 and self.tabs.currentWidget():
            search=self.tabs.currentWidget().findChild(QLineEdit,'fieldSearch')
            if search:search.setFocus();search.selectAll();return
        self.search.setFocus();self.search.selectAll()

    def select_game(self,game):
        if not game.editable:
            QMessageBox.information(self,game.title,'Compatibility pending\n\n'+game.description+'\n\nEditing is not available for this game yet.');return
        if self.save and self.save.game==game.id:self.show_editor();return
        files=[p for g,p in self.files if g==game.id]
        if files:self.load(game.id,files[0])
        else:self.open_file(game.id)

    def open_file(self,game=None):
        if not isinstance(game,str):game=None
        filename,_=QFileDialog.getOpenFileName(self,'Open a save','', 'Save files (*.sav *.png *.xml *.psd *.PSD *.cfg *.CFG);;All files (*)')
        if filename:self.open_path(Path(filename),game)

    def open_path(self,path,game=None):
        if game is None:
            try:game=identify_game(path)
            except (ValueError,OSError) as error:
                QMessageBox.warning(self,'Could not identify the save',str(error));return
        if not BY_ID[game].editable:
            QMessageBox.information(self,'Format pending','This game does not have an editor yet.');return
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
        if game in ('webfishing','ror2','alice'):
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
        notices=save.warnings+getattr(save,'notes',[])
        self.warning.setText('\n'.join(notices));self.warning.setVisible(bool(notices))
        self.repair.blockSignals(True);self.repair.setChecked(False);self.repair.setVisible(bool(save.warnings));self.repair.blockSignals(False)
        self.editor_nav.setEnabled(True)
        self.save_steps.setText('01  Review values\n02  Apply to active save\n03  Keep your backup' if game in ('webfishing','ror2','alice') else '01  Review values\n02  Export a separate copy\n03  Keep your backup')
        if gameinfo.experimental:
            self.install_note.setText(self.install_note.text()+' Experimental support: in-game validation is still pending.')
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
        preferred=['Economy','Difficulty','Weapons','Skills','Health','Dresses','Memories','Bottles','Snouts','Radula rooms','Story and chapters','Chapter select','Characters','Skins and recolors','Artifacts','Items and equipment','Logs','Newt Altars','Progress','Combat']
        ordered=sorted(groups,key=lambda name:(preferred.index(name) if name in preferred else len(preferred),name))
        for name in ordered:
            fields=groups[name]
            scroll=QScrollArea();scroll.setWidgetResizable(True)
            content=QWidget();box=layout(content,True,4,12)
            box.addWidget(label(name,'section'))
            box.addWidget(label('Only fields you change will be modified.','muted',True))
            unlock_fields=[field for field in fields if field.fmt == 'xml-unlock' or field.boolean]
            if unlock_fields:
                actions=QHBoxLayout()
                actions.addWidget(button('Unlock category' if self.save.game=='ror2' else 'Enable all',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,1),'primary'))
                if self.save.game=='alice':actions.addWidget(button('Disable all',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,0)))
                actions.addWidget(button('Restore category',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,None)))
                actions.addStretch();box.addLayout(actions)
            field_filter=QLineEdit();field_filter.setObjectName('fieldSearch');field_filter.setPlaceholderText('Search fields or item IDs…')
            field_filter.setAccessibleName('Search '+name);field_filter.setClearButtonEnabled(True);box.addWidget(field_filter)
            empty=label('No fields match this search.','muted');empty.hide();box.addWidget(empty)
            rows=[]
            for field in fields:
                row=QFrame();row.setObjectName('field');line=layout(row,False,8,16)
                caption=QVBoxLayout();caption.addWidget(label(field.label))
                if field.fmt == 'xml-unlock' or field.boolean or field.choices:
                    caption.addWidget(label(f'Original: {value_text(field,field.value)}  ·  {field.key.removeprefix("unlock:")}','small',True))
                else:
                    caption.addWidget(label(f'Original: {number_text(field.value)}  ·  Range: {field.minimum:,}–{field.maximum:,}','small',True))
                if field.note:caption.addWidget(label(field.note,'small',True))
                line.addLayout(caption,1)
                key=(self.slot_index,field.key)
                if field.fmt == 'xml-unlock' or field.boolean:
                    entry=QCheckBox('Unlocked' if self.save.game=='ror2' else 'Enabled')
                    entry.setChecked(bool(int(self.edits.get(key,field.value))))
                    entry.toggled.connect(lambda checked,k=key,f=field,e=entry:self.unlock_changed(k,f,e,checked))
                    self.mark_unlock(entry,field,entry.isChecked())
                elif field.choices:
                    entry=QComboBox();entry.addItems(field.choices);entry.setFixedWidth(190)
                    entry.setCurrentIndex(int(self.edits.get(key,field.value)))
                    entry.currentIndexChanged.connect(lambda value,k=key,f=field,e=entry:self.choice_changed(k,f,e,value))
                    self.mark_unlock(entry,field,entry.currentIndex())
                else:
                    entry=QLineEdit(self.edits.get(key,number_text(field.value)))
                    entry.setFixedWidth(130);entry.setAlignment(Qt.AlignmentFlag.AlignRight)
                    entry.textChanged.connect(lambda text,k=key,f=field,e=entry:self.edit_changed(k,f,e,text))
                    self.mark_entry(entry,field,entry.text())
                entry.setAccessibleName(field.label)
                self.inputs[key]=entry;line.addWidget(entry)
                box.addWidget(row);rows.append((field.label.casefold()+' '+field.key.casefold(),row))
            def filter_rows(text,rs=rows,message=empty):
                query=text.casefold().strip()
                matches=0
                for searchable,row in rs:
                    visible=query in searchable;row.setVisible(visible);matches+=visible
                message.setVisible(not matches)
            field_filter.textChanged.connect(filter_rows)
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

    def choice_changed(self,key,field,entry,value):
        if value == field.value:self.edits.pop(key,None)
        else:self.edits[key]=str(value)
        self.mark_unlock(entry,field,value);self.update_summary()

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
        direct=self.save.game in ('webfishing','ror2','alice')
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
        if self.save.game=='alice':
            updated=Save(output,'alice')
            final_fields={field.key:field for field in updated.slots[0].fields}
            requested={key for index,key in self.validated_changes()}
            automatic=[]
            for field in self.save.slots[0].fields:
                final=final_fields.get(field.key)
                if final and field.key not in requested and final.value != field.value:
                    automatic.append(f'{field.label}: {value_text(field,field.value)} → {value_text(final,final.value)}')
            if automatic:
                text.setPlainText(text.toPlainText()+'\n\nAutomatic related changes\n'+'\n'.join(automatic))
            box.addWidget(label('Related state is synchronized automatically when affected; automatic field changes are listed above.','small',True))
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

    def open_backups(self):
        if not self.save:return
        dialog=QDialog(self);dialog.setWindowTitle('Backups and restore');dialog.resize(720,440)
        box=layout(dialog,True,24,14);box.addWidget(label('Restore a previous save','title'))
        box.addWidget(label('Restoring creates a backup of your current file first. Close the game before restoring.','muted',True))
        choice=QComboBox();choice.setAccessibleName('Available backups');box.addWidget(choice)
        details=label('','muted',True);box.addWidget(details)
        try:backups=backup_files(self.path)
        except OSError as error:
            QMessageBox.warning(self,'Could not list backups',str(error));return
        for path in backups:
            date=datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            choice.addItem(date+'  ·  '+path.name,path)
        if not backups:details.setText('No backups found beside this save. You can choose an original .bak file manually.')
        def describe():
            path=choice.currentData()
            if path:details.setText(str(path))
        choice.currentIndexChanged.connect(describe);describe()
        def browse():
            filename,_=QFileDialog.getOpenFileName(dialog,'Choose an original backup',str(self.path.parent),'Save backups (*.bak)')
            if filename:
                path=Path(filename);choice.addItem(path.name,path);choice.setCurrentIndex(choice.count()-1);restore.setEnabled(True)
        box.addWidget(button('Choose backup…',browse));box.addStretch()
        actions=QHBoxLayout();actions.addWidget(button('Close',dialog.reject));actions.addStretch()
        def apply_backup():
            path=choice.currentData()
            if not path:return
            try:Save(read_limited(path),self.save.game)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'Invalid backup',str(error));return
            if not self.may_discard():return
            answer=QMessageBox.question(dialog,'Restore backup','Restore this backup to the active save?\n\n'+str(path)+'\n\nThe current save will be backed up first.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
            if answer!=QMessageBox.StandardButton.Yes:return
            try:backup=restore_backup(self.path,path,self.save.game)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'Could not restore backup',str(error));return
            self.edits={};self.repair.setChecked(False);dialog.accept()
            self.load(self.save.game,self.path)
            QMessageBox.information(self,'Backup restored','Save restored. Your previous file is preserved at:\n'+str(backup))
        restore=button('Restore selected backup',apply_backup,'primary');restore.setEnabled(bool(backups));actions.addWidget(restore);box.addLayout(actions)
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
    # Offscreen checks may have no system font collection in restricted runners.
    if '--smoke-test' in sys.argv and sys.platform=='win32' and not QFontDatabase.families():
        for font in ('segoeui.ttf','seguisym.ttf'):
            QFontDatabase.addApplicationFont(str(Path(os.environ.get('SystemRoot','C:/Windows'))/'Fonts'/font))
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
                    'version':VERSION,
                    'games':len(window.visible_games),'icon':not app.windowIcon().isNull(),
                    'ror2Unlocks':len(UNLOCK_IDS),
                    'frozen':bool(getattr(sys,'frozen',False))}
            destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
            window.grab().save(str(destination.with_suffix('.png')))
            app.exit(0 if all(covers.values()) else 1)
        QTimer.singleShot(1000,check_startup)
    sys.exit(app.exec())

if __name__=='__main__':main()
