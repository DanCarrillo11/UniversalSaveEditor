"""UniversalSaveEditor desktop interface. SPDX-License-Identifier: GPL-3.0-or-later."""
import sys
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import Qt, QUrl, QTimer, Signal, QRectF, QPointF, QSettings
from PySide6.QtGui import QDesktopServices, QIcon, QKeySequence, QShortcut, QPixmap, QFontDatabase, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QStackedWidget, QComboBox,
    QTabWidget, QCheckBox, QMessageBox, QFileDialog, QDialog, QTextEdit,
    QLayout, QInputDialog,
)
from core import Save, discover, read_limited, replace_current, identify_game, backup_files, restore_backup
from catalog import GAMES, BY_ID, PLATFORMS
from artwork import Artwork
from editor_layout import organize_fields
from ror2_unlocks import UNLOCK_IDS
from version import VERSION
from appearance import PALETTES, stylesheet
from favorites import FavoriteButton
from motion import ViewTransition

ROOT=Path(__file__).resolve().parent

def platform_pixmap(key,size=18,scale=1):
    renderer=QSvgRenderer(str(ROOT/'assets/platforms'/PLATFORMS[key].icon))
    if not renderer.isValid():return QPixmap()
    pixmap=QPixmap(round(size*scale),round(size*scale))
    pixmap.setDevicePixelRatio(scale);pixmap.fill(Qt.GlobalColor.transparent)
    # SVG bounds are logical pixels; default rendering uses the physical
    # pixmap dimensions and applies the display scale twice on HiDPI screens.
    painter=QPainter(pixmap)
    renderer.render(painter,QRectF(QPointF(0,0),pixmap.deviceIndependentSize()))
    painter.end()
    return pixmap

def platform_row(game):
    row=QWidget();row.setObjectName('cardPlatforms')
    row.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    box=layout(row,False,0,6)
    for key in game.platforms:
        platform=PLATFORMS[key]
        icon=QLabel();icon.setObjectName('platformIcon');icon.setFixedSize(18,18)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter);icon.setScaledContents(True)
        icon.setPixmap(platform_pixmap(key,scale=row.devicePixelRatioF()))
        icon.setAccessibleName(platform.name+' logo')
        text=label(platform.name,'cardPlatform');text.setAccessibleName('Platform: '+platform.name)
        box.addWidget(icon);box.addWidget(text)
    box.addStretch()
    row.setAccessibleName('Platforms for '+game.title+': '+', '.join(PLATFORMS[p].name for p in game.platforms))
    return row

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
        self.artwork=None;self.motion_enabled=True
    def enterEvent(self,event):
        if self.artwork:self.artwork.set_hovered(True,self.motion_enabled)
        super().enterEvent(event)
    def leaveEvent(self,event):
        if self.artwork:self.artwork.set_hovered(False,self.motion_enabled)
        super().leaveEvent(event)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):self.clicked.emit()
        super().mouseReleaseEvent(event)
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Space):self.clicked.emit();event.accept();return
        super().keyPressEvent(event)

