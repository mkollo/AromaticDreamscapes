from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton
from list_data_widget import ListDataWidget
from functools import partial

class OdourBottleWidget(ListDataWidget):
    def __init__(self, controller):
        ignore_buttons = ["plus", "minus", "up", "down"]
        headers = ["Name", "Chemicals", "Ratios", "Min ppm", "Max ppm", "Error"]
        super().__init__("Odour Bottles", double_select_callback=lambda row: self.show_odour_bottle_dialog(row), headers=headers, ignore_buttons=ignore_buttons)

        self.odour_bottles_file = "resources/odour_bottles.tsv"
        self.controller = controller
        self.load_data_from_file(self.odour_bottles_file, prompt=False)

    def show_odour_bottle_dialog(self, row):
            dialog = QDialog()
            dialog.setWindowTitle("Edit Odour Bottle")

            name_label = QLabel("Name:")
            name_edit = QLineEdit()
            min_vp_label = QLabel("Min VP:")
            min_vp_edit = QLineEdit()
            max_vp_label = QLabel("Max VP:")
            max_vp_edit = QLineEdit()

            left_layout = QVBoxLayout()
            left_label = QLabel("Chemicals:")
            left_table = QTableWidget()
            left_table.setColumnCount(1)
            left_table.setHorizontalHeaderLabels(["Chemical"])
            left_table.horizontalHeader().setStretchLastSection(True)
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda: self.remove_chemical(left_table))
            left_layout.addWidget(left_label)
            left_layout.addWidget(left_table)
            left_layout.addWidget(remove_button)

            right_layout = QVBoxLayout()
            right_label = QLabel("Odour Chemicals:")
            right_table = QTableWidget()
            right_table.setColumnCount(3)
            right_table.setHorizontalHeaderLabels(["Chemical", "VP (ppm)", "SD"])
            right_table.horizontalHeader().setStretchLastSection(True)
            right_layout.addWidget(right_label)
            right_layout.addWidget(right_table)

            main_layout = QVBoxLayout()
            top_layout = QHBoxLayout()
            top_layout.addWidget(name_label)
            top_layout.addWidget(name_edit)
            top_layout.addWidget(min_vp_label)
            top_layout.addWidget(min_vp_edit)
            top_layout.addWidget(max_vp_label)
            top_layout.addWidget(max_vp_edit)
            main_layout.addLayout(top_layout)
            main_layout.addLayout(left_layout)
            main_layout.addLayout(right_layout)
            dialog.setLayout(main_layout)

            result = dialog.exec_()
            if result == QDialog.Accepted:                
                pass

            def remove_chemical(self, table):
                row = table.currentRow()
                if row >= 0:
                    table.removeRow(row)