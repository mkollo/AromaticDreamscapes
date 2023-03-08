import time
from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QPushButton, QProgressBar
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainter, QFont, QPen
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QTimer
import numpy as np


class FlowDataView(QMainWindow):

    sequence_complete = pyqtSignal(np.ndarray)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.min_value = -0.2
        self.max_value = 2
        self.flow_chart = QChart()
        self.flow_back_series = QLineSeries()
        self.flow_front_series = QLineSeries()
        zeroline = QLineSeries()
        zeroline.append(QPointF(0, 0))
        zeroline.append(QPointF(5, 0))
        zeroline.setPen(QPen(Qt.black))
        self.flow_back_series.setPen(QPen(Qt.blue))
        self.flow_front_series.setPen(QPen(Qt.red))
        self.flow_chart.addSeries(zeroline)
        self.flow_chart.addSeries(self.flow_back_series)
        self.flow_chart.addSeries(self.flow_front_series)
        self.flow_chart.createDefaultAxes()
        self.flow_chart.setTitle('Flow Signal')
        self.flow_chart.legend().hide()
        self.flow_chart.axes(Qt.Horizontal)[
            0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart.axes(Qt.Vertical)[0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart_view = QChartView(self.flow_chart)
        self.flow_chart_view.setRenderHint(QPainter.Antialiasing)
        self.flow_chart.axes(Qt.Vertical)[0].setRange(-0.05, 0.2)
        self.flow_chart.axes(Qt.Horizontal)[0].setRange(0, 5)
        self.flow_chart_view.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout()
        layout.addWidget(self.flow_chart_view)

        self.setWindowTitle('Flow Signal Chart')
        self.setGeometry(100, 100, 800, 600)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
       
        self.sequence_complete.connect(self.update_flow_chart)

        main_frame = QFrame()
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)

        self.start_button = QPushButton("Start")
        # self.start_button.clicked.connect(self.run_test_sequence)
        layout.addWidget(self.start_button)
        self.run_sequence([3, 4], [0.5, 0.5], "TEST")

    def run_sequence(self, odour_valves=[], duty_cycles=[], label="RESET"):
        self.work_thread = QThread()
        self.progress_thread = QThread()
        self.worker = PlayValveSequenceWorker(self.controller, odour_valves, duty_cycles, label)
        self.progress_worker = ProgressWorker()

        self.worker.moveToThread(self.work_thread)
        self.progress_worker.moveToThread(self.progress_thread)

        self.progress_worker.progress.connect(self.progress_bar.setValue)
        self.progress_worker.finished.connect(self.progress_thread.quit)

        self.worker.result.connect(self.sequence_complete.emit)
        self.work_thread.finished.connect(self.work_thread.deleteLater)
        self.start_button.setEnabled(False)
        self.work_thread.started.connect(self.worker.run)
        self.progress_thread.started.connect(self.progress_worker.run)
        self.progress_thread.finished.connect(self.update_finished_progress_bar)

        self.work_thread.start()
        self.progress_thread.start()

    def update_flow_chart(self, trace):
        x_data = np.arange(trace.shape[1]) / \
            self.controller.get_sampling_rate()
        y_data_back = trace[0, :]
        y_data_front = trace[1, :]
        points_back = [QPointF(x, y) for x, y in zip(x_data, y_data_back)]
        points_front = [QPointF(x, y) for x, y in zip(x_data, y_data_front)]
        self.flow_back_series.replace(points_back)
        self.flow_front_series.replace(points_front)
        self.min_value = np.min([self.min_value, np.min(trace) * 1.5])
        self.max_value = np.max([self.max_value, np.max(trace) * 1.25])
        self.flow_chart.axes(Qt.Vertical)[0].setRange(
            self.min_value, self.max_value)

    def update_finished_progress_bar(self):
        self.progress_bar.setValue(100)
        self.start_button.setEnabled(True)


class PlayValveSequenceWorker(QObject):
    result = pyqtSignal(np.ndarray)

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

class ProgressWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        print("starting progress worker")

    def run(self):
        for i in range(100):
            time.sleep(0.05)
            self.progress.emit(i + 1)
        self.finished.emit()
