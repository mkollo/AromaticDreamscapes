from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainter, QFont, QPen
from PyQt5.QtCore import Qt
import numpy as np


class FlowDataView(QMainWindow):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Flow Signal Chart')
        self.setGeometry(100, 100, 800, 600)        
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
        self.flow_chart.axes(Qt.Horizontal)[0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart.axes(Qt.Vertical)[0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart_view = QChartView(self.flow_chart)
        self.flow_chart_view.setRenderHint(QPainter.Antialiasing)
        self.flow_chart.axes(Qt.Vertical)[0].setRange(-0.05, 0.2)
        self.flow_chart.axes(Qt.Horizontal)[0].setRange(0, 5)
        self.flow_chart_view.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout()
        layout.addWidget(self.flow_chart_view)

        main_frame = QFrame()
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.run_test_sequence)
        layout.addWidget(self.start_button)
        self.default_state()

    def run_test_sequence(self):
        trace = self.controller.play_valve_sequence([2, 4, 14], [0.4, 0.6, 0.5], "test")

    def default_state(self):
        trace = self.controller.play_valve_sequence()
        x_data = np.arange(trace.shape[1]) / self.controller.get_sampling_rate()
        y_data_back = trace[0, :]
        y_data_front = trace[1, :]
        points_back = [QPointF(x, y) for x, y in zip(x_data, y_data_back)]
        points_front = [QPointF(x, y) for x, y in zip(x_data, y_data_front)]
        self.flow_back_series.replace(points_back)
        self.flow_front_series.replace(points_front)

        self.min_value = np.min([self.min_value, np.min(trace) * 1.5])
        self.max_value = np.max([self.max_value, np.max(trace) * 1.25])
        self.flow_chart.axes(Qt.Vertical)[0].setRange(self.min_value, self.max_value)
