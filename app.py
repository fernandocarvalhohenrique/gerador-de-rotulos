import streamlit as st
from weasyprint import HTML

st.set_page_config(page_title="Gerador de Rótulos de Óleo Lubrificante", layout="wide")

st.title("🛢️ Gerador de Rótulos e Contra-Rótulos de Lubrificantes")
st.markdown("Preencha os campos abaixo. As frases de segurança e legislação ANP/CONAMA são mantidas automaticamente.")

# --- BARRA LATERAL: SELEÇÃO DE TEMPLATE ---
st.sidebar.header("🎨 Configuração de Layout")
modelo_selecionado = st.sidebar.selectbox(
    "Selecione o Modelo de Rótulo:",
    ["Modelo Padrão Lubrificantes (Frente + Contra-Rótulo)", "Modelo Compacto / Minimalista"]
)

# --- BANCO DE DADOS DE NORMAS ---
NORMAS_DB = {
    "Linha Leve & Ciclo Otto (Gasolina/Flex/GNV)": [
        "API SP", "API SN Plus", "API SN", "API SM", "API SL",
        "ACEA A3/B4", "ACEA A5/B5", "ACEA C2", "ACEA C3", "ACEA C5", "ACEA C6",
        "VW 502 00 / 505 00", "VW 508 00 / 509 00", "GM Dexos 1 Gen 3", "GM Dexos 2",
        "MB 229.3", "MB 229.5", "MB 229.51", "BMW Longlife-01", "BMW Longlife-04",
        "FIAT 9.55535-GS1", "Ford WSS-M2C948-B", "Porsche A40", "Renault RN0700 / RN0710"
    ],
    "Linha Pesada (Diesel)": [
        "API CK-4", "API CJ-4", "API CI-4 / SL", "API CH-4",
        "ACEA E4", "ACEA E6", "ACEA E7", "ACEA E9", "ACEA E11",
        "MB 228.31", "MB 228.51", "Volvo VDS-4.5", "MAN M 3775", "Cummins CES 20086", "Scania LDF-4"
    ],
    "Motos (2T e 4T)": [
        "JASO MA2", "JASO MA", "JASO MB", "API SL (Moto)",
        "JASO FD (2T)", "JASO FC (2T)", "ISO-L-EGD (2T)", "API TC (2T)"
    ],
    "Transmissão, Engrenagens e Hidráulico (Gear, ATF, TASA)": [
        "API GL-4", "API GL-5", "SAE J306",
        "Dexron VI (ATF)", "Dexron III-H (ATF)", "Mercon LV", "Allison C4",
        "Type A Suffix A (TASA)", "ZF TE-ML 02L / 11B / 16A", "DIN 51524 Part 2 (HLP)"
    ]
}

VISCOSIDADES = [
    "SAE 0W-16", "SAE 0W-20", "SAE 0W-30", "SAE 5W-20", "SAE 5W-30", "SAE 5W-40",
    "SAE 10W-30", "SAE 10W-40", "SAE 15W-40", "SAE 20W-50",
    "SAE 30", "SAE 40", "SAE 50",
    "SAE 75W-80", "SAE 75W-90", "SAE 80W-90", "SAE 85W-140", "ISO VG 68", "ISO VG 100"
]

VOLUMES = ["500 mL", "1 Litro", "4 Litros", "5 Litros", "20 Litros", "200 Litros"]

# --- DADOS DE ENTRADA ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Informações da Frente do Rótulo")
    marca_comercial = st.text_input("Marca Comercial / Nome do Produto", "GYN-LUB")
    viscosidade = st.selectbox("Viscosidade (SAE / ISO)", VISCOSIDADES, index=7)
    tipo_oleo = st.selectbox("Tipo de Base", ["Mineral", "Semissintético", "Sintético"])
    volume = st.selectbox("Volume da Embalagem", VOLUMES, index=1)
    
    linha_produto = st.selectbox("Linha / Marca d'água de Fundo", [
        "Linha Leve (Carro)", "Linha Pesada (Caminhão)", "Moto (Motocicleta)", 
        "2 Tempos (Roçadeira/Motor)", "Gear (Engrenagem)", "ATF (Câmbio)", 
        "TASA (Volante/Direção)", "Marítimo (Barco)"
    ])
    
    desc_opcional = st.text_area("Descrição Opcional na Frente (Melhoria Visual)", 
                                 "Óleo lubrificante de alta performance desenvolvido para proporcionar máxima proteção e durabilidade ao motor.")

