import csv
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd
from list_data_widget import ListDataWidget
from skimage.color import lab2rgb
from colormath.color_conversions import convert_color
import matplotlib.ticker as ticker


from odour_bottle_widget import OdourBottleWidget

class SequenceWidget(ListDataWidget):
    def __init__(self, odour_bottle_widget: OdourBottleWidget, chemical_widget: OdourBottleWidget):
        self.odour_bottle_widget = odour_bottle_widget
        self.chemical_widget = chemical_widget
        self.distance_file = "resources/canberra_all.csv"
        self.map_file = "resources/canberra_all_mds.csv"

        ignore_buttons = ["plus", "minus", "up", "down"]
        headers = ["Name", "O1", "O2", "O3", "O4", "Reward?"]
        extra_buttons = [
            {'icon': 'optimumppm', 'callback': lambda: self.plot_ideal_ppm()}
        ]

        super().__init__("Sequences", 
        drop_callback=lambda source_id, source_row, target_row: self.drop_bottle(source_id, source_row, target_row),
        headers=headers, ignore_buttons=ignore_buttons,
        extra_buttons=extra_buttons)

        # self.sequences_file = "resources/sequences.tsv"
        # self.load_data_from_file(self.sequences_filesequences_file, prompt=False)
        self.base_list.resizeColumnsToContents()
        self.base_list.update_widget()
       
    def get_last_emtpy_slot(self, row):
        for i in range(1, 5):
            if self.base_list.data.iloc[row, i] == "":
                return i
        return -1

    def add_bottle(self, source_row, target_row):
        col = self.get_last_emtpy_slot(target_row)
        if col >= 0:
            self.base_list.data.loc[target_row, col] = self.odour_bottle_widget.base_list.data.loc[source_row, "Name"]
            self.base_list.update_widget()
        
    def add_sequence(self, source_row):
        dialog = NameInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            self.base_list.add_row([name, "", "", "", "", ""])
            self.add_bottle(source_row, self.base_list.data.shape[0] - 1)
    
    def drop_bottle(self, source_id, source_row, target_row):
        if source_id == id(self.odour_bottle_widget):
            if target_row < 0:
                self.add_sequence(source_row)
            else:
                self.add_bottle(source_row, target_row)
            # self.drop_bottle_from_bottle(source_row, target_row)


class NameInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New sequence")
        layout = QVBoxLayout(self)
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        button_box = QHBoxLayout()
        layout.addLayout(button_box)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(cancel_button)
    def get_name(self):
        return self.name_edit.text()