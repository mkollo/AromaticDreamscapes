from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit
from list_data_widget import ListDataWidget

from odour_chemical_widget import OdourChemicalWidget

class OdourBottleWidget(ListDataWidget):
    def __init__(self, chemical_widget: OdourChemicalWidget):
        self.chemical_widget = chemical_widget        
        ignore_buttons = ["plus", "minus", "up", "down"]
        headers = ["Name", "Chemicals", "Ratios", "Min ppm", "Max ppm", "Error?"]
        super().__init__("Odour Bottles", 
        double_select_callback=lambda row: self.show_ratio_edit_dialog(row), 
        drop_callback=lambda source_id, source_row, target_row: self.drop_component(source_id, source_row, target_row),
        headers=headers, ignore_buttons=ignore_buttons)

        self.odour_bottles_file = "resources/odour_bottles.tsv"
        self.load_data_from_file(self.odour_bottles_file, prompt=False)

    def get_chemicals(self, row):
        return self.base_list.data.iloc[row,:]["Chemicals"].split(", ")

    def update_equal_ratios(self, row):
        chemicals = self.get_chemicals(row)
        if len(chemicals) == 1:
            self.base_list.data.loc[row, "Ratios"] = "1"
        else:
            self.base_list.data.loc[row, "Ratios"] = ", ".join(["{:.2g}".format(1.0/len(chemicals))] * len(chemicals))

    def add_chemical(self, row, chemical):
        chemicals = self.get_chemicals(row)
        if chemicals == ['']:
            self.base_list.data.loc[row, "Chemicals"] = chemical
        else:
            chemicals.append(chemical)
            self.base_list.data.loc[row, "Chemicals"] = ', '.join(chemicals)
        self.base_list.data = self.base_list.data.reset_index(drop=True)
        self.update_equal_ratios(row)
        self.base_list.update_widget()

    def drop_component(self, source_id, source_row, target_row):
        if source_id == id(self.chemical_widget):
            self.add_chemical(target_row, self.chemical_widget.base_list.data.iloc[source_row,:]["Code"])         
    
    def show_ratio_edit_dialog(self, row):
        dialog = QDialog()
        dialog.setWindowTitle("Edit Ratios")
        layout = QGridLayout()
        chemicals = self.get_chemicals(row)
        ratios = self.base_list.data.iloc[row,:]["Ratios"].split(", ")
        for i in range(len(chemicals)):
            layout.addWidget(QLabel(chemicals[i]), i, 0)
            layout.addWidget(QLineEdit(ratios[i]), i, 1)
        dialog.setLayout(layout)
        dialog.exec_()