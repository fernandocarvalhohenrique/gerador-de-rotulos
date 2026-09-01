# --- BANCO DE DADOS SQLITE (COM MIGRAÇÃO AUTOMÁTICA) ---
def init_db():
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    
    # 1. Cria a tabela caso não exista
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT,
            produtor TEXT,
            cnpj TEXT,
            endereco TEXT,
            sac TEXT,
            quimico TEXT,
            crq TEXT,
            anp TEXT,
            logo_base64 TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # 2. Garante que a coluna 'is_admin' exista mesmo em bancos antigos
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # A coluna já existe, ignora o erro
        
    # 3. Tabela Global de Normas
    c.execute('''
        CREATE TABLE IF NOT EXISTS normas_globais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            norma TEXT UNIQUE
        )
    ''')
    
    # 4. Inserção / Atualização segura da conta Administrador padrão
    c.execute("SELECT username FROM usuarios WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("""
            INSERT INTO usuarios (username, password, produtor, cnpj, is_admin)
            VALUES ('admin', 'admin123', 'Administração do Sistema', '00.000.000/0000-00', 1)
        """)
    else:
        c.execute("UPDATE usuarios SET is_admin = 1 WHERE username = 'admin'")
        
    conn.commit()
    conn.close()
