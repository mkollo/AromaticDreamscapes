from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QPoint, QMimeData
from PyQt5.QtGui import QColor, QPalette, QPainter, QBrush, QDrag
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem, QWidget, QStyledItemDelegate, QStyle, QStyleOptionButton, QApplication
import pandas as pd

selected_color = "#94FEDF"
hover_color = "#E4EFFF"
selected_hover_color = "#A4E8DF"

class BaseListWidget(QTableWidget):
    row_clicked = pyqtSignal(int)
    row_double_clicked = pyqtSignal(int)
    row_dropped = pyqtSignal(int, int, int)

    def __init__(self, headers, select_callback, double_select_callback, drop_callback, color_data=None, parent=None):
        super().__init__(parent)
        self.selected_row = None        
        self.headers = headers
        self.data = pd.DataFrame(columns=headers)
        self.color_data = color_data  # added to store the color data

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
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setDragEnabled(True)        
        self.setDragDropMode(QTableWidget.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDropIndicatorShown(True)

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
        delegate.hovered.connect(self._on_row_hovered)
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
        self.row_dropped.connect(lambda source_id, source_row, target_row: drop_callback(source_id, source_row, target_row))
        self.drag_start_pos = -1

    def set_color_data(self, color_data):
        self.color_data = color_data
        self.update_widget()

    def update_widget(self):
        self.setRowCount(0)       
        for i_row, row in self.data.iterrows():
            self.insertRow(i_row)
            for i_col, header in enumerate(self.headers):
                if header.endswith('?') and row.iloc[i_col] == '':
                    self.data.iloc[i_row, i_col] = False
                if self.headers[i_col].endswith("?"):
                    checkbox = QStyleOptionButton()
                    checkbox.rect = self.visualRect(self.model().index(i_row, i_col))
                    checkbox.state |= QStyle.State_Enabled
                    if self.data.iloc[i_row, i_col]=="True":
                        checkbox.state |= QStyle.State_On
                    else:
                        checkbox.state |= QStyle.State_Off
                else:
                    item = QTableWidgetItem(str(self.data.iloc[i_row, i_col]).replace("\n", ""))
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    if self.color_data is not None:
                        color = self.color_data[i_row, i_col]
                        if color != "":
                            item.setBackground(QColor(color))
                    self.setItem(i_row, i_col, item)            
            self.resizeColumnsToContents()
            
    def add_row(self, row_data):
        self.data.loc[len(self.data)] = row_data
        self.data.reset_index()
        i_row = self.rowCount()
        self.insertRow(i_row)
        for i_col, value in enumerate(row_data):
            if self.headers[i_col].endswith("?"):
                for row in range(self.rowCount()):
                    checkbox = QStyleOptionButton()
                    checkbox.rect = self.visualRect(self.model().index(row, i_col))
                    checkbox.state |= QStyle.State_Enabled
                    if self.data.iloc[row, i_col]=="True":
                        checkbox.state |= QStyle.State_On
                    else:
                        checkbox.state |= QStyle.State_Off
            else:
                item = QTableWidgetItem(str(value).replace("\n", ""))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if self.color_data is not None:
                    color = self.color_data[i_row, i_col]
                    if color != "":
                        item.setBackground(QColor(color))
                self.setItem(i_row, i_col, item)            
        self.resizeColumnsToContents()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())        
        for col in range(self.columnCount()):
            for row in range(self.rowCount()):
                index = self.model().index(row, col)
                if self.color_data is not None:                                        
                    color = self.color_data[row, col]
                    if color == "":
                        if self.hover_row == row:
                            color = hover_color if self.selected_row != row else selected_hover_color
                        elif self.selected_row == row:
                            color = selected_color
                        else:
                            color = "#FFFFFF"            
                    painter.setBrush(QBrush(QColor(color)))
                    painter.setPen(Qt.NoPen)
                    painter.drawRect(self.visualRect(index))
                    cell_rect = self.visualRect(index)
                if self.headers[col].endswith("?"):
                    checkbox = QStyleOptionButton()
                    checkbox.initFrom(self)
                    checkbox.rect = self.visualRect(self.model().index(row, col))
                    if self.data.iloc[row, col] == "True":
                        checkbox.state |= QStyle.State_On
                    else:
                        checkbox.state |= QStyle.State_Off
                    checkbox_rect = self.style().subElementRect(QStyle.SE_CheckBoxIndicator, checkbox)
                    checkbox_size = checkbox_rect.size()
                    cell_rect = self.visualRect(self.model().index(row, col))
                    cell_size = cell_rect.size()
                    x = cell_rect.left() + (cell_size.width() - checkbox_size.width()) / 2
                    y = cell_rect.top() + (cell_size.height() - checkbox_size.height()) / 2
                    checkbox_rect.moveTopLeft(QPoint(x, y))
                    checkbox.rect = checkbox_rect
                    self.style().drawControl(QStyle.CE_CheckBox, checkbox, painter, self)
                else:                   
                    painter.setPen(Qt.black)
                    painter.drawText(self.visualRect(index), Qt.AlignCenter, self.data.iloc[row, col])
              
                
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # Only start the drag if the mouse has moved at least 5 pixels
            if (event.pos() - self.drag_start_pos).manhattanLength() > 4:
                selected_row = self.currentRow()
                if selected_row != -1:
                    drag = QDrag(self)
                    mime_data = QMimeData()
                    mime_data.setData('application/x-myapp-source_row', selected_row.to_bytes(4, byteorder='little'))  # Set the source row number as integer data                   
                    mime_data.setData('application/x-myapp-source_id', id(self.parent().parent()).to_bytes(4, byteorder='little')) # Set the source row number as integer data
                    # mime_data.setData('application/x-myapp-parent-type', self.parent().parent().__class__.__name__.encode()) # Set the parent type as byte data
                    # mime_data.setData('application/x-myapp-dataframe', pickle.dumps(self.data))
                    drag.setMimeData(mime_data)
                    pixmap = self.grab(self.visualRect(self.model().index(selected_row+1, 0))) # Get the pixmap of the selected row
                    drag.setPixmap(pixmap)
                    drag.setHotSpot(event.pos() - self.visualRect(self.model().index(selected_row+1, 0)).topLeft()) # Set the hot spot to the mouse cursor position within the pixmap
                    drag.exec_()
        else:
            if self.rect().contains(event.pos()):
                self._on_row_hovered(self.rowAt(event.pos().y()))          
        super().mouseMoveEvent(event)

    def dropEvent(self, event):       
        if event.mimeData().hasFormat('application/x-myapp-source_row') and event.mimeData().hasFormat('application/x-myapp-source_id'):            
            source_id = int.from_bytes(event.mimeData().data('application/x-myapp-source_id'), byteorder='little')
            source_row = int.from_bytes(event.mimeData().data('application/x-myapp-source_row'), byteorder='little')
            target_row = self.rowAt(event.pos().y())
            # df_bytes = event.mimeData().data('application/x-myapp-dataframe')
            # dataframe = pickle.loads(df_bytes)
            self.row_dropped.emit(source_id, source_row, target_row)

    def select_row(self, row):
        self.selectRow(row)
        self.selected_row = row

    def remove_row_data(self, row):
        if row >= 0 and row < self.rowCount():
            self.removeRow(row)
            self.setRowCount(self.rowCount() - 1)
            if row == self.selected_row:
                self.selected_row = None
            self.data = self.data.drop(index=row)  # Remove the row from the dataframe
        self.resizeColumnsToContents()

    def get_row_data(self, row_index):
        row_data = self.data.iloc[row_index].tolist()  # Retrieve a row from the dataframe and convert to a list
        return row_data

    def mousePressEvent(self, event):        
        index = self.indexAt(event.pos())
        row = index.row() 
        col = index.column()
        if not index.isValid():
            super().mousePressEvent(event)
            return
        if self.headers[col].endswith("?"):
            if event.button() == Qt.LeftButton:                
                state =  self.data.loc[row, self.headers[col]] == "True"
                self.data.loc[row, self.headers[col]] = str(not state)
                self.viewport().update()
                return
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)
        
    def insert_row_data(self, row_index, row_data=None):
        self.insertRow(row_index)
        self.setRowCount(self.rowCount()+1)
        if row_data is not None:
            for col, value in enumerate(row_data):                
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.setItem(row_index, col, item)
            self.data = self.data.append(pd.Series(row_data, index=self.data.columns), ignore_index=True)  # Insert the row into the dataframe
        else:
            for col in range(self.columnCount()):            
                item = QTableWidgetItem("")
                item.setFlags(Qt.ItemIsEnabled | Qt.NoItemFlags)
                item.setBackground(QColor("#FFFFFF"))
                self.setItem(row_index, col, item)
                self.setCellWidget(row_index, col, self._get_widget())
            self.data = self.data.append(pd.Series([None] * len(self.data.columns), index=self.data.columns), ignore_index=True)  # Insert an empty row into the dataframe
        self.resizeColumnsToContents()

    def move_selected_item_up(self):
        if self.selected_row is not None:
            row = self.selected_row
            if row != 0:
                self.data.loc[row-1,:], self.data.loc[row,:] = self.data.loc[row,:].copy(), self.data.loc[row-1,:].copy()
                self.selected_row = row - 1
                self.update_widget()

    def move_selected_item_down(self):
        if self.selected_row is not None:
            row = self.selected_row
            if row != self.data.shape[0]-1:
                self.data.loc[row+1,:], self.data.loc[row,:] = self.data.loc[row,:].copy(), self.data.loc[row+1,:].copy()                
                self.selected_row = row + 1
                self.update_widget()

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
        
        self.hover_row = index
        self.viewport().update()  # Schedule a repaint of the viewport   

    def eventFilter(self, source, event):
        if source is self.viewport() and event.type() == QEvent.Paint:
            if self.mouse_pos:
                index = self.indexAt(self.mouse_pos)
                if index.isValid():
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
    hovered = pyqtSignal(int)

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

