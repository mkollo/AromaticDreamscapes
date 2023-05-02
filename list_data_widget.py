import csv
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from base_list import BaseListWidget

def no_action(self):
    pass

class ListDataWidget(QWidget):
    def __init__(self, title, headers, select_callback=lambda row:no_action, double_select_callback=lambda row:no_action, drop_callback=lambda source_id, source_row, target_row:no_action, color_data=None, ignore_buttons=[], extra_buttons=[]):
        super().__init__()

        self.title = title
        self.headers = headers

        self.group_box = QGroupBox(title)

        self.base_list = BaseListWidget(
            headers=headers, select_callback=select_callback, double_select_callback=double_select_callback, drop_callback=drop_callback)

        button_layout = QHBoxLayout()
        buttons = [{'icon': 'plus', 'callback': self.add_data_row}, {'icon': 'minus', 'callback': self.remove_data_row}, {'icon': 'up', 'callback': self.base_list.move_selected_item_up}, {'icon': 'down', 'callback': self.base_list.move_selected_item_down}, {'icon': 'extra_placehoder'}, {'icon': 'stretch'}, {'icon': 'load', 'callback': self.load_data}, {'icon': 'save', 'callback': self.save_data}]
        self.add_buttons(button_layout, buttons, ignore_buttons, extra_buttons)

        group_box_layout = QVBoxLayout()
        group_box_layout.addLayout(button_layout)
        group_box_layout.addWidget(self.base_list)
        self.group_box.setLayout(group_box_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.group_box)
        self.setLayout(layout)

    def add_buttons(self, button_layout, buttons, ignore_buttons, extra_buttons):
        for b in buttons:
            if b['icon'] == 'stretch':
                button_layout.addStretch()
            elif b['icon'] == 'extra_placehoder':
                for eb in extra_buttons:
                    button = QPushButton(QIcon("icons/" + eb['icon'] + ".png"), "")
                    button.clicked.connect(eb['callback'])
                    button_layout.addWidget(button)
            elif b['icon'] not in ignore_buttons:
                button = QPushButton(QIcon("icons/" + b['icon'] + ".png"), "")
                button.clicked.connect(b['callback'])
                button_layout.addWidget(button)    

    def get_column(self, key):
        return self.base_list.data[key]
        
    def add_data_row(self):
        pass

    def remove_data_row(self):
        reply = QMessageBox.question(
            self, 'Remove row', 'Are you sure you want remove this row?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            print(self.base_list.selected_row)
            print(self.base_list.data)
            self.base_list.removeRow(self.base_list.selected_row)
            if self.base_list.data.shape[0]>1:
                self.base_list.data.drop(self.base_list.selected_row, inplace=True, axis=0)
            else:
                self.base_list.data = self.base_list.data.iloc[0:0]
            print(self.base_list.data)
            self.base_list.selected_row = None
            self.base_list.update()

            
    def load_data_from_file(self, file_path, prompt=True):
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            if prompt:
                reply = QMessageBox.question(self, 'Table overwrite', 'Are you sure you want overwrite the "' +
                                                self.title + '" table?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    return        
            self.base_list.setRowCount(0)
            self.selected_row = None
            self.data = None
            for row in reader:     
                row_values = list(row.values())
                for i, header in enumerate(self.headers):
                    if header.endswith('?') and row_values[i] == '':
                        row_values[i] = False    
                self.base_list.add_row(row_values)
            
    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load table", "", "TSV files (*.tsv);;All files (*.*)")
        if file_path:
            self.load_data_from_file(file_path)

    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save table", "", "TSV files (*.tsv);;All files (*.*)")
        if file_path:
            self.base_list.data.to_csv(file_path, sep='\t', index=False)

