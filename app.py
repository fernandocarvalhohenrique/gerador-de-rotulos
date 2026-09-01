import base64
import io
import sqlite3
import qrcode
from PIL import Image
import streamlit as st
from weasyprint import HTML

st.set_page_config(page_title="Gerador de Rótulos de Óleo Lubrificante - ANP", layout="wide")

# --- BANCO DE DADOS SQLITE (COM MIGRAÇÃO AUTOMÁTICA) ---
def init_db():
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    
    # 1. Tabela de Usuários
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
    
    try:
        c.execute("ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Coluna já existe
        
    # 2. Tabela Global de Normas
    c.execute('''
        CREATE TABLE IF NOT EXISTS normas_globais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            norma TEXT UNIQUE
        )
    ''')

    # 3. Tabela Global de Viscosidades / Graus SAE & ISO
    c.execute('''
        CREATE TABLE IF NOT EXISTS graus_viscosidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grau TEXT UNIQUE
        )
    ''')
    
    # Inserção do Admin Padrão
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

init_db()

def popular_dados_iniciais():
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    
    # Normas
    c.execute("SELECT COUNT(*) FROM normas_globais")
    if c.fetchone()[0] == 0:
        normas_padrao = [
            ("Linha Leve & Ciclo Otto", "API SP"), ("Linha Leve & Ciclo Otto", "API SN Plus"), ("Linha Leve & Ciclo Otto", "ACEA C3"),
            ("Linha Pesada (Diesel)", "API CK-4"), ("Linha Pesada (Diesel)", "API CI-4 / SL"), ("Linha Pesada (Diesel)", "ACEA E9"),
            ("Motos (2T e 4T)", "JASO MA2"), ("Motos (2T e 4T)", "JASO FD (2T)"),
            ("Transmissão & Hidráulico", "API GL-4"), ("Transmissão & Hidráulico", "API GL-5"), ("Transmissão & Hidráulico", "Dexron VI (ATF)")
        ]
        c.executemany("INSERT OR IGNORE INTO normas_globais (categoria, norma) VALUES (?, ?)", normas_padrao)

    # Viscosidades
    c.execute("SELECT COUNT(*) FROM graus_viscosidade")
    if c.fetchone()[0] == 0:
        graus_padrao = [
            ("SAE 30",), ("SAE 40",), ("SAE 50",), ("SAE 5W-30",), ("SAE 5W-40",), 
            ("SAE 10W-30",), ("SAE 10W-40",), ("SAE 15W-40",), ("SAE 20W-50",), 
            ("SAE 80W-90",), ("SAE 85W-140",), ("ISO VG 32",), ("ISO VG 46",), ("ISO VG 68",), ("ISO VG 100",), ("ISO VG 150",)
        ]
        c.executemany("INSERT OR IGNORE INTO graus_viscosidade (grau) VALUES (?)", graus_padrao)

    conn.commit()
    conn.close()

popular_dados_iniciais()

# --- AUTENTICAÇÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.sidebar.title("🔐 Autenticação de Usuário")

if st.session_state.usuario_logado is None:
    aba_auth = st.sidebar.radio("Selecione:", ["Login", "Cadastrar Nova Empresa"])
    
    if aba_auth == "Login":
        user_input = st.sidebar.text_input("Usuário / Login:")
        pass_input = st.sidebar.text_input("Senha:", type="password")
        if st.sidebar.button("Entrar"):
            conn = sqlite3.connect("rotulos_app.db")
            c = conn.cursor()
            c.execute("SELECT username, is_admin FROM usuarios WHERE username = ? AND password = ?", (user_input, pass_input))
            user_data = c.fetchone()
            conn.close()
            
            if user_data:
                st.session_state.usuario_logado = user_data[0]
                st.session_state.is_admin = bool(user_data[1])
                st.sidebar.success(f"Bem-vindo, {user_input}!")
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha incorretos.")
                
    elif aba_auth == "Cadastrar Nova Empresa":
        new_user = st.sidebar.text_input("Novo Usuário / Login:")
        new_pass = st.sidebar.text_input("Nova Senha:", type="password")
        cad_produtor = st.sidebar.text_input("Razão Social Empresa:")
        cad_cnpj = st.sidebar.text_input("CNPJ:")
        eh_adm = st.sidebar.checkbox("Cadastrar como Administrador (ADM)")
        
        if st.sidebar.button("Criar Conta"):
            if new_user and new_pass:
                try:
                    conn = sqlite3.connect("rotulos_app.db")
                    c = conn.cursor()
                    c.execute("INSERT INTO usuarios (username, password, produtor, cnpj, is_admin) VALUES (?, ?, ?, ?, ?)",
                              (new_user, new_pass, cad_produtor, cad_cnpj, 1 if eh_adm else 0))
                    conn.commit()
                    conn.close()
                    st.sidebar.success("Conta criada! Faça o login na aba 'Login'.")
                except sqlite3.IntegrityError:
                    st.sidebar.error("Usuário já existe.")
            else:
                st.sidebar.error("Preencha usuário e senha.")
    st.warning("⚠️ Faça login na barra lateral para acessar o sistema.")
    st.stop()
else:
    st.sidebar.write(f"Usuário: *{st.session_state.usuario_logado}*")
    if st.session_state.is_admin:
        st.sidebar.info("👑 Perfil: Administrador")
    else:
        st.sidebar.info("🏢 Perfil: Empresa / Cliente")
        
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.session_state.is_admin = False
        st.rerun()

# --- PAINEL DO ADMINISTRADOR ---
if st.session_state.is_admin:
    st.title("👑 Painel do Administrador")
    tab_gerador, tab_admin = st.tabs(["🛢️ Gerador de Rótulos", "⚙️ Gestão de Usuários & Empresas"])
    
    with tab_admin:
        st.subheader("👥 Usuários e Empresas Cadastradas")
        conn = sqlite3.connect("rotulos_app.db")
        c = conn.cursor()
        c.execute("SELECT username, produtor, cnpj, crq, anp, is_admin FROM usuarios")
        usuarios_lista = c.fetchall()
        conn.close()
        
        st.table([
            {
                "Usuário/Login": u[0],
                "Razão Social": u[1],
                "CNPJ": u[2],
                "CRQ": u[3],
                "ANP": u[4],
                "Perfil": "Administrador" if u[5] else "Cliente"
            } for u in usuarios_lista
        ])
        
        st.subheader("🗑️ Remover Usuário")
        opcoes_remocao = [u[0] for u in usuarios_lista if u[0] != st.session_state.usuario_logado]
        if opcoes_remocao:
            user_to_delete = st.selectbox("Selecione um usuário para remover:", opcoes_remocao)
            if st.button("Excluir Usuário Selecionado"):
                conn = sqlite3.connect("rotulos_app.db")
                c = conn.cursor()
                c.execute("DELETE FROM usuarios WHERE username = ?", (user_to_delete,))
                conn.commit()
                conn.close()
                st.success(f"Usuário '{user_to_delete}' removido com sucesso!")
                st.rerun()

# --- CARREGAR DADOS DO USUÁRIO LOGADO ---
conn = sqlite3.connect("rotulos_app.db")
c = conn.cursor()
c.execute("SELECT produtor, cnpj, endereco, sac, quimico, crq, anp, logo_base64 FROM usuarios WHERE username = ?", (st.session_state.usuario_logado,))
u_data = c.fetchone()
conn.close()

def gerar_qr_code_base64(texto):
    if not texto or not texto.strip():
        return ""
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

FONTS_DB = {
    "Arial / Helvetica (Padrão Limpo)": "Arial, Helvetica, sans-serif",
    "Impact / Heavy (Destaque Robusto)": "Impact, 'Arial Black', sans-serif",
    "Montserrat / Segoe UI (Moderna)": "'Segoe UI', Roboto, Montserrat, sans-serif",
    "Trebuchet MS / Technical (Industrial)": "'Trebuchet MS', sans-serif",
    "Courier New (Técnica / Laboratório)": "'Courier New', Courier, monospace",
    "Georgia / Serif (Clássica Elegante)": "Georgia, 'Times New Roman', serif"
}

st.title("🛢️ Gerador de Rótulos de Lubrificantes (Padrão ANP)")

# --- CONFIGURAÇÕES DE DESIGN E IMAGENS ---
st.subheader("🎨 Estilo, Fontes e Logotipo")
col_design1, col_design2, col_design3 = st.columns(3)

with col_design1:
    nome_topo_empresa = st.text_input("Nome/Sigla do Topo (Header):", "DULUB")
    fonte_titulo = st.selectbox("Fonte dos Títulos / Marca:", list(FONTS_DB.keys()), index=1)

with col_design2:
    fonte_corpo = st.selectbox("Fonte do Corpo / Especificações:", list(FONTS_DB.keys()), index=0)
    fonte_alerta = st.selectbox("Fonte de Advertências / Alertas:", list(FONTS_DB.keys()), index=0)

with col_design3:
    upload_logo = st.file_uploader("Upload Logotipo da Empresa (PNG/JPG):", type=["png", "jpg", "jpeg"])
    logo_b64 = u_data[7] if u_data and u_data[7] else ""
    if upload_logo is not None:
        image = Image.open(upload_logo)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        logo_b64 = base64.b64encode(buffered.getvalue()).decode()

# --- NOVO PAINEL DE ILUSTRAÇÃO / MARCA D'ÁGUA ---
st.subheader("🖼️ Imagem Ilustrativa do Rótulo (Carro, Engrenagem, Vetores)")
col_img1, col_img2, col_img3, col_img4 = st.columns(4)

with col_img1:
    upload_ilustracao = st.file_uploader("Subir Imagem Ilustrativa (PNG/JPG):", type=["png", "jpg", "jpeg"])
    ilustracao_b64 = ""
    if upload_ilustracao is not None:
        img_ilustr = Image.open(upload_ilustracao)
        buffered = io.BytesIO()
        img_ilustr.save(buffered, format="PNG")
        ilustracao_b64 = base64.b64encode(buffered.getvalue()).decode()

with col_img2:
    posicao_rotulo = st.selectbox("Aplicar a imagem em:", ["Frente do Rótulo", "Contrarrótulo", "Ambos os Rótulos"])
    modo_exibicao = st.selectbox("Modo de Exibição:", ["Sobreposta / Destacada", "Marca d'Água (Fundo Suave)"])

with col_img3:
    posicao_vertical = st.selectbox("Alinhamento Vertical:", ["Centro", "Topo", "Fundo (Base)"])
    posicao_horizontal = st.selectbox("Alinhamento Horizontal:", ["Centro", "Esquerda", "Direita"])

with col_img4:
    tamanho_imagem = st.slider("Tamanho da Imagem (px):", min_value=30, max_value=250, value=90, step=10)
    opacidade_watermark = st.slider("Opacidade (Marca d'Água):", min_value=0.05, max_value=0.50, value=0.15, step=0.05) if modo_exibicao == "Marca d'Água (Fundo Suave)" else 1.0

# --- DADOS DO PRODUTO ---
col_prod, col_tec = st.columns(2)

with col_prod:
    st.subheader("📌 Dados do Produto")
    marca_comercial = st.text_input("Marca Comercial", "DULUB TASA")
    
    # Buscar Graus SAE / ISO do Banco
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    c.execute("SELECT grau FROM graus_viscosidade ORDER BY grau")
    graus_cadastrados = [row[0] for row in c.fetchall()]
    conn.close()
    
    viscosidade = st.selectbox("Viscosidade (Grau SAE / ISO):", graus_cadastrados, index=0)
    
    # Cadastrar novo Grau SAE / ISO
    novo_grau = st.text_input("➕ Cadastrar Novo Grau SAE / ISO:")
    if st.button("Salvar Novo Grau SAE/ISO"):
        if novo_grau.strip():
            conn = sqlite3.connect("rotulos_app.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO graus_viscosidade (grau) VALUES (?)", (novo_grau.strip(),))
                conn.commit()
                st.success(f"Grau '{novo_grau}' adicionado com sucesso!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.warning("Este grau de viscosidade já está cadastrado.")
            conn.close()
            
    tipo_oleo = st.selectbox("Natureza do Produto (Frente e Trás geram automático):", ["Mineral", "Semissintético", "Sintético"])
    volume = st.selectbox("Volume", ["1 Litro", "4 Litros", "20 Litros", "200 Litros"], index=0)
    desc_frente = st.text_area("Descrição Comercial (Frente):", "Óleo lubrificante para direção hidráulica e transmissões automáticas.")

with col_tec:
    st.subheader("⚙️ Especificações & Contrarrótulo")
    campo_aplicacao = st.text_input("Campo de Aplicação (Contrarrótulo):", "tasa / Direção Hidráulica")
    composicao_prod = st.text_area("Composição (Contrarrótulo):", "Óleo básico mineral e pacote de aditivos de alta performance (Extrema Pressão).")
    
    # Normas da Tabela Global
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT norma FROM normas_globais ORDER BY norma")
    normas_totais = [row[0] for row in c.fetchall()]
    conn.close()
    
    normas_frente = st.multiselect("Normas na Frente:", normas_totais, default=["SAE 30"] if "SAE 30" in normas_totais else [])
    normas_tras = st.text_input("Especificações Atendidas (Contrarrótulo):", "SAE 30 - TASA")
    
    nova_norma = st.text_input("➕ Cadastrar Nova Norma no Banco Global:")
    if st.button("Salvar Norma Global"):
        if nova_norma.strip():
            conn = sqlite3.connect("rotulos_app.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO normas_globais (categoria, norma) VALUES (?, ?)", ("Geral", nova_norma.strip()))
                conn.commit()
                st.success(f"Norma '{nova_norma}' adicionada!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.warning("Esta norma já existe no banco.")
            conn.close()

    codigo_barras_txt = st.text_input("Código de Barras (Texto/EAN-13):", "7891234567890")
    qr_code_link = st.text_input("Link para QR Code (Site/FISPQ/SAC):", "https://www.ipabr.com.br")

# --- DADOS DA EMPRESA ---
st.subheader("🏢 Dados da Empresa")
col_e1, col_e2 = st.columns(2)

with col_e1:
    produtor = st.text_input("Razão Social (PRODUTOR / DETENTOR):", value=u_data[0] if u_data and u_data[0] else "INDUSTRIA PETROQUIMICA APOLLO")
    cnpj_produtor = st.text_input("CNPJ:", value=u_data[1] if u_data and u_data[1] else "37.413.384/0001-84")
    endereco_produtor = st.text_input("Endereço:", value=u_data[2] if u_data and u_data[2] else "Av. Adroaldo José Bombardelli, 1835 - Ponta Grossa/PR")
    sac_empresa = st.text_input("SAC / Contato / Site:", value=u_data[3] if u_data and u_data[3] else "+55 (42) 2702-0500 - www.ipabr.com.br")

with col_e2:
    quimico_resp = st.text_input("Químico Responsável:", value=u_data[4] if u_data and u_data[4] else "Rafael Costa da Cunha")
    crq_num = st.text_input("Nº CRQ / Região:", value=u_data[5] if u_data and u_data[5] else "CRQ IX: 09303534")
    registro_anp = st.text_input("Registro ANP:", value=u_data[6] if u_data and u_data[6] else "24076")

if st.button("💾 Salvar Meus Dados da Empresa"):
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    c.execute("""
        UPDATE usuarios 
        SET produtor=?, cnpj=?, endereco=?, sac=?, quimico=?, crq=?, anp=?, logo_base64=?
        WHERE username=?
    """, (produtor, cnpj_produtor, endereco_produtor, sac_empresa, quimico_resp, crq_num, registro_anp, logo_b64, st.session_state.usuario_logado))
    conn.commit()
    conn.close()
    st.success("Dados da empresa salvos com sucesso!")

# --- VISUALIZAÇÃO ---
qr_b64 = gerar_qr_code_base64(qr_code_link)
img_logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 45px; max-width: 180px; margin-bottom: 2mm;" />' if logo_b64 else ""
img_qr_html = f'<img src="data:image/png;base64,{qr_b64}" style="width: 55px; height: 55px;" />' if qr_b64 else ""

# Lógica CSS para Imagem Ilustrativa / Marca d'Água
css_align_v = "top: 10px;" if posicao_vertical == "Topo" else ("bottom: 10px;" if posicao_vertical == "Fundo (Base)" else "top: 50%; transform: translateY(-50%);")
css_align_h = "left: 10px;" if posicao_horizontal == "Esquerda" else ("right: 10px;" if posicao_horizontal == "Direita" else "left: 50%; transform: translateX(-50%);")

if posicao_vertical == "Centro" and posicao_horizontal == "Centro":
    css_align_center = "top: 50%; left: 50%; transform: translate(-50%, -50%);"
else:
    css_align_center = f"{css_align_v} {css_align_h}"

img_ilustr_html = f'''
<img src="data:image/png;base64,{ilustracao_b64}" style="
    position: absolute;
    {css_align_center}
    max-height: {tamanho_imagem}px;
    opacity: {opacidade_watermark};
    z-index: {'0' if modo_exibicao == "Marca d'Água (Fundo Suave)" else '2'};
    pointer-events: none;
" />
''' if ilustracao_b64 else ""

img_frente = img_ilustr_html if ilustracao_b64 and posicao_rotulo in ["Frente do Rótulo", "Ambos os Rótulos"] else ""
img_tras = img_ilustr_html if ilustracao_b64 and posicao_rotulo in ["Contrarrótulo", "Ambos os Rótulos"] else ""

st.subheader("👁️ Pré-Visualização em Tempo Real (Croqui)")

html_croqui = f"""
<div style="font-family: {FONTS_DB[fonte_corpo]}; border: 2px solid #1a365d; padding: 15px; border-radius: 8px; background-color: #ffffff; color: #1a365d;">
    <div style="display: flex; justify-content: space-between;">
        
        <!-- FRENTE -->
        <div style="width: 48%; border: 1px solid #cbd5e0; padding: 12px; border-radius: 6px; position: relative; overflow: hidden;">
            {img_frente}
            <div style="text-align: center; position: relative; z-index: 1;">
                {img_logo_html}
                <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 14pt; font-weight: bold;">{nome_topo_empresa}</div>
                <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 20pt; font-weight: 900; margin: 5px 0;">{marca_comercial}</div>
                <div style="background-color: #1a365d; color: #fff; font-size: 18pt; font-weight: bold; padding: 6px; border-radius: 4px;">{viscosidade}</div>
                <div style="font-size: 9pt; margin-top: 8px; font-style: italic;">{desc_frente}</div>
                <div style="margin-top: 10px; font-size: 9pt; text-align: left; background-color: #f7fafc; padding: 6px; border: 1px solid #e2e8f0;">
                    <strong>NORMAS:</strong> {" ".join(normas_frente)}
                </div>
            </div>
            <div style="text-align: right; font-weight: bold; margin-top: 15px; font-size: 12pt; position: relative; z-index: 1;">{volume}</div>
        </div>
        
        <!-- CONTRARRÓTULO -->
        <div style="width: 48%; border: 1px solid #cbd5e0; padding: 12px; border-radius: 6px; font-size: 8pt; color: #2d3748; display: flex; flex-direction: column; justify-content: space-between; position: relative; overflow: hidden;">
            {img_tras}
            <div style="position: relative; z-index: 1;">
                <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 11pt; font-weight: bold; color: #1a365d; text-transform: uppercase;">{nome_topo_empresa}</div>
                <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 11pt; font-weight: bold; color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 2px; margin-bottom: 6px;">{marca_comercial} {viscosidade}</div>
                
                <p style="margin: 3px 0;"><strong>NATUREZA DO PRODUTO:</strong> {tipo_oleo}</p>
                <p style="margin: 3px 0;"><strong>CAMPO DE APLICAÇÃO:</strong> {campo_aplicacao}</p>
                <p style="margin: 3px 0;"><strong>ESPECIFICAÇÕES ATENDIDAS:</strong> {normas_tras}</p>
                <p style="margin: 3px 0;"><strong>COMPOSIÇÃO:</strong> {composicao_prod}</p>
                
                <!-- FRASES OBRIGATÓRIAS DE ADVERTÊNCIA -->
                <div style="font-family: {FONTS_DB[fonte_alerta]}; background-color: #ebf8ff; border: 1px solid #bbe3f8; padding: 6px; margin: 8px 0; font-size: 7.5pt; line-height: 1.25; border-radius: 4px;">
                    <p style="margin-bottom: 4px;"><strong>ADVERTÊNCIA:</strong> Não despeje óleo em ralos, esgotos ou curso d'água. A embalagem e o lubrificante são recicláveis, destinem-os a pontos de coletas autorizados conforme resolução do CONAMA nº 362/05.</p>
                    <p style="margin-bottom: 4px;"><strong>PRECAUÇÃO:</strong> Em caso de contato com os olhos ou a pele, lave bem com água. Se ingerido, procure imediatamente um médico. Mantenha fora do alcance de crianças e animais domésticos. O produto pode causar irritação moderada à pele e irritação ocular grave. Evite inalar vapores, névoas ou gases.</p>
                    <p><strong>VALIDADE:</strong> 5 anos desde que armazenado e lacrado em local seco, limpo e protegido do sol.</p>
                </div>
                
                <!-- DADOS DA EMPRESA -->
                <div style="font-size: 7.5pt; line-height: 1.3; color: #1a202c; margin-top: 6px;">
                    <div><strong>PRODUTOR / DETENTOR:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                    <div><strong>ENDEREÇO:</strong> {endereco_produtor}</div>
                    <div><strong>RESPONSÁVEL TÉCNICO:</strong> {quimico_resp} - {crq_num}</div>
                    <div><strong>REGISTRO ANP:</strong> {registro_anp}</div>
                    <div><strong>SAC:</strong> {sac_empresa}</div>
                </div>
            </div>
            
            <!-- RODAPÉ OBRIGATÓRIO -->
            <div style="margin-top: 10px; position: relative; z-index: 1;">
                <div style="background-color: #1a365d; color: #ffffff; text-align: center; font-weight: bold; padding: 5px; font-size: 8pt; text-transform: uppercase; border-radius: 3px; letter-spacing: 0.5px;">
                    SIGA AS RECOMENDAÇÕES DO FABRICANTE DO VEÍCULO
                </div>
            </div>
        </div>
    </div>
</div>
"""

st.components.v1.html(html_croqui, height=480, scrolling=True)

# --- GERAR PDF ---
if st.button("🚀 Gerar Croqui Oficial em PDF", type="primary"):
    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4 landscape; margin: 8mm; }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: {FONTS_DB[fonte_corpo]}; color: #1a202c; padding: 2mm; }}
            .label-table {{ width: 100%; border-collapse: separate; border-spacing: 12px 0; }}
            .label-cell {{ width: 50%; vertical-align: top; }}
            .label-card {{
                border: 3px solid #1a365d; border-radius: 10px; background-color: #ffffff;
                padding: 6mm; min-height: 175mm; position: relative; overflow: hidden;
                display: flex; flex-direction: column; justify-content: space-between;
            }}
            .top-header-brand {{
                font-family: {FONTS_DB[fonte_titulo]}; text-align: center; font-size: 14pt; font-weight: 900; color: #1a365d;
                letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1mm;
            }}
            .front-brand {{ font-family: {FONTS_DB[fonte_titulo]}; font-size: 26pt; font-weight: 900; color: #1a365d; text-align: center; text-transform: uppercase; line-height: 1.1; }}
            .viscosity-badge {{ background: #1a365d; color: #ffffff; text-align: center; font-size: 26pt; font-weight: 900; padding: 4mm 2mm; border-radius: 8px; margin: 3mm 0; }}
            .anp-regulatory-box {{ font-family: {FONTS_DB[fonte_alerta]}; background-color: #ebf8ff; border: 1.5px solid #bbe3f8; padding: 3mm; border-radius: 6px; margin: 3mm 0; font-size: 7.2pt; line-height: 1.25; }}
            .company-info {{ font-size: 7.2pt; color: #1a202c; border-top: 1px dashed #cbd5e0; padding-top: 2mm; margin-top: 2mm; line-height: 1.3; }}
            .footer-recommendation {{ background-color: #1a365d; color: #ffffff; text-align: center; font-weight: bold; padding: 3mm; font-size: 9pt; text-transform: uppercase; border-radius: 4px; letter-spacing: 0.5px; margin-top: 3mm; }}
            .volume-tag {{ position: absolute; bottom: 6mm; right: 6mm; font-size: 15pt; font-weight: 900; color: #1a365d; z-index: 1; }}
        </style>
    </head>
    <body>
        <table class="label-table">
            <tr>
                <!-- FRENTE -->
                <td class="label-cell">
                    <div class="label-card">
                        {img_frente}
                        <div style="position: relative; z-index: 1;">
                            <div style="text-align: center;">{img_logo_html}</div>
                            <div class="top-header-brand">{nome_topo_empresa}</div>
                            <div class="front-brand">{marca_comercial}</div>
                            <div class="viscosity-badge">{viscosidade}</div>
                            <div style="font-size: 9pt; text-align: center; margin-bottom: 3mm;">{desc_frente}</div>
                            <div style="border: 1px solid #cbd5e0; padding: 3mm; font-size: 9pt; background-color: rgba(255,255,255,0.85);">
                                <strong>ESPECIFICAÇÕES:</strong><br>{" ".join(normas_frente)}
                            </div>
                        </div>
                        <div class="volume-tag">{volume}</div>
                    </div>
                </td>
                
                <!-- CONTRARRÓTULO -->
                <td class="label-cell">
                    <div class="label-card">
                        {img_tras}
                        <div style="position: relative; z-index: 1;">
                            <div class="top-header-brand" style="text-align: left;">{nome_topo_empresa}</div>
                            <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 12pt; font-weight: 900; color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 1.5mm; margin-bottom: 3mm;">{marca_comercial} {viscosidade}</div>
                            
                            <div style="font-size: 8pt; line-height: 1.4;">
                                <div><strong>NATUREZA DO PRODUTO:</strong> {tipo_oleo}</div>
                                <div><strong>CAMPO DE APLICAÇÃO:</strong> {campo_aplicacao}</div>
                                <div><strong>ESPECIFICAÇÕES ATENDIDAS:</strong> {normas_tras}</div>
                                <div><strong>COMPOSIÇÃO:</strong> {composicao_prod}</div>
                            </div>
                            
                            <!-- FRASES OBRIGATÓRIAS -->
                            <div class="anp-regulatory-box">
                                <p style="margin-bottom: 1.5mm;"><strong>ADVERTÊNCIA:</strong> Não despeje óleo em ralos, esgotos ou curso d'água. A embalagem e o lubrificante são recicláveis, destinem-os a pontos de coletas autorizados conforme resolução do CONAMA nº 362/05.</p>
                                <p style="margin-bottom: 1.5mm;"><strong>PRECAUÇÃO:</strong> Em caso of contato com os olhos ou a pele, lave bem com água. Se ingerido, procure imediatamente um médico. Mantenha fora do alcance de crianças e animais domésticos. O produto pode causar irritação moderada à pele e irritação ocular grave. Evite inalar vapores, névoas ou gases.</p>
                                <p><strong>VALIDADE:</strong> 5 anos desde que armazenado e lacrado em local seco, limpo e protegido do sol.</p>
                            </div>
                            
                            <!-- DADOS DA EMPRESA -->
                            <div class="company-info">
                                <div><strong>PRODUTOR / DETENTOR:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                                <div><strong>ENDEREÇO:</strong> {endereco_produtor}</div>
                                <div><strong>RESPONSÁVEL TÉCNICO:</strong> {quimico_resp} - {crq_num}</div>
                                <div><strong>REGISTRO ANP:</strong> {registro_anp}</div>
                                <div><strong>SAC:</strong> {sac_empresa}</div>
                            </div>
                        </div>
                        
                        <!-- BARRA DE RECOMENDAÇÃO -->
                        <div style="position: relative; z-index: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2mm;">
                                <div>{img_qr_html}</div>
                                <div style="font-family: monospace; font-size: 10pt; font-weight: bold; border: 1px solid #000; padding: 1.5mm 3mm; background-color: #fff;">|||||||| {codigo_barras_txt} ||||||||</div>
                            </div>
                            <div class="footer-recommendation">
                                SIGA AS RECOMENDAÇÕES DO FABRICANTE DO VEÍCULO
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    output_pdf = "rotulo_oficial.pdf"
    HTML(string=pdf_html).write_pdf(output_pdf)
    
    st.success("✅ PDF regulatório gerado com sucesso!")
    with open(output_pdf, "rb") as f:
        st.download_button(
            label="📥 Baixar Croqui Oficial em PDF",
            data=f,
            file_name=f"croqui_anp_{st.session_state.usuario_logado}{marca_comercial.lower().replace(' ', '')}.pdf",
            mime="application/pdf"
        )
