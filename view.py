import time
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QPushButton, QProgressBar, QLabel, QGroupBox
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
import numpy as np

from flow_chart import FlowChart


class FlowDataView(QMainWindow):

    sequence_complete = pyqtSignal(np.ndarray)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.flow_chart = FlowChart(controller.get_sampling_rate())
        
        layout = QVBoxLayout()
        layout.addWidget(self.flow_chart.flow_chart_view)

        self.setWindowTitle('Odour Playlist Composer')
        self.setGeometry(100, 100, 800, 600)
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("")
        group_box = QGroupBox("Current pulse")
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.progress_label)
        group_box_layout.addWidget(self.progress_bar)
        group_box.setLayout(group_box_layout)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(group_box)
      
        self.sequence_complete.connect(self.flow_chart.update)
        main_frame = QFrame()
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)

        self.start_button = QPushButton("Play " + self.controller.get_current_sequence()['label'])
        self.start_button.clicked.connect(self.run_next_sequence)
        layout.addWidget(self.start_button)
        self.run_next_sequence()

    def run_next_sequence(self):
        self.run_sequence(self.controller.get_next_sequence())

    def run_sequence(self, params):
        odour_valves=params['valves']
        duty_cycles=params['duty_cycles']
        label=params['label']

        self.progress_label.setText(label)
        self.work_thread = QThread()
        self.progress_thread = QThread()
        self.worker = PlayValveSequenceWorker(self.controller, odour_valves, duty_cycles, label)
        self.progress_worker = ProgressWorker()

        self.worker.moveToThread(self.work_thread)
        self.progress_worker.moveToThread(self.progress_thread)

        self.progress_worker.progress.connect(self.progress_bar.setValue)
        self.progress_worker.finished.connect(self.progress_thread.quit)

        self.worker.result.connect(self.sequence_complete.emit)
        self.worker.finished.connect(self.work_thread.quit)
        self.start_button.setEnabled(False)
        self.work_thread.started.connect(self.worker.run)
        self.progress_thread.started.connect(self.progress_worker.run)
        self.progress_thread.finished.connect(self.update_finished_progress_bar)

        self.work_thread.start()
        self.progress_thread.start()

 
    def update_finished_progress_bar(self):
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)

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


class ProgressWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(100):
            time.sleep(0.05)
            self.progress.emit(i + 1)
        self.finished.emit()
