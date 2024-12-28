import sqlite3
from bcrypt import hashpw, gensalt, checkpw


# Conectar (ou criar) ao banco de dados SQLite
conexao = sqlite3.connect('sistema_clinico.db')

# Criar um cursor para executar comandos SQL
cursor = conexao.cursor()

# Comandos SQL para criar as tabelas
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password BLOB NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('admin', 'padrao'))
);
"""

create_clientes_table = """
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    endereco TEXT,
    email TEXT UNIQUE,
    data_nascimento DATE
);
"""

create_medicos_table = """
CREATE TABLE IF NOT EXISTS medicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT UNIQUE,
    crm TEXT NOT NULL UNIQUE
);
"""

create_consultas_table = """
CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    medico_id INTEGER NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('agendada', 'concluida')),
    FOREIGN KEY(cliente_id) REFERENCES clientes(id),
    FOREIGN KEY(medico_id) REFERENCES medicos(id)
);
"""

# Executar os comandos SQL
cursor.execute(create_users_table)
cursor.execute(create_clientes_table)
cursor.execute(create_medicos_table)
cursor.execute(create_consultas_table)
ad_pw = hashpw('admin'.encode(), gensalt())
cursor.execute('''
    INSERT INTO users (nome, username, password, email, role)
    SELECT ?, ?, ?, ?, ?
    WHERE NOT EXISTS (
        SELECT 1 FROM users WHERE username = ?
    )
''', ('Administrador', 'admin', ad_pw, 'null@email.com', 'admin', 'admin'))


conexao.commit()


class UserManager:
    def __init__(self, db_path):
        # Inicializa a conexão com o banco de dados.
        self.db_path = db_path

    def _connect(self):
        # Cria uma conexão com o banco de dados
        return sqlite3.connect(self.db_path)

    def create_user(self, nome, username, password, email, role='padrao'):
        hashed_password = hashpw(password.encode(), gensalt())
        
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (nome, username, password, email, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome, username, hashed_password, email, role))
                conn.commit()
                return True, "User created successfully"
                
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists"
            if "email" in str(e):
                return False, "Email already exists"
            return False, str(e)
            
    def _validate_username(self, username):
        return (3 <= len(username) <= 30) and ' ' not in username
        
    def _validate_email(self, email):
        return '@' in email and '.' in email
        
    def _validate_password(self, password):
        return len(password) >= 8

    def authenticate(self, username, password):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password, role FROM users WHERE username = ? OR email = ?", (username, username))
                row = cursor.fetchone()

                if row:
                    stored_password = row[0]  # This should be the hashed binary data
                    if isinstance(stored_password, str):
                        stored_password = stored_password.encode()  # Ensure it's bytes

                    if checkpw(password.encode(), stored_password):
                        return True, row[1]
                
                return False, print("Invalid username or password")
        except sqlite3.Error as e:
            return False, str(e)
    
    def get_all_users(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, username, email, role FROM users")
                rows = cursor.fetchall()
                users = []
                for row in rows:
                    users.append({
                        'id': row[0],
                        'nome': row[1],
                        'username': row[2],
                        'email': row[3],
                        'role': row[4]
                    })
                return users  # List of tuples containing user data
        except sqlite3.Error as e:
            print(f"Erro ao buscar usuários: {e}")
            return []

    def update_user(self, user_id, nome, username, password, email, role):
        try:
            hashed_password = hashpw(password.encode(), gensalt())

            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET nome = ?, username = ?, password = ?, email = ?, role = ? 
                    WHERE id = ?
                """, (nome, username, hashed_password, email, role, user_id))
                conn.commit()
                return True, "User updated successfully"

        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return False, "Username already exists"
            if "email" in str(e):
                return False, "Email already exists"
            return False, str(e)

        except Exception as e:
            return False, str(e)

    def delete_user(self, user_id):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                # Delete the user with the specified ID
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                print(f"User with ID {user_id} removed successfully.")
        except sqlite3.Error as e:
            print(f"Error removing user: {e}")

