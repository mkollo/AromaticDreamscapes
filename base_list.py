from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QColor, QPalette, QPainter, QBrush
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget, QStyledItemDelegate, QStyle, QStyleOptionButton, QApplication

selected_color = "#D4FEDF"
hover_color = "#D4EEFF"
selected_hover_color = "#D4E8EF"

class BaseListWidget(QTableWidget):
    row_clicked = pyqtSignal(int)
    row_double_clicked = pyqtSignal(int)

    def __init__(self, headers, select_callback, double_select_callback, parent=None):
        super().__init__(parent)
        self.selected_row = None
        self.data = []
        self.headers = headers

        self.original_palette = QPalette()
        self.original_palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        self.original_palette.setColor(QPalette.Window, QColor("#C6D9F1"))
        self.original_palette.setColor(QPalette.Highlight, QColor(selected_color))
        self.original_palette.setColor(QPalette.HighlightedText, QColor("#000000"))
        self.setPalette(self.original_palette)

        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels([h.replace("\n", "") for h in headers])

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        self.setAlternatingRowColors(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setFocusPolicy(Qt.NoFocus)

        self.horizontalHeader().setMouseTracking(True)
        self.verticalHeader().setMouseTracking(True)
        self.setHorizontalHeader(NoHoverHeaderView(Qt.Horizontal, self))
        self.setVerticalHeader(NoHoverHeaderView(Qt.Vertical, self))
        delegate = RowHoverDelegate(self)
        self.setItemDelegate(delegate)

        self.setMouseTracking(True)

        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

        self.clicked.connect(self._on_row_clicked)
        self.doubleClicked.connect(self._on_row_double_clicked)

        title_row = TitleItem("")
        self.setItem(0, 0, title_row)
        for col in range(1, len(headers)):
            self.setItem(0, col, QTableWidgetItem(""))
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setUpdatesEnabled(True)

        self.hover_row = -1  # Added to track the currently hovered row
        self.mouse_pos = None  # Added to track the current mouse position

        self.row_clicked.connect(lambda row: select_callback(row))
        self.row_double_clicked.connect(lambda row: double_select_callback(row))

    def add_data(self, data):
        self.data = data
        for row in data:
            self.add_row(list(row.values()))
        self.resizeColumnsToContents()

    def add_row(self, row_data):
        i_row = self.rowCount()
        self.insertRow(i_row)
        for i_col, value in enumerate(row_data):
            item = QTableWidgetItem(str(value).replace("\n", ""))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.setItem(i_row, i_col, item)
        self.data.append(row_data)
        self.resizeColumnsToContents()

    def select_row(self, row):
        self.selectRow(row)
        self.selected_row = row

    def remove_row_data(self, row):
        if row >= 0 and row < self.rowCount():
            self.removeRow(row)
            self.setRowCount(self.rowCount() - 1)
            if row == self.selected_row:
                self.selected_row = None
        self.resizeColumnsToContents()

    def get_row_data(self, row_index):
        row_data = []
        for col in range(self.columnCount()):
            item = self.item(row_index, col)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append('')                
        return row_data

    def insert_row_data(self, row_index, row_data=None):
        self.insertRow(row_index)
        self.setRowCount(self.rowCount()+1)
        if row_data is not None:
            for col, value in enumerate(row_data):                
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.setItem(row_index, col, item)
        else:
            for col in range(self.columnCount()):            
                item = QTableWidgetItem("")
                item.setFlags(Qt.ItemIsEnabled | Qt.NoItemFlags)
                item.setBackground(QColor("#FFFFFF"))
                self.setItem(row_index, col, item)
                self.setCellWidget(row_index, col, self._get_widget())
        self.resizeColumnsToContents()

    def move_selected_item_up(self):
        if self.selected_row is not None:
            row = self.selected_row
            if row < 1:
                return
            new_row = row - 1
            self.insert_row_data(new_row, self.get_row_data(row))
            self.remove_row_data(row + 1)
            self.select_row(new_row)
            self.selected_row = new_row

    def move_selected_item_down(self):
        if self.selected_row is not None:
            row = self.selected_row
            if row >= self.rowCount() - 1:
                return
            new_row = row + 2
            self.insert_row_data(new_row, self.get_row_data(row))
            self.remove_row_data(row)
            self.select_row(new_row - 1)
            self.selected_row = new_row - 1

    def get_selected_row(self):
        return self.selected_row

    def _get_widget(self):
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), QColor("#FFFFFF"))
        widget.setPalette(palette)
        return widget

    def _on_row_clicked(self, index):
        self.selected_row = index.row()
        self.row_clicked.emit(index.row())

    def _on_row_double_clicked(self, index):
        self.selected_row = index.row()
        self.row_double_clicked.emit(index.row())

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()  # Update mouse position
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hover_row = -1  # Reset hover row when mouse leaves table
        super().leaveEvent(event)

    def _get_widget(self):
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(widget.backgroundRole(), QColor("#FFFFFF"))
        widget.setPalette(palette)
        return widget

    def _on_row_hovered(self, index):
        self.hover_row = index.row()
        self.viewport().update()  # Schedule a repaint of the viewport

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.hover_row >= 0:
            # Calculate the rect of the hovered row
            rect = self.visualRect(self.model().index(self.hover_row, 0))

            # Draw a blue background for the entire row
            painter = QPainter(self.viewport())
            if (self.hover_row == self.selected_row):
                painter.fillRect(rect, QColor(selected_hover_color))
            else:
                painter.fillRect(rect, QColor(hover_color))

           
             # Draw the text for each cell in the row
            for col in range(self.columnCount()):
                rect = self.visualRect(self.model().index(self.hover_row, col))
                text = self.model().data(self.model().index(self.hover_row, col))
                painter.drawText(rect.translated(3, 0), Qt.AlignVCenter | Qt.AlignLeft, text)

    def eventFilter(self, source, event):
        if source is self.viewport() and event.type() == QEvent.Paint:
            if self.mouse_pos:
                # Get the index of the cell under the mouse cursor
                index = self.indexAt(self.mouse_pos)

                if index.isValid():
                    # Emit a signal when the hovered row changes
                    row = index.row()
                    if row != self.hover_row:
                        self._on_row_hovered(index)

            # Reset mouse position
            self.mouse_pos = None

        return super().eventFilter(source, event)

class TitleItem(QTableWidgetItem):

    def __init__(self, text):
        super().__init__(text)
        self.setFlags(Qt.ItemIsEnabled | Qt.NoItemFlags)

class NoHoverHeaderView(QHeaderView):
    def event(self, event):
        if event.type() == QEvent.HoverMove:
            return False
        return super().event(event)

    def mousePressEvent(self, event):
        pass

class RowHoverDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if index.row() == self.parent().hover_row:
            if (index.row() == self.parent().selected_row):
                brush = QBrush(QColor(selected_hover_color))
            else:
                brush = QBrush(QColor(hover_color))
            painter.fillRect(option.rect, brush)
        else:
            super().paint(painter, option, index)

