import base64
import io
import sqlite3
import qrcode
from PIL import Image
import streamlit as st
from weasyprint import HTML

st.set_page_config(page_title="Gerador de Rótulos de Óleo Lubrificante - ANP", layout="wide")

# --- BANCO DE DADOS SQLITE (LOGIN E ISOLAMENTO MULTI-TENANT) ---
def init_db():
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    # Tabela de Usuários e Dados Pessoais da Empresa
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
            logo_base64 TEXT
        )
    ''')
    # Tabela Global de Normas
    c.execute('''
        CREATE TABLE IF NOT EXISTS normas_globais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT,
            norma TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Carga inicial de normas padrão se a tabela estiver vazia
def popular_normas_iniciais():
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM normas_globais")
    if c.fetchone()[0] == 0:
        normas_padrao = [
            ("Linha Leve & Ciclo Otto", "API SP"), ("Linha Leve & Ciclo Otto", "API SN Plus"), ("Linha Leve & Ciclo Otto", "ACEA C3"),
            ("Linha Pesada (Diesel)", "API CK-4"), ("Linha Pesada (Diesel)", "API CI-4 / SL"), ("Linha Pesada (Diesel)", "ACEA E9"),
            ("Motos (2T e 4T)", "JASO MA2"), ("Motos (2T e 4T)", "JASO FD (2T)"),
            ("Transmissão & Hidráulico", "API GL-4"), ("Transmissão & Hidráulico", "API GL-5"), ("Transmissão & Hidráulico", "Dexron VI (ATF)")
        ]
        c.executemany("INSERT OR IGNORE INTO normas_globais (categoria, norma) VALUES (?, ?)", normas_padrao)
        conn.commit()
    conn.close()

popular_normas_iniciais()

# --- SISTEMA DE AUTENTICAÇÃO ---
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

st.sidebar.title("🔐 Autenticação de Usuário")

if st.session_state.usuario_logado is None:
    aba_auth = st.sidebar.radio("Selecione:", ["Login", "Cadastrar Nova Empresa"])
    
    if aba_auth == "Login":
        user_input = st.sidebar.text_input("Usuário / Login:")
        pass_input = st.sidebar.text_input("Senha:", type="password")
        if st.sidebar.button("Entrar"):
            conn = sqlite3.connect("rotulos_app.db")
            c = conn.cursor()
            c.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (user_input, pass_input))
            user_data = c.fetchone()
            conn.close()
            
            if user_data:
                st.session_state.usuario_logado = user_input
                st.sidebar.success(f"Bem-vindo, {user_input}!")
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha incorretos.")
                
    elif aba_auth == "Cadastrar Nova Empresa":
        new_user = st.sidebar.text_input("Novo Usuário / Login:")
        new_pass = st.sidebar.text_input("Nova Senha:", type="password")
        cad_produtor = st.sidebar.text_input("Razão Social Empresa:")
        cad_cnpj = st.sidebar.text_input("CNPJ:")
        if st.sidebar.button("Criar Conta"):
            if new_user and new_pass:
                try:
                    conn = sqlite3.connect("rotulos_app.db")
                    c = conn.cursor()
                    c.execute("INSERT INTO usuarios (username, password, produtor, cnpj) VALUES (?, ?, ?, ?)",
                              (new_user, new_pass, cad_produtor, cad_cnpj))
                    conn.commit()
                    conn.close()
                    st.sidebar.success("Conta criada com sucesso! Faça login.")
                except sqlite3.IntegrityError:
                    st.sidebar.error("Usuário já existe.")
            else:
                st.sidebar.error("Preencha usuário e senha.")
    st.warning("⚠️ Faça login na barra lateral para acessar o gerador de rótulos da sua empresa.")
    st.stop()
else:
    st.sidebar.write(f"Logged in como: *{st.session_state.usuario_logado}*")
    if st.sidebar.button("Sair / Logout"):
        st.session_state.usuario_logado = None
        st.rerun()

# --- CARREGAR DADOS DO USUÁRIO CONECTADO ---
conn = sqlite3.connect("rotulos_app.db")
c = conn.cursor()
c.execute("SELECT produtor, cnpj, endereco, sac, quimico, crq, anp, logo_base64 FROM usuarios WHERE username = ?", (st.session_state.usuario_logado,))
u_data = c.fetchone()
conn.close()

