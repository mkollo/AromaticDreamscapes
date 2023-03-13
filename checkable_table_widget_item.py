from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QCheckBox

class CheckableTableWidgetItem(QTableWidgetItem):
    stateChanged = pyqtSignal(int, int, bool)

    def __init__(self, checked=False):
        super().__init__()
        self.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
        self.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.stateChanged.connect(self._on_state_changed)

    def data(self, role):
        if role == Qt.CheckStateRole:
            return self.checkState()
        return super().data(role)

    def setData(self, role, value):
        if role == Qt.CheckStateRole and self.checkState() != value:
            self.stateChanged.emit(self.row(), self.column(), value == Qt.Checked)
        super().setData(role, value)

    def __lt__(self, other):
        return self.checkState() < other.checkState()

    def _on_state_changed(self, state):
        self.setCheckState(state)
