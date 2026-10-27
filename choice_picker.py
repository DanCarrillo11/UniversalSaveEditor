"""Search long option lists without changing native choice indexes.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox,QDialog,QLabel,QLineEdit,QListWidget,
    QListWidgetItem,QPushButton,QVBoxLayout,QHBoxLayout)
from editor_search import matches_query


class ChoiceDialog(QDialog):
    def __init__(self, combo):
        super().__init__(combo)
        self.combo=combo
        self.choice=None
        self.setWindowTitle('Choose '+(combo.accessibleName() or 'an option'))
        self.resize(660,560)
        box=QVBoxLayout(self);box.setContentsMargins(24,24,24,24);box.setSpacing(12)
        title=QLabel(combo.accessibleName() or 'Choose an option',self)
        title.setTextFormat(Qt.TextFormat.PlainText);title.setWordWrap(True)
        title.setObjectName('editorSectionTitle');box.addWidget(title)
        self.search=QLineEdit(self);self.search.setObjectName('choiceSearch')
        self.search.setPlaceholderText('Type a name to filter options…');self.search.setClearButtonEnabled(True)
        self.search.setAccessibleName('Search available options');box.addWidget(self.search)
        self.count=QLabel(self);self.count.setObjectName('editorBreadcrumb');box.addWidget(self.count)
        self.results=QListWidget(self);self.results.setObjectName('choiceResults')
        self.results.setAccessibleName('Matching options');self.results.setWordWrap(True)
        box.addWidget(self.results,1)
        actions=QHBoxLayout();cancel=QPushButton('Cancel',self);cancel.clicked.connect(self.reject)
        actions.addWidget(cancel);actions.addStretch()
        self.select=QPushButton('Choose option',self);self.select.setObjectName('primary')
        self.select.setDefault(True);self.select.clicked.connect(self.accept_choice);actions.addWidget(self.select)
        box.addLayout(actions)
        self.search.textChanged.connect(self.filter_options)
        self.results.currentItemChanged.connect(self.update_selection)
        self.results.itemActivated.connect(self.accept_choice)
        self.filter_options();self.search.setFocus()

    def filter_options(self):
        self.results.clear()
        current=None;first=None
        for index in range(self.combo.count()):
            text=self.combo.itemText(index)
            if not matches_query(text,self.search.text(),aliases=False):continue
            item=QListWidgetItem(text,self.results)
            item.setData(Qt.ItemDataRole.UserRole,index)
            source=self.combo.model().index(index,self.combo.modelColumn(),self.combo.rootModelIndex())
            enabled=bool(self.combo.model().flags(source)&Qt.ItemFlag.ItemIsEnabled)
            if not enabled:
                item.setFlags(item.flags()&~(Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsSelectable))
                item.setToolTip('Unavailable for this save.')
            else:
                if first is None:first=item
                if index==self.combo.currentIndex():current=item
        if current is not None or first is not None:
            self.results.setCurrentItem(current if current is not None else first)
        self.count.setText(f'{self.results.count():,} matching options' if self.results.count() else 'No options match. Try a shorter name.')
        self.update_selection()

    def update_selection(self,*args):
        item=self.results.currentItem()
        self.select.setEnabled(bool(item and item.flags()&Qt.ItemFlag.ItemIsEnabled))

    def accept_choice(self,*args):
        item=self.results.currentItem()
        if item is None or not item.flags()&Qt.ItemFlag.ItemIsEnabled:return
        self.choice=item.data(Qt.ItemDataRole.UserRole)
        self.accept()


class SearchableComboBox(QComboBox):
    def showPopup(self):
        if self.count()<18:
            super().showPopup();return
        dialog=ChoiceDialog(self)
        try:
            if dialog.exec()==QDialog.DialogCode.Accepted and dialog.choice is not None:
                index=dialog.choice
                source=self.model().index(index,self.modelColumn(),self.rootModelIndex())
                if 0<=index<self.count() and self.model().flags(source)&Qt.ItemFlag.ItemIsEnabled:
                    self.setCurrentIndex(index)
        finally:
            self.hidePopup()
            dialog.deleteLater()
