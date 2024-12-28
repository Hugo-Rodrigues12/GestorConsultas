from PySide6.QtWidgets import (
    QMainWindow, QDialog, QLabel, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QApplication, QTableView, QHeaderView, QMessageBox,
    QFormLayout, QHBoxLayout, QComboBox, QMenuBar, QDateEdit, QSizePolicy, QTimeEdit
)
from PySide6.QtCore import QDate, QTime, Qt
from PySide6.QtGui import QPixmap, QStandardItemModel, QStandardItem, QAction, QIcon
from root import user_manager, consulta_manager, medico_manager, cliente_manager, LIGHT_THEME, DARK_THEME, current_theme
import sys

class StartWindow(QMainWindow):
    """
    Main entry point window displaying logo and login button
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestor de Consultar V1')
    
        # Label to display the logo image
        self.image_label = QLabel()
        pixmap = QPixmap('assets/logo_medico.png')
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(480, 270)

        # Button to initiate the login process
        self.button = QPushButton('Iniciar Sessão')
        self.button.clicked.connect(self.on_button_click)
    
        # Vertical layout for the central widget
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.button)
    
        # Setting the central widget of the main window
        central_widget = QWidget()
        central_widget.setLayout(layout)
    
        self.setCentralWidget(central_widget)

    def on_button_click(self):
        # Open the login window when the button is clicked
        login = LoginWindow(self)
        login.exec()

class LoginWindow(QDialog):
    """
    Login dialog window for user authentication
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        screen = QApplication.primaryScreen().geometry()
        # Set the geometry of the login window to center it on the screen
        self.setGeometry((screen.width() - 400) // 2, (screen.height() - 200) // 2, 500, 200)
        layout = QVBoxLayout(self)

        # Create label and input for username or email
        self.user_label = QLabel('Username ou Email:')
        self.user_input = QLineEdit()

        # Create label and input for password
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # Set password input to hide characters

        # Create login button and connect it to the login function
        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(lambda: self.call_login(self.user_input.text(), self.password_input.text()))

        # Add widgets to the layout
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
    
    def call_login(self, username, password):
        global role
        # Authenticate the user with the provided username and password
        user = user_manager.authenticate(username, password)
        if user[0]:  # If authentication is successful
            role = user[1]  # Store the user's role
            self.consultas = ConsultasMainWindow(role)  # Create an instance of the main window
            self.consultas.show()  # Show the main window

            self.accept()  # Close the login dialog
            
            if self.parent():  # If there is a parent window, close it
                self.parent().close()
        else:
            # Show a warning message if authentication fails
            QMessageBox.warning(self, 'Falha no Login', 'Nome de utilizador ou palavra-passe inválidos. Por favor, tente novamente.')

class ConsultasMainWindow(QMainWindow):
    """
    Main application window displaying today's consultations and menu options
    """
    def __init__(self, role):
        super().__init__()
        self.setWindowTitle("Consultas do Dia")
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width() // 2, screen.height() // 2)

        # Store child windows as attributes
        self.past_consultas_window = None
        self.future_consultas_window = None
        self.users_window = None

        # Create menu bar and add menus
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)
        self.files_menu = menu_bar.addMenu("Ficheiros")
        self.consultas_menu = menu_bar.addMenu("Consultas")
        self.theme_menu = menu_bar.addMenu("Theme")

        # Theme actions
        switch_theme_action = QAction('Switch Theme', self)
        switch_theme_action.triggered.connect(lambda: self.toggle_theme())
    
        self.theme_menu.addAction(switch_theme_action)

        # Consultation actions
        consultas_passadas_action = QAction('Consultas Passadas', self)
        consultas_passadas_action.triggered.connect(lambda: self.call_past())
        consultas_futuras_action = QAction('Consultas Futuras', self)
        consultas_futuras_action.triggered.connect(lambda: self.call_future())
        users_action = QAction('Utilizadores', self)
        users_action.triggered.connect(lambda: self.call_users(role))
        medicos_action = QAction('Medicos', self)
        medicos_action.triggered.connect(lambda: self.call_medicos())
        clientes_action = QAction('Clientes', self)
        clientes_action.triggered.connect(lambda: self.call_clientes())
        about_action = QAction('Sobre', self)
        about_action.triggered.connect(lambda: self.call_about())
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(lambda: self.logout())

        self.consultas_menu.addAction(consultas_passadas_action)
        self.consultas_menu.addAction(consultas_futuras_action)
        self.files_menu.addAction(users_action)
        self.files_menu.addAction(medicos_action)
        self.files_menu.addAction(clientes_action)
        self.files_menu.addAction(about_action)
        self.files_menu.addAction(logout_action)

        # Initialize widgets for displaying consultations
        self.label = QLabel("Consultas Disponíveis:")
        self.consultas_table = QTableView()

        # Configure table properties
        self.consultas_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.consultas_table.setSelectionBehavior(QTableView.SelectRows)
        self.consultas_table.setSelectionMode(QTableView.SingleSelection)

        # Set up the model for the table
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', 'Nome Doente', 'Nome Medico', 'Data', 'Hora', 'Estado'])
        self.refresh_table()
        self.consultas_table.setModel(self.model)
        self.consultas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.consultas_table.setColumnHidden(0, True)  # Optionally hide the ID column

        # Initialize buttons for editing and canceling consultations
        self.edit_btn = QPushButton("Editar Consulta")
        self.edit_btn.clicked.connect(lambda: self.call_edit())
    
        self.cancel_btn = QPushButton("Cancelar Consulta")
        self.cancel_btn.clicked.connect(self.delete_selected_consulta)
    
        # Set up the layout for the main window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.consultas_table)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(button_layout)

        # Set central widget with the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def refresh_table(self):
        """
        Clears the current table and reloads all data from the database.
        """
        self.model.removeRows(0, self.model.rowCount())  # Clear the table

        results = consulta_manager.get_today_consultas()  # Fetch consultations for today
        for row in results:
            new_row = [
                QStandardItem(str(row['id'])),  # consulta_id
                QStandardItem(row['cliente_nome']),  # cliente_nome
                QStandardItem(row['medico_nome']),  # medico_nome
                QStandardItem(row['data']),  # data
                QStandardItem(row['hora']),  # hora
                QStandardItem(row['status'])  # status
            ]
            self.model.appendRow(new_row)  # Add the new row to the table

    def delete_selected_consulta(self):
        """
        Deletes the selected consultation after user confirmation.
        """
        selected_indexes = self.consultas_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione uma consulta para cancelar.")
            return

        selected_row = selected_indexes[0].row()
        consulta_id = self.model.data(self.model.index(selected_row, 0))  # Get ID from the selected row

        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirmação",
            f"Tens a certeza de que quer cancelar a consulta com ID {consulta_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            consulta_manager.del_consulta(consulta_id)  # Remove from the database
            self.model.removeRow(selected_row)  # Remove from the table model
            self.refresh_table()  # Refresh the table
            QMessageBox.information(self, "Sucesso", "Consulta cancelada com sucesso.")

    def call_edit(self):
        """
        Opens the edit dialog for the selected consultation.
        """
        selected_indexes = self.consultas_table.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Seleção inválida", "Por favor, selecione uma consulta para editar.")
            return

        selected_row = selected_indexes[0].row()
        consulta_id = int(self.consultas_table.model().item(selected_row, 0).text())  # Get consulta ID

        # Open the dialog in "edit" mode
        dialog = ConsultaEditar(mode='edit', consulta_id=consulta_id)
        dialog.set_data(consulta_id, *[
            self.consultas_table.model().item(selected_row, col).text() 
            for col in range(1, self.model.columnCount())
        ])  # Pass data from the selected row

        if dialog.exec() == QDialog.Accepted:  # Refresh the table if dialog is accepted
            self.refresh_table()

    def call_past(self):
        """
        Opens the window for past consultations.
        """
        if self.past_consultas_window is None or not self.past_consultas_window.isVisible():
            self.past_consultas_window = TodasConsultas(past=True)
            self.past_consultas_window.show()

    def call_future(self):
        """
        Opens the window for future consultations.
        """
        if self.future_consultas_window is None or not self.future_consultas_window.isVisible():
            self.future_consultas_window = TodasConsultas(past=False)
            self.future_consultas_window.show()

    def call_users(self, role):
        """
        Opens the user management window based on user role.
        """
        if role == 'padrao':
            QMessageBox.warning(self, 'Permissão insuficiente', 'Não tem permissão para ver os Utilizadores')
        else:
            users = TodosUsers()
            users.show()

    def call_medicos(self):
        """
        Opens the doctors management window.
        """
        medicos = TodosMedicos()
        medicos.show()

    def call_clientes(self):
        """
        Opens the clients management window.
        """
        clientes = TodosClientes()
        clientes.show()

    def call_about(self):
        about = About()
        about.exec()
    
    def toggle_theme(self):
        """
        Changes the application theme between light and dark modes.
        """
        global current_theme
        current_theme = LIGHT_THEME if current_theme == DARK_THEME else DARK_THEME
        QApplication.instance().setStyleSheet(current_theme)
        self.update()  # Forces a visual refresh

    def logout(self):
        """
        Handles the logout action, returning to the StartWindow.
        """
        global role
        confirm = QMessageBox.question(
            self,
            "Confirmação de Logout",
            "Tem certeza de que deseja sair?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            role = None  # Clear the role variable
            self.close()  # Close the current window
            self.start_window = StartWindow()  # Reopen the start window
            self.start_window.show()

class ConsultaEditar(QDialog):
    """
    Dialog for adding or editing consultation details
    """
    def __init__(self, mode='add', consulta_id=None):
        super().__init__()
        self.setWindowTitle("Detalhes da Consulta")
        self.setFixedSize(400, 300)

        self.mode = mode
        self.consulta_id = consulta_id if mode == 'edit' else None

        # Create layout for input fields
        self.form_layout = QFormLayout()

        # Initialize fields for client, doctor, date, time, and status
        self.nome_cliente_field = QComboBox()  # ComboBox for selecting the client
        self.nome_medico_field = QComboBox()  # ComboBox for selecting the doctor
        self.data_field = QDateEdit()  # Date selection field
        self.data_field.setCalendarPopup(True)
        self.hora_field = QTimeEdit()  # Time selection field
        self.status_field = QComboBox()
        self.status_field.addItems(["agendada", "concluida"])

        # Add fields to the form layout
        self.form_layout.addRow("Nome do Cliente:", self.nome_cliente_field)
        self.form_layout.addRow("Nome do Médico:", self.nome_medico_field)
        self.form_layout.addRow("Data:", self.data_field)
        self.form_layout.addRow("Hora:", self.hora_field)
        self.form_layout.addRow("Status:", self.status_field)

        # Create layout for buttons
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)  # Close dialog without saving
        self.save_button.clicked.connect(self.save_consulta)  # Save consultation and close dialog

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.form_layout)
        self.layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

        # Populate the combo boxes for client and doctor
        self.populate_cliente_combo()
        self.populate_medico_combo()

    def load_consulta_data(self, consulta_id):
        """
        Load data for an existing consultation when editing.
        """
        consulta = consulta_manager.get_consulta(consulta_id)  # Retrieve existing consultation data
        
        if consulta:
            cliente_id = consulta[1]  # Extract client ID
            medico_id = consulta[2]  # Extract doctor ID
            data = consulta[3]  # Extract date
            hora = consulta[4]  # Extract time
            status = consulta[5]  # Extract status

            # Set data in the form fields
            self.data_field.setText(data)
            self.hora_field.setText(hora)
            self.status_field.setCurrentText(status)

            # Populate combo boxes with the client and doctor
            self.populate_cliente_combo(cliente_nome=cliente_id)
            self.populate_medico_combo(medico_nome=medico_id)

    def save_consulta(self):
        """
        Handles saving the new consultation to the database.
        Based on the mode, it either adds or updates the consultation.
        """
        data = self.get_data()  # Get the data from the form

        # Validate required fields
        if not data["cliente_id"] or not data["medico_id"] or not data["data"] or not data["hora"] or not data["status"]:
            QMessageBox.warning(self, "Campos obrigatórios", "Por favor, preencha todos os campos obrigatórios.")
            return
        
        try:
            if self.mode == 'add':  # Adding a new consultation
                consulta_manager.add_consulta(
                    data["cliente_id"], 
                    data["medico_id"], 
                    data["data"], 
                    data["hora"], 
                    data["status"]
                )
                QMessageBox.information(self, "Consulta Adicionada", "A consulta foi adicionada com sucesso!")
            elif self.mode == 'edit':  # Editing an existing consultation
                consulta_manager.update_consulta(
                    self.consulta_id, 
                    data["cliente_id"], 
                    data["medico_id"], 
                    data["data"], 
                    data["hora"], 
                    data["status"]
                )
                QMessageBox.information(self, "Consulta Atualizada", "A consulta foi atualizada com sucesso!")
            self.accept()  # Close the dialog
        
        except ValueError as e:
            QMessageBox.warning(self, "Erro", f"Erro ao adicionar/atualizar consulta: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Ocorreu um erro: {e}")

    def populate_cliente_combo(self, selected_cliente_nome=None):
        """
        Populates the client combo box with names and ids.
        Optionally selects the given client name.
        """
        clientes = cliente_manager.get_all_clients()  # Retrieve all clients
        self.nome_cliente_field.clear()  # Clear previous items
        for cliente in clientes:
            self.nome_cliente_field.addItem(cliente['nome'], cliente['id'])  # Add client name and ID
        if selected_cliente_nome:
            # If a name is passed, select the corresponding item
            index = self.nome_cliente_field.findText(selected_cliente_nome)
            if index != -1:
                self.nome_cliente_field.setCurrentIndex(index)

    def populate_medico_combo(self, selected_medico_nome=None):
        """
        Populates the doctor combo box with names and ids.
        Optionally selects the given doctor name.
        """
        medicos = medico_manager.get_all_medicos()  # Retrieve all doctors
        self.nome_medico_field.clear()  # Clear previous items
        for medico in medicos:
            self.nome_medico_field.addItem(medico['nome'], medico['id'])  # Add doctor name and ID
        if selected_medico_nome:
            # If a name is passed, select the corresponding item
            index = self.nome_medico_field.findText(selected_medico_nome)
            if index != -1:
                self.nome_medico_field.setCurrentIndex(index)

    def set_data(self, consulta_id, cliente_id, medico_id, data, hora, status):
        """
        Sets the data for the consultation fields.
        """
        self.consulta_id = consulta_id
        self.data_field.setDate(QDate.fromString(data, 'yyyy-MM-dd'))  # Set date from string
        self.hora_field.setTime(QTime.fromString(hora, 'HH:mm'))  # Set time from string
        self.status_field.setCurrentText(status)

        self.populate_cliente_combo(selected_cliente_nome=cliente_id)  # Populate client combo
        self.populate_medico_combo(selected_medico_nome=medico_id)  # Populate doctor combo

    def get_data(self):
        """
        Returns the data from the form, including the selected IDs.
        """
        return {
            "consulta_id": self.consulta_id,
            "cliente_id": self.nome_cliente_field.currentData(),  # Get client ID (stored data)
            "medico_id": self.nome_medico_field.currentData(),  # Get doctor ID (stored data)
            "data": self.data_field.date().toString('yyyy-MM-dd'),  # Get formatted date
            "hora": self.hora_field.time().toString('HH:mm'),  # Get formatted time
            "status": self.status_field.currentText()
        }

