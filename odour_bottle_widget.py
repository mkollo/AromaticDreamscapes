import csv
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd
from list_data_widget import ListDataWidget
from skimage.color import lab2rgb
from colormath.color_conversions import convert_color
import matplotlib.ticker as ticker


from odour_chemical_widget import OdourChemicalWidget

class OdourBottleWidget(ListDataWidget):
    def __init__(self, chemical_widget: OdourChemicalWidget):
        self.chemical_widget = chemical_widget                
        self.distance_file = "data/canberra_all.csv"
        self.map_file = "data/canberra_all_mds.csv"

        ignore_buttons = ["plus", "minus", "up", "down"]
        headers = ["Name", "Chemicals", "Ratios", "Min ppm", "Max ppm", "CV ppm", "Error?"]
        extra_buttons = [
            {'icon': 'distancematrix', 'callback': lambda: self.plot_distance_matrix(self.get_column("Name"))}, 
            {'icon': 'pointmap', 'callback': lambda: self.plot_point_map(self.get_column("Name"))},
            {'icon': 'optimumppm', 'callback': lambda: self.plot_ideal_ppm()},
            {'icon': 'minus', 'callback': lambda: self.empty_bottle()}
        ]

        super().__init__("Odour Bottles", 
        double_select_callback=lambda row: self.show_ratio_edit_dialog(row), 
        drop_callback=lambda source_id, source_row, target_row: self.drop_component(source_id, source_row, target_row),
        headers=headers, ignore_buttons=ignore_buttons,
        extra_buttons=extra_buttons)

        self.odour_bottles_file = "data/odour_bottles.tsv"
        self.load_data_from_file(self.odour_bottles_file, prompt=False)
        self.update_bottle_colors()     

    def get_color(self, name):
        if name == "AIR":
            return [0, 0, 0]
        else:
            row_index = self.base_list.data.loc[self.base_list.data['Name'] == name].index[0]
            return self.get_bottle_colors()[row_index]

    def update_bottle_colors(self):
        color_data = np.empty(self.base_list.data.shape, dtype=object)
        color_data[:] = ""
        color_data[:,0] = self.get_bottle_colors()
        self.base_list.set_color_data(color_data)

    def empty_bottle(self):
        row = self.base_list.selected_row
        if row!=None:
            self.base_list.data.iloc[row, 1] = ""
            self.update_equal_ratios(row)
            self.update_ppms(row)
            self.base_list.update_widget()        
            self.update_bottle_colors()

    def get_distance_matrix(self):
            chem_data = self.chemical_widget.base_list.data.iloc[1:, :]
            with open(self.distance_file, 'r') as f:
                reader = csv.reader(f)
                data_chemicals = np.array(list(reader), dtype=float)
            data = np.zeros((16, 16))
            for i in range(16):
                for j in range(16):                    
                    chemicals_i = self.get_chemicals(i)
                    chemicals_j = self.get_chemicals(j)
                    if chemicals_i!=['AIR'] and chemicals_j!=['AIR']:
                        data[i, j] = np.min([data_chemicals[chem_data.loc[:, "Code"] == chemical_i, chem_data.loc[:, "Code"] == chemical_j] for chemical_i in chemicals_i for chemical_j in chemicals_j])
            data = np.delete(data, np.where([chemicals == ['AIR'] for chemicals in [self.get_chemicals(i) for i in range(16)]])[0], axis=0)
            data = np.delete(data, np.where([chemicals == ['AIR'] for chemicals in [self.get_chemicals(i) for i in range(16)]])[0], axis=1)
            return data

    def plot_distance_matrix(self, labels):
            data = self.get_distance_matrix()
            labels = labels[[(chemicals != ['AIR']) and (chemicals != ['']) for chemicals in [self.get_chemicals(i) for i in range(len(labels))]]]
            fig, ax = plt.subplots(figsize=(6, 6))
            im = ax.imshow(data, cmap='bwr', interpolation='nearest',
                        vmin=np.min(data), vmax=np.max(data))
            ax.set_xticks(np.arange(len(labels)))
            ax.set_xticklabels(labels, rotation=90, fontsize=12)
            ax.set_yticks(np.arange(len(labels)))
            ax.set_yticklabels(labels, fontsize=12)
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

    def get_point_map(self, drop_oil=True):
        chem_data = self.chemical_widget.base_list.data.iloc[1:, :]
        with open(self.map_file, 'r') as f:
            reader = csv.reader(f)
            data_chemicals = np.array(list(reader), dtype=float)  
        data = np.zeros((16, 2))
        for i in range(16):
            chemicals_i = self.get_chemicals(i)
            if chemicals_i!=['AIR']:
                data[i, 0] = np.mean([np.mean(data_chemicals[chem_data.loc[:, "Code"] == chemical_i, 0]) for chemical_i in chemicals_i])
                data[i, 1] = np.mean([np.mean(data_chemicals[chem_data.loc[:, "Code"] == chemical_i, 1]) for chemical_i in chemicals_i])
        if drop_oil:
            data = np.delete(data, np.where([chemicals == ['AIR'] for chemicals in [self.get_chemicals(i) for i in range(16)]])[0], axis=0)
        return data

    def get_bottle_colors(self, drop_oil=False):        
        return self.generate_smooth_colors(self.get_point_map(drop_oil=drop_oil))

    def generate_smooth_colors(self, coords):
        def get_color_at_position(x, y):
            r = np.nan_to_num(self.start_color[0] + (self.end_color[0] - self.start_color[0]) * x)
            g = np.nan_to_num(self.start_color[1] + (self.end_color[1] - self.start_color[1]) * y * (1 - x))
            b = np.nan_to_num(self.start_color[2] + (self.end_color[2] - self.start_color[2]) * (1 - x) * (1 - y))
            return (r, g, b)
        x, y = coords[:, 0], coords[:, 1]
        x = (x - np.min(x)) / (np.max(x) - np.min(x))
        y = (y - np.min(y)) / (np.max(y) - np.min(y))
        self.start_color = (0.2, 0.6, 1)
        self.end_color = (1, 1, 0)
        rgb = [get_color_at_position(x[i], y[i]) for i in range(coords.shape[0])]

        hex_colors = ['#' + ''.join([format(int(c*255), '02x') for c in rgb[i]]) for i in range(coords.shape[0])]
        return hex_colors


    def plot_point_map(self, labels):
        data = self.get_point_map()
        labels = labels[[(chemicals != ['AIR']) and (chemicals != ['']) for chemicals in [self.get_chemicals(i) for i in range(len(labels))]]]
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.scatter(data[:, 0], data[:, 1], s=220, c=self.generate_smooth_colors(data), edgecolors='black', linewidths=0.5)
        for i, label in enumerate(labels):
            ax.annotate(label, (data[i, 0], data[i, 1]), fontsize=12, textcoords=("offset points"), xytext=(5, -15), ha='left')
        canvas = FigureCanvas(fig)
        dialog = QDialog()
        dialog.setWindowTitle("Chemical space map (Canberra MDS)")
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.resize(800, 800)
        dialog.exec_()

    def get_chemicals(self, row):
        return self.base_list.data.loc[row, "Chemicals"].split(", ")

    def get_chemical_data(self, row):
        chemicals = self.get_chemicals(row)
        return pd.concat(self.chemical_widget.get_chemical_data(chemicals), ignore_index=True)

    def update_equal_ratios(self, row):
        chemicals = self.get_chemicals(row)        
        if len(chemicals) == 1:
            self.base_list.data.loc[row, "Ratios"] = "1"
        else:
            self.base_list.data.loc[row, "Ratios"] = ", ".join(["{:.2g}".format(1.0/len(chemicals))] * len(chemicals))

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

    def get_ideal_ppm(self):
        steps = 200
        errors = np.zeros((self.base_list.data.shape[0], steps))
        ppms = np.linspace(0.1, 200, steps)        
        correct_rows = np.where([(chemicals != ['AIR']) and (chemicals != ['']) for chemicals in [self.get_chemicals(i) for i in range(self.base_list.data.shape[0])]])[0]
        for row in correct_rows:
            chemical_data = self.get_chemical_data(row)
            chemical_data["Max_ppm"] = chemical_data["Saturated_ppm"].astype(float) / 4
            chemical_data["Min_ppm"] = chemical_data["Saturated_ppm"].astype(float) / 40
            for si in range(steps):
                errors[row, si] = max(np.clip(np.max(chemical_data["Min_ppm"]/ppms[si]),1,np.inf), np.clip((ppms[si]/(np.min(chemical_data["Max_ppm"])+1e-6)),1,np.inf))
        errors_median = np.median(errors, axis=0)
        errors_min = np.min(errors, axis=0)
        
        errors_max = np.max(errors, axis=0)
        ideal_ppm = ppms[np.argmin(errors_max)]
        return ppms, errors_median, errors_min, errors_max, ideal_ppm

    def update_ppms(self, row):
        chemical_data = self.get_chemical_data(row)
        chemical_data["Max_ppm"] = chemical_data["Saturated_ppm"].astype(float) / 4
        chemical_data["Min_ppm"] = chemical_data["Saturated_ppm"].astype(float) / 40        
        self.base_list.data.loc[row, "Min ppm"] = "{:.2f}".format(np.nan_to_num(chemical_data["Min_ppm"].mean()))
        self.base_list.data.loc[row, "Max ppm"] = "{:.2f}".format(np.nan_to_num(chemical_data["Max_ppm"].mean()))
        self.base_list.data.loc[row, "CV ppm"] = "{:.0f} %".format(np.nan_to_num(chemical_data["Saturated_ppm"].astype(float).std()/chemical_data["Saturated_ppm"].astype(float).mean()*100))
        
    def add_chemical(self, row, chemical):
        chemicals = self.get_chemicals(row)
        if chemicals == ['']:
            self.base_list.data.loc[row, "Chemicals"] = chemical
        else:
            chemicals.append(chemical)
            self.base_list.data.loc[row, "Chemicals"] = ', '.join(chemicals)
        self.base_list.data = self.base_list.data.reset_index(drop=True)
        self.update_equal_ratios(row)
        self.update_ppms(row)
        self.base_list.update_widget()        
        self.update_bottle_colors()

    def drop_component(self, source_id, source_row, target_row):
        if source_id == id(self.chemical_widget):
            self.add_chemical(target_row, self.chemical_widget.base_list.data.iloc[source_row,:]["Code"])         
    
    def show_ratio_edit_dialog(self, row):
        pass