# Class Cliente
class ClienteManager:
    def __init__(self, id=None, nome=None, telefone=None, endereco=None, email=None, data_nascimento=None):
        # Initialize attributes
        self.__id = id
        self.__nome = nome
        self.__telefone = telefone
        self.__endereco = endereco
        self.__email = email
        self.__data_nascimento = data_nascimento
        
    def get_nome(self):
        return self.__nome
    
    def get_telefone(self):
        return self.__telefone
    
    def get_endereco(self):
        return self.__endereco
    
    def get_email(self):
        return self.__email
    
    def get_data_nascimento(self):
        return self.__data_nascimento

    def set_nome(self, nome):
        self.__nome = nome

    def set_telefone(self, telefone):
        self.__telefone = telefone

    def set_endereco(self, endereco):
        self.__endereco = endereco

    def set_email(self, email):
        self.__email = email

    def set_data_nascimento(self, data_nascimento):
        self.__data_nascimento = data_nascimento
        
    # Método para adicionar um novo cliente ao banco de dados
    @staticmethod
    def add_cliente(nome, telefone, endereco, email, data_nascimento):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clientes (nome, telefone, endereco, email, data_nascimento)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome, telefone, endereco, email, data_nascimento))
                conn.commit()

        except sqlite3.Error as e:
            print(f"Erro ao adicionar cliente: {e}")
            raise
            
    # Método para atualizar um cliente existente no banco de dados
    @staticmethod
    def update_cliente(id, nome, telefone, endereco, email, data_nascimento):
        with sqlite3.connect("sistema_clinico.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clientes
                SET nome=?, telefone=?, endereco=?, email=?, data_nascimento=?
                WHERE id=?
            """, (nome, telefone, endereco, email, data_nascimento, id))
            conn.commit()
            print("Cliente atualizado com sucesso!")
            
    # Método para excluir um cliente do banco de dados
    @staticmethod
    def delete_cliente(id):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clientes WHERE id=?", (id,))
                conn.commit()
                print("Cliente removido com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao excluir cliente: {e}")
            raise

    @staticmethod
    def get_all_clients():
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, telefone, endereco, email, data_nascimento FROM clientes")
                rows = cursor.fetchall()
                clientes = []
                for row in rows:
                    clientes.append({
                        'id': row[0],
                        'nome': row[1],
                        'telefone': row[2],
                        'endereco': row[3],
                        'email': row[4],
                        'data_nascimento': row[5]
                    })
                return clientes
        except sqlite3.Error as e:
            print(f"Erro ao buscar clientes: {e}")
            return []

    def __str__(self):
        return f"Cliente: {self.__nome}, Telefone: {self.__telefone}"

# Class medico 
class MedicoManager:
    def __init__(self, nome=None, telefone=None, email=None, crm=None):
        self.__nome = nome
        self.__telefone = telefone
        self.__email = email
        self.__crm = crm
    
    @property
    def nome(self):
        return self.__nome
    
    @nome.setter 
    def nome(self, value):
        self.__nome = value

    @property
    def telefone(self):
        return self.__telefone
    
    @telefone.setter
    def telefone(self, value):
        self.__telefone = value

    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, value):
        self.__email = value

    @property
    def crm(self):
        return self.__crm
    
    @crm.setter
    def crm(self, value):
        self.__crm = value

    def __str__(self):
        return f"Médico: {self.__nome}"            
    
    # Método para adicionar um novo médico ao banco de dados
    def add_medico(self, nome, telefone, email, crm):

        with sqlite3.connect("sistema_clinico.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO medicos (nome, telefone, email, crm) VALUES (?, ?, ?, ?);''', (nome, telefone, email, crm))
            conn.commit()
    
    # Método para atualizar um médico existente no banco de dados
    def update_medico(self, medico_id, nome, telefone, email, crm):
        # Dar update à base de dados
        with sqlite3.connect("sistema_clinico.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""UPDATE medicos
                    SET nome = ?, telefone = ?, email = ?, crm = ?
                    WHERE id = ?;""", (nome, telefone, email, crm, medico_id))
            conn.commit()
            print("Dados do médico atualizados com sucesso!")

    # Método para excluir um médico do banco de dados
    def delete_medico(self, medico_id):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                # Apagar oo médico com o id passado como parâmetro
                cursor.execute("DELETE FROM medicos WHERE id = ?", (medico_id,))
                conn.commit()
                print(f"Medic with ID {medico_id} removed successfully.")
        except sqlite3.Error as e:
            print(f"Error removing medic: {e}")    

    def get_all_medicos(self):
        with sqlite3.connect('sistema_clinico.db') as conn:
            cursor = conn.cursor()
            query = "SELECT id, nome, telefone, email, crm FROM medicos;"
            cursor.execute(query)
            rows = cursor.fetchall()
            medicos = []
            for row in rows:
                medicos.append({
                    'id': row[0],
                    'nome': row[1],
                    'telefone': row[2],
                    'email': row[3],
                    'crm': row[4]
                })
            return medicos