with col2:
    st.subheader("⚙️ Especificações & Contra-Rótulo")
    
    cat_normas = st.selectbox("Categoria de Normas no Banco", list(NORMAS_DB.keys()))
    normas_frente = st.multiselect("Normas para aparecer na FRENTE", NORMAS_DB[cat_normas], default=NORMAS_DB[cat_normas][:2])
    normas_costas = st.multiselect("Normas Adicionais para o CONTRA-RÓTULO", NORMAS_DB[cat_normas], default=NORMAS_DB[cat_normas][:4])
    
    aplicacao_padrao = st.selectbox("Campo de Aplicação (Sugestões)", [
        "Veículos a Gasolina, Flex, Etanol e GNV (Linha Leve)",
        "Motores Diesel de Alta Carga (Linha Pesada)",
        "Motocicletas 4 Tempos",
        "Engrenagens Hipóides e Caixas de Mudança",
        "Transmissões Automáticas e Direções Hidráulicas",
        "Outro (Digitar personalizado)"
    ])
    if aplicacao_padrao == "Outro (Digitar personalizado)":
        campo_aplicacao = st.text_input("Digite o Campo de Aplicação Customizado:")
    else:
        campo_aplicacao = aplicacao_padrao

st.subheader("🏢 Dados da Empresa (Campos Editáveis)")
col_emp1, col_emp2 = st.columns(2)

with col_emp1:
    produtor = st.text_input("Produtor", "LUBRIFICANTES FENIX LTDA")
    cnpj_produtor = st.text_input("CNPJ Produtor", "59.723.874/0001-10")
    endereco_produtor = st.text_input("Endereço", "Av. Paris, 3716 - Centro Industrial - Paulínia/SP")
    detentor_registro = st.text_input("Detentor do Registro", "Guia Lub Lubrificantes Ltda")

with col_emp2:
    quimico_resp = st.text_input("Químico Responsável", "Gleyson Afonso Rodrigues de Faria")
    crq_num = st.text_input("Nº CRQ / Região", "CRQ nº 12201185 XII Região")
    registro_anp = st.text_input("Registro do Produto ANP (deixe em branco se não houver)", "21849")
    fornecedor_marca = st.text_input("Marca do Fornecedor (Opcional)", "Distribuído por GuiaLub")

# --- LÓGICA DE AUTOMAÇÃO DE COMPOSIÇÃO ---
if tipo_oleo == "Mineral":
    texto_frente_tipo = "ÓLEO MINERAL"
    composicao_contra = "Óleo básico mineral e pacote de aditivos."
elif tipo_oleo == "Sintético":
    texto_frente_tipo = "ÓLEO SINTÉTICO"
    composicao_contra = "Óleos básicos sintéticos e aditivos multifuncionais."
else: # Semissintético
    texto_frente_tipo = "ÓLEO SEMISSINTÉTICO"
    composicao_contra = "Óleo básico mineral e sintético e pacote de aditivos."

# --- SVGs PARA MARCA D'ÁGUA ---
WATERMARKS = {
    "Linha Leve (Carro)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.85 7h10.29l1.04 3H5.81l1.04-3zM19 17H5v-4h14v4z"/><circle cx="7.5" cy="14.5" r="1.5"/><circle cx="16.5" cy="14.5" r="1.5"/></svg>',
    "Linha Pesada (Caminhão)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M20 8h-3V4H1v13h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-1.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM17 12V9.5h2.47l1.88 2.5H17z"/></svg>',
    "Gear (Engrenagem)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M19.43 12.98c.04-.32.07-.64.07-.98s-.03-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64l2.11 1.65c-.04.32-.07.65-.07.98s.03.66.07.98l-2.11 1.65c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.03.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1c.23.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.65zM12 15.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"/></svg>',
    "Moto (Motocicleta)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M19.44 9.03L15.41 5H11v2h3.59l2 2H5c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5c0-.35-.04-.69-.11-1.01L13 14v-2l-3.32-2H6.83c.36-.6.98-1 1.67-1h7.09l2.85 2.85c.39.39 1.02.39 1.41 0l1.41-1.41c.39-.39.39-1.02 0-1.41zM5 17c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm14-8c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/></svg>',
    "2 Tempos (Roçadeira/Motor)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    "ATF (Câmbio)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    "TASA (Volante/Direção)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-3.87 2.76-7.1 6.44-7.82l1.56 4.68V12h0v3h2v-3l1.56-4.68C17.24 4.9 20 8.13 20 12c0 4.41-3.59 8-8 8z"/></svg>',
    "Marítimo (Barco)": '<svg viewBox="0 0 24 24"><path fill="#000" d="M20 21c-1.39 0-2.78-.47-4-1.32-2.44 1.71-5.56 1.71-8 0C6.78 20.53 5.39 21 4 21H2v2h2c1.38 0 2.74-.35 4-.99 2.52 1.29 5.48 1.29 8 0 1.26.64 2.62.99 4 .99h2v-2h-2zM3.95 19H4c1.1 0 2.2-.29 3.2-.85 2.48 1.39 5.12 1.39 7.6 0 1 .56 2.1.85 3.2.85h.05l1.9-5.7-1.95-.65V11l-6-4-6 4v1.8l-1.95.65L3.95 19z"/></svg>'
}

