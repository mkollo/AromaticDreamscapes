from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np

class PlayValveSequenceWorker(QObject):
    result = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self, controller, odour_valves, duty_cycles, label):
        super().__init__()
        self.controller = controller
        self.odour_valves = odour_valves
        self.duty_cycles = duty_cycles
        self.label = label

    def run(self):
        trace = self.controller.play_valve_sequence(
            self.odour_valves, self.duty_cycles, self.label)
        self.result.emit(trace)
        self.finished.emit()