from PyQt5.QtWidgets import QMainWindow, QFrame, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

class FlowDataView(QMainWindow):
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle('Flow Signal Chart')
        self.setGeometry(100, 100, 800, 600)

        self.flow_chart = QChart()
        self.flow_series = QLineSeries()
        self.flow_chart.addSeries(self.flow_series)
        self.flow_chart.createDefaultAxes()
        self.flow_chart.setTitle('Flow Signal')
        self.flow_chart.legend().hide()

        self.flow_chart_view = QChartView(self.flow_chart)
        self.flow_chart_view.setRenderHint(QPainter.Antialiasing)

        layout = QVBoxLayout()
        layout.addWidget(self.flow_chart_view)

        main_frame = QFrame()
        main_frame.setLayout(layout)
        self.setCentralWidget(main_frame)

        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_flow_chart)
        self.timer.start()

    def update_flow_chart(self):
        flow_data = self.controller.get_flow()
        self.flow_series.append(len(self.flow_series), flow_data)
        self.flow_chart.scroll(1, 0)
