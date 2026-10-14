"""Visible category sections and character navigation for the save editor.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from collections import Counter
import weakref

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QHBoxLayout, QVBoxLayout, QGridLayout, QScrollArea, QSizePolicy,
)


def category_title(game, name):
    if name != 'Collection':
        return name
    return {'alice': 'Collectibles', 'recom': 'Cards', 'bbs': 'Commands',
            're5': 'Library', 're6': 'Equipment'}.get(game, 'Inventory')


class FieldControls(dict):
    """Materialize a requested field through the real section/page navigation."""
    def __init__(self, reveal):
        super().__init__()
        self._reveal = weakref.WeakMethod(reveal)

    def __missing__(self, key):
        reveal = self._reveal()
        if reveal is not None:
            reveal(key)
        if key not in self:
            raise KeyError(key)
        return dict.__getitem__(self, key)


class AttributeGrid(QWidget):
    """Keep short attribute controls together without squeezing narrow windows."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('attributeGrid')
        self.rows = []
        self.columns = 0
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(12)

    def add_row(self, row):
        self.rows.append(row)
        self.columns = 0
        self.reflow()

    def reflow(self):
        columns = 2 if self.width() >= 840 else 1
        if columns == self.columns:
            return
        self.columns = columns
        while self.grid.count():
            self.grid.takeAt(0)
        for index, row in enumerate(self.rows):
            self.grid.addWidget(row, index // columns, index % columns)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, int(columns == 2))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reflow()


class SectionNavigation(QWidget):
    """Two visible levels: section list, with character buttons when needed.

    The hidden selector is a state adapter for existing editor integrations;
    users navigate exclusively with the list and character buttons.
    """
    changed = Signal()

    def __init__(self, category, state, title, parent=None):
        super().__init__(parent)
        self.category, self.state = category, state
        self.title = title
        self.active_section = None
        self.character_buttons = {}
        self.setObjectName('categoryWorkspace')
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)
        self.side = QFrame(self)
        self.side.setObjectName('sectionSidebar')
        self.side.setFixedWidth(190)
        side = QVBoxLayout(self.side)
        side.setContentsMargins(10, 16, 10, 10)
        caption = QLabel(title.upper(), self.side)
        caption.setObjectName('navigationCaption')
        side.addWidget(caption)
        self.list = QListWidget(self.side)
        self.list.setObjectName('sectionNavigation')
        self.list.setAccessibleName('Sections in ' + title)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        side.addWidget(self.list, 1)
        root.addWidget(self.side)
        self.main = QWidget(self)
        self.main.setObjectName('clearSurface')
        self.main.setMinimumWidth(0)
        self.content = QVBoxLayout(self.main)
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(12)
        root.addWidget(self.main, 1)

        self.selector = QComboBox(self)
        self.selector.setObjectName('sectionSelector')
        self.selector.setAccessibleName(category.selector_label + ' in ' + title)
        selections = list(dict.fromkeys(s.selection for s in category.sections))
        if category.selector_label != 'Character':
            self.selector.addItem('Overview', '')
        for value in selections:
            self.selector.addItem(value, value)
        selected = state.get('selection', selections[0])
        if selected not in selections:
            selected = selections[0]
        self.selector.setCurrentIndex(self.selector.findData(selected))
        self.selector.hide()

        if category.selector_label == 'Character':
            self.characters = QScrollArea(self.main)
            self.characters.setObjectName('characterStrip')
            self.characters.setAccessibleName('Choose a character')
            self.characters.setWidgetResizable(True)
            self.characters.setFixedHeight(54)
            self.characters.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.characters.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            chips = QWidget()
            chips.setObjectName('clearSurface')
            row = QHBoxLayout(chips)
            row.setContentsMargins(0, 0, 0, 6)
            row.setSpacing(8)
            for value in selections:
                chip = QPushButton(value, chips)
                chip.setObjectName('characterChip')
                chip.setCheckable(True)
                chip.setAutoExclusive(True)
                chip.setAccessibleName('Choose ' + value)
                chip.setCursor(Qt.CursorShape.PointingHandCursor)
                chip.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
                chip.clicked.connect(lambda checked=False, name=value: self.select_character(name))
                row.addWidget(chip)
                self.character_buttons[value] = chip
            row.addStretch()
            self.characters.setWidget(chips)
            self.content.addWidget(self.characters)

        self.breadcrumb = QLabel(self.main)
        self.breadcrumb.setObjectName('editorBreadcrumb')
        self.content.addWidget(self.breadcrumb)
        self.heading = QLabel(self.main)
        self.heading.setObjectName('editorSectionTitle')
        self.heading.setWordWrap(True)
        self.content.addWidget(self.heading)
        self.list.currentItemChanged.connect(self._select_section)
        self.selector.currentIndexChanged.connect(self._select_group)
        self._select_group()

    def select_character(self, name):
        self.selector.setCurrentIndex(self.selector.findData(name))

    def _select_group(self):
        selected = self.selector.currentData()
        self.state['selection'] = selected
        for name, chip in self.character_buttons.items():
            chip.setChecked(name == selected)
        available = [s for s in self.category.sections
                     if self.category.selector_label != 'Character' or s.selection == selected]
        duplicates = Counter(s.name for s in available)
        remembered = self.state.setdefault('sections', {}).get(selected)
        chosen = next((s for s in available if (s.selection, s.name) == remembered), None)
        if chosen is None:
            chosen = next((s for s in available if s.selection == selected), available[0])
        self.list.blockSignals(True)
        self.list.clear()
        for section in available:
            text = section.name if duplicates[section.name] == 1 else section.selection + ' · ' + section.name
            item = QListWidgetItem(text, self.list)
            item.setData(Qt.ItemDataRole.UserRole, self.category.sections.index(section))
            item.setToolTip(section.selection + ' · ' + section.name)
            if section is chosen:
                self.list.setCurrentItem(item)
        self.list.blockSignals(False)
        self.active_section = chosen if selected else None
        self._update_heading()
        self.changed.emit()

    def _select_section(self, item, previous=None):
        if item is None:
            return
        self.active_section = self.category.sections[item.data(Qt.ItemDataRole.UserRole)]
        selected = self.active_section.selection
        self.state['selection'] = selected
        self.state.setdefault('sections', {})[selected] = (selected, self.active_section.name)
        self.selector.blockSignals(True)
        self.selector.setCurrentIndex(self.selector.findData(selected))
        self.selector.blockSignals(False)
        self._update_heading()
        self.changed.emit()

    def _update_heading(self):
        section = self.active_section
        self.heading.setText(section.name if section else 'Overview')
        trail = self.title
        if self.character_buttons:
            trail += ' / ' + self.selector.currentData()
        self.breadcrumb.setText(trail)

    def set_search_state(self, query, changed_only=False):
        self.heading.setText('Search results' if query else 'Pending changes' if changed_only
                             else self.active_section.name if self.active_section else 'Overview')
        self.list.setEnabled(not query and not changed_only)

    def includes(self, section, query='', changed_only=False):
        return bool(query or changed_only or self.active_section is None or section is self.active_section)
