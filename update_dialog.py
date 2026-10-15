"""Nonblocking update controls, shared by the light/dark application theme.

SPDX-License-Identifier: GPL-3.0-or-later
"""
import sys
from PySide6.QtCore import Qt,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QTextEdit,QCheckBox,QProgressBar
from updates import RELEASES


class UpdatesDialog(QDialog):
    def __init__(self,client,automatic,on_automatic,on_install,parent):
        super().__init__(parent);self.client=client
        self.setObjectName('updatesDialog');self.setWindowTitle('UniversalSaveEditor updates');self.resize(680,560)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        box=QVBoxLayout(self);box.setContentsMargins(24,24,24,24);box.setSpacing(14)
        title=QLabel('Keep your editor up to date');title.setObjectName('title');box.addWidget(title)
        current=QLabel('Installed version  '+client.current);current.setObjectName('muted');box.addWidget(current)
        self.status=QLabel();self.status.setTextFormat(Qt.TextFormat.PlainText);self.status.setWordWrap(True)
        self.status.setObjectName('updateStatus');box.addWidget(self.status)
        self.progress=QProgressBar();self.progress.setObjectName('updateProgress');box.addWidget(self.progress)
        self.notes=QTextEdit();self.notes.setReadOnly(True);self.notes.setObjectName('updateNotes');self.notes.setPlaceholderText('Release notes will appear here.');box.addWidget(self.notes,1)
        self.automatic=QCheckBox('Check for updates on startup');self.automatic.setObjectName('automaticUpdates')
        self.automatic.setChecked(automatic);self.automatic.toggled.connect(on_automatic);box.addWidget(self.automatic)
        privacy=QLabel('Update checks contact GitHub. Your saves stay on this device. Downloads and restarts always require your action.')
        privacy.setObjectName('muted');privacy.setWordWrap(True);box.addWidget(privacy)
        actions=QHBoxLayout();box.addLayout(actions)
        self.check=QPushButton('Check for updates');self.check.setObjectName('checkUpdates');self.check.clicked.connect(client.check);actions.addWidget(self.check)
        self.download=QPushButton('Download update');self.download.setObjectName('downloadUpdate');self.download.clicked.connect(client.download);actions.addWidget(self.download)
        self.install=QPushButton('Restart and update');self.install.setObjectName('installUpdate');self.install.clicked.connect(on_install);actions.addWidget(self.install)
        self.cancel=QPushButton('Cancel download');self.cancel.setObjectName('cancelUpdate');self.cancel.clicked.connect(client.cancel);actions.addWidget(self.cancel)
        links=QHBoxLayout();box.addLayout(links)
        release=QPushButton('Official releases');release.clicked.connect(lambda:QDesktopServices.openUrl(QUrl(client.release.page if client.release else RELEASES)));links.addWidget(release)
        self.folder=QPushButton('Open download folder');self.folder.clicked.connect(self.open_download);links.addWidget(self.folder)
        links.addStretch();close=QPushButton('Close');close.clicked.connect(self.close);links.addWidget(close)
        client.changed.connect(self.refresh);self.refresh()

    def open_download(self):
        if self.client.downloaded:QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.client.downloaded.parent)))

    def refresh(self):
        c=self.client;busy=c.state in ('checking','downloading')
        self.status.setText(c.message);self.check.setEnabled(not busy)
        self.download.setEnabled(c.state=='available');self.install.setVisible(bool(getattr(sys,'frozen',False) and sys.platform=='win32'))
        self.install.setEnabled(c.state=='ready');self.folder.setEnabled(c.state=='ready')
        self.cancel.setVisible(busy);self.cancel.setText('Cancel download' if c.state=='downloading' else 'Cancel check')
        self.progress.setVisible(busy or c.state=='ready')
        if c.state=='checking' or c.state=='downloading' and not c.received:self.progress.setRange(0,0)
        else:
            self.progress.setRange(0,1000);self.progress.setValue(1000 if c.state=='ready' else round(1000*c.received/max(1,c.expected)))
            self.progress.setFormat('Verified' if c.state=='ready' else f'{c.received/1048576:.1f} / {c.expected/1048576:.1f} MB · %p%')
        if c.release:self.notes.setPlainText(c.release.notes)

    def closeEvent(self,event):
        if self.client.busy:self.client.cancel()
        super().closeEvent(event)
