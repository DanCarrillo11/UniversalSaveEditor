"""Modern library and local backup controls for UniversalSaveEditor.

The editor and its save parsers stay in app.py/core.py. This module only
presents discovered games/files and makes verified local backup copies.
"""
import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from artwork import Artwork
from catalog import BY_ID, GAMES
from core import Save, read_limited, replace_current


def label(text, name='', wrap=False):
    widget = QLabel(text)
    widget.setObjectName(name)
    widget.setWordWrap(wrap)
    widget.setTextFormat(Qt.TextFormat.PlainText)
    return widget


def button(text, handler, name=''):
    widget = QPushButton(text)
    widget.setObjectName(name)
    widget.setCursor(Qt.CursorShape.PointingHandCursor)
    widget.clicked.connect(handler)
    return widget


def column(widget, margins=0, spacing=12):
    box = QVBoxLayout(widget)
    box.setContentsMargins(margins, margins, margins, margins)
    box.setSpacing(spacing)
    return box


def wipe(box):
    while box.count():
        item = box.takeAt(0)
        if item.widget():
            item.widget().hide()
            item.widget().deleteLater()
        elif item.layout():
            wipe(item.layout())


def build_library(window):
    window.preview_game_id = 'webfishing'
    window.preview_file = None
    window.library_mode = 'library'
    window.library_columns = 3

    page = QWidget()
    outer = QHBoxLayout(page)
    outer.setContentsMargins(22, 22, 18, 18)
    outer.setSpacing(16)

    center = QWidget()
    content = column(center, 0, 15)

    head = QHBoxLayout()
    heading = QVBoxLayout()
    heading.setSpacing(2)
    heading.addWidget(label('BIBLIOTECA PERSONAL', 'eyebrow'))
    heading.addWidget(label('Mis juegos', 'title'))
    head.addLayout(heading)
    head.addStretch()
    head.addWidget(button('Actualizar', window.scan))
    head.addWidget(button('+ Abrir partida', window.open_file, 'primary'))
    content.addLayout(head)

    hint = label('Tus partidas locales, siempre bajo tu control.', 'muted', True)
    content.addWidget(hint)

    filters = QHBoxLayout()
    filters.setSpacing(8)
    window.search = QLineEdit()
    window.search.setPlaceholderText('Buscar juegos...')
    window.search.setAccessibleName('Search games')
    window.search.setClearButtonEnabled(True)
    window.search.textChanged.connect(window.render_cards)
    filters.addWidget(window.search, 1)
    window.filter_buttons = []
    for key, name in [('all', 'Todos'), ('ready', 'Editables'), ('pending', 'Próximamente')]:
        control = button(name, lambda checked=False, k=key: window.set_filter(k), 'filter')
        control.setCheckable(True)
        control.setChecked(key == 'all')
        window.filter_buttons.append((key, control))
        filters.addWidget(control)
    content.addLayout(filters)

    toolbar = QHBoxLayout()
    window.available = label(
        str(sum(game.editable for game in GAMES)) + ' EDITORES DISPONIBLES', 'success')
    window.detected = label('0 ARCHIVOS ENCONTRADOS', 'muted')
    toolbar.addWidget(window.available)
    toolbar.addSpacing(14)
    toolbar.addWidget(window.detected)
    toolbar.addStretch()
    window.sort_combo = QComboBox()
    window.sort_combo.addItems(['Orden original', 'Nombre A-Z', 'Nombre Z-A'])
    window.sort_combo.currentIndexChanged.connect(window.render_cards)
    toolbar.addWidget(window.sort_combo)
    content.addLayout(toolbar)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    container = QWidget()
    window.grid = QGridLayout(container)
    window.grid.setContentsMargins(0, 0, 8, 0)
    window.grid.setHorizontalSpacing(12)
    window.grid.setVerticalSpacing(14)
    scroll.setWidget(container)
    content.addWidget(scroll, 1)
    content.addWidget(label(
        'Solo los juegos marcados como editables tienen un editor activo. '
        'Los demás están en investigación.', 'small', True))
    outer.addWidget(center, 1)

    pane = QFrame()
    pane.setObjectName('inspector')
    pane.setFixedWidth(330)
    ins_layout = column(pane, 16, 10)
    window.inspector_scroll = QScrollArea()
    window.inspector_scroll.setWidgetResizable(True)
    window.inspector_content = QWidget()
    window.inspector_box = column(window.inspector_content, 0, 12)
    window.inspector_scroll.setWidget(window.inspector_content)
    ins_layout.addWidget(window.inspector_scroll)
    outer.addWidget(pane)
    window.stack.addWidget(page)


def _files_for(window, game_id):
    return [Path(p) for gid, p in window.files if gid == game_id]


def _backups_for(source):
    if source is None:
        return []
    source = Path(source)
    files = list(source.parent.glob(source.name + '.manual-*.bak'))
    files += list(source.parent.glob(source.name + '.original-*.bak'))
    return sorted(set(files), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)


