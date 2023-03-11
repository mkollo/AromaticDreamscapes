from matplotlib.colors import LogNorm
from list_data_widget import ListDataWidget
import csv
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class OdourChemicalWidget(ListDataWidget):
    def __init__(self, controller):
        with open("resources/odour_chemicals.tsv", "r") as f:
            headers = f.readline().split("\t")
        ignore_buttons = ["plus", "minus", "up", "down", "load", "save"]
        extra_buttons = [{'icon': 'distancematrix', 'callback': lambda: self.plot_distance_matrix(
            "resources/canberra_all.csv", self.get_column(0))}, {'icon': 'pointmap', 'callback': lambda: plot_point_map("resources/canberra_all_mds.csv", self.get_column(0), self.get_column(1))}]
        super().__init__("Odour Chemicals", headers, ignore_buttons=ignore_buttons, extra_buttons=extra_buttons)
        self.odour_chemicals_file = "resources/odour_chemicals.tsv"
        self.controller = controller
        self.load_data_from_file(self.odour_chemicals_file, prompt=False)

    def plot_distance_matrix(self, csv_file_path, labels):
        with open(csv_file_path, 'r') as f:
            reader = csv.reader(f)
            data = np.array(list(reader), dtype=float)
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(data, cmap='bwr', interpolation='nearest',
                       vmin=np.min(data), vmax=np.max(data))
        ax.set_xticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=8)
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels, fontsize=8)
        cbar = ax.figure.colorbar(im, ax=ax)
        canvas = FigureCanvas(fig)
        dialog = QDialog()
        dialog.setWindowTitle("Chemical distance matrix (Canberra)")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.exec_()

def plot_point_map(csv_file_path, labels, sat_ppm):
    sat_ppm = np.array([float(s)+ 1e-9 for s in sat_ppm], dtype=float)
    
    with open(csv_file_path, 'r') as f:
        reader = csv.reader(f)
        data = np.array(list(reader), dtype=float)    
    labels = labels[1:]
    sat_ppm = sat_ppm[1:]
    fig, ax = plt.subplots(figsize=(6, 6))

    im = ax.scatter(data[:, 0], data[:, 1], s=40, c=sat_ppm, cmap='YlOrRd', norm=LogNorm(vmin=np.min(sat_ppm), vmax=np.max(sat_ppm)))

    for i, label in enumerate(labels):
        ax.annotate(label, (data[i, 0], data[i, 1]))

    cbar = fig.colorbar(im, ax=ax, orientation='horizontal', label='Saturated concentration (ppm)', pad=0.15)

    cbar.ax.set_xscale('log')

    canvas = FigureCanvas(fig)

    dialog = QDialog()
    dialog.setWindowTitle("Chemical space map (Canberra MDS)")

    layout = QVBoxLayout()
    layout.addWidget(canvas)
    dialog.setLayout(layout)

    dialog.exec_()
