import time

from PyQt5.QtWidgets import QProgressBar, QLabel, QGroupBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import QObject, pyqtSignal


class SequenceMonitor(QGroupBox):

    def __init__(self):
        super().__init__("Current pulse")
        self.progress_bar = QProgressBar()        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("font-weight: bold;")
        self.layout = QGridLayout()
        self.layout.addWidget(self.progress_label, 0, 0, 1, 1)
        self.layout.addWidget(self.progress_bar, 0, 1, 1, 2)
        self.setLayout(self.layout)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
      

class SequenceProgressWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(100):
            time.sleep(0.05)
            self.progress.emit(i + 1)
        self.finished.emit()