def render_cards(window):
    if not hasattr(window, 'grid'):
        return
    wipe(window.grid)
    query = window.search.text().casefold().strip()
    games = [
        game for game in GAMES
        if query in (game.title + ' ' + game.subtitle + ' ' + game.family + ' ' + game.description).casefold()
        and (window.filter == 'all' or game.editable == (window.filter == 'ready'))
    ]
    sort = window.sort_combo.currentIndex()
    if sort == 1:
        games.sort(key=lambda item: item.title.casefold())
    elif sort == 2:
        games.sort(key=lambda item: item.title.casefold(), reverse=True)
    window.visible_games = [game.id for game in games]

    columns = 3 if window.width() >= 1220 else 2
    window.library_columns = columns
    for index, game in enumerate(games):
        card = QFrame()
        card.setObjectName('card')
        card.setProperty('selected', game.id == window.preview_game_id)
        card.setMinimumWidth(170)
        box = column(card, 9, 6)
        art = Artwork(game)
        art.setFixedHeight(155)
        box.addWidget(art)
        name = label(game.title, 'cardTitle', True)
        box.addWidget(name)
        box.addWidget(label(game.subtitle, 'small', True))
        count = len(_files_for(window, game.id))
        box.addWidget(label(
            str(count) + (' archivo detectado' if count == 1 else ' archivos detectados')
            if count else 'Sin partidas detectadas', 'small'))
        state = label('EDITOR ACTIVO' if game.editable else 'EN DESARROLLO',
                      'badge' if game.editable else 'pending')
        box.addWidget(state)
        features = label(game.description, 'cardDescription', True)
        features.setAccessibleName('Editor features for ' + game.title)
        features.setMaximumHeight(30)
        box.addWidget(features)
        actions = QHBoxLayout()
        actions.setSpacing(5)
        actions.addWidget(button('Detalles', lambda checked=False, g=game.id: choose_game(window, g)))
        actions.addWidget(button(
            'Editar →' if game.editable else 'Estado',
            lambda checked=False, g=game: window.select_game(g), 'cardAction'))
        box.addLayout(actions)
        window.grid.addWidget(card, index // columns, index % columns)

    if not games:
        window.grid.addWidget(
            label('No hay juegos que coincidan con la búsqueda.', 'muted', True),
            0, 0, 1, columns)
    for col in range(3):
        window.grid.setColumnStretch(col, 1 if col < columns else 0)
    window.grid.setRowStretch((len(games) + columns - 1) // columns, 1)
    render_preview(window)


def choose_game(window, game_id):
    window.preview_game_id = game_id
    window.preview_file = None
    render_cards(window)


def choose_file(window, source):
    window.preview_file = Path(source)
    render_preview(window)


def render_preview(window):
    if not hasattr(window, 'inspector_box'):
        return
    box = window.inspector_box
    wipe(box)
    game = BY_ID.get(window.preview_game_id, GAMES[0])
    files = _files_for(window, game.id)
    if window.preview_file not in files:
        window.preview_file = files[0] if files else None

    box.addWidget(label(
        {'library': 'DETALLES DEL JUEGO', 'backups': 'RESPALDOS',
         'restore': 'RESTAURAR PARTIDA'}.get(window.library_mode, 'DETALLES'), 'eyebrow'))

    identity = QHBoxLayout()
    cover = Artwork(game)
    cover.setFixedSize(96, 132)
    identity.addWidget(cover)
    text = QVBoxLayout()
    text.addWidget(label(game.title, 'section', True))
    text.addWidget(label(game.subtitle, 'muted', True))
    text.addWidget(label('Editor disponible' if game.editable else 'Próximamente',
                         'success' if game.editable else 'small', True))
    text.addStretch()
    identity.addLayout(text, 1)
    box.addLayout(identity)
    description = label(game.description, 'muted', True)
    box.addWidget(description)

    box.addWidget(label('PARTIDAS ENCONTRADAS', 'eyebrow'))
    if files:
        for path in files[:10]:
            selected = path == window.preview_file
            choice = button(('●  ' if selected else '○  ') + path.name,
                            lambda checked=False, p=path: choose_file(window, p), 'fileChoice')
            choice.setToolTip(str(path))
            choice.setProperty('selected', selected)
            box.addWidget(choice)
        if len(files) > 10:
            box.addWidget(label('+' + str(len(files) - 10) + ' archivos más', 'small'))
    else:
        box.addWidget(label(
            'No se encontró una partida en las carpetas habituales. '
            'Puedes abrir una manualmente.', 'muted', True))

    source = window.preview_file
    if source is not None:
        try:
            size = source.stat().st_size
            box.addWidget(label(
                'Seleccionado: ' + source.name + '\nTamaño: ' + f'{size / 1024:.1f}' + ' KB',
                'small', True))
        except OSError:
            box.addWidget(label('El archivo ya no está disponible.', 'warning', True))

    backups = _backups_for(source)
    box.addWidget(label('COPIAS DE SEGURIDAD', 'eyebrow'))
    if backups:
        for backup in backups[:5]:
            stamp = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%d/%m/%Y %H:%M')
            box.addWidget(label(backup.name + '\n' + stamp, 'backupEntry', True))
        if len(backups) > 5:
            box.addWidget(label('+' + str(len(backups) - 5) + ' copias más', 'small'))
    else:
        box.addWidget(label('Todavía no hay respaldos para esta partida.', 'small', True))

    box.addWidget(label('ACCIONES', 'eyebrow'))
    row = QHBoxLayout()
    edit = button('Abrir editor', lambda: window.select_game(game), 'primary')
    edit.setEnabled(game.editable)
    row.addWidget(edit)
    folder = button('Abrir carpeta', lambda: open_folder(window))
    folder.setEnabled(source is not None)
    row.addWidget(folder)
    box.addLayout(row)
    actions = QHBoxLayout()
    create = button('Respaldar', lambda: backup_save(window), 'backupAction')
    create.setEnabled(source is not None)
    actions.addWidget(create)
    restore = button('Restaurar', lambda: restore_save(window), 'restoreAction')
    restore.setEnabled(source is not None and game.editable and bool(backups))
    actions.addWidget(restore)
    box.addLayout(actions)
    box.addWidget(label(
        'Al editar, el programa conserva el original. '
        'Al restaurar, crea otra copia antes de reemplazar.', 'small', True))
    box.addStretch()


def open_folder(window):
    if window.preview_file is None:
        return
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(window.preview_file.parent)))


