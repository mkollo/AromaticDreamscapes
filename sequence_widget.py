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
        self.distance_file = "data/canberra_all.csv"
        self.map_file = "data/canberra_all_mds.csv"

        ignore_buttons = ["plus"]
        headers = ["Name", "O1", "O2", "O3", "O4", "Reward?"]
        extra_buttons = [
            {'icon': 'optimumppm', 'callback': lambda: self.plot_ideal_ppm()}
        ]

        super().__init__("Sequences", 
        drop_callback=lambda source_id, source_row, target_row: self.drop_bottle(source_id, source_row, target_row),
        headers=headers, ignore_buttons=ignore_buttons,
        extra_buttons=extra_buttons)

        self.sequences_file = "Z:\\COMPUTING\\OdorSeqPython\\sequences.tsv"
        self.load_data_from_file(self.sequences_file, prompt=False)        
        self.base_list.resizeColumnsToContents()
        self.base_list.update_widget()
        self.update_sequence_colors()

    def get_sequence_bottles(self):
        sequence_bottles = []
        for seq_idx, seq_row in self.base_list.data.iterrows():
            for bottle_idx, bottle_row in self.odour_bottle_widget.base_list.data.iterrows():
                for bottle_num, bottle_name in enumerate(seq_row[1:5], 1):  # Start enumeration at 1
                    if bottle_row["Name"] == bottle_name:
                        row_with_seq_and_bottle_num = bottle_row.copy()
                        row_with_seq_and_bottle_num["Sequence"] = seq_idx + 1  # Add 1 to make it 1-based index
                        row_with_seq_and_bottle_num["Bottle"] = bottle_num
                        sequence_bottles.append(row_with_seq_and_bottle_num)
        return pd.DataFrame(sequence_bottles)

    def update_sequence_colors(self):
        color_data = np.empty(self.base_list.data.shape, dtype=object)
        color_data[:] = ""
        for i in range(self.base_list.data.shape[0]):
            for j in range(1, 5):
                name = self.base_list.data.iloc[i, j]
                if name != "":
                    color_data[i, j] = self.odour_bottle_widget.get_color(name)

        self.base_list.set_color_data(color_data)

    def load_data_from_file(self, file_path, prompt=True):
        return super().load_data_from_file(file_path, prompt)

    def get_last_emtpy_slot(self, row):
        for i in range(1, 5):
            if self.base_list.data.iloc[row, i] == "":
                return i
        return 0

    def add_bottle(self, source_row, target_row):
        col = self.get_last_emtpy_slot(target_row)
        if col >= 0:
            self.base_list.data.loc[target_row, self.headers[col]] = self.odour_bottle_widget.base_list.data.loc[source_row, "Name"]
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

    def get_chemical_data(self):
        sequence_bottles = self.get_sequence_bottles()
        nested_list = [chemical.split(",") for chemical in sequence_bottles["Chemicals"]]
        chemicals = [item.strip() for sublist in nested_list for item in sublist]
        return pd.concat(self.chemical_widget.get_chemical_data(chemicals), ignore_index=True)

    def get_ideal_ppm(self):
        steps = 500
        ppms = np.linspace(0.1, 200, steps)
        all_chemical_data = self.get_chemical_data()
        errors = np.zeros((all_chemical_data.shape[0], steps))
        for row in range(all_chemical_data.shape[0]):
            chemical_data = all_chemical_data.iloc[row,:]
            chemical_data["Max_ppm"] = float(chemical_data["Saturated_ppm"]) / 4
            chemical_data["Min_ppm"] = float(chemical_data["Saturated_ppm"]) / 40
            for si in range(steps):
                errors[row, si] = max(np.clip(np.max(chemical_data["Min_ppm"]/ppms[si]),1,np.inf), np.clip((ppms[si]/(np.min(chemical_data["Max_ppm"])+1e-6)),1,np.inf))
        errors_median = np.median(errors, axis=0)
        errors_min = np.min(errors, axis=0)        
        errors_max = np.max(errors, axis=0)
        ideal_ppm = ppms[np.argmin(errors_max)]
        return ppms, errors_median, errors_min, errors_max, ideal_ppm
        
    def plot_ideal_ppm(self):
        ppms, errors_median, errors_min, errors_max, ideal_ppm = self.get_ideal_ppm()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.fill_between(ppms, errors_min, errors_max, color="lightblue")
        ax.plot(ppms, errors_median, color="navy")
        ax.vlines(ideal_ppm, min(errors_min), max(errors_max), color="darkgrey", linestyle="dashed")       
        ax.text(ideal_ppm, ax.get_ylim()[1], f'{ideal_ppm:.2f} ppm', ha='center', va='bottom', color='darkgrey')
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
        ax.set_xlabel("Target concentration (ppm)")
        ax.set_ylabel("Error (actual / target concentration)")
        canvas = FigureCanvas(fig)
        dialog = QDialog()
        dialog.setWindowTitle("Closest match to ideal ppm (min/max/median)")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.resize(800, 800)
        dialog.exec_()        


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