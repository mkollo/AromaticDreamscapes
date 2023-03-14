import csv
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd
from list_data_widget import ListDataWidget
from skimage.color import lab2rgb
from colormath.color_conversions import convert_color
from odour_bottle_widget import OdourBottleWidget
from odour_chemical_widget import OdourChemicalWidget
from sequence_widget import SequenceWidget

class ProtocolWidget(ListDataWidget):
    def __init__(self, sequence_widget:SequenceWidget, odour_bottle_widget: OdourBottleWidget, chemical_widget: OdourBottleWidget):
        self.sequence_widget = sequence_widget
        self.odour_bottle_widget = odour_bottle_widget
        self.chemical_widget = chemical_widget

        self.distance_file = "data/canberra_all.csv"
        self.map_file = "data/canberra_all_mds.csv"

        ignore_buttons = ["plus"]
        headers = ["Name", "O1", "O2", "O3", "O4", "Reward?", "On?"]
        extra_buttons = [           
        ]

        super().__init__("Protocols", 
        drop_callback=lambda source_id, source_row, target_row: self.drop_sequence(source_id, source_row, target_row),
        headers=headers, ignore_buttons=ignore_buttons,
        extra_buttons=extra_buttons)

        # self.sequences_file = "data/protocol.tsv"
        # self.load_data_from_file(self.sequences_file, prompt=False)        
        self.base_list.resizeColumnsToContents()
        self.base_list.update_widget()

    def drop_sequence(self, source_id, source_row, target_row):
        if source_id == id(self.sequence_widget):
            print(source_row)
       