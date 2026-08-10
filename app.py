import streamlit as st
from weasyprint import HTML

st.set_page_config(page_title="Gerador de Rótulos de Óleo Lubrificante", layout="wide")

st.title("🛢️ Gerador de Rótulos e Contra-Rótulos de Lubrificantes")
st.markdown("Preencha os campos abaixo. As frases de segurança e legislação ANP/CONAMA são mantidas automaticamente.")

# --- BARRA LATERAL: SELEÇÃO DE TEMPLATE ---
st.sidebar.header("🎨 Configuração de Layout")
modelo_selecionado = st.sidebar.selectbox(
    "Selecione o Modelo de Rótulo:",
    [
        "Modelo Padrão Lubrificantes (Frente + Contra-Rótulo)",
        "Modelo IPA / Petroquímica Apollo (Estilo Exemplo)",
        "Modelo Compacto / Minimalista"
    ]
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
    marca_comercial = st.text_input("Marca Comercial / Linha", "SINTHETIC SUPER")
    viscosidade = st.selectbox("Viscosidade (SAE / ISO)", VISCOSIDADES, index=4)
    tipo_oleo = st.selectbox("Tipo de Base", ["Sintético", "Semissintético", "Mineral"])
    volume = st.selectbox("Volume da Embalagem", VOLUMES, index=1)
    
    linha_produto = st.selectbox("Linha / Aplicação Recomendada", [
        "Linha Leve (Carro)", "Linha Pesada (Caminhão)", "Moto (Motocicleta)", 
        "2 Tempos (Roçadeira/Motor)", "Gear (Engrenagem)", "ATF (Câmbio)", 
        "TASA (Volante/Direção)", "Marítimo (Barco)"
    ])
    
    desc_opcional = st.text_area(
        "Descrição Opcional na Frente / Aplicação", 
        "Formulado para motores de veículos leves movidos a flex e GNV."
    )

with col2:
    st.subheader("⚙️ Especificações & Contra-Rótulo")
    
    cat_normas = st.selectbox("Categoria de Normas no Banco", list(NORMAS_DB.keys()))
    
    # Opções dinâmicas para evitar erro ao trocar de categoria
    opcoes_disponiveis = NORMAS_DB[cat_normas]
    
    normas_frente = st.multiselect(
        "Normas para aparecer na FRENTE", 
        opcoes_disponiveis, 
        default=[opcoes_disponiveis[0]]
    )
    normas_costas = st.multiselect(
        "Normas Adicionais para o CONTRA-RÓTULO", 
        opcoes_disponiveis, 
        default=[opcoes_disponiveis[0]]
    )
    
    campo_aplicacao = st.text_input("Campo de Aplicação:", "Motores de veículos leves movidos a flex e GNV")
    
    beneficios_txt = st.text_area(
        "Benefícios (Exclusivo Modelo IPA):",
        "Óleo lubrificante sintético formulado para motores leves. Suas principais características incluem excelente proteção contra desgaste e corrosão e controle de formação de depósitos no motor, garantindo boa limpeza e durabilidade."
    )

st.subheader("🏢 Dados da Empresa (Campos Editáveis)")
col_emp1, col_emp2 = st.columns(2)

with col_emp1:
    produtor = st.text_input("Produtor", "Indústria Petroquímica Apollo")
    cnpj_produtor = st.text_input("CNPJ Produtor", "37.413.384/0001-84")
    endereco_produtor = st.text_input("Endereço", "Av. Adroaldo José Bombardelli, 1835 - Ponta Grossa/PR")
    sac_empresa = st.text_input("SAC / Contato", "+55 (42) 2702-0500 - www.ipabr.com.br")

with col_emp2:
    quimico_resp = st.text_input("Químico Responsável", "Rafael Costa da Cunha")
    crq_num = st.text_input("Nº CRQ / Região", "CRQ IX: 09303534")
    registro_anp = st.text_input("Registro ANP", "24076")

# --- LÓGICA DE COMPOSIÇÃO ---
if tipo_oleo == "Sintético":
    texto_frente_tipo = "ÓLEO LUBRIFICANTE SINTÉTICO"
    composicao_contra = "Óleo sintético com aditivos antidesgaste, antioxidante, anticorrosivo, antiespumante, detergente, dispersante, melhorador de ponto de fluidez e melhorador de índice de viscosidade."
elif tipo_oleo == "Mineral":
    texto_frente_tipo = "ÓLEO LUBRIFICANTE MINERAL"
    composicao_contra = "Óleo básico mineral e pacote de aditivos de alta performance."
else:
    texto_frente_tipo = "ÓLEO LUBRIFICANTE SEMISSINTÉTICO"
    composicao_contra = "Óleos básicos mineral e sintético com aditivos multifuncionais."

# --- BOTÃO DE GERAR PDF ---
if st.button("🚀 Gerar PDF do Rótulo", type="primary"):
    
    str_normas_frente = " ".join(normas_frente) if normas_frente else ""
    str_normas_costas = f"{viscosidade} - {' '.join(normas_costas)}" if normas_costas else viscosidade

    # -------------------------------------------------------------
    # OPT 1: MODELO OFICIAL CEBR / PADRÃO
    # -------------------------------------------------------------
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
                    <td class="label-cell">
                        <div class="label-card">
                            <div class="front-brand">{marca_comercial}</div>
                            <div class="viscosity-badge">{viscosidade}</div>
                            <div class="type-pill">{texto_frente_tipo}</div>
                            <div class="front-desc">{desc_opcional}</div>
                            <div class="specs-box-front"><strong>ESPECIFICAÇÕES:</strong><br>{str_normas_frente}</div>
                            <div class="volume-tag">{volume}</div>
                        </div>
                    </td>
                    <td class="label-cell">
                        <div class="label-card">
                            <div class="back-title">{marca_comercial} {viscosidade}</div>
                            <div class="field-group"><span class="field-label">NATUREZA DO PRODUTO:</span> {tipo_oleo}</div>
                            <div class="field-group"><span class="field-label">CAMPO DE APLICAÇÃO:</span> {campo_aplicacao}</div>
                            <div class="field-group"><span class="field-label">ESPECIFICAÇÕES ATENDIDAS:</span> {str_normas_costas}</div>
                            <div class="field-group"><span class="field-label">COMPOSIÇÃO:</span> {composicao_contra}</div>
                            <div class="mandatory-section"><strong>MEIO AMBIENTE / CONAMA:</strong> Resolução CONAMA nº 362/05.</div>
                            <div class="company-info">
                                <div><strong>Produtor:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                                <div><strong>Endereço:</strong> {endereco_produtor}</div>
                                <div><strong>Químico Resp.:</strong> {quimico_resp} - {crq_num}</div>
                                <div><strong>ANP:</strong> {registro_anp}</div>
                            </div>
                            <div class="footer-banner">SIGA AS RECOMENDAÇÕES DO FABRICANTE DO VEÍCULO</div>
                        </div>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    # -------------------------------------------------------------
    # OPT 2: MODELO IPA / PETROQUÍMICA APOLLO
    # -------------------------------------------------------------
    elif modelo_selecionado == "Modelo IPA / Petroquímica Apollo (Estilo Exemplo)":
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: 100mm 150mm; margin: 0; }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Helvetica', 'Arial', sans-serif; }}
                body {{ background-color: #1e2229; color: #ffffff; padding: 4mm; }}
                .label-container {{
                    border: 2px solid #333945; border-radius: 8px; background-color: #181b20;
                    padding: 5mm; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
                }}
                .header-brand {{ text-align: center; border-bottom: 2px solid #00a651; padding-bottom: 3mm; }}
                .company-name {{ font-size: 8pt; font-weight: bold; letter-spacing: 1px; color: #a0aec0; text-transform: uppercase; }}
                .product-line {{ font-size: 18pt; font-weight: 900; color: #ffffff; margin: 1mm 0; text-transform: uppercase; }}
                .viscosity-box {{
                    background-color: #00a651; color: #ffffff; font-size: 16pt; font-weight: 900;
                    text-align: center; padding: 2mm; border-radius: 4px; margin: 2mm 0;
                }}
                .sub-info {{ font-size: 8.5pt; text-align: center; color: #e2e8f0; font-weight: bold; margin-bottom: 3mm; }}
                .section-title {{ font-size: 7.5pt; font-weight: bold; color: #00a651; text-transform: uppercase; margin-top: 2mm; border-bottom: 1px solid #2d3748; }}
                .text-body {{ font-size: 6.5pt; color: #cbd5e1; margin-top: 1mm; text-align: justify; line-height: 1.2; }}
                .info-grid {{ font-size: 6.5pt; margin-top: 2mm; background-color: #0f1115; padding: 2mm; border-radius: 4px; border: 1px solid #2d3748; }}
                .info-grid div {{ margin-bottom: 1px; }}
                .footer-ipa {{ text-align: center; font-size: 6pt; color: #a0aec0; border-top: 1px solid #2d3748; padding-top: 2mm; margin-top: 2mm; }}
                .volume-badge {{ float: right; font-size: 10pt; font-weight: bold; color: #00a651; }}
            </style>
        </head>
        <body>
            <div class="label-container">
                <div>
                    <div class="header-brand">
                        <div class="company-name">{produtor}</div>
                        <div class="product-line">{marca_comercial}</div>
                    </div>
                    
                    <div class="viscosity-box">{viscosidade} | {str_normas_frente}</div>
                    <div class="sub-info">{texto_frente_tipo} <span class="volume-badge">Conteúdo {volume}</span></div>
                    
                    <div class="text-body" style="text-align: center; font-style: italic; color: #94a3b8;">
                        {desc_opcional}
                    </div>

                    <div class="section-title">BENEFÍCIOS:</div>
                    <div class="text-body">{beneficios_txt}</div>

                    <div class="section-title">COMPOSIÇÃO:</div>
                    <div class="text-body">{composicao_contra}</div>

                    <div class="section-title">PRECAUÇÕES E ATENÇÃO:</div>
                    <div class="text-body">
                        Mantenha fora do alcance de crianças e animais domésticos. Evite contato com olhos e pele. Preserve o meio ambiente. Os lubrificantes e suas embalagens são recicláveis conforme Resolução CONAMA.
                    </div>
                </div>

                <div>
                    <div class="info-grid">
                        <div><strong>NATUREZA DO PRODUTO:</strong> {tipo_oleo} | <strong>ANP:</strong> {registro_anp}</div>
                        <div><strong>ESPECIFICAÇÕES:</strong> {str_normas_costas}</div>
                        <div><strong>Produtor:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                        <div><strong>Endereço:</strong> {endereco_produtor}</div>
                        <div><strong>Resp. Técnico:</strong> {quimico_resp} - {crq_num}</div>
                    </div>

                    <div class="footer-ipa">
                        SAC: {sac_empresa} | Indústria Brasileira
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    # -------------------------------------------------------------
    # OPT 3: MODELO COMPACTO
    # -------------------------------------------------------------
    else:
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><style>body {{ font-family: monospace; font-size: 9pt; }}</style></head>
        <body>
            <h2>{marca_comercial} - {viscosidade}</h2>
            <p><strong>TIPO:</strong> {tipo_oleo}</p>
            <p><strong>NORMAS:</strong> {str_normas_frente}</p>
            <p><strong>PRODUTOR:</strong> {produtor}</p>
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
