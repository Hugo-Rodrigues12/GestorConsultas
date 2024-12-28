from database import *

LIGHT_THEME = """
    QMainWindow, QDialog {
        background-color: #F0F4F8;
    }
    QPushButton {
        background-color: #2B8A9C;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #1E6B7C;
    }
    QTableView {
        background-color: #FFFFFF;
        border: 1px solid #B5D6DC;
        gridline-color: #C5DEE4;
        border-radius: 8px;
        margin: 4px;
        selection-background-color: #E8F1F5;
        selection-color: #1B5566;
    }
    QTableView::item {
        border-bottom: 1px solid #D5E6EC;
        padding: 4px;
    }
    QHeaderView::section {
        background-color: #E8F1F5;
        color: #1B5566;
        padding: 8px;
        border: none;
        border-right: 1px solid #B5D6DC;
        border-bottom: 1px solid #B5D6DC;
        font-weight: bold;
        font-size: 13px;
    }
    QHeaderView {
        background-color: #E8F1F5;
        color: #1B5566;
    }
    QTableCornerButton::section {
        background-color: #E8F1F5;
        border: none;
    }
    QLineEdit, QDateEdit, QComboBox, QTimeEdit {
        padding: 8px;
        border: 2px solid #D5E6EC;
        border-radius: 6px;
        background-color: #FFFFFF;
        color: #1B5566;
        font-size: 13px;
    }
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTimeEdit:focus {
        border: 2px solid #2B8A9C;
    }
    QLabel {
        color: #1B5566;
        font-weight: 500;
        font-size: 13px;
    }
    QMenuBar {
        background-color: #F0F4F8;
        border-bottom: 1px solid #D5E6EC;
    }
    QMenuBar::item:selected {
        background-color: #E8F1F5;
        border-radius: 4px;
    }
    QMenu {
        background-color: #FFFFFF;
        color: #1B5566;
        border: 1px solid #D5E6EC;
        border-radius: 6px;
        padding: 5px;
    }
    QMenu::item:selected {
        background-color: #E8F1F5;
        border-radius: 4px;
    }
    QComboBox::drop-down, QDateEdit::drop-down, QTimeEdit::drop-down {
        border: none;
        padding-right: 8px;
    }
    QComboBox::down-arrow, QDateEdit::down-arrow, QTimeEdit::down-arrow {
        width: 12px;
        height: 12px;
        image: url(assets/arrow_down_light.png);
        margin-right: 8px;
    }
    QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        border: 2px solid #D5E6EC;
        border-radius: 6px;
        selection-background-color: #E8F1F5;
        selection-color: #1B5566;
        padding: 4px;
    }
    QTimeEdit::up-button, QTimeEdit::down-button {
        background: transparent;
        border: none;
    }
    QTimeEdit::up-arrow {
        width: 12px;
        height: 12px;
        image: url(assets/arrow_up_light.png);
        margin-right: 8px;
    }
"""

DARK_THEME = """
    QMainWindow, QDialog {
        background-color: #1A2027;
    }
    QPushButton {
        background-color: #2B8A9C;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #3AA8BD;
    }
    QTableView {
        background-color: #232B35;
        border: 1px solid #2B8A9C;
        gridline-color: #2F3A45;
        border-radius: 8px;
        margin: 4px;
        color: #E8F1F5;
        selection-background-color: #2B8A9C;
        selection-color: #FFFFFF;
    }
    QTableView::item {
        border-bottom: 1px solid #2F3A45;
        padding: 4px;
    }
    QHeaderView::section {
        background-color: #1E2630;
        color: #E8F1F5;
        padding: 8px;
        border: none;
        border-right: 1px solid #2F3A45;
        border-bottom: 1px solid #2F3A45;
        font-weight: bold;
        font-size: 13px;
    }
    QHeaderView {
        background-color: #1E2630;
        color: #E8F1F5;
    }
    QTableCornerButton::section {
        background-color: #1E2630;
        border: none;
    }
    QLineEdit, QDateEdit, QComboBox, QTimeEdit {
        padding: 8px;
        border: 2px solid #2F3A45;
        border-radius: 6px;
        background-color: #232B35;
        color: #E8F1F5;
        font-size: 13px;
    }
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QTimeEdit:focus {
        border: 2px solid #2B8A9C;
    }
    QLabel {
        color: #E8F1F5;
        font-weight: 500;
        font-size: 13px;
    }
    QMenuBar {
        background-color: #1A2027;
        border-bottom: 1px solid #2F3A45;
        color: #E8F1F5;
    }
    QMenuBar::item:selected {
        background-color: #232B35;
        border-radius: 4px;
    }
    QMenu {
        background-color: #1A2027;
        color: #E8F1F5;
        border: 1px solid #2F3A45;
        border-radius: 6px;
        padding: 5px;
    }
    QMenu::item:selected {
        background-color: #232B35;
        border-radius: 4px;
    }
    QComboBox::drop-down, QDateEdit::drop-down, QTimeEdit::drop-down {
        border: none;
        padding-right: 8px;
    }
    QComboBox::down-arrow, QDateEdit::down-arrow, QTimeEdit::down-arrow {
        width: 12px;
        height: 12px;
        image: url(assets/arrow_down_dark.png);
        margin-right: 8px;
    }
    QComboBox QAbstractItemView {
        background-color: #232B35;
        border: 2px solid #2F3A45;
        border-radius: 6px;
        selection-background-color: #2B8A9C;
        selection-color: #FFFFFF;
        color: #E8F1F5;
        padding: 4px;
    }
    QTimeEdit::up-button, QTimeEdit::down-button {
        background: transparent;
        border: none;
    }
    QTimeEdit::up-arrow {
        width: 12px;
        height: 12px;
        image: url(assets/arrow_up_dark.png);
        margin-right: 8px;
    }
"""

current_theme = LIGHT_THEME

# User
user_manager = UserManager('sistema_clinico.db')
consulta_manager = ConsultasManager()
medico_manager = MedicoManager()
cliente_manager = ClienteManager()