class TodasConsultas(QMainWindow):
    """
    Window displaying all past or future consultations
    """
    def __init__(self, past):
        super().__init__()
        if past:
            self.setWindowTitle('Consultas Passadas')
        else:
            self.setWindowTitle("Consultas Futuras")
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width() // 2, screen.height() // 2)

        # Initialize the table for displaying consultations
        self.consultas_table = QTableView()

        # Allow the table to expand dynamically
        self.consultas_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set selection behavior for the table
        self.consultas_table.setSelectionBehavior(QTableView.SelectRows)
        self.consultas_table.setSelectionMode(QTableView.SingleSelection)

        # Set up the model for the table with headers
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', 'Nome Doente', 'Nome Medico', 'Data', 'Hora', 'Estado'])
        self.refresh_table(past)
        self.consultas_table.setModel(self.model)
        self.consultas_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.consultas_table.setColumnHidden(0, True)

        # Set text color to red if past consultations
        if past:
            self.consultas_table.setStyleSheet("QTableView { color: red; }")

        # Initialize layout for the main window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.consultas_table)

        # Add buttons for future consultations
        if not past:
            button_layout = QHBoxLayout()  # Create a horizontal layout for buttons

            self.add_btn = QPushButton('Marcar Consulta')
            self.add_btn.clicked.connect(lambda: self.call_add(past))
            button_layout.addWidget(self.add_btn)

            self.edit_btn = QPushButton("Editar Consulta")
            self.edit_btn.clicked.connect(lambda: self.call_edit(past))
            button_layout.addWidget(self.edit_btn)
        
            self.cancel_btn = QPushButton("Cancelar Consulta")
            self.cancel_btn.clicked.connect(self.delete_selected_consulta)
            button_layout.addWidget(self.cancel_btn)

            self.layout.addLayout(button_layout)  # Add the button layout to the main layout

        # Set the central widget with the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def delete_selected_consulta(self):
        # Check if a row is selected
        selected_indexes = self.consultas_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Invalid Selection", "Please select a consultation to cancel.")
            return

        # Get the consultation ID from the selected row
        selected_row = selected_indexes[0].row()
        consulta_id = self.model.data(self.model.index(selected_row, 0))  # ID is in column 0

        # Ask for confirmation before deletion
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to cancel the consultation with ID {consulta_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Remove from the database
            consulta_manager.del_consulta(consulta_id)

            # Remove from the table model
            self.model.removeRow(selected_row)

            QMessageBox.information(self, "Success", "Consultation canceled successfully.")

    def call_add(self, past):
        # Open the dialog to add a new consultation
        add_consulta = ConsultaEditar(mode='add')
        if add_consulta.exec() == QDialog.Accepted:
            self.refresh_table(past)

    def call_edit(self, past):
        selected_indexes = self.consultas_table.selectionModel().selectedRows()

        # Check if a row is selected
        if not selected_indexes:
            QMessageBox.warning(self, "Seleção inválida", "Por favor, selecione uma consulta para editar.")
            return

        # Get the selected row
        selected_row = selected_indexes[0].row()
        consulta_id = int(self.consultas_table.model().item(selected_row, 0).text())  # Get consulta ID from the table

        # Open the dialog in "edit" mode, passing the selected consulta_id
        dialog = ConsultaEditar(mode='edit', consulta_id=consulta_id)
        
        # Pass the data to the dialog from the selected row
        dialog.set_data(consulta_id, *[
            self.consultas_table.model().item(selected_row, col).text() 
            for col in range(1, self.model.columnCount())
        ])  

        if dialog.exec() == QDialog.Accepted:  # If the dialog is accepted
            # Refresh the table to reflect any changes
            self.refresh_table(past)

    def refresh_table(self, past):
        # Clear the current model
        self.model.removeRows(0, self.model.rowCount())

        # Fetch and populate the data based on consultation type
        if past:
            results = consulta_manager.get_past_consultas()
        else:
            results = consulta_manager.get_future_consultas()
        
        for row in results:
            new_row = [
                QStandardItem(str(row['id'])),           # consulta_id
                QStandardItem(row['cliente_nome']),      # cliente_nome
                QStandardItem(row['medico_nome']),       # medico_nome
                QStandardItem(row['data']),              # data
                QStandardItem(row['hora']),              # hora
                QStandardItem(row['status'])             # status
            ]
            self.model.appendRow(new_row)

class TodosUsers(QMainWindow):
    """
    Window for managing system users
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todos os utilizadores")
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width() // 2, screen.height() // 2)

        # Initialize the user table view
        self.users_table = QTableView()

        # Allow the table to expand dynamically
        self.users_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
        # Set selection behavior and mode for the table
        self.users_table.setSelectionBehavior(QTableView.SelectRows)
        self.users_table.setSelectionMode(QTableView.SingleSelection)

        # Initialize the model for the user data
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', 'Nome', 'Username ', 'Email', 'Role'])
        self.refresh_table()  # Load initial data into the table
        self.users_table.setModel(self.model)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Initialize buttons for user actions
        self.add_btn = QPushButton('Adicionar Utilizador')
        self.add_btn.clicked.connect(lambda: self.call_add())

        self.edit_btn = QPushButton("Editar Utilizador")
        self.edit_btn.clicked.connect(lambda: self.call_edit())
    
        self.cancel_btn = QPushButton("Remover Utilizador")
        self.cancel_btn.clicked.connect(self.delete_selected_user)

        # Set up the layout for the main window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.users_table)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(button_layout)

        # Set the central widget with the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def refresh_table(self):
        """
        Clears the current table and reloads all user data from the database.
        """
        self.model.removeRows(0, self.model.rowCount())  # Clear existing rows

        # Fetch and populate the user data
        results = user_manager.get_all_users()  # Fetch all users
        for row in results:
            new_row = [
                QStandardItem(str(row['id'])),
                QStandardItem(row['nome']),
                QStandardItem(row['username']),
                QStandardItem(row['email']),
                QStandardItem(row['role'])
            ]
            self.model.appendRow(new_row)  # Add new row to the model

    def call_add(self):
        # Open the dialog to add a new user
        add_user = UserEditar(mode='add')
        if add_user.exec() == QDialog.Accepted:
            self.refresh_table()  # Refresh the table after adding

    def call_edit(self):
        # Get selected user for editing
        selected_indexes = self.users_table.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um utilizador para editar.")
            return
        
        selected_row = selected_indexes[0].row()  # Get the first selected row
        user_id = int(self.users_table.model().item(selected_row, 0).text())

        # Retrieve user data for the selected row
        nome_utilizador = self.users_table.model().item(selected_row, 1).text()
        username = self.users_table.model().item(selected_row, 2).text()
        password_utilizador = ""  # Placeholder for password
        email_utilizador = self.users_table.model().item(selected_row, 3).text()
        role = self.users_table.model().item(selected_row, 4).text()

        # Open the dialog to edit the selected user
        edit_user = UserEditar(mode='edit', user_id=user_id)
        edit_user.set_data(user_id, nome_utilizador, username, password_utilizador, email_utilizador, role)
        
        if edit_user.exec() == QDialog.Accepted:
            self.refresh_table()  # Refresh the table after editing
    
    def delete_selected_user(self):
        # Check if a user is selected for deletion
        selected_indexes = self.users_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione um utilizador para remover.")
            return

        selected_row = selected_indexes[0].row()  # Get the selected row
        user_id = self.model.data(self.model.index(selected_row, 0))  # Get user ID

        # Confirm deletion with the user
        confirm = QMessageBox.question(
            self,
            "Confirmação",
            f"Tens a certeza que queres remover o utilizador com ID {user_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                user_manager.delete_user(user_id)  # Remove user from the database
                self.refresh_table()  # Refresh the table after deletion

                QMessageBox.information(self, "Sucesso", "Utilizador removido com sucesso.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao remover utilizador: {e}")

class UserEditar(QDialog):
    """
    Dialog for adding or editing user details
    """
    def __init__(self, mode='add', user_id=None):
        super().__init__()
        self.mode = mode
        self.user_id = user_id if mode == 'edit' else None

        # Set window title based on mode
        if mode == 'add':
            self.setWindowTitle("Adicinar Utilizador")
        elif mode == 'edit':
            self.setWindowTitle("Editar Utilizador")
        
        self.setFixedSize(400, 300)

        # Create form layout for input fields
        self.form_layout = QFormLayout()

        # Initialize input fields
        self.nome_utilizador_field = QLineEdit()
        self.username_field = QLineEdit()
        self.pass_utilizador_field = QLineEdit()
        self.email_user_field = QLineEdit()
        self.role_field = QComboBox()
        self.role_field.addItems(["padrao", "admin"])

        # Add input fields to the form layout
        self.form_layout.addRow("Nome do Utilizador:", self.nome_utilizador_field)
        self.form_layout.addRow("Username:", self.username_field)
        self.form_layout.addRow("Password do Utilizador:", self.pass_utilizador_field)
        self.form_layout.addRow("Email do Utilizador:", self.email_user_field)
        self.form_layout.addRow("Role:", self.role_field)

        # Create button layout for save and cancel buttons
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)  # Close dialog without saving
        self.save_button.clicked.connect(self.save_user)  # Save user data and close dialog

        # Set up main layout
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.form_layout)
        self.layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)

    def save_user(self):
        """
        Validates and saves user data to database
        """
        data = self.get_data()

        # Check for empty fields
        if not all([data["nome"], data["username"], data["password"], data["email"], data["role"]]):
            QMessageBox.warning(self, "Campos em falta", "Por favor, preencha todos os campos.")
            return

        try:
            # Add or update user based on mode
            if self.mode == 'add':
                user_manager.create_user(
                    data["nome"],
                    data["username"],
                    data["password"],
                    data["email"],
                    data["role"]
                )
                QMessageBox.information(self, "Utilizador Adicionado", "O utilizador foi adicionada com sucesso!")
            elif self.mode == 'edit':
                user_manager.update_user(
                    self.user_id,
                    data["nome"],
                    data["username"],
                    data["password"],
                    data["email"],
                    data["role"]
                )
                QMessageBox.information(self, "Utilizador Atualizado", "O utilizador foi atualizado com sucesso!")
            self.accept()
        
        except ValueError as e:
            QMessageBox.warning(self, "Erro", f"Erro ao adicionar/atualizar utilizador: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Ocorreu um erro: {e}")
    
    def set_data(self, user_id, nome_utilizador, username, password_utilizador, email_utilizador, role):
        # Set user data in the fields for editing
        self.user_id = user_id
        self.nome_utilizador_field.setText(str(nome_utilizador))
        self.username_field.setText(str(username))
        self.pass_utilizador_field.setText(str(password_utilizador))
        self.email_user_field.setText(str(email_utilizador))
        self.role_field.setCurrentText(role)
    
    def get_data(self):
        # Retrieve data from input fields
        return {
            "id": self.user_id,
            "nome": self.nome_utilizador_field.text(),
            "username": self.username_field.text(),
            "password": self.pass_utilizador_field.text(),
            "email": self.email_user_field.text(),
            "role": self.role_field.currentText()
        }

class TodosMedicos(QMainWindow):
    """
    Window for managing medical staff
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todos os Medicos")
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width() // 2, screen.height() // 2)

        # Initialize the table view for displaying medicos
        self.medicos_table = QTableView()

        # Set the table to expand dynamically
        self.medicos_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Configure selection behavior and mode for the table
        self.medicos_table.setSelectionBehavior(QTableView.SelectRows)
        self.medicos_table.setSelectionMode(QTableView.SingleSelection)

        # Set up the model for the table and refresh data
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', 'Nome', 'Telefone ', 'Email', 'CRM'])
        self.refresh_table()
        self.medicos_table.setModel(self.model)
        self.medicos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.medicos_table.setColumnHidden(0, True)

        # Initialize buttons for adding, editing, and removing medicos
        self.add_btn = QPushButton('Adicionar Medico')
        self.add_btn.clicked.connect(lambda: self.call_add())

        self.edit_btn = QPushButton("Editar Medico")
        self.edit_btn.clicked.connect(lambda: self.call_edit())
    
        self.cancel_btn = QPushButton("Remover Medico")
        self.cancel_btn.clicked.connect(self.delete_selected_medic)

        # Set up the layout for the main window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.medicos_table)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(button_layout)

        # Set the central widget with the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)  
  
    def refresh_table(self):
        """
        Clears the current table and reloads all data from the database.
        """
        self.model.removeRows(0, self.model.rowCount())  # Clear the table

        results = medico_manager.get_all_medicos()  # Fetch all medicos from the database
        for row in results:
            new_row = [
                QStandardItem(str(row['id'])),
                QStandardItem(row['nome']),
                QStandardItem(row['telefone']),
                QStandardItem(row['email']),
                QStandardItem(row['crm'])
            ]
            self.model.appendRow(new_row)  # Add the new row to the table

    def delete_selected_medic(self):
        # Check if a row is selected
        selected_indexes = self.medicos_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione um médico para remover.")
            return

        # Get the medic ID from the first column of the selected row
        selected_row = selected_indexes[0].row()
        medico_id = self.model.data(self.model.index(selected_row, 0))  # ID is in column 0
        nome = self.model.data(self.model.index(selected_row, 1))  # Name is in column 1

        # Ask for confirmation before deletion
        confirm = QMessageBox.question(
            self,
            "Confirmação",
            f"Tem certeza de que deseja remover o médico \"{nome}\"?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                # Remove from the database
                medico_manager.delete_medico(medico_id)

                # Remove from the table model
                self.model.removeRow(selected_row)

                QMessageBox.information(self, "Sucesso", "Médico removido com sucesso.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao remover médico: {e}")

    def call_add(self):
        # Open the dialog to add a new medico
        add_medico = MedicoEditar(mode='add')
        if add_medico.exec() == QDialog.Accepted:
            self.refresh_table() 

    def call_edit(self):
        # Check if a row is selected for editing
        selected_indexes = self.medicos_table.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um medico para editar.")
            return
        
        # Get the first selected row (assuming single selection)
        selected_row = selected_indexes[0].row()
        medico_id = int(self.medicos_table.model().item(selected_row, 0).text())

        # Open the dialog to edit the selected medico
        edit_medico = MedicoEditar(mode='edit', medico_id=medico_id)

        # Set the data for the selected medico in the edit dialog
        edit_medico.set_data(medico_id, *[
            self.medicos_table.model().item(selected_row, col).text()
            for col in range(1, self.model.columnCount())
        ])

        if edit_medico.exec() == QDialog.Accepted:
            self.refresh_table()

class MedicoEditar(QDialog):
    """
    Dialog for adding or editing medical staff details
    """
    def __init__(self, mode='add', medico_id=None):
        super().__init__()
        if mode == 'add':
            self.setWindowTitle("Adicionar Médico")
        elif mode == 'edit':
            self.setWindowTitle("Editar Médico")
        self.setFixedSize(400, 300)

        self.mode = mode
        self.medico_id = medico_id if mode == 'edit' else None

        self.nome_medico_field = QLineEdit()
        self.telefone_medico_field = QLineEdit()
        self.email_medico_field = QLineEdit()
        self.crm_field = QLineEdit()

        # Create a form layout for input fields
        self.form_layout = QFormLayout()

        # Add input fields to the form layout
        self.form_layout.addRow("Nome do Medico:", self.nome_medico_field)
        self.form_layout.addRow("Telefone:", self.telefone_medico_field)
        self.form_layout.addRow("Email do Medico:", self.email_medico_field)
        self.form_layout.addRow("CRM:", self.crm_field)

        # Create a layout for buttons
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)  # Close dialog without saving
        self.save_button.clicked.connect(self.save_medico)  # Save and close dialog

        # Set the main layout for the dialog
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.form_layout)
        self.layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
    
    def save_medico(self):
        """
        Validates and saves medical staff data to database
        """
        data = self.get_data()

        if not all([data["nome"], data["telefone"], data["email"], data["crm"]]):
            QMessageBox.warning(self, "Campos em falta", "Por favor, preencha todos os campos.")
            return

        try:
            if self.mode == 'add':
                medico_manager.add_medico(
                    data['nome'],
                    data['telefone'],
                    data['email'],
                    data['crm']
                )
                QMessageBox.information(self, 'Medico Adicionado', 'O medico foi adicionado com sucesso!')
            elif self.mode == 'edit':
                medico_manager.update_medico(
                    self.medico_id,
                    data['nome'],
                    data['telefone'],
                    data['email'],
                    data['crm']
                )
                QMessageBox.information(self, 'Medico Atualizado', 'O medico foi atualizado com sucesso!')
            self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Erro", f"Erro ao adicionar/atualizar medico: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Ocorreu um erro: {e}")
    
    def get_data(self):
        return {
            "id": self.medico_id,
            "nome": self.nome_medico_field.text(),
            "telefone": self.telefone_medico_field.text(),
            "email": self.email_medico_field.text(),
            "crm": self.crm_field.text()
        }
    
    def set_data(self, medico_id, nome_medico, telefone_medico, email_medico, crm):
        self.medico_id = medico_id
        self.nome_medico_field.setText(nome_medico)
        self.telefone_medico_field.setText(telefone_medico)
        self.email_medico_field.setText(email_medico)
        self.crm_field.setText(crm)    

