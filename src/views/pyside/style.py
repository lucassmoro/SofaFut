STYLE = """
QMainWindow, QWidget {
    background: #f7f4ef;
    color: #260d33;
}
QLabel[role="title"] {
    color: #003f69;
    font-size: 28px;
    font-weight: 800;
}
QLineEdit, QComboBox {
    background: #ffffff;
    border: 1px solid #b3aca4;
    border-radius: 6px;
    padding: 7px 10px;
    min-height: 22px;
}
QPushButton {
    background: #003f69;
    color: #ffffff;
    border: 0;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 700;
}
QPushButton:hover {
    background: #106b87;
}
QTableWidget, QTextEdit {
    background: #ffffff;
    border: 1px solid #d7d0c8;
    border-radius: 8px;
    gridline-color: transparent;
}
QTableWidget[role="data-table"] {
    alternate-background-color: #f7f1ea;
    selection-background-color: #cce5ee;
    selection-color: #123247;
}
QTableWidget[role="data-table"]::item {
    padding: 8px 10px;
    border-bottom: 1px solid #ece4dc;
}
QTableWidget[role="data-table"]::item:selected {
    background: #cce5ee;
    color: #123247;
}
QTableWidget[role="data-table"] QTableCornerButton::section {
    background: #003f69;
    border: 0;
}
QHeaderView::section {
    background: #003f69;
    color: #ffffff;
    padding: 9px 10px;
    border: 0;
    font-weight: 700;
    border-right: 1px solid #0f5672;
}
QScrollBar:vertical {
    background: #efe8df;
    width: 12px;
    margin: 4px 2px 4px 0;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #b8aa98;
    min-height: 28px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #9a8a78;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #efe8df;
    height: 12px;
    margin: 0 4px 2px 4px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #b8aa98;
    min-width: 28px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover {
    background: #9a8a78;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QTabBar::tab {
    background: #b3aca4;
    color: #260d33;
    padding: 9px 16px;
    font-weight: 700;
}
QTabBar::tab:selected {
    background: #003f69;
    color: #ffffff;
}
"""