selected_watermark = WATERMARKS.get(linha_produto, WATERMARKS["Linha Leve (Carro)"])

# --- BOTÃO DE GERAR PDF ---
if st.button("🚀 Gerar PDF do Rótulo", type="primary"):
    
    str_normas_frente = " | ".join(normas_frente) if normas_frente else "Conforme especificações técnicas"
    str_normas_costas = ", ".join(normas_costas) if normas_costas else "API / ACEA"
    registro_anp_txt = f"Registro ANP: {registro_anp}" if registro_anp.strip() else "Produto isento ou registro em andamento"
    fornecedor_txt = f"<div><strong>Fornecedor:</strong> {fornecedor_marca}</div>" if fornecedor_marca.strip() else ""

    # TEMPLATE 1: SEU MODELO ORIGINAL COMPLETO (SUL/NORMA ANP/GHS)
    if modelo_selecionado == "Modelo Padrão Lubrificantes (Frente + Contra-Rótulo)":
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4 portrait; margin: 12mm; background-color: #f4f6f8; }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }}
                body {{ color: #2c3e50; line-height: 1.3; }}
                .label-table {{ width: 100%; border-collapse: separate; border-spacing: 15px 0; }}
                .label-cell {{ width: 50%; vertical-align: top; }}
                .label-card {{
                    border: 3px solid #1a365d; border-radius: 12px; background-color: #ffffff;
                    padding: 15px; position: relative; min-height: 520px;
                }}
                .watermark {{
                    position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%);
                    opacity: 0.06; width: 75%; pointer-events: none; z-index: 0;
                }}
                .card-content {{ position: relative; z-index: 1; }}
                .front-brand {{ font-size: 24pt; font-weight: 900; color: #1a365d; text-align: center; text-transform: uppercase; }}
                .viscosity-badge {{
                    background: linear-gradient(135deg, #1a365d, #2b6cb0); color: white;
                    text-align: center; font-size: 26pt; font-weight: bold; padding: 8px; border-radius: 8px; margin: 15px 0;
                }}
                .type-pill {{
                    background-color: #e2e8f0; color: #2d3748; text-align: center; font-size: 11pt;
                    font-weight: bold; padding: 5px; border-radius: 20px; text-transform: uppercase; margin-bottom: 12px;
                }}
                .front-desc {{ font-size: 9pt; text-align: center; color: #4a5568; margin-bottom: 15px; }}
                .specs-box-front {{ border: 1px solid #cbd5e0; background-color: #f7fafc; padding: 8px; border-radius: 6px; font-size: 8.5pt; }}
                .volume-tag {{ position: absolute; bottom: 15px; right: 15px; font-size: 15pt; font-weight: 900; color: #1a365d; }}
                
                .back-title {{ font-size: 11pt; font-weight: bold; color: #1a365d; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 8px; text-transform: uppercase; }}
                .field-group {{ margin-bottom: 5px; font-size: 7.5pt; }}
                .field-label {{ font-weight: bold; color: #2d3748; }}
                .mandatory-section {{ background-color: #fffaf0; border: 1px solid #feebc8; padding: 5px; border-radius: 4px; margin-top: 6px; font-size: 6.5pt; color: #744210; }}
                .company-info {{ font-size: 6.5pt; color: #4a5568; border-top: 1px dashed #cbd5e0; padding-top: 5px; margin-top: 6px; }}
                .footer-banner {{ background-color: #1a365d; color: white; text-align: center; font-weight: bold; font-size: 6.8pt; padding: 4px; border-radius: 4px; margin-top: 6px; }}
            </style>
        </head>
        <body>
            <table class="label-table">
                <tr>
                    <!-- FRENTE -->
                    <td class="label-cell">
                        <div class="label-card">
                            <div class="watermark">{selected_watermark}</div>
                            <div class="card-content">
                                <div class="front-brand">{marca_comercial}</div>
                                <div class="viscosity-badge">{viscosidade}</div>
                                <div class="type-pill">{texto_frente_tipo}</div>
                                <div class="front-desc">{desc_opcional}</div>
                                <div class="specs-box-front">
                                    <strong>ESPECIFICAÇÕES:</strong><br>{str_normas_frente}
                                </div>
                                <div class="volume-tag">{volume}</div>
                            </div>
                        </div>
                    </td>
                    <!-- CONTRA-RÓTULO -->
                    <td class="label-cell">
                        <div class="label-card">
                            <div class="card-content">
                                <div class="back-title">{marca_comercial} {viscosidade} {texto_frente_tipo}</div>
                                <div class="field-group"><span class="field-label">NATUREZA DO PRODUTO:</span> {tipo_oleo}</div>
                                <div class="field-group"><span class="field-label">CAMPO DE APLICAÇÃO:</span> {campo_aplicacao}</div>
                                <div class="field-group"><span class="field-label">ESPECIFICAÇÕES ATENDIDAS:</span> {str_normas_costas}</div>
                                <div class="field-group"><span class="field-label">COMPOSIÇÃO:</span> {composicao_contra}</div>
                                
                                <div class="mandatory-section">
                                    <strong>MEIO AMBIENTE / CONAMA:</strong> Não despeje óleo em ralos ou cursos d'água. A embalagem e o lubrificante são recicláveis. Destine-os aos pontos de coleta autorizados conforme Resolução CONAMA nº 362/05.
                                </div>
                                <div class="mandatory-section" style="background-color: #f7fafc; border-color: #e2e8f0; color: #2d3748;">
                                    <strong>PRECAUÇÕES:</strong> Lavar bem em caso de contato com os olhos ou a pele. Se ingerido, procurar um médico. Manter fora do alcance de crianças e animais domésticos.
                                </div>
                                
                                <div class="company-info">
                                    <div><strong>Produtor:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                                    <div><strong>Endereço:</strong> {endereco_produtor}</div>
                                    <div><strong>Detentor do Registro:</strong> {detentor_registro}</div>
                                    <div><strong>Químico Resp.:</strong> {quimico_resp} - {crq_num}</div>
                                    <div><strong>{registro_anp_txt}</strong> | <strong>Validade:</strong> Indeterminada</div>
                                    <div><strong>Lote / Fab:</strong> Vide Embalagem</div>
                                    {fornecedor_txt}
                                </div>
                                
                                <div class="footer-banner">SIGA AS RECOMENDAÇÕES DO FABRICANTE DO VEÍCULO</div>
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    # TEMPLATE 2: OPÇÃO ALTERNATIVA (EXEMPLO COMPACTO)
    else:
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4 portrait; margin: 15mm; }}
                body {{ font-family: 'Courier New', monospace; font-size: 9pt; line-height: 1.4; }}
                .box {{ border: 2px solid #000; padding: 10px; margin-bottom: 10px; }}
                .title {{ font-size: 16pt; font-weight: bold; text-align: center; border-bottom: 1px solid #000; padding-bottom: 5px; }}
            </style>
        </head>
        <body>
            <div class="box">
                <div class="title">{marca_comercial} - {viscosidade}</div>
                <p><strong>TIPO:</strong> {texto_frente_tipo}</p>
                <p><strong>VOLUME:</strong> {volume}</p>
                <p><strong>ESPECIFICAÇÕES:</strong> {str_normas_frente}</p>
            </div>
            <div class="box">
                <p><strong>APLICAÇÃO:</strong> {campo_aplicacao}</p>
                <p><strong>PRODUTOR:</strong> {produtor} ({cnpj_produtor})</p>
                <p><strong>RESPONSÁVEL TÉCNICO:</strong> {quimico_resp} - {crq_num}</p>
            </div>
        </body>
        </html>
        """
    
    # Gerar arquivo PDF
    output_pdf = "rotulo_gerado.pdf"
    HTML(string=html_template).write_pdf(output_pdf)
    
    st.success("✅ Rótulo gerado com sucesso!")
    with open(output_pdf, "rb") as file:
        st.download_button(
            label="📥 Baixar Rótulo em PDF",
            data=file,
            file_name=f"rotulo_{marca_comercial.lower().replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
