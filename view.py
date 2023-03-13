from PyQt5.QtWidgets import QMainWindow, QFrame, QGridLayout, QPushButton
from PyQt5.QtCore import  QThread, pyqtSignal
import numpy as np

from flow_chart import FlowChart
from odour_bottle_widget import OdourBottleWidget
from odour_chemical_widget import OdourChemicalWidget
from pid_chart import PidChart
from sequence_monitor import SequenceMonitor, SequenceProgressWorker
from play_valve_sequence_worker import PlayValveSequenceWorker

class FlowDataView(QMainWindow):

    sequence_complete = pyqtSignal(np.ndarray)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Aromatic Dreamscapes')
        self.setGeometry(100, 100, 800, 600)

        self.flow_chart = FlowChart(controller.get_sampling_rate())
        self.pid_chart = PidChart(controller.get_sampling_rate())
        self.sequence_monitor = SequenceMonitor()        
        self.start_button = QPushButton("Play next:  " + self.controller.get_current_sequence()['label'])
        self.start_button.clicked.connect(self.run_next_sequence)        
        self.sequence_complete.connect(self.flow_chart.update)
        self.sequence_complete.connect(self.pid_chart.update)
        self.sequence_monitor.layout.addWidget(self.start_button, 0, 3, 1, 2)
        self.odour_chemicals = OdourChemicalWidget()
        self.odour_bottles = OdourBottleWidget(self.odour_chemicals)
        main_frame = QFrame()
        layout = QGridLayout(main_frame)
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)
        layout.addWidget(self.flow_chart, 0, 0, 3, 1)
        layout.addWidget(self.pid_chart, 3, 0, 3, 1)
        layout.addWidget(self.sequence_monitor, 6, 0, 1, 1)
        layout.addWidget(self.odour_bottles, 0, 1, 3, 1)
        layout.addWidget(self.odour_chemicals, 0, 2, 3, 1)

        self.flow_chart.setMouseTracking(True)
        self.pid_chart.setMouseTracking(True)
        self.sequence_monitor.setMouseTracking(True)

        self.run_next_sequence()

    def run_next_sequence(self):
        self.run_sequence(self.controller.get_next_sequence())

    def run_sequence(self, params):
        odour_valves=params['valves']
        duty_cycles=params['duty_cycles']
        label=params['label']

        self.sequence_monitor.progress_label.setText(label)
        self.work_thread = QThread()
        self.progress_thread = QThread()
        self.worker = PlayValveSequenceWorker(self.controller, odour_valves, duty_cycles, label)
        self.progress_worker = SequenceProgressWorker()

        self.worker.moveToThread(self.work_thread)
        self.progress_worker.moveToThread(self.progress_thread)

        self.progress_worker.progress.connect(self.sequence_monitor.progress_bar.setValue)
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
        self.sequence_monitor.progress_bar.setValue(100)
        self.start_button.setEnabled(True)


