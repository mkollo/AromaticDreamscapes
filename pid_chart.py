from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QPainter, QFont, QPen, QColor
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import numpy as np


class PidChart(QWidget):

    def __init__(self, sampling_rate):
        super().__init__()
        self.chart = QChart()
        self.pid_series = QLineSeries()
        self.pid_series.setName("MiniPID signal")
        self.chart.legend().setVisible(False)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.min_value = -0.2
        self.max_value = 2

        self.pid_series.setPen(QPen(QColor(255, 165, 0)))
        self.chart.addSeries(self.pid_series)
        self.chart.createDefaultAxes()
        self.chart.legend().show()
        self.chart.axes(Qt.Horizontal)[0].setLabelsFont(QFont("Arial", 10))
        self.chart.axes(Qt.Vertical)[0].setLabelsFont(QFont("Arial", 10))
        self.flow_chart_view = QChartView(self.chart)
        self.flow_chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart.axes(Qt.Vertical)[0].setRange(-0.05, 0.2)
        self.chart.axes(Qt.Horizontal)[0].setRange(0, 5)
        self.flow_chart_view.setContentsMargins(20, 20, 20, 20)

        self.chart.axes(Qt.Horizontal)[0].setTitleText("Time (s)")
        self.chart.axes(Qt.Vertical)[0].setTitleText("MiniPID value")
        self.sampling_rate = sampling_rate

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.flow_chart_view)
        self.setLayout(layout)

    def update(self, trace):
        x_data = np.arange(trace.shape[1]) / self.sampling_rate
        y_data_pid = trace[2, :]
        points_pid = [QPointF(x, y) for x, y in zip(x_data, y_data_pid)]
        self.pid_series.replace(points_pid)
        self.min_value = np.min([self.min_value, np.min(trace) * 1.5])
        self.max_value = np.max([self.max_value, np.max(trace) * 1.25])
        self.chart.axes(Qt.Vertical)[0].setRange(self.min_value, self.max_value)

    def set_min_value(self, min_value):
        self.min_value = min_value

    def set_max_value(self, max_value):
        self.max_value = max_value