class TodosClientes(QMainWindow):
    """
    Window for managing clients/patients
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todos os Clientes")
        screen = QApplication.primaryScreen().geometry()
        self.resize(screen.width() // 2, screen.height() // 2)

        # Initialize the table view for displaying clients
        self.clientes_table = QTableView()
        self.clientes_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow the table to expand

        # Configure selection behavior for the table
        self.clientes_table.setSelectionBehavior(QTableView.SelectRows)
        self.clientes_table.setSelectionMode(QTableView.SingleSelection)

        # Set up the model for the table and load initial data
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', 'Nome', 'Telefone', 'Endereço', 'Email', 'Data Nascimento'])
        self.refresh_table()
        self.clientes_table.setModel(self.model)
        self.clientes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.clientes_table.setColumnHidden(0, True)  # Hide the ID column

        # Initialize buttons for adding, editing, and removing clients
        self.add_btn = QPushButton('Adicionar Cliente')
        self.add_btn.clicked.connect(lambda: self.call_add())

        self.edit_btn = QPushButton("Editar Cliente")
        self.edit_btn.clicked.connect(lambda: self.call_edit())

        self.cancel_btn = QPushButton("Remover Cliente")
        self.cancel_btn.clicked.connect(self.delete_selected_cliente)

        # Set up the layout for the main window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.clientes_table)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(button_layout)

        # Set the central widget with the layout
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def refresh_table(self):
        """
        Clear the current table and reload all data from the database.
        """
        self.model.removeRows(0, self.model.rowCount())  # Clear the table

        results = cliente_manager.get_all_clients()  # Fetch all clients from the database
        for row in results:
            new_row = [
                QStandardItem(str(row['id'])),
                QStandardItem(row['nome']),
                QStandardItem(row['telefone']),
                QStandardItem(row['endereco']),
                QStandardItem(row['email']),
                QStandardItem(row['data_nascimento'])
            ]
            self.model.appendRow(new_row)  # Add the new row to the table

    def call_add(self):
        """Open the dialog to add a new client."""
        cliente_dialog = ClienteEditar(mode='add')
        if cliente_dialog.exec() == QDialog.Accepted:  # If the dialog is accepted
            self.refresh_table()

    def call_edit(self):
        """Open the dialog to edit the selected client."""
        selected_indexes = self.clientes_table.selectionModel().selectedRows()

        if not selected_indexes:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um cliente para editar.")
            return
        
        # Get the first selected row (assuming single selection)
        selected_row = selected_indexes[0].row()
        cliente_id = int(self.clientes_table.model().item(selected_row, 0).text())

        edit_cliente = ClienteEditar(mode='edit', cliente_id=cliente_id)

        edit_cliente.set_data(cliente_id, *[
            self.clientes_table.model().item(selected_row, col).text()
            for col in range(1, self.model.columnCount())
        ])

        if edit_cliente.exec() == QDialog.Accepted:
            self.refresh_table()

    def delete_selected_cliente(self):
        """Remove the selected client from the database and the table."""
        selected_indexes = self.clientes_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Seleção Inválida", "Por favor, selecione um cliente para remover.")
            return

        selected_row = selected_indexes[0].row()
        cliente_id = self.model.data(self.model.index(selected_row, 0))  # ID is in column 0

        # Ask for confirmation before deletion
        confirm = QMessageBox.question(
            self,
            "Confirmação",
            f"Tem a certeza de que deseja remover o cliente com ID {cliente_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                cliente_manager.delete_cliente(cliente_id)  # Remove from the database
                self.model.removeRow(selected_row)  # Remove from the table model
                QMessageBox.information(self, "Sucesso", "Cliente removido com sucesso.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao remover cliente: {e}")

class ClienteEditar(QDialog):
    """
    Dialog for adding or editing client/patient details
    """
    def __init__(self, mode='add', cliente_id=None):
        super().__init__()
        if mode == 'add':
            self.setWindowTitle("Adicionar Cliente")
        elif mode == 'edit':
            self.setWindowTitle("Editar Cliente")
        self.setFixedSize(400, 300)

        self.mode = mode
        self.cliente_id = cliente_id if mode == 'edit' else None

        # Create input fields for client information
        self.nome_cliente_field = QLineEdit()
        self.telefone_cliente_field = QLineEdit()
        self.endereco_cliente_field = QLineEdit()
        self.email_cliente_field = QLineEdit()
        self.data_nascimento_cliente_field = QDateEdit()
        self.data_nascimento_cliente_field.setCalendarPopup(True)
        self.data_nascimento_cliente_field.setDate(QDate.currentDate())
        self.data_nascimento_cliente_field.setDisplayFormat("yyyy-MM-dd")

        # Form layout for input fields
        self.form_layout = QFormLayout()
        self.form_layout.addRow("Nome do Cliente:", self.nome_cliente_field)
        self.form_layout.addRow("Telefone:", self.telefone_cliente_field)
        self.form_layout.addRow("Endereco do Cliente:", self.endereco_cliente_field)
        self.form_layout.addRow("Email do Cliente:", self.email_cliente_field)
        self.form_layout.addRow("Data de Nascimento:", self.data_nascimento_cliente_field)

        # Layout for buttons
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.save_cliente)

        # Main layout for the dialog
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.form_layout)
        self.layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
    
    def save_cliente(self):
        """
        Validates and saves client data to database
        """
        data = self.get_data()

        # Check for empty fields
        if not data['nome'] or not data['telefone'] or not data['endereco'] or not data['email']:
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha todos os campos obrigatórios.")
            return

        try:
            if self.mode == 'add':
                cliente_manager.add_cliente(
                    data['nome'],
                    data['telefone'],
                    data['endereco'],
                    data['email'],
                    data['data_nascimento']
                )
                QMessageBox.information(self, 'Cliente Adicionado', 'O cliente foi adicionado com sucesso!')
            elif self.mode == 'edit':
                cliente_manager.update_cliente(
                    self.cliente_id,
                    data['nome'],
                    data['telefone'],
                    data['endereco'],
                    data['email'],
                    data['data_nascimento']
                )
                QMessageBox.information(self, 'Cliente Atualizado', 'O cliente foi atualizado com sucesso!')
            self.accept()
    
        except ValueError as e:
            QMessageBox.warning(self, "Erro", f"Erro ao adicionar/atualizar cliente: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Ocorreu um erro: {e}")

    def set_data(self, cliente_id, nome, telefone, endereco, email, data_nascimento):
        self.cliente_id = cliente_id
        self.nome_cliente_field.setText(nome)
        self.telefone_cliente_field.setText(telefone)
        self.endereco_cliente_field.setText(endereco)
        self.email_cliente_field.setText(email)
        
        # Set the date in the date field
        date_parts = data_nascimento.split("-")  # Assuming format "yyyy-MM-dd"
        year, month, day = map(int, date_parts)
        self.data_nascimento_cliente_field.setDate(QDate(year, month, day))
    
    def get_data(self):
        return {
            "id": self.cliente_id,
            "nome": self.nome_cliente_field.text(),
            "telefone": self.telefone_cliente_field.text(),
            "endereco": self.endereco_cliente_field.text(),
            "email": self.email_cliente_field.text(),
            "data_nascimento": self.data_nascimento_cliente_field.date().toString("yyyy-MM-dd")
        }

class About(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sobre")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        title = QLabel("Desenvolvedores")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        developers = QLabel("Hugo Rodrigues\nMiguel Amaral\nJean Will")
        developers.setAlignment(Qt.AlignCenter)
        
        cat = QLabel("© ᓚᘏᗢ")
        cat.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        
        layout.addWidget(title)
        layout.addWidget(developers)
        layout.addWidget(cat)
        
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(LIGHT_THEME)
    
    # Set application icon
    app_icon = QIcon("assets/icon.png")
    app.setWindowIcon(app_icon)
    
    window = StartWindow()
    window.show()
    
    sys.exit(app.exec())
