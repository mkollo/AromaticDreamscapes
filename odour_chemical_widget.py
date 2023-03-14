from matplotlib.colors import LogNorm
from list_data_widget import ListDataWidget
import csv
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class OdourChemicalWidget(ListDataWidget):
    def __init__(self):
        self.distance_file = "data/canberra_all.csv"
        self.map_file = "data/canberra_all_mds.csv"
        with open("data/odour_chemicals.tsv", "r") as f:
            headers = f.readline().split("\t")
        ignore_buttons = ["plus", "minus", "up", "down", "load", "save"]
        extra_buttons = [
            {'icon': 'distancematrix', 'callback': lambda: self.plot_distance_matrix(self.get_column("Name"))}, 
            {'icon': 'pointmap', 'callback': lambda: self.plot_point_map(self.get_column("Name"), self.get_column("Saturated_ppm"))}
            ]
        super().__init__("Odour Chemicals", headers, ignore_buttons=ignore_buttons, extra_buttons=extra_buttons)
        self.odour_chemicals_file = "data/odour_chemicals.tsv"
        self.load_data_from_file(self.odour_chemicals_file, prompt=False)
        color_data = np.empty(self.base_list.data.shape, dtype=object)
        color_data[:] = ""
        self.base_list.set_color_data(color_data)

    def get_chemical_data(self, codes):        
        return [self.base_list.data.loc[self.base_list.data['Code']==code,:] for code in codes]

    def plot_distance_matrix(self, labels):
        with open(self.distance_file, 'r') as f:
            reader = csv.reader(f)
            data = np.array(list(reader), dtype=float)
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(data, cmap='bwr', interpolation='nearest',
                       vmin=np.min(data), vmax=np.max(data))
        ax.set_xticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=6)
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels, fontsize=5)
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.set_label("Canberra distance", rotation=-90, va="bottom")
        canvas = FigureCanvas(fig)
        dialog = QDialog()
        dialog.setWindowTitle("Chemical distance matrix (Canberra)")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.resize(800, 800)
        dialog.exec_()

    def plot_point_map(self, labels, sat_ppm):
        sat_ppm = np.array([float(s)+ 1e-9 for s in sat_ppm], dtype=float)
        with open(self.map_file, 'r') as f:
            reader = csv.reader(f)
            data = np.array(list(reader), dtype=float)  
        labels = labels[1:]
        sat_ppm = sat_ppm[1:]
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.scatter(data[:, 0], data[:, 1], s=40, c=sat_ppm, cmap='YlOrRd', norm=LogNorm(vmin=np.min(sat_ppm), vmax=np.max(sat_ppm)))
        for i, label in enumerate(labels):
            ax.annotate(label, (data[i, 0], data[i, 1]), fontsize=5)
        cbar = fig.colorbar(im, ax=ax, orientation='horizontal', label='Saturated concentration (ppm)', pad=0.15)
        cbar.ax.set_xscale('log')
        cbar.set_label("Saturated concentration (ppm)", rotation=0, va="bottom")
        canvas = FigureCanvas(fig)
        dialog = QDialog()
        dialog.setWindowTitle("Chemical space map (Canberra MDS)")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.resize(800, 800)
        dialog.exec_()