class Window(QMainWindow):
    def __init__(self,settings=None):
        super().__init__()
        self.setWindowTitle('UniversalSaveEditor — your save library')
        self.resize(1536,960)
        self.setMinimumSize(1100,720)
        self.setAcceptDrops(True)
        self.settings=settings
        stored=settings.value('library/favorites',[],type=list) if settings is not None else []
        self.favorites={game_id for game_id in stored if isinstance(game_id,str) and game_id in BY_ID}
        self.favorites_only=False
        self.transition=ViewTransition(self)
        preferred=settings.value('appearance/theme','light',type=str) if settings is not None else 'light'
        self.theme=preferred if preferred in PALETTES else 'light'
        self.setStyleSheet(stylesheet(self.theme))
        self.files=[];self.save=None;self.path=None;self.inputs={};self.edits={}
        self.exported_state=None;self.slot_index=0;self.filter='all';self.selected_game='kh1'
        self.editor_view_state={};self.editor_page_game=None
        self.last_directory='';self.category_filters=[];self._batch_edit=False
        if settings is not None:
            self.last_directory=settings.value('files/lastDirectory','',type=str)
        self.grid_columns=0;self.grid_available_width=0;self._reflow_pending=False
        root=QWidget();self.setCentralWidget(root)
        window=layout(root,True,0,0)
        header=QFrame();header.setObjectName('appHeader');header.setFixedHeight(82)
        head=layout(header,False,24,14)
        icon=QLabel();icon.setPixmap(QPixmap(str(ROOT/'assets/memory-card-icon.png')).scaled(42,42,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));icon.setFixedSize(48,48)
        head.addWidget(icon)
        brand=QVBoxLayout();brand.setSpacing(1);brand.addWidget(label('UniversalSaveEditor','brand'));brand.addWidget(label('Your games. Your progress. One editor.','muted'))
        head.addLayout(brand);head.addStretch();head.addWidget(label('Offline · On your device','headerStatus'))
        self.appearance_button=button('',self.toggle_theme,'appearanceToggle');self.appearance_button.setFixedWidth(116)
        head.addWidget(self.appearance_button);self.update_appearance_button()
        window.addWidget(header)
        shell=QHBoxLayout();shell.setContentsMargins(0,0,0,0);shell.setSpacing(0);window.addLayout(shell,1)
        side=QFrame();side.setObjectName('sidebar');side.setFixedWidth(208)
        nav=layout(side,True,14,8)
        nav.addSpacing(8)
        nav.addWidget(label('Workspace','eyebrow'))
        self.library_nav=button('▦   Library',self.show_library,'nav');self.library_nav.setCheckable(True)
        self.editor_nav=button('✎   Save editor',self.show_editor,'nav');self.editor_nav.setCheckable(True);self.editor_nav.setEnabled(False)
        nav.addWidget(self.library_nav);nav.addWidget(self.editor_nav)
        self.favorites_nav=button('☆   Favorites',self.show_favorites,'nav');self.favorites_nav.setCheckable(True)
        self.favorites_nav.setAccessibleName('Show favorite games');nav.addWidget(self.favorites_nav)
        nav.addSpacing(18)
        nav.addWidget(label('Collections','eyebrow'))
        for name in dict.fromkeys(game.family for game in GAMES):
            nav.addWidget(button(name.title(),lambda checked=False,n=name:self.collection(n),'nav'))
        nav.addStretch()
        self.saving_heading=label('Saving','eyebrow');nav.addWidget(self.saving_heading)
        self.saving_note=label('Apply updates the opened save directly. No automatic backups.','muted',True);nav.addWidget(self.saving_note)
        nav.addSpacing(8)
        self.reduce_motion=QCheckBox('Reduce motion')
        self.reduce_motion.setToolTip('Turn off view fades and animated cover highlights')
        self.reduce_motion.setChecked(settings.value('appearance/reduceMotion',False,type=bool) if settings is not None else False)
        self.reduce_motion.toggled.connect(self.update_motion)
        nav.addWidget(self.reduce_motion);self.update_motion()
        nav.addWidget(button('?   Guide and about',self.open_guide,'nav'))
        nav.addWidget(label('v'+VERSION,'small'))
        shell.addWidget(side)
        self.stack=QStackedWidget();shell.addWidget(self.stack,1)
        self.build_library();self.build_editor()
        self.statusBar().showMessage('Ready · Local processing')
        QShortcut(QKeySequence('Ctrl+O'),self,activated=self.open_file)
        QShortcut(QKeySequence('Ctrl+Return'),self,activated=self.review)
        QShortcut(QKeySequence('Ctrl+S'),self,activated=self.review)
        QShortcut(QKeySequence('Ctrl+F'),self,activated=self.focus_search)
        self.scan();self.show_library()
        if settings is not None and settings.contains('window/geometry'):
            self.restoreGeometry(settings.value('window/geometry'))

    def update_appearance_button(self):
        target='dark' if self.theme=='light' else 'light'
        self.appearance_button.setText('Dark mode' if target=='dark' else 'Light mode')
        self.appearance_button.setAccessibleName('Switch to '+target+' appearance')
        self.appearance_button.setToolTip('Use '+target+' appearance')

    def toggle_theme(self):
        self.theme='dark' if self.theme=='light' else 'light'
        self.setStyleSheet(stylesheet(self.theme));self.update_appearance_button()

    def update_motion(self):
        enabled=not self.reduce_motion.isChecked()
        self.transition.enabled=enabled
        if not enabled:self.transition.stop()
        for card in getattr(self,'game_cards',{}).values():
            card.motion_enabled=enabled
            if card.artwork:card.artwork.set_hovered(card.underMouse(),False)

    def toggle_favorite(self,game_id):
        if game_id not in BY_ID:return
        if game_id in self.favorites:self.favorites.remove(game_id)
        else:self.favorites.add(game_id)
        position=self.library_scroll.verticalScrollBar().value()
        focused=QApplication.focusWidget()
        restore_focus=focused is not None and focused.objectName()=='favoriteButton'
        self.render_cards()
        if restore_focus:
            card=self.game_cards.get(game_id)
            if card:card.favorite_button.setFocus(Qt.FocusReason.OtherFocusReason)
            else:self.favorites_nav.setFocus(Qt.FocusReason.OtherFocusReason)
        self.library_scroll.verticalScrollBar().setValue(position)

    def show_favorites(self):
        self.favorites_only=True
        self.search.blockSignals(True);self.search.clear();self.search.blockSignals(False)
        self.platform_filter.blockSignals(True);self.platform_filter.setCurrentIndex(0);self.platform_filter.blockSignals(False)
        self.filter='all'
        self.status_filter.blockSignals(True);self.status_filter.setCurrentIndex(0);self.status_filter.blockSignals(False)
        self.render_cards();self.switch_view(0)
        self.library_nav.setChecked(False);self.favorites_nav.setChecked(True);self.editor_nav.setChecked(False)

    def switch_view(self,index):
        if self.stack.currentIndex()==index:return
        self.transition.stop()
        self.stack.setCurrentIndex(index)
        self.transition.fade(self.stack.currentWidget())

    def build_library(self):
        page=QWidget();box=layout(page,True,14,10)
        top=QGridLayout();self.library_toolbar=top
        self.search=QLineEdit();self.search.setPlaceholderText('Search games…');self.search.setAccessibleName('Search games');self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.render_cards);top.addWidget(self.search,0,0);top.setColumnStretch(0,1)
        self.library_filter_controls=QWidget();filters=layout(self.library_filter_controls,False,0,10)
        self.platform_filter=QComboBox();self.platform_filter.addItem('Platform: All','all')
        self.platform_filter.setAccessibleName('Platform filter')
        for key in dict.fromkeys(p for game in GAMES for p in game.platforms):
            self.platform_filter.addItem('Platform: '+PLATFORMS[key].name,key)
        self.platform_filter.currentIndexChanged.connect(self.render_cards);filters.addWidget(self.platform_filter)
        self.status_filter=QComboBox();self.status_filter.addItem('All games','all');self.status_filter.addItem('Editors available','ready');self.status_filter.addItem('Coming soon','pending')
        self.status_filter.setAccessibleName('Editor availability filter')
        self.status_filter.currentIndexChanged.connect(lambda:self.set_filter(self.status_filter.currentData()));filters.addWidget(self.status_filter)
        self.sort_filter=QComboBox();self.sort_filter.addItem('Sort: A–Z','az');self.sort_filter.addItem('Sort: Z–A','za');self.sort_filter.addItem('Sort: Ready first','ready')
        self.sort_filter.setAccessibleName('Sort games')
        self.sort_filter.currentIndexChanged.connect(self.render_cards);filters.addWidget(self.sort_filter)
        refresh=button('↻',self.scan,'iconButton');refresh.setFixedWidth(44);refresh.setAccessibleName('Refresh save discovery');refresh.setToolTip('Find saves in the usual folders again');filters.addWidget(refresh)
        top.addWidget(self.library_filter_controls,0,1)
        top.addWidget(button('+  Open save',self.open_file,'primary'),0,2);box.addLayout(top)
        content_row=QHBoxLayout();content_row.setSpacing(12)
        library=QFrame();library.setObjectName('libraryPanel');library_box=layout(library,True,12,10)
        heading=QHBoxLayout();self.library_title=label('Game library','libraryTitle');heading.addWidget(self.library_title);heading.addStretch();self.library_count=label('','small');heading.addWidget(self.library_count);library_box.addLayout(heading)
        scroll=QScrollArea();scroll.setWidgetResizable(True);self.library_scroll=scroll
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content=QWidget();self.grid=QGridLayout(content);self.grid.setContentsMargins(0,0,4,0);self.grid.setHorizontalSpacing(8);self.grid.setVerticalSpacing(14)
        self.grid.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        scroll.setWidget(content);library_box.addWidget(scroll,1);content_row.addWidget(library,1)
        self.detail=QFrame();self.detail.setObjectName('detailPanel');self.detail.setFixedWidth(350)
        detail_outer=layout(self.detail,True,4,0)
        self.detail_scroll=QScrollArea();self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.viewport().setObjectName('clearSurface')
        self.detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        detail_content=QWidget();detail_content.setObjectName('clearSurface');self.detail_box=layout(detail_content,True,12,10)
        self.detail_scroll.setWidget(detail_content);detail_outer.addWidget(self.detail_scroll);content_row.addWidget(self.detail)
        box.addLayout(content_row,1)
        footer=QHBoxLayout();self.available=label(f'{sum(game.editable for game in GAMES):02d} editors available','muted');self.detected=label('00 save files detected','muted')
        footer.addWidget(self.available);footer.addSpacing(18);footer.addWidget(self.detected);footer.addStretch();footer.addWidget(label('●  Ready','readyStatus'));footer.addWidget(label('v'+VERSION,'small'));box.addLayout(footer)
        self.stack.addWidget(page)

    def build_editor(self):
        page=QWidget();outer=layout(page,True,20,10)
        top=QHBoxLayout();titles=QVBoxLayout()
        self.editor_eyebrow=label('SAVE EDITOR','eyebrow');self.editor_title=label('Your save','title',True)
        titles.addWidget(self.editor_eyebrow);titles.addWidget(self.editor_title);top.addLayout(titles,1)
        top.addWidget(button('Open another…',self.open_file));outer.addLayout(top)
        self.backup_button=button('Restore existing backup',self.open_backups)
        top.addWidget(self.backup_button)
        self.editor_subtitle=label('','muted',True);outer.addWidget(self.editor_subtitle)
        self.file_combo=QComboBox();self.file_combo.setAccessibleName('Save file');self.file_combo.activated.connect(self.select_file)
        selectors=QHBoxLayout();selectors.addWidget(self.file_combo,1)
        self.slot_combo=QComboBox();self.slot_combo.setAccessibleName('Save slot');self.slot_combo.activated.connect(self.change_slot)
        selectors.addWidget(self.slot_combo,1);outer.addLayout(selectors)
        self.warning=label('','warning',True);outer.addWidget(self.warning)
        self.editor_notes=label('','info',True);outer.addWidget(self.editor_notes)
        self.repair=QCheckBox('Repair the integrity check when applying changes')
        self.repair.toggled.connect(self.update_summary);outer.addWidget(self.repair)
        body=QHBoxLayout();body.setSpacing(14)
        self.tabs=QTabWidget();self.tabs.setUsesScrollButtons(True);body.addWidget(self.tabs,1)
        side=QFrame();side.setObjectName('panel');side.setFixedWidth(275);summary=layout(side,True,18,12)
        summary.addWidget(label('Your changes','eyebrow'))
        self.change_count=label('No changes','section');summary.addWidget(self.change_count)
        self.summary_description=label('Compare your edits with the file you opened.','muted',True);summary.addWidget(self.summary_description)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        scroll.viewport().setObjectName('clearSurface')
        self.summary_content=QWidget();self.summary_box=layout(self.summary_content,True,0,10)
        self.summary_content.setObjectName('clearSurface')
        scroll.setWidget(self.summary_content);summary.addWidget(scroll,1)
        self.save_steps=label('01  Review values\n02  Apply to the opened save\n03  Return to the game','small',True)
        summary.addWidget(self.save_steps)
        self.review_button=button('Review and apply  →',self.review,'primary');self.review_button.setToolTip('Review pending changes (Ctrl+S or Ctrl+Enter)');summary.addWidget(self.review_button)
        self.reset_button=button('Reset changes',self.reset);summary.addWidget(self.reset_button)
        body.addWidget(side);outer.addLayout(body,1)
        self.install_note=label('','small',True);outer.addWidget(self.install_note)
        self.stack.addWidget(page)

    def scan(self):
        try:self.files=discover()
        except OSError as error:
            QMessageBox.warning(self,'Search failed',str(error));return
        self.detected.setText(f'{len(self.files)} saves found')
        self.render_cards()
        self.statusBar().showMessage(f'{len(self.files)} files found in the usual folders · Drag a file here to open it')

    def set_filter(self,key):
        self.filter=key
        if hasattr(self,'status_filter') and self.status_filter.currentData()!=key:
            self.status_filter.blockSignals(True);self.status_filter.setCurrentIndex(self.status_filter.findData(key));self.status_filter.blockSignals(False)
        self.render_cards()

    def collection(self,name):
        self.show_library()
        self.set_filter('all');self.search.setText(name);self.show_library()

    def render_cards(self):
        if not hasattr(self,'grid'):return
        clear(self.grid)
        for row in range(self.grid.rowCount()):self.grid.setRowStretch(row,0)
        search=self.search.text().casefold().strip()
        platform=self.platform_filter.currentData() if hasattr(self,'platform_filter') else 'all'
        games=[g for g in GAMES if search in (g.title+' '+g.subtitle+' '+g.family+' '+g.description).casefold()
               and (self.filter=='all' or g.editable==(self.filter=='ready'))
               and (platform=='all' or platform in g.platforms)]
        if self.favorites_only:games=[g for g in games if g.id in self.favorites]
        order=self.sort_filter.currentData() if hasattr(self,'sort_filter') else 'az'
        games.sort(key=lambda g:(not g.editable,g.title) if order=='ready' else g.title,reverse=order=='za')
        games.sort(key=lambda g:g.id not in self.favorites)
        self.library_title.setText('Favorites' if self.favorites_only else 'Game library')
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
            cover_box=QGridLayout(cover);cover_box.setContentsMargins(0,0,0,0)
            card.artwork=Artwork(game,height=int((card_width-18)*1.5));card.motion_enabled=not self.reduce_motion.isChecked()
            cover_box.addWidget(card.artwork,0,0)
            favorite=FavoriteButton(game.title,game.id in self.favorites)
            favorite.clicked.connect(lambda checked=False,g=game.id:self.toggle_favorite(g))
            card.favorite_button=favorite
            cover_box.addWidget(favorite,0,0,Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignRight)
            card_box.addWidget(cover)
            title=label(game.title,'cardTitle',True);card_box.addWidget(title)
            features=label(game.description,'cardDescription',True);features.setAccessibleName('Editor features for '+game.title);features.hide();card_box.addWidget(features)
            count=sum(g==game.id for g,p in self.files)
            state=('Experimental' if game.experimental else 'Editor ready' if game.editable else 'Coming soon')+(f' · {count} save'+('s' if count!=1 else '') if count else '')
            card.setToolTip(game.title+'\n'+', '.join(PLATFORMS[p].name for p in game.platforms)+' · '+state)
            card_box.addWidget(platform_row(game))
            self.grid.addWidget(card,index//columns,index%columns)
        if not games:
            empty=QWidget();empty_box=layout(empty,True,18,12)
            no_favorites=self.favorites_only and not self.favorites
            empty_box.addWidget(label('No favorites yet' if no_favorites else 'No games found','section'))
            empty_box.addWidget(label('Use the star on a cover to keep your favorite games here.' if no_favorites else 'Try another name or reset the library filters.','muted',True))
            empty_box.addWidget(button('Browse games' if no_favorites else 'Reset filters',self.show_library if no_favorites else self.reset_library_filters));self.grid.addWidget(empty,0,0,1,columns)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)
        self.grid.activate()
        content=self.library_scroll.widget()
        content.setMinimumSize(0,self.grid.minimumSize().height())
        content.resize(self.library_scroll.viewport().width(),max(content.minimumHeight(),self.library_scroll.viewport().height()))
        self.render_game_detail()

    def reset_library_filters(self):
        self.search.clear();self.platform_filter.setCurrentIndex(0);self.status_filter.setCurrentIndex(0)

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
        row=QHBoxLayout();row.addWidget(label('EXPERIMENTAL' if game.experimental else 'AVAILABLE' if game.editable else 'COMING SOON','experimental' if game.experimental else 'badge' if game.editable else 'pending'));row.addStretch();info.addLayout(row)
        info.addWidget(label(game.title,'detailTitle',True));info.addWidget(label(game.subtitle,'muted',True))
        info.addSpacing(4);info.addWidget(label(f'{len(files)} save file'+('s' if len(files)!=1 else '')+' detected','small',True))
        info.addStretch()
        open_button=button('Open editor',lambda:self.open_selected_game(),'primary');open_button.setEnabled(game.editable);info.addWidget(open_button)
        hero.addLayout(info,1);self.detail_box.addLayout(hero)
        line=QFrame();line.setObjectName('divider');line.setFixedHeight(1);self.detail_box.addWidget(line)
        self.detail_box.addWidget(label('Editor features','eyebrow'))
        features=label(game.description,'detailDescription',True);features.setAccessibleName('Editor features for '+game.title);self.detail_box.addWidget(features)
        line=QFrame();line.setObjectName('divider');line.setFixedHeight(1);self.detail_box.addWidget(line)
        self.detail_box.addWidget(label('Save files','eyebrow'))
        if files:
            for path in files[:3]:
                row=QFrame();row.setObjectName('saveRow');row_box=layout(row,False,10,8)
                details=QVBoxLayout();details.setSpacing(2)
                open_save=button(path.name,lambda checked=False,p=path,g=game.id:self.load(g,p),'saveLink')
                open_save.setAccessibleName('Open '+path.name);open_save.setToolTip(str(path));details.addWidget(open_save)
                try:
                    metadata=path.stat();size=metadata.st_size
                    size=f'{size/1048576:.1f} MB' if size>=1048576 else f'{size/1024:.1f} KB'
                    size+='  ·  '+datetime.fromtimestamp(metadata.st_mtime).strftime('%Y-%m-%d %H:%M')
                except OSError:size='Local save'
                details.addWidget(label(size,'small',True));row_box.addLayout(details,1)
                folder=button('↗',lambda checked=False,p=path:self.open_save_folder(p),'rowMenu');folder.setAccessibleName('Open folder for '+path.name);folder.setToolTip('Open save folder');row_box.addWidget(folder);row.setToolTip(str(path));self.detail_box.addWidget(row)
            if len(files)>3:self.detail_box.addWidget(label(f'+ {len(files)-3} more','small'))
        else:self.detail_box.addWidget(label('No save detected in the usual folders.','muted',True))
        self.detail_box.addStretch()
        self.detail_box.addWidget(label('Actions','eyebrow'))
        choose=button('Choose save file…',lambda:self.open_file(game.id));choose.setEnabled(game.editable);self.detail_box.addWidget(choose)
        if files:self.detail_box.addWidget(button('Open save folder',lambda:self.open_save_folder(files[0])))
        if not game.editable:self.detail_box.addWidget(label('Support for this game will be added in a future update.','small',True))

    def open_selected_game(self):
        if self.selected_game:self.select_game(BY_ID[self.selected_game])

    def open_save_folder(self,path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(path).parent)))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        if hasattr(self,'save_steps'):
            compact=self.height()<850
            self.save_steps.setVisible(not compact);self.summary_description.setVisible(not compact)
            self.saving_heading.setVisible(not compact);self.saving_note.setVisible(not compact)
        if not hasattr(self,'library_scroll') or self._reflow_pending:return
        self._reflow_pending=True
        QTimer.singleShot(80,self.reflow_library)

    def reflow_library(self):
        self._reflow_pending=False
        if not hasattr(self,'library_scroll'):return
        compact=self.width()<1400
        row,column,row_span,column_span=self.library_toolbar.getItemPosition(self.library_toolbar.indexOf(self.library_filter_controls))
        if row != int(compact):
            self.library_toolbar.addWidget(self.library_filter_controls,1 if compact else 0,0 if compact else 1,1,3 if compact else 1)
            self.library_toolbar.activate()
        available=max(180,self.library_scroll.viewport().width())
        columns=max(1,(available+8)//188)
        if columns!=self.grid_columns or abs(available-self.grid_available_width)>8:
            position=self.library_scroll.verticalScrollBar().value()
            self.render_cards()
            self.library_scroll.verticalScrollBar().setValue(position)

    def show_library(self):
        if self.favorites_only:
            self.favorites_only=False;self.render_cards()
        self.switch_view(0);self.library_nav.setChecked(True);self.editor_nav.setChecked(False);self.favorites_nav.setChecked(False)

    def show_editor(self):
        if self.save:
            self.switch_view(1);self.library_nav.setChecked(False);self.editor_nav.setChecked(True);self.favorites_nav.setChecked(False)

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
        folder=str(self.path.parent) if self.path else self.last_directory
        filename,_=QFileDialog.getOpenFileName(self,'Open a save',folder, 'Save files (*.sav *.png *.mps *.bin *.xml *.psd *.PSD *.cfg *.CFG);;All files (*)')
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
        try:
            raw = read_limited(path)
            account = getattr(self, 'kh3_accounts', {}).get(str(path))
            try:
                save = Save(raw,game,path=path,account_id=account)
            except ValueError as error:
                from kh3_pc import AccountIdRequired
                if not isinstance(error, AccountIdRequired):raise
                account, accepted = QInputDialog.getText(self,'Encrypted PC save','Enter the original SteamID64. Files in their normal save folder are detected automatically. A downloaded or copied save needs the original owner\'s SteamID64:')
                if not accepted:return False
                save = Save(raw,game,path=path,account_id=account.strip())
                if not hasattr(self, 'kh3_accounts'):self.kh3_accounts = {}
                self.kh3_accounts[str(path)] = account.strip()
        except (ValueError,OSError) as error:
            QMessageBox.warning(self,'Could not open the save',str(error));return False
        self.save=save;self.path=Path(path);self.edits={};self.inputs={};self.exported_state=None;self.slot_index=0
        self.last_directory=str(self.path.parent)
        gameinfo=BY_ID[game];self.selected_game=game
        self.editor_title.setText(gameinfo.title)
        self.editor_eyebrow.setText('EDITOR / '+gameinfo.subtitle.upper())
        self.editor_subtitle.setText(gameinfo.description)
        self.review_button.setText('Review and apply  →')
        self.install_note.setText('Apply updates the opened file in its current location and keeps its name. No automatic backup is created. Close the game before applying.')
        self.file_combo.blockSignals(True);self.file_combo.clear()
        paths=[p for g,p in self.files if g==game]
        if self.path not in paths:paths.append(self.path)
        for p in paths:self.file_combo.addItem(p.name,p)
        self.file_combo.setCurrentIndex(paths.index(self.path));self.file_combo.setToolTip(str(self.path));self.file_combo.blockSignals(False)
        self.slot_combo.blockSignals(True);self.slot_combo.clear()
        self.slot_combo.addItems([s.name for s in save.slots]);self.slot_combo.blockSignals(False)
        self.slot_combo.setVisible(len(save.slots)>1)
        self.warning.setText('\n'.join(save.warnings));self.warning.setVisible(bool(save.warnings))
        notes=getattr(save,'notes',[]);self.editor_notes.setText('\n'.join(notes));self.editor_notes.setVisible(bool(notes))
        self.repair.blockSignals(True);self.repair.setChecked(False);self.repair.setVisible(bool(save.warnings));self.repair.blockSignals(False)
        self.editor_nav.setEnabled(True)
        if gameinfo.experimental:
            self.install_note.setText(self.install_note.text()+' Experimental support: in-game validation is still pending.')
        self.render_fields();self.show_editor()
        return True

    def select_file(self,index):
        target=self.file_combo.itemData(index)
        if not self.load(self.save.game,target):
            self.file_combo.setCurrentIndex(self.file_combo.findData(self.path))

    def change_slot(self,index):
        if self.save and index>=0:self.slot_index=index;self.render_fields()

    def render_fields(self):
        previous=self.tabs.tabText(self.tabs.currentIndex()) if self.editor_page_game==self.save.game else ''
        self.editor_page_game=self.save.game
        self.inputs={};self.category_filters=[]
        while self.tabs.count():
            widget=self.tabs.widget(0);self.tabs.removeTab(0);widget.deleteLater()
        for category in organize_fields(self.save.game,self.save.slots[self.slot_index].fields):
            self.tabs.addTab(self.build_category(category),category.name)
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index)==previous:self.tabs.setCurrentIndex(index);break
        self.update_summary()

    def build_category(self,category):
        page=QWidget();box=layout(page,True,4,10)
        scroll=QScrollArea();scroll.setWidgetResizable(True)
        content=QWidget();sections_box=layout(content,True,0,12)
        box.addWidget(label(category.description,'muted',True))
        state=self.editor_view_state.setdefault((self.save.game,str(self.path),category.name),{})
        selections=list(dict.fromkeys(section.selection for section in category.sections))
        selector=QComboBox(page);selector.setObjectName('sectionSelector')
        selector.setAccessibleName(category.selector_label+' in '+category.name)
        if category.selector_label!='Character':selector.addItem('All sections','')
        for name in selections:selector.addItem(name,name)
        default='' if category.name in ('Progress','Records') else selections[0]
        selected=state.get('selection',default)
        selector.setCurrentIndex(max(0,selector.findData(selected)))
        controls=QHBoxLayout()
        field_filter=QLineEdit();field_filter.setObjectName('fieldSearch')
        field_filter.setPlaceholderText('Search fields by name or item ID…')
        field_filter.setAccessibleName('Search '+category.name);field_filter.setClearButtonEnabled(True)
        field_filter.setText(state.get('query',''));controls.addWidget(field_filter,1)
        if len(selections)>1:
            selector.setFixedWidth(190);selector.setToolTip('Choose a '+category.selector_label.lower());controls.addWidget(selector)
        else:selector.hide()
        box.addLayout(controls)
        tools=QHBoxLayout();changed_only=QCheckBox('Changed only');changed_only.setObjectName('changedOnly')
        changed_only.setAccessibleName('Show changed fields in '+category.name);changed_only.setChecked(state.get('changed_only',False))
        matches=label('','small');matches.setObjectName('fieldCount');tools.addWidget(changed_only);tools.addStretch();tools.addWidget(matches);box.addLayout(tools)
        empty=label('No fields match this section and search.','muted');empty.hide();sections_box.addWidget(empty)
        blocks=[]
        for section in category.sections:
            block=QFrame();block.setObjectName('editorSection');section_box=layout(block,True,10,6)
            header=button('',lambda:None,'sectionToggle');header.setCheckable(True)
            header.setAccessibleName(section.selection+' · '+section.name)
            collapsed=state.setdefault('collapsed',{}).get((section.selection,section.name),section.name.endswith(' form'))
            header.setChecked(not collapsed);section_box.addWidget(header)
            body=QWidget();body.setObjectName('clearSurface');body_box=layout(body,True,0,8)
            unlock_fields=[field for field in section.fields if field.fmt=='xml-unlock' or field.boolean]
            if unlock_fields:
                actions=QHBoxLayout()
                actions.addWidget(button('Unlock section' if self.save.game=='ror2' else 'Enable all',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,1),'primary'))
                if self.save.game=='alice':actions.addWidget(button('Disable all',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,0)))
                actions.addWidget(button('Restore section',lambda checked=False,fs=unlock_fields:self.set_unlock_fields(fs,None)))
                actions.addStretch();body_box.addLayout(actions)
            rows=[]
            for field in section.fields:
                row=self.build_field_row(field)
                body_box.addWidget(row)
                searchable=' '.join((field.label,field.key,section.name,section.selection)).casefold()
                rows.append((searchable,row,field.key))
            section_box.addWidget(body);sections_box.addWidget(block)
            blocks.append((section,block,header,body,rows))

        def filter_sections():
            query=field_filter.text().casefold().strip();selection=selector.currentData()
            state['query']=field_filter.text();state['selection']=selection
            state['changed_only']=changed_only.isChecked()
            total=0
            for section,block,header,body,rows in blocks:
                eligible=not selection or selection==section.selection
                count=0
                for searchable,row,key in rows:
                    visible=eligible and query in searchable and (not changed_only.isChecked() or (self.slot_index,key) in self.edits)
                    row.setVisible(visible);count+=visible
                block.setVisible(bool(count));total+=count
                expanded=header.isChecked() or bool(query) or changed_only.isChecked()
                header.setText(('▾  ' if expanded else '▸  ')+section.name+f'  ·  {count}')
                body.setVisible(expanded)
            empty.setVisible(not total)
            empty.setText('No pending changes match this section and search.' if changed_only.isChecked() else 'No fields match this section and search.')
            matches.setText(f'{total} field'+('s' if total!=1 else '')+' shown')
        def toggle_section(checked,section):
            state['collapsed'][(section.selection,section.name)]=not checked
            filter_sections()
        for section,block,header,body,rows in blocks:
            header.toggled.connect(lambda checked,s=section:toggle_section(checked,s))
        selector.currentIndexChanged.connect(lambda:filter_sections())
        field_filter.textChanged.connect(lambda:filter_sections())
        changed_only.toggled.connect(lambda:filter_sections());self.category_filters.append(filter_sections)
        filter_sections()
        sections_box.addStretch();scroll.setWidget(content);box.addWidget(scroll,1)
        return page

    def build_field_row(self,field):
        row=QFrame();row.setObjectName('field');line=layout(row,False,8,16)
        caption=QVBoxLayout();caption.addWidget(label(field.label))
        if field.fmt == 'xml-unlock' or field.boolean or field.choices:
            caption.addWidget(label(f'Original: {value_text(field,field.value)}  ·  {field.key.removeprefix("unlock:")}','small',True))
        else:
            caption.addWidget(label(f'Original: {number_text(field.value)}  ·  Range: {field.minimum:,}–{field.maximum:,}','small',True))
        if field.note:caption.addWidget(label(field.note,'small',True))
        error_label=label('','fieldError',True);error_label.hide();caption.addWidget(error_label)
        line.addLayout(caption,1)
        key=(self.slot_index,field.key)
        if field.fmt == 'xml-unlock' or field.boolean:
            entry=QCheckBox('Unlocked' if self.save.game=='ror2' else 'Owned' if self.save.game=='maxpayne' else 'Enabled')
            entry.setChecked(bool(int(self.edits.get(key,field.value))))
            entry.toggled.connect(lambda checked,k=key,f=field,e=entry:self.unlock_changed(k,f,e,checked))
        elif field.choices:
            entry=QComboBox();entry.addItems(field.choices);entry.setFixedWidth(190)
            entry.setCurrentIndex(int(self.edits.get(key,field.value)))
            entry.currentIndexChanged.connect(lambda value,k=key,f=field,e=entry:self.choice_changed(k,f,e,value))
        else:
            entry=QLineEdit(self.edits.get(key,number_text(field.value)))
            entry.setFixedWidth(130);entry.setAlignment(Qt.AlignmentFlag.AlignRight)
            entry.textChanged.connect(lambda text,k=key,f=field,e=entry:self.edit_changed(k,f,e,text))
        entry.setAccessibleName(field.label)
        self.inputs[key]=entry;line.addWidget(entry)
        revert=button('↶',lambda checked=False,k=key:self.restore_field(k),'fieldReset')
        revert.setAccessibleName('Reset '+field.label);revert.setToolTip('Restore the value from the opened file')
        line.addWidget(revert)
        entry._reset_button=revert;entry._error_label=error_label;entry._field_row=row
        if isinstance(entry,QLineEdit):self.mark_entry(entry,field,entry.text())
        else:self.mark_unlock(entry,field,entry.isChecked() if isinstance(entry,QCheckBox) else entry.currentIndex())
        return row

    def restore_field(self,key):
        field=next(f for f in self.save.slots[key[0]].fields if f.key==key[1])
        entry=self.inputs.get(key)
        if isinstance(entry,QLineEdit):entry.setText(number_text(field.value))
        elif isinstance(entry,QCheckBox):entry.setChecked(bool(field.value))
        elif isinstance(entry,QComboBox):entry.setCurrentIndex(int(field.value))
        self.edits.pop(key,None);self.update_summary()

    def set_unlock_fields(self,fields,value):
        self._batch_edit=True
        try:
            for field in fields:
                key=(self.slot_index,field.key)
                checkbox=self.inputs.get(key)
                if isinstance(checkbox,QCheckBox):
                    checkbox.setChecked(bool(field.value if value is None else value))
        finally:self._batch_edit=False;self.update_summary()

    def mark_unlock(self,entry,field,checked):
        changed=int(checked) != field.value
        if isinstance(entry,QCheckBox):
            states=('Locked','Unlocked') if self.save.game=='ror2' else ('Not owned','Owned') if self.save.game=='maxpayne' else ('Disabled','Enabled')
            entry.setText(states[bool(checked)])
        entry.setProperty('changed',changed)
        entry._reset_button.setEnabled(changed)
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
        try:
            value=field.parse(text);valid=True;changed=value!=field.value;error=''
        except ValueError as failure:
            valid=False;changed=True;error=str(failure)
        entry.setProperty('invalid',changed and not valid);entry.setProperty('changed',changed)
        entry._reset_button.setEnabled(changed)
        entry._error_label.setText(error);entry._error_label.setVisible(not valid)
        entry.setToolTip(error if not valid else f'Allowed range: {field.minimum:,}–{field.maximum:,}')
        entry.style().unpolish(entry);entry.style().polish(entry)

    def edit_changed(self,key,field,entry,text):
        try:unchanged=field.parse(text)==field.value
        except ValueError:unchanged=False
        if unchanged:self.edits.pop(key,None)
        else:self.edits[key]=text
        self.mark_entry(entry,field,text);self.update_summary()

    def validated_changes(self):
        changes={}
        for (index,key),text in self.edits.items():
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            try:value=field.parse(text)
            except ValueError as error:
                message=str(error);raise ValueError(message if message.startswith(field.label+':') else f'{field.label}: {message}')
            if not field.minimum<=value<=field.maximum:raise ValueError(f'{field.label}: use a value between {field.minimum} and {field.maximum}.')
            changes[(index,key)]=value
        return changes

    def update_summary(self):
        if not hasattr(self,'summary_box') or self._batch_edit:return
        clear(self.summary_box)
        count=len(self.edits)
        self.change_count.setText(f'{count:02d} change'+('s' if count!=1 else '') if count else 'No changes')
        visible_edits=list(self.edits.items())
        for (index,key),text in visible_edits[:80]:
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            item=QWidget();item.setObjectName('clearSurface');item_box=layout(item,True,0,3)
            heading=QHBoxLayout();heading.addWidget(label(field.label,'summaryName',True),1)
            undo=button('↶',lambda checked=False,k=(index,key):self.restore_field(k),'fieldReset');undo.setToolTip('Undo this change');undo.setAccessibleName('Undo '+field.label+' in '+self.save.slots[index].name);heading.addWidget(undo);item_box.addLayout(heading)
            item_box.addWidget(label(f'{value_text(field,field.value)}  →  {value_text(field,text) if text else "…"}','muted',True))
            if len(self.save.slots)>1:item_box.addWidget(label(self.save.slots[index].name,'small',True))
            self.summary_box.addWidget(item)
        if len(visible_edits)>80:
            self.summary_box.addWidget(label(f'+ {len(visible_edits)-80} more changes','muted',True))
        if not count:self.summary_box.addWidget(label('Your edits will appear here.','muted',True))
        if self.repair.isChecked():self.summary_box.addWidget(label('The CRC will be repaired in the opened save.','success',True))
        valid=True
        try:self.validated_changes()
        except ValueError as error:
            valid=False;self.summary_box.addWidget(label(str(error),'warning',True))
        self.summary_box.addStretch()
        has_work=bool(count or self.repair.isChecked())
        can_repair=not self.save or not self.save.warnings or self.repair.isChecked()
        self.review_button.setEnabled(bool(self.save and has_work and valid and can_repair))
        self.reset_button.setEnabled(has_work)
        if self.save:
            marker=' *' if has_work else ''
            self.setWindowTitle(f'UniversalSaveEditor — {BY_ID[self.save.game].title}{marker}')
            state=f'{count} pending change'+('s' if count!=1 else '') if count else 'No pending changes'
            if not valid:state+=' · Fix invalid values before applying'
            elif self.repair.isChecked():state+=' · Integrity repair selected'
            elif self.save.warnings:state+=' · Integrity repair required'
            self.statusBar().showMessage(f'{self.path.name} · {state}')
        for refresh in self.category_filters:refresh()

    def reset(self):
        if self.save and self.may_discard():
            self.edits={};self.exported_state=None;self.repair.setChecked(False);self.render_fields()

    def review(self):
        if not self.save or not self.review_button.isEnabled():return
        try:output=self.save.patched(self.validated_changes(),repair_crc=self.repair.isChecked())
        except ValueError as error:
            QMessageBox.warning(self,'Review your edits',str(error));return
        dialog=QDialog(self);dialog.setWindowTitle('Review and apply');dialog.resize(650,550)
        box=layout(dialog,True,24,16)
        box.addWidget(label('ONE LAST LOOK','eyebrow'));box.addWidget(label('Your edited save','title'))
        box.addWidget(label(f'Changes will be saved directly to {self.path.name}. No automatic backup is created.','muted',True))
        text=QTextEdit();text.setReadOnly(True)
        lines=[]
        for (index,key),value in self.validated_changes().items():
            field=next(f for f in self.save.slots[index].fields if f.key==key)
            lines.append(f'{self.save.slots[index].name}\n{field.label}: {value_text(field,field.value)} → {value_text(field,value)}')
        if self.repair.isChecked():lines.append('Repair the save block CRC in the opened save.')
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
        if BY_ID[self.save.game].experimental:
            box.addWidget(label('Experimental support: in-game validation is still pending.','small',True))
        actions=QHBoxLayout();actions.addWidget(button('Back',dialog.reject));actions.addStretch()
        def write():
            try:replace_current(self.path,self.save.raw,output)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'Could not apply changes',str(error));return
            slot_index=self.slot_index
            self.exported_state=self.state_signature();dialog.accept()
            self.load(self.save.game,self.path)
            self.slot_combo.setCurrentIndex(slot_index);self.change_slot(slot_index)
            self.statusBar().showMessage(f'Changes applied to {BY_ID[self.save.game].title} · Save updated and verified')
            QMessageBox.information(self,'Changes applied',f'Save updated:\n{self.path}')
        actions.addWidget(button('Apply to active save',write,'primary'));box.addLayout(actions)
        dialog.exec()

    def open_backups(self):
        if not self.save:return
        dialog=QDialog(self);dialog.setWindowTitle('Restore existing backup');dialog.resize(720,440)
        box=layout(dialog,True,24,14);box.addWidget(label('Restore a previous save','title'))
        box.addWidget(label('Restore a backup you already have. This replaces the opened save without creating a new backup. Close the game before restoring.','muted',True))
        choice=QComboBox();choice.setAccessibleName('Available backups');box.addWidget(choice)
        details=label('','muted',True);box.addWidget(details)
        try:backups=backup_files(self.path)
        except OSError as error:
            QMessageBox.warning(self,'Could not list backups',str(error));return
        for path in backups:
            try:date=datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            except OSError:continue
            choice.addItem(date+'  ·  '+path.name,path)
        if not choice.count():details.setText('No backups found beside this save. You can choose an original .bak file manually.')
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
            try:Save(read_limited(path),self.save.game,path=self.path,account_id=self.save.account_id)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'Invalid backup',str(error));return
            if not self.may_discard():return
            answer=QMessageBox.question(dialog,'Restore backup','Restore this backup to the opened save?\n\n'+str(path)+'\n\nThe current file will be replaced. No new backup will be created.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.Cancel,QMessageBox.StandardButton.Cancel)
            if answer!=QMessageBox.StandardButton.Yes:return
            try:restore_backup(self.path,path,self.save.game,account_id=self.save.account_id)
            except (ValueError,OSError) as error:
                QMessageBox.warning(dialog,'Could not restore backup',str(error));return
            self.edits={};self.repair.setChecked(False);dialog.accept()
            self.load(self.save.game,self.path)
            QMessageBox.information(self,'Backup restored','Save restored:\n'+str(self.path))
        restore=button('Restore selected backup',apply_backup,'primary');restore.setEnabled(bool(choice.count()));actions.addWidget(restore);box.addLayout(actions)
        dialog.exec()

    def open_guide(self):
        dialog=QDialog(self);dialog.setWindowTitle('UniversalSaveEditor guide');dialog.resize(760,650)
        box=layout(dialog,True,24,16);box.addWidget(label('Before returning to the game','title'))
        text=QTextEdit();text.setReadOnly(True);text.setMarkdown((ROOT/'README.md').read_text(encoding='utf-8'))
        box.addWidget(text,1);box.addWidget(button('Got it',dialog.accept));dialog.exec()

    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls() and len(event.mimeData().urls())==1 and event.mimeData().urls()[0].isLocalFile():event.acceptProposedAction()

    def dropEvent(self,event):
        urls=event.mimeData().urls()
        if len(urls)!=1 or not urls[0].isLocalFile():event.ignore();return
        self.open_path(Path(urls[0].toLocalFile()));event.acceptProposedAction()

    def closeEvent(self,event):
        if self.may_discard():
            if self.settings is not None:
                self.settings.setValue('window/geometry',self.saveGeometry())
                self.settings.setValue('files/lastDirectory',self.last_directory)
                self.settings.setValue('appearance/theme',self.theme)
                self.settings.setValue('appearance/reduceMotion',self.reduce_motion.isChecked())
                self.settings.setValue('library/favorites',sorted(self.favorites))
                self.settings.sync()
            self.transition.stop()
            event.accept()
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
    window=Window(settings=None if '--smoke-test' in sys.argv else QSettings('UniversalSaveEditor','UniversalSaveEditor'));window.show()
    if '--smoke-test' in sys.argv:
        # Used by release validation; exercises the packaged resources and Qt.
        import json
        destination=Path(sys.argv[sys.argv.index('--smoke-test')+1])
        def check_startup():
            from kh3_pc import transform, derive_key
            import re
            cipher = transform(bytes(16),'smoke-test',True)
            crypto_ready = len(derive_key('smoke-test')) == 32 and transform(cipher,'smoke-test') == bytes(16)
            try:
                from re_engine_container import blowfish_cbc,KEYS,_aes
                from re_hashes import city64
                from re5_save import encode,decode,FILE_SIZE
                from re6_save import Re6Save
                from re_hd_save import ReHdSave
                marker=blowfish_cbc(b'DSSSDSSS',KEYS['re2'],True)
                vector=_aes(bytes.fromhex('6bc1bee22e409f96e93d7e117393172a'),
                            bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c'),
                            bytes.fromhex('000102030405060708090a0b0c0d0e0f'))
                resident_evil_ready=(blowfish_cbc(marker,KEYS['re2'])==b'DSSSDSSS'
                                     and vector.hex()=='3b3fd92eb72dad20333449f8e83cfb4a'
                                     and city64(b'')==0x9ae16a3b2f90404f
                                     and bytes(decode(encode(bytes(FILE_SIZE))))==bytes(FILE_SIZE))
            except Exception:
                resident_evil_ready=False
            crypto_ready=crypto_ready and resident_evil_ready
            covers={g.id:not Artwork._cache[g.id].isNull() for g in GAMES}
            report={'title':window.windowTitle(),'covers':covers,
                    'platformIcons':{p:not platform_pixmap(p).isNull() for p in PLATFORMS},
                    'version':VERSION,
                    'appearance':window.theme,
                    'appearanceReady':all(not re.search(r'@[A-Za-z]+@',stylesheet(theme)) for theme in PALETTES) and QSvgRenderer(str(ROOT/'assets/ui/check.svg')).isValid(),
                    'cryptoReady':crypto_ready,
                    'residentEvilReady':resident_evil_ready,
                    'games':len(window.visible_games),'icon':not app.windowIcon().isNull(),
                    'ror2Unlocks':len(UNLOCK_IDS),
                    'frozen':bool(getattr(sys,'frozen',False))}
            destination.write_text(json.dumps(report,indent=2),encoding='utf-8')
            window.grab().save(str(destination.with_suffix('.png')))
            app.exit(0 if crypto_ready and report['appearanceReady'] and all(covers.values()) and all(report['platformIcons'].values()) else 1)
        QTimer.singleShot(1000,check_startup)
    sys.exit(app.exec())

if __name__=='__main__':main()