def backup_bytes(source):
    """Preserve an exact verified copy; never alter the source save."""
    source = Path(source)
    original = read_limited(source)
    if read_limited(source) != original:
        raise ValueError('La partida cambió durante la lectura. Vuelve a intentarlo.')
    suffix = datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    target = source.with_name(source.name + '.manual-' + suffix + '.bak')
    try:
        with target.open('xb') as handle:
            handle.write(original)
            handle.flush()
            os.fsync(handle.fileno())
        if hashlib.sha256(read_limited(target)).digest() != hashlib.sha256(original).digest():
            raise OSError('No se pudo verificar la copia.')
        if read_limited(source) != original:
            raise ValueError('La partida cambió mientras se realizaba el respaldo.')
    except (OSError, ValueError):
        target.unlink(missing_ok=True)
        raise
    return target


def backup_save(window):
    if window.preview_file is None:
        return
    try:
        target = backup_bytes(window.preview_file)
    except (OSError, ValueError) as error:
        QMessageBox.warning(window, 'No se pudo respaldar', str(error))
        return
    render_preview(window)
    window.statusBar().showMessage('Respaldo verificado: ' + str(target))
    QMessageBox.information(window, 'Respaldo creado', 'Copia guardada en:\n' + str(target))


def restore_save(window):
    source = window.preview_file
    if source is None:
        return
    game_id = window.preview_game_id
    backups = _backups_for(source)
    if not backups:
        QMessageBox.information(window, 'Sin respaldos', 'Esta partida no tiene copias disponibles.')
        return
    filename, _ = QFileDialog.getOpenFileName(
        window, 'Elegir copia de seguridad', str(source.parent),
        'Copias de seguridad (*.bak)')
    if not filename:
        return
    selected = Path(filename).resolve()
    # Do not allow unrelated files or a backup belonging to another save.
    if selected not in {p.resolve() for p in backups}:
        QMessageBox.warning(window, 'Copia no válida',
                            'Elige una copia que pertenezca a la partida seleccionada.')
        return
    try:
        replacement = read_limited(selected)
        Save(replacement, game_id)
        current = read_limited(source)
    except (OSError, ValueError) as error:
        QMessageBox.warning(window, 'Copia no válida', str(error))
        return
    decision = QMessageBox.question(
        window, 'Confirmar restauración',
        'Se reemplazará esta partida:\n' + str(source)
        + '\n\nAntes se guardará otra copia del archivo actual. '
        'Cierra el juego antes de continuar.',
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No)
    if decision != QMessageBox.StandardButton.Yes:
        return
    if window.save is not None and window.path == source and not window.may_discard():
        return
    try:
        preserved = replace_current(source, current, replacement)
    except (OSError, ValueError) as error:
        QMessageBox.warning(window, 'Restauración fallida', str(error))
        return
    if window.path == source:
        window.save = None
        window.edits = {}
        window.exported_state = None
        window.repair.setChecked(False)
        window.editor_nav.setEnabled(False)
    window.scan()
    window.show_library(window.library_mode)
    QMessageBox.information(
        window, 'Partida restaurada',
        'Se restauró la partida y se conservó la versión anterior en:\n' + str(preserved))
