from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChartView, QLineSeries
from PyQt5.QtGui import QPainter, QFont, QPen
from PyQt5.QtCore import QPointF
import numpy as np


class FlowChart:

    def __init__(self, sampling_rate):
        self.chart = QChart()
        self.back_series = QLineSeries()
        self.front_series = QLineSeries()
        self.back_series.setName("Back")
        self.front_series.setName("Front")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.min_value = -0.2
        self.max_value = 2

        zeroline = QLineSeries()
        zeroline.append(QPointF(0, 0))
        zeroline.append(QPointF(5, 0))
        zeroline.setPen(QPen(Qt.black))

        self.back_series.setPen(QPen(Qt.blue))
        self.front_series.setPen(QPen(Qt.red))
        self.chart.addSeries(zeroline)
        self.chart.addSeries(self.back_series)
        self.chart.addSeries(self.front_series)
        self.chart.createDefaultAxes()
        self.chart.legend().show()
        self.chart.axes(Qt.Horizontal)[0].setLabelsFont(QFont("Arial", 14))
        self.chart.axes(Qt.Vertical)[0].setLabelsFont(QFont("Arial", 14))
        self.flow_chart_view = QChartView(self.chart)
        self.flow_chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart.axes(Qt.Vertical)[0].setRange(-0.05, 0.2)
        self.chart.axes(Qt.Horizontal)[0].setRange(0, 5)
        self.flow_chart_view.setContentsMargins(20, 20, 20, 20)

        self.chart.axes(Qt.Horizontal)[0].setTitleText("Time (s)")
        self.chart.axes(Qt.Vertical)[0].setTitleText("Flow (l/min)")
        self.sampling_rate = sampling_rate

    def update(self, trace):
        x_data = np.arange(trace.shape[1]) / self.sampling_rate
        y_data_back = trace[0, :]
        y_data_front = trace[1, :]
        points_back = [QPointF(x, y) for x, y in zip(x_data, y_data_back)]
        points_front = [QPointF(x, y) for x, y in zip(x_data, y_data_front)]
        self.back_series.replace(points_back)
        self.front_series.replace(points_front)
        self.min_value = np.min([self.min_value, np.min(trace) * 1.5])
        self.max_value = np.max([self.max_value, np.max(trace) * 1.25])
        self.chart.axes(Qt.Vertical)[0].setRange(self.min_value, self.max_value)

    def set_min_value(self, min_value):
        self.min_value = min_value

    def set_max_value(self, max_value):
        self.max_value = max_value
