import sqlite3
from flask_bcrypt import Bcrypt
from datetime import datetime

# Inicializar bcrypt
bcrypt = Bcrypt()

# Conectar ao banco de dados
conn = sqlite3.connect('backend/instance/contentai.db')
cursor = conn.cursor()

# Dados do novo usuário
email = 'lbiel213@gmail.com'
password = 'petam004'
name = 'Admin User'  # Nome opcional
is_premium = True
is_admin = True

# Hash da senha
password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

# Inserir usuário
cursor.execute('''
    INSERT INTO users (email, password_hash, name, is_premium, is_admin, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', (email, password_hash, name, is_premium, is_admin, datetime.utcnow()))

# Commit e fechar
conn.commit()
conn.close()

print("Usuário criado com sucesso!")
print(f"Email: {email}")
print(f"Senha: {password}")
print(f"Admin: {is_admin}")
print(f"Premium: {is_premium}")
