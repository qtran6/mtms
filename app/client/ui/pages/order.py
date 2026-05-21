from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
    QApplication,
    QHeaderView,
    QStyledItemDelegate
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Allow this page to receive focus when clicked so we can
        # move focus away from child input widgets with a single click.
        self.setFocusPolicy(Qt.ClickFocus)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(24, 24, 24, 24)
        self._grid.setHorizontalSpacing(24)
        self._grid.setVerticalSpacing(18)
        self._grid.setColumnStretch(0, 3)
        self._grid.setColumnStretch(1, 2)

        self._customer_name_box = self._customer_name_text_box()
        self._table = self._createTable()
        self._item_input_box = self._addItemUI()

        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)
        left_layout.addWidget(self._customer_name_box)
        left_layout.addWidget(self._table)
        left_layout.setStretch(0, 0)
        left_layout.setStretch(1, 1)

        self._grid.addWidget(left_column, 0, 0)
        self._grid.addWidget(self._item_input_box, 0, 1, 2, 1)


    def _customer_name_text_box(self) -> QHBoxLayout:
        customer_name_box = QFrame()
        customer_name_box.setObjectName("customer_name_box")
        customer_name_layout = QHBoxLayout(customer_name_box)
        customer_name_layout.setContentsMargins(20, 16, 20, 16)
        customer_name_layout.setSpacing(12)

        text = QLabel("Tên khách hàng:")
        self._customer_text_box = QLineEdit()
        self._customer_text_box.setPlaceholderText("Nhập tên khách hàng...")

        customer_name_layout.addWidget(text)
        customer_name_layout.addWidget(self._customer_text_box)
        
        return customer_name_box
    

    def _createTable(self) -> QWidget:
        table_box = QFrame()
        table_box.setObjectName("table_box")
        table_layout = QVBoxLayout(table_box)
        table_layout.setContentsMargins(12, 12, 12, 12)

        table = QTableView()

        # Create a simple standard model with 10 rows and 4 columns
        model = QStandardItemModel(10, 5)
        model.setHorizontalHeaderLabels(["TT", "Tên HH", "Số lượng", "Đơn giá", "Thành tiền"])

        table.setModel(model)
        table.setObjectName("table_view")

        # Set column widths and make Tên HH stretch
        h_header = table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # TT
        h_header.setSectionResizeMode(1, QHeaderView.Stretch)           # Tên HH - stretches
        h_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Số lượng
        h_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Đơn giá
        h_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Thành tiền

        # Set alignment for each column
        table.setItemDelegateForColumn(0, AlignDelegate("center")) # TT column centered
        table.setItemDelegateForColumn(1, AlignDelegate("left"))   # Tên HH column left-aligned
        table.setItemDelegateForColumn(2, AlignDelegate("center")) # Số lượng column centered
        table.setItemDelegateForColumn(3, AlignDelegate("right")) # Đơn giá column right-aligned
        table.setItemDelegateForColumn(4, AlignDelegate("right")) # Thành tiền column right-aligned

        # Hide vertical header and add TT column as order numbers
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(28)
        
        # Populate TT column with row numbers
        for row in range(10):
            item = QStandardItem(str(row + 1))
            model.setItem(row, 0, item)

        table_layout.addWidget(table)

        # Keep a reference to the view and model for theming or updates
        self._table_view = table
        self._table_model = model

        return table_box
    

    def _addItemToTable(self, item):
        ...


    def _addItemUI(self) -> QWidget:
        box = QFrame()
        box.setObjectName("item_box")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        brand_label = QLabel("Thương hiệu:")
        brand_input = QLineEdit()
        brand_input.setPlaceholderText("Nhập thương hiệu...")
        model_label = QLabel("Tên hàng hóa:")
        model_input = QLineEdit()
        model_input.setPlaceholderText("Nhập tên hàng hóa...")

        # layout.addWidget(brand_label)
        layout.addWidget(brand_input)
        # layout.addWidget(model_label)
        layout.addWidget(model_input)
        layout.addStretch(1)
        return box
    

    def mousePressEvent(self, event):
        # Clear focus from whichever widget currently has it when clicking
        # anywhere on this page (single click clears focus from inputs).
        focused = QApplication.focusWidget()
        if focused and focused is not self:
            try:
                focused.clearFocus()
            except Exception:
                pass
        # Give the page itself focus so no child remains focused.
        self.setFocus()
        super().mousePressEvent(event)


    def apply_theme(self, t: dict): 
        self.setStyleSheet(f"background: {t['background']};")

        # Apply styling to the customer name box
        self._customer_name_box.setStyleSheet(f"""
            QFrame#customer_name_box {{
                border: none;
                background: {t['background']};
            }}
        """)
        self._customer_text_box.setStyleSheet(f"""
            QLineEdit {{
                background: {t['background']};
                color: {t['text']};
                border: none;
                padding: 4px;
            }}
        """)
        # Apply styling to the item input box
        self._item_input_box.setStyleSheet(f"""
            QFrame#item_box {{
                border: none;
                background: {t['background']};
            }}
        """)
        # Apply styling to the table view (applies to the view and its header)
        if hasattr(self, '_table_view'):
            self._table_view.setStyleSheet(f"""
                QTableView {{
                    background: {t['background']};
                    color: {t['text']};
                    gridline-color: {t['border']};
                    border: none;
                }}
                QTableView QTableCornerButton:section {{
                    background: {t['background']};
                    color: {t['text']};
                    border: 1px solid {t['border']};
                }}
                QHeaderView::section {{
                    background: {t['background']};
                    color: {t['text']};
                    border: 1px solid {t['border']};
                }}
            """)


class AlignDelegate(QStyledItemDelegate):
    def __init__(self, alignment_name, parent=None):
        super().__init__(parent)
        alignment_map = {
            "left": Qt.AlignLeft | Qt.AlignVCenter,
            "center": Qt.AlignCenter,
            "right": Qt.AlignRight | Qt.AlignVCenter
        }
        self._alignment = alignment_map.get(alignment_name, Qt.AlignLeft | Qt.AlignVCenter)

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = self._alignment