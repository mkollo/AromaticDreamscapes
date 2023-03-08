import sys
from PyQt5.QtWidgets import QApplication
from model import ValveModel
from controller import ValveController
from view import FlowDataView

app = QApplication(sys.argv)

model = ValveModel()
controller = ValveController(model)
view = FlowDataView(controller)

view.show()
 
sys.exit(app.exec_())