# --- HELPER DE QR CODE ---
def gerar_qr_code_base64(texto):
    if not texto.strip():
        return ""
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- BIBLIOTECA DE FONTES EXPANDIDA ---
FONTS_DB = {
    "Arial / Helvetica (Padrão Limpo)": "Arial, Helvetica, sans-serif",
    "Impact / Heavy (Destaque Robusto)": "Impact, 'Arial Black', sans-serif",
    "Montserrat / Segoe UI (Moderna)": "'Segoe UI', Roboto, Montserrat, sans-serif",
    "Trebuchet MS / Technical (Industrial)": "'Trebuchet MS', sans-serif",
    "Courier New (Técnica / Laboratório)": "'Courier New', Courier, monospace",
    "Georgia / Serif (Clássica Elegante)": "Georgia, 'Times New Roman', serif"
}

st.title("🛢️ Gerador de Rótulos de Lubrificantes (Padrão ANP)")

# --- CONFIGURAÇÕES DO RÓTULO E DESIGN ---
st.subheader("🎨 Estilo, Fontes e Imagens")
col_design1, col_design2, col_design3 = st.columns(3)

with col_design1:
    nome_topo_empresa = st.text_input("Nome/Sigla do Topo (Header):", "IPA")
    fonte_titulo = st.selectbox("Fonte dos Títulos / Marca:", list(FONTS_DB.keys()), index=1)

with col_design2:
    fonte_corpo = st.selectbox("Fonte do Corpo / Especificações:", list(FONTS_DB.keys()), index=0)
    fonte_alerta = st.selectbox("Fonte de Advertências / Alertas:", list(FONTS_DB.keys()), index=4)

with col_design3:
    upload_logo = st.file_uploader("Upload Logotipo da Empresa (PNG/JPG):", type=["png", "jpg", "jpeg"])
    logo_b64 = u_data[7] if u_data and u_data[7] else ""
    if upload_logo is not None:
        image = Image.open(upload_logo)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        logo_b64 = base64.b64encode(buffered.getvalue()).decode()

col_prod, col_tec = st.columns(2)

with col_prod:
    st.subheader("📌 Dados do Produto")
    marca_comercial = st.text_input("Marca Comercial", "MULTI GEAR SUPER")
    viscosidade = st.selectbox("Viscosidade", ["SAE 85W-140", "SAE 15W-40", "SAE 5W-30", "SAE 20W-50", "SAE 75W-90", "ISO VG 68"], index=0)
    tipo_oleo = st.selectbox("Tipo de Base", ["Mineral", "Semissintético", "Sintético"])
    volume = st.selectbox("Volume", ["1 Litro", "4 Litros", "20 Litros", "200 Litros"], index=0)
    desc_frente = st.text_area("Descrição Comercial (Frente):", "Óleo lubrificante mineral para caixas de mudança e eixos diferenciais.")

