from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit
from list_data_widget import ListDataWidget

from odour_chemical_widget import OdourChemicalWidget

class OdourBottleWidget(ListDataWidget):
    def __init__(self):
        ignore_buttons = ["plus", "minus", "up", "down"]
        headers = ["Name", "Chemicals", "Ratios", "Min ppm", "Max ppm", "Error?"]
        super().__init__("Odour Bottles", double_select_callback=lambda row: self.show_odour_bottle_dialog(row), headers=headers, ignore_buttons=ignore_buttons)

        self.odour_bottles_file = "resources/odour_bottles.tsv"
        self.load_data_from_file(self.odour_bottles_file, prompt=False)

    def show_odour_bottle_dialog(self, row):
        dialog = QDialog()
        dialog.setWindowTitle("Odour Bottle Dialog")

        name_label = QLabel("Name:")
        name_edit = QLineEdit()
        min_vp_label = QLabel("Min VP:")
        min_vp_edit = QLineEdit()
        max_vp_label = QLabel("Max VP:")
        max_vp_edit = QLineEdit()

        component_list = ListDataWidget("Components", headers=["Name", "min VP (ppm)", "max VP (ppm)"], ignore_buttons=["save", "load"])
        chemical_list = OdourChemicalWidget()
        
        main_layout = QGridLayout()
        main_layout.addWidget(name_label, 0, 0, 1, 1)
        main_layout.addWidget(name_edit, 0, 1, 1, 1)
        main_layout.addWidget(min_vp_label, 0, 2, 1, 1)
        main_layout.addWidget(min_vp_edit, 0, 3, 1, 1)
        main_layout.addWidget(max_vp_label, 0, 4, 1, 1)
        main_layout.addWidget(max_vp_edit, 0, 5, 1, 1)
        main_layout.addLayout(component_list, 1, 0, 3, 3)
        main_layout.addLayout(chemical_list, 1, 3, 3, 3)
        
        dialog.setLayout(main_layout)