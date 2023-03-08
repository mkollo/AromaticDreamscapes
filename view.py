from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout, QPushButton
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QTimer, QPointF
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtCore import Qt
import numpy as np

class FlowDataView(QMainWindow):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Flow Signal Chart')
        self.setGeometry(100, 100, 800, 600)

        self.min_value = -0.15
        self.max_value = 0.5
        self.flow_chart = QChart()
        self.flow_series = QLineSeries()
        self.flow_chart.addSeries(self.flow_series)
        self.flow_chart.createDefaultAxes()
        self.flow_chart.setTitle('Flow Signal')
        self.flow_chart.legend().hide()
        self.flow_chart.axes(Qt.Horizontal)[0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart.axes(Qt.Vertical)[0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart_view = QChartView(self.flow_chart)
        self.flow_chart_view.setRenderHint(QPainter.Antialiasing)
        self.flow_chart.axes(Qt.Vertical)[0].setRange(-0.05, 0.2)
        self.flow_chart.axes(Qt.Horizontal)[0].setRange(0, 3)

        self.flow_chart_view.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout()
        layout.addWidget(self.flow_chart_view)

        main_frame = QFrame()
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_valve_states)
        layout.addWidget(self.start_button)
        self.start_valve_states()
        self.flow_series.clear()
        for i, value in enumerate(trace):
            self.flow_series.append(QPointF(i, value[0]))
        self.update_flow_chart()

    def start_valve_states(self):
        front_valve_states = [0] * 16
        back_valve_states = [1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
        trace = self.controller.set_valve_states(front_valve_states, back_valve_states)
        self.flow_series.clear()
        for i, value in enumerate(trace):
            self.flow_series.append(i, value)

        self.update_flow_chart()

    def update_flow_chart(self):
        flow_data = np.array([p.y() for p in self.flow_series.pointsVector()])
        self.min_value = np.min([self.min_value, np.min(flow_data * 1.5)])
        self.max_value = np.max([self.max_value, np.max(flow_data * 1.25)])

        # self.max_value = max(self.max_value, flow_data * 1.25)
        self.flow_chart.axes(Qt.Vertical)[0].setRange(self.min_value, self.max_value)
        self.flow_chart.setTitle(str(flow_data))