class ConsultasManager:
    def __init__(self, data=None, hora=None, medico=None, cliente=None):
        self.__data = data
        self.__hora = hora
        self.__medico = medico
        self.__cliente = cliente

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, value):
        self.__data = value
    
    @property
    def hora(self):
        return self.__hora
    
    @hora.setter
    def hora(self, value):
        self.__hora = value
    
    @property
    def medico(self):
        return self.__medico
    
    @medico.setter
    def medico(self, value):
        self.__medico = value
    
    @property
    def cliente(self):
        return self.__cliente
    
    @cliente.setter
    def cliente(self, value):
        self.__cliente = value
    
    def __str__(self):
        return f"Consulta: {self.__data} - {self.__hora}"

    # Constantes SQL
    SQL_SELECT_QUERY = """
        SELECT consultas.id, clientes.nome AS cliente_nome, medicos.nome AS medico_nome, consultas.data, consultas.hora, consultas.status 
        FROM consultas 
        INNER JOIN clientes ON consultas.cliente_id = clientes.id 
        INNER JOIN medicos ON consultas.medico_id = medicos.id
    """

    def get_future_consultas(self):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                query = self.SQL_SELECT_QUERY + " WHERE DATE(consultas.data) >= DATE('now')"
                cursor.execute(query)
                rows = cursor.fetchall()
                consultas = []
                for row in rows:
                    consultas.append({
                        'id': row[0],
                        'cliente_nome': row[1],
                        'medico_nome': row[2],
                        'data': row[3],
                        'hora': row[4],
                        'status': row[5]
                    })
                print(f"Fetched {len(consultas)} future consultations.")
                return consultas
        except sqlite3.Error as e:
            print(f"Error fetching future consultations: {e}")
            return []

    def get_past_consultas(self):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                query = self.SQL_SELECT_QUERY + " WHERE DATE(consultas.data) < DATE('now')"
                cursor.execute(query)
                rows = cursor.fetchall()
                consultas = []
                for row in rows:
                    consultas.append({
                        'id': row[0],
                        'cliente_nome': row[1],
                        'medico_nome': row[2],
                        'data': row[3],
                        'hora': row[4],
                        'status': row[5]
                    })
                print(f"Fetched {len(consultas)} past consultations.")
                return consultas
        except sqlite3.Error as e:
            print(f"Error fetching past consultations: {e}")
            return []

    def get_today_consultas(self):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                query = self.SQL_SELECT_QUERY + " WHERE DATE(consultas.data) = DATE('now')"
                cursor.execute(query)
                rows = cursor.fetchall()
                consultas = []
                for row in rows:
                    consultas.append({
                        'id': row[0],
                        'cliente_nome': row[1],
                        'medico_nome': row[2],
                        'data': row[3],
                        'hora': row[4],
                        'status': row[5]
                    })
                print(f"Fetched {len(consultas)} consultations for today.")
                return consultas
        except sqlite3.Error as e:
            print(f"Error fetching today's consultations: {e}")
            return []

    def add_consulta(self, cliente, medico, data, hora, status):
        if not cliente or not medico or not data or not hora:
            raise ValueError("Todos os campos devem ser preenchidos.")
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO consultas (cliente_id, medico_id, data, hora, status) 
                    VALUES (?, ?, ?, ?, ?)
                """, (cliente, medico, data, hora, status))
                conn.commit()
                print("Consulta added successfully.")
        except sqlite3.Error as e:
            print(f"Error adding consulta: {e}")
            raise

    def update_consulta(self, consulta_id, cliente_id, medico_id, data, hora, status):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE consultas 
                    SET cliente_id=?, medico_id=?, data=?, hora=?, status=?
                    WHERE id=?
                """, (cliente_id, medico_id, data, hora, status, consulta_id))
                conn.commit()
                print(f"Consulta {consulta_id} updated successfully.")
        except sqlite3.Error as e:
            print(f"Error updating consulta {consulta_id}: {e}")
            return None

    def get_consulta(self, consulta_id):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT consultas.id, clientes.nome AS cliente_nome, medicos.nome AS medico_nome, consultas.data, consultas.hora, consultas.status
                    FROM consultas
                    JOIN clientes ON consultas.cliente_id = clientes.id
                    JOIN medicos ON consultas.medico_id = medicos.id
                    WHERE consultas.id = ?
                """, (consulta_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching consulta {consulta_id}: {e}")
            return None

    def del_consulta(self, consulta_id):
        try:
            with sqlite3.connect("sistema_clinico.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))
                conn.commit()
                print(f"Consulta with ID {consulta_id} removed successfully.")
        except sqlite3.Error as e:
            print(f"Error removing consulta {consulta_id}: {e}")
