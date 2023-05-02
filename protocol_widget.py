from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from PyQt5.QtWidgets import QPushButton, QSpinBox, QHBoxLayout, QLineEdit
import numpy as np
import pandas as pd
from controller import OdourSeqController
from list_data_widget import ListDataWidget
from odour_bottle_widget import OdourBottleWidget
from sequence_widget import SequenceWidget
from random import shuffle

class ProtocolWidget(ListDataWidget):
    def __init__(self, sequence_widget:SequenceWidget, odour_bottle_widget: OdourBottleWidget, chemical_widget: OdourBottleWidget, controller=OdourSeqController):
        self.sequence_widget = sequence_widget
        self.odour_bottle_widget = odour_bottle_widget
        self.chemical_widget = chemical_widget
        self.controller = controller

        self.distance_file = "data/canberra_all.csv"
        self.map_file = "data/canberra_all_mds.csv"

        ignore_buttons = ["plus"]
        headers = ["Name", "O1", "O2", "O3", "O4", "Reward?", "Duty cycles"]
        extra_buttons = [           
        ]

        super().__init__("Protocols", 
        drop_callback=lambda source_id, source_row, target_row: self.drop_sequence(source_id, source_row, target_row),
        headers=headers, ignore_buttons=ignore_buttons,
        extra_buttons=extra_buttons)
        
        components_layout = QHBoxLayout()

        self.target_ppm_inputbox = QLineEdit()
        self.target_ppm_inputbox.setPlaceholderText("Target ppm")
        self.target_ppm_inputbox.setToolTip("Target ppm")
        self.target_ppm = 20.0
        self.target_ppm_inputbox.setText("{:.1f} ppm".format(self.target_ppm))
        self.target_ppm_inputbox.setFixedWidth(100)
        self.target_ppm_inputbox.textChanged.connect(self.update_target_ppm)
        components_layout.addWidget(self.target_ppm_inputbox)

        self.repetitions_spinbox = QSpinBox()
        self.repetitions_spinbox.setRange(1, 1000)
        self.repetitions_spinbox.setValue(1)
        self.repetitions_spinbox.setToolTip("Number of repetitions")
        self.repetitions_spinbox.valueChanged.connect(self.update_repetitions)
        components_layout.addWidget(self.repetitions_spinbox)

        self.randomize_button = QPushButton("Randomize")
        self.randomize_button.setToolTip("Randomize")
        self.randomize_button.clicked.connect(self.randomize_data)
        components_layout.addWidget(self.randomize_button)

        self.run_protocol_button = QPushButton(QIcon("icons/play.png"), "")
        self.run_protocol_button.setToolTip("Run protocol")
        self.run_protocol_button.clicked.connect(self.run_protocol)
        self.run_protocol_button.setStyleSheet("background-color: lightgrey")
        components_layout.addWidget(self.run_protocol_button)

        self.stop_protocol_button = QPushButton(QIcon("icons/stop.png"), "")
        self.stop_protocol_button.setToolTip("Stop protocol")
        self.stop_protocol_button.clicked.connect(self.stop_protocol)
        components_layout.addWidget(self.stop_protocol_button)

        # Add the horizontal layout to the main layout
        self.group_box.layout().addLayout(components_layout)
        # button_layout.addWidget(button)
        self.sequences_file = "Z:\\COMPUTING\\OdorSeqPython\\protocols.tsv"
        self.load_data_from_file(self.sequences_file, prompt=False)        
        self.base_list.resizeColumnsToContents()
        self.base_list.update_widget()
        self.update_sequence_colors()

    def update_target_ppm(self):
        self.target_ppm = float(self.target_ppm_inputbox.text().split(" ")[0])        

    def update_repetitions(self):
        repetitions = self.repetitions_spinbox.value()
        unique_data = self.base_list.data.drop_duplicates(ignore_index=True)
        repeated_data = pd.concat([unique_data] * repetitions, ignore_index=True)
        self.base_list.data = repeated_data
        self.update_sequence_colors()

    def clear_data(self):
        self.base_list.data = self.base_list.data.iloc[0:0]  # Clear the data while keeping the structure
        self.update_sequence_colors()

    def randomize_data(self):
        randomized_data = self.base_list.data.sample(frac=1).reset_index(drop=True)
        self.base_list.data = randomized_data
        self.update_sequence_colors()

    def update_sequence_colors(self):
        color_data = np.empty(self.base_list.data.shape, dtype=object)
        color_data[:] = ""
        for i in range(self.base_list.data.shape[0]):
            for j in range(1, 5):
                name = self.base_list.data.iloc[i, j]
                if name != "":
                    color_data[i, j] = self.odour_bottle_widget.get_color(name)

        self.base_list.set_color_data(color_data)

    def run_protocol(self):
        if (self.base_list.selected_row is None) or (self.base_list.selected_row < 0):
            self.base_list.select_row(0)
        self.run_sequence_thread = RunSequenceThread(self.controller, self.base_list.data, self.odour_bottle_widget.base_list.data)
        self.run_sequence_thread.update_row_signal.connect(self.base_list.select_row)
        self.run_sequence_thread.start()
        self.run_protocol_button.setStyleSheet("background-color: darkgreen")


    @pyqtSlot()
    def stop_protocol(self):
        self.run_sequence_thread.stop()
        self.run_sequence_thread.wait()
        self.run_protocol_button.setStyleSheet("background-color: grey")


    def drop_sequence(self, source_id, source_row, target_row):
        if source_id == id(self.sequence_widget):
            sequence_data = self.sequence_widget.base_list.data.iloc[source_row]            
            sequence_data["Duty cycles"] = self.get_duty_cycles(sequence_data[["O1", "O2", "O3", "O4"]].values)
            # self.base_list.data, sequence_data = self.base_list.data.align(sequence_data, axis=1)
            # self.base_list.data = pd.concat([self.base_list.data, sequence_data], ignore_index=True, axis=0)
            self.base_list.data = self.base_list.data.append(sequence_data, ignore_index=True)
            self.update_sequence_colors()

    def get_duty_cycles(self, bottles):        
        duty_cycles = []
        for bottle in bottles:
            bottle_row = self.odour_bottle_widget.base_list.data[self.odour_bottle_widget.base_list.data["Name"] == bottle].index[0]
            bottle_chemicals = self.odour_bottle_widget.get_chemicals(bottle_row)
            chemical_data = self.chemical_widget.get_chemical_data(bottle_chemicals)
            sat_ppms = np.array([float(d["Saturated_ppm"]) for d in chemical_data])
            duty_cycles.append(np.clip(self.target_ppm / np.mean(sat_ppms), 0.05, 1))
        return str(duty_cycles)
            

class RunSequenceThread(QThread):
    update_row_signal = pyqtSignal(int)

    def __init__(self, controller, base_list_data, bottle_data):
        super().__init__()
        self.controller = controller
        self.base_list_data = base_list_data
        self.bottle_data = bottle_data
        self.running = True

    def run(self):
        for index, row in self.base_list_data.iterrows():
            if not self.running:
                break            
            bottle_names = row[["O1", "O2", "O3", "O4"]].values
            odour_valves = [np.where(self.bottle_data["Name"] == bottle_name)[0][0]+1 for bottle_name in bottle_names]
            duty_cycles = row["Duty cycles"]
            duty_cycles = duty_cycles.replace("[", "").replace("]", "")
            duty_cycles = duty_cycles.split(", ")
            duty_cycles = [float(x) for x in duty_cycles]
            label = row["Name"]
            self.controller.play_valve_sequence(odour_valves, duty_cycles, label)                        
            self.update_row_signal.emit(index)
            self.sleep(20)

    def stop(self):
        self.running = False
