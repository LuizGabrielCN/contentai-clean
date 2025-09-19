import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('backend/instance/contentai.db')
cursor = conn.cursor()

# Executar consulta
cursor.execute("SELECT id, email, name, is_premium, is_admin, created_at, last_login FROM users")

# Obter resultados
users = cursor.fetchall()

# Imprimir cabeçalhos
print("ID | Email | Name | Premium | Admin | Created At | Last Login")
print("-" * 80)

# Imprimir cada usuário
for user in users:
    print(f"{user[0]} | {user[1]} | {user[2] or 'N/A'} | {user[3]} | {user[4]} | {user[5]} | {user[6] or 'Never'}")

# Fechar conexão
conn.close()
