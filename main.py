import sys
from PyQt5.QtWidgets import QApplication
from model import FlowDataModel
from controller import FlowDataController
from view import FlowDataView

app = QApplication(sys.argv)

model = FlowDataModel('AI', 'ai1')
controller = FlowDataController(model)
view = FlowDataView(controller)

view.show()

sys.exit(app.exec_())
