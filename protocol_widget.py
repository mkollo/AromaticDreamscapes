from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QSpinBox, QHBoxLayout
import numpy as np
import pandas as pd
from list_data_widget import ListDataWidget
from odour_bottle_widget import OdourBottleWidget
from sequence_widget import SequenceWidget
from random import shuffle

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
        
        components_layout = QHBoxLayout()

        # Create the repetitions spinbox
        self.repetitions_spinbox = QSpinBox()
        self.repetitions_spinbox.setRange(1, 1000)
        self.repetitions_spinbox.setValue(1)
        self.repetitions_spinbox.setToolTip("Number of repetitions")
        self.repetitions_spinbox.valueChanged.connect(self.update_repetitions)
        components_layout.addWidget(self.repetitions_spinbox)

        # Create the randomize button
        self.randomize_button = QPushButton("Randomize")
        self.randomize_button.setToolTip("Randomize")
        self.randomize_button.clicked.connect(self.randomize_data)
        components_layout.addWidget(self.randomize_button)

        # Create the run protocol button
        self.run_protocol_button = QPushButton(QIcon("icons/play.png"), "")
        self.run_protocol_button.setToolTip("Run protocol")
        self.run_protocol_button.clicked.connect(self.run_protocol)
        components_layout.addWidget(self.run_protocol_button)

        # Add the horizontal layout to the main layout
        self.group_box.layout().addLayout(components_layout)
        # button_layout.addWidget(button)
        # self.sequences_file = "data/protocol.tsv"
        # self.load_data_from_file(self.sequences_file, prompt=False)        
        self.base_list.resizeColumnsToContents()
        self.base_list.update_widget()
        self.update_sequence_colors()

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
        pass

    def drop_sequence(self, source_id, source_row, target_row):
        if source_id == id(self.sequence_widget):
            sequence_data = self.sequence_widget.base_list.data.iloc[source_row]
            self.base_list.data = self.base_list.data.append(sequence_data, ignore_index=True)
            self.update_sequence_colors()

