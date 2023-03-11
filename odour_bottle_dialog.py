from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton

class OdourBottleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Odour Bottle Dialog")

        # Top input fields
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        min_vp_label = QLabel("Min VP:")
        self.min_vp_edit = QLineEdit()
        max_vp_label = QLabel("Max VP:")
        self.max_vp_edit = QLineEdit()

        # Left list widget
        left_layout = QVBoxLayout()
        left_label = QLabel("Chemicals:")
        self.left_table = QTableWidget()
        self.left_table.setColumnCount(1)
        self.left_table.setHorizontalHeaderLabels(["Chemical"])
        self.left_table.horizontalHeader().setStretchLastSection(True)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_chemical)
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.left_table)
        left_layout.addWidget(remove_button)

        # Right odour chemical widget
        right_layout = QVBoxLayout()
        right_label = QLabel("Odour Chemicals:")
        self.right_table = QTableWidget()
        self.right_table.setColumnCount(3)
        self.right_table.setHorizontalHeaderLabels(["Chemical", "VP (ppm)", "SD"])
        self.right_table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.right_table)

        # Main layout
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(name_label)
        top_layout.addWidget(self.name_edit)
        top_layout.addWidget(min_vp_label)
        top_layout.addWidget(self.min_vp_edit)
        top_layout.addWidget(max_vp_label)
        top_layout.addWidget(self.max_vp_edit)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def remove_chemical(self):
        row = self.left_table.currentRow()
        if row >= 0:
            self.left_table.removeRow(row)