with col_tec:
    st.subheader("⚙️ Especificações & Recursos Adicionais")
    
    # Carregar Normas Globais do Banco
    conn = sqlite3.connect("rotulos_app.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT norma FROM normas_globais")
    normas_totais = [row[0] for row in c.fetchall()]
    conn.close()
    
    normas_frente = st.multiselect("Normas na Frente:", normas_totais, default=["API GL-5"] if "API GL-5" in normas_totais else [])
    
    # Adicionar Nova Norma Global
    nova_norma = st.text_input("➕ Cadastrar Nova Norma no Banco Global:")
    if st.button("Salvar Norma Global"):
        if nova_norma.strip():
            conn = sqlite3.connect("rotulos_app.db")
            c = conn.cursor()
            try:
                c.execute("INSERT INTO normas_globais (categoria, norma) VALUES (?, ?)", ("Geral", nova_norma.strip()))
                conn.commit()
                st.success(f"Norma '{nova_norma}' adicionada para todos os usuários!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.warning("Esta norma já existe no banco.")
            conn.close()

    codigo_barras_txt = st.text_input("Código de Barras (Texto/EAN-13):", "7891234567890")
    qr_code_link = st.text_input("Link para QR Code (Site/FISPQ/SAC):", "https://www.ipabr.com.br")

# --- DADOS DA EMPRESA (SALVOS EXCLUSIVAMENTE PARA ESTE USUÁRIO) ---
st.subheader("🏢 Dados da Empresa (Exclusivos do seu Usuário)")
col_e1, col_e2 = st.columns(2)

with col_e1:
    produtor = st.text_input("Razão Social:", value=u_data[0] if u_data and u_data[0] else "")
    cnpj_produtor = st.text_input("CNPJ:", value=u_data[1] if u_data and u_data[1] else "")
    endereco_produtor = st.text_input("Endereço:", value=u_data[2] if u_data and u_data[2] else "")
    sac_empresa = st.text_input("SAC / Contato:", value=u_data[3] if u_data and u_data[3] else "")

with col_e2:
    quimico_resp = st.text_input("Químico Responsável:", value=u_data[4] if u_data and u_data[4] else "")
    crq_num = st.text_input("Nº CRQ / Região:", value=u_data[5] if u_data and u_data[5] else "")
    registro_anp = st.text_input("Registro ANP:", value=u_data[6] if u_data and u_data[6] else "")

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
    st.success("Dados da empresa salvos com sucesso no seu perfil!")

# --- PREPARAÇÃO DAS IMAGENS/CÓDIGOS EM BASE64 ---
qr_b64 = gerar_qr_code_base64(qr_code_link)
img_logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height: 45px; max-width: 180px; margin-bottom: 2mm;" />' if logo_b64 else ""
img_qr_html = f'<img src="data:image/png;base64,{qr_b64}" style="width: 65px; height: 65px;" />' if qr_b64 else ""

# --- PRÉ-VISUALIZAÇÃO EM TEMPO REAL ---
st.subheader("👁️ Pré-Visualização em Tempo Real (Croqui)")

html_croqui = f"""
<div style="font-family: {FONTS_DB[fonte_corpo]}; border: 2px solid #1a365d; padding: 15px; border-radius: 8px; background-color: #ffffff; color: #1a365d;">
    <div style="display: flex; justify-content: space-between;">
        <!-- FRENTE -->
        <div style="width: 48%; border: 1px solid #cbd5e0; padding: 12px; border-radius: 6px; position: relative;">
            <div style="text-align: center;">
                {img_logo_html}
                <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 14pt; font-weight: bold;">{nome_topo_empresa}</div>
                <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 20pt; font-weight: 900; margin: 5px 0;">{marca_comercial}</div>
                <div style="background-color: #1a365d; color: #fff; font-size: 18pt; font-weight: bold; padding: 6px; border-radius: 4px;">{viscosidade}</div>
                <div style="font-size: 9pt; margin-top: 8px; font-style: italic;">{desc_frente}</div>
                <div style="margin-top: 10px; font-size: 9pt; text-align: left; background-color: #f7fafc; padding: 6px; border: 1px solid #e2e8f0;">
                    <strong>NORMAS:</strong> {" ".join(normas_frente)}
                </div>
            </div>
            <div style="text-align: right; font-weight: bold; margin-top: 15px; font-size: 12pt;">{volume}</div>
        </div>
        
        <!-- CONTRA-RÓTULO -->
        <div style="width: 48%; border: 1px solid #cbd5e0; padding: 12px; border-radius: 6px; font-size: 8pt; color: #2d3748;">
            <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 11pt; font-weight: bold; color: #1a365d; border-bottom: 1px solid #1a365d;">{marca_comercial} {viscosidade}</div>
            <p style="margin-top: 4px;"><strong>NATUREZA:</strong> {tipo_oleo}</p>
            
            <div style="font-family: {FONTS_DB[fonte_alerta]}; background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 6px; margin: 6px 0; font-size: 7.5pt; line-height: 1.2;">
                <strong>ADVERTÊNCIA:</strong> Não despeje óleo em esgotos. Embalagem reciclável (CONAMA nº 362/05).<br>
                <strong>PRECAUÇÃO:</strong> Evite contato com os olhos e pele. Mantenha fora do alcance de crianças.<br>
                <strong>VALIDADE:</strong> 5 anos.
            </div>
            
            <div style="font-size: 7.5pt; line-height: 1.3;">
                <div><strong>PRODUTOR:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                <div><strong>RESP. TÉCNICO:</strong> {quimico_resp} - {crq_num} | <strong>ANP:</strong> {registro_anp}</div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                <div>{img_qr_html}</div>
                <div style="font-family: monospace; font-size: 10pt; font-weight: bold; border: 1px solid #000; padding: 3px 8px;">||||||| {codigo_barras_txt} |||||||</div>
            </div>
        </div>
    </div>
</div>
"""

st.components.v1.html(html_croqui, height=380, scrolling=True)

# --- BOTÃO DE GERAR PDF ---
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
                padding: 6mm; min-height: 175mm; position: relative;
                display: flex; flex-direction: column; justify-content: space-between;
            }}
            .top-header-brand {{
                font-family: {FONTS_DB[fonte_titulo]}; text-align: center; font-size: 14pt; font-weight: 900; color: #1a365d;
                letter-spacing: 2px; text-transform: uppercase; margin-bottom: 1mm;
            }}
            .front-brand {{ font-family: {FONTS_DB[fonte_titulo]}; font-size: 26pt; font-weight: 900; color: #1a365d; text-align: center; text-transform: uppercase; line-height: 1.1; }}
            .viscosity-badge {{ background: #1a365d; color: #ffffff; text-align: center; font-size: 26pt; font-weight: 900; padding: 4mm 2mm; border-radius: 8px; margin: 3mm 0; }}
            .anp-regulatory-box {{ font-family: {FONTS_DB[fonte_alerta]}; background-color: #f8fafc; border: 1.5px solid #cbd5e1; padding: 2.5mm; border-radius: 6px; margin: 2.5mm 0; font-size: 7pt; line-height: 1.25; }}
            .company-info {{ font-size: 7pt; color: #475569; border-top: 1px dashed #cbd5e0; padding-top: 2mm; margin-top: 2mm; }}
            .volume-tag {{ position: absolute; bottom: 6mm; right: 6mm; font-size: 15pt; font-weight: 900; color: #1a365d; }}
        </style>
    </head>
    <body>
        <table class="label-table">
            <tr>
                <td class="label-cell">
                    <div class="label-card">
                        <div>
                            <div style="text-align: center;">{img_logo_html}</div>
                            <div class="top-header-brand">{nome_topo_empresa}</div>
                            <div class="front-brand">{marca_comercial}</div>
                            <div class="viscosity-badge">{viscosidade}</div>
                            <div style="font-size: 9pt; text-align: center; margin-bottom: 3mm;">{desc_frente}</div>
                            <div style="border: 1px solid #cbd5e0; padding: 3mm; font-size: 9pt;">
                                <strong>ESPECIFICAÇÕES:</strong><br>{" ".join(normas_frente)}
                            </div>
                        </div>
                        <div class="volume-tag">{volume}</div>
                    </div>
                </td>
                <td class="label-cell">
                    <div class="label-card">
                        <div>
                            <div class="top-header-brand" style="text-align: left;">{nome_topo_empresa}</div>
                            <div style="font-family: {FONTS_DB[fonte_titulo]}; font-size: 12pt; font-weight: 900; color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 1.5mm; margin-bottom: 3mm;">{marca_comercial} {viscosidade}</div>
                            <div style="font-size: 8pt; margin-bottom: 2mm;"><strong>NATUREZA DO PRODUTO:</strong> {tipo_oleo}</div>
                            
                            <div class="anp-regulatory-box">
                                <p style="margin-bottom: 1.5mm;"><strong>ADVERTÊNCIA:</strong> Não despeje óleo em ralos, esgotos ou curso d'água. A embalagem e o lubrificante são recicláveis, destinem-os a pontos de coletas autorizados conforme resolução do CONAMA nº 362/05.</p>
                                <p style="margin-bottom: 1.5mm;"><strong>PRECAUÇÃO:</strong> Em caso de contato com os olhos ou a pele, lave bem com água. Mantenha fora do alcance de crianças.</p>
                                <p><strong>VALIDADE:</strong> 5 anos desde que armazenado em local seco e sob o sol.</p>
                            </div>
                            
                            <div class="company-info">
                                <div><strong>PRODUTOR:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                                <div><strong>ENDEREÇO:</strong> {endereco_produtor}</div>
                                <div><strong>RESPONSÁVEL TÉCNICO:</strong> {quimico_resp} - {crq_num}</div>
                                <div><strong>REGISTRO ANP:</strong> {registro_anp} | <strong>SAC:</strong> {sac_empresa}</div>
                            </div>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3mm;">
                            <div>{img_qr_html}</div>
                            <div style="font-family: monospace; font-size: 11pt; font-weight: bold; border: 1px solid #000; padding: 2mm 4mm;">|||||||| {codigo_barras_txt} ||||||||</div>
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
