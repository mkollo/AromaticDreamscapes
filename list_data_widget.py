import csv
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from base_list import BaseListWidget

class ListDataWidget(QWidget):
    def __init__(self, title, headers, select_callback):
        super().__init__()
        self.title = title
        self.group_box = QGroupBox(title)

        self.base_list = BaseListWidget(headers=headers, select_callback=select_callback)
        group_box_layout = QVBoxLayout()
        self.group_box.setLayout(group_box_layout)

        add_button = QPushButton(QIcon("icons/plus.png"), "")
        # add_button.clicked.connect(self.base_list.add_item)

        remove_button = QPushButton(QIcon("icons/minus.png"), "")
        # remove_button.clicked.connect(self.base_list.remove_selected_items)

        move_up_button = QPushButton(QIcon("icons/up.png"), "")
        move_up_button.clicked.connect(self.base_list.move_selected_item_up)

        move_down_button = QPushButton(QIcon("icons/down.png"), "")
        move_down_button.clicked.connect(self.base_list.move_selected_item_down)

        load_button = QPushButton(QIcon("icons/load.png"), "")
        load_button.clicked.connect(self.load_data)

        save_button = QPushButton(QIcon("icons/save.png"), "")
        save_button.clicked.connect(self.save_data)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(move_up_button)
        button_layout.addWidget(move_down_button)
        button_layout.addStretch()
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)

        group_box_layout.addLayout(button_layout)
        group_box_layout.addWidget(self.base_list)

        layout = QVBoxLayout()
        layout.addWidget(self.group_box)

        self.setLayout(layout)

    def add_data(self, data):
        self.base_list.add_data(data)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load table", "", "TSV files (*.tsv);;All files (*.*)")
        if file_path:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f, delimiter='\t')
                reply = QMessageBox.question(self, 'Table overwrite', 'Are you sure you want overwrite the "' + self.title + '" table?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.base_list.setRowCount(0)
                    self.selected_row = None
                    self.data = None
                    for row in reader:                        
                        self.base_list.add_row(row.values())
                    else:
                        pass

    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save table", "", "TSV files (*.tsv);;All files (*.*)")
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.base_list.headers, delimiter='\t')
                writer.writeheader()
                for d in self.base_list.data:
                    writer.writerow(d)
