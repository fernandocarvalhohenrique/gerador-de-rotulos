import streamlit as st
from weasyprint import HTML

st.set_page_config(page_title="Gerador de Rótulos de Óleo Lubrificante - ANP", layout="wide")

st.title("🛢️ Gerador de Rótulos e Contra-Rótulos de Lubrificantes (Padrão ANP)")
st.markdown("Plataforma de geração de croquis regulatórios para submissão à ANP e gráfica.")

# --- BARRA LATERAL: SELEÇÃO DE TEMPLATE ---
st.sidebar.header("🎨 Configuração de Layout")
modelo_selecionado = st.sidebar.selectbox(
    "Selecione o Modelo de Rótulo:",
    [
        "Modelo Padrão Lubrificantes (Frente + Contra-Rótulo)",
        "Modelo IPA / Petroquímica Apollo (Frente + Contra-Rótulo)",
        "Modelo Compacto / Minimalista"
    ]
)

# --- INICIALIZAÇÃO DO BANCO DE NORMAS NA SESSÃO ---
if "normas_db" not in st.session_state:
    st.session_state.normas_db = {
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
            "Type A Suffix A (TASA)", "ZF TE-ML 02L / 11B / 16A", "ZF TE-ML 08", "ZF TE-ML 07A", "DIN 51524 Part 2 (HLP)"
        ]
    }

# --- DICIONÁRIO DE ÍCONES VETORIAIS (SVG) ---
ICON_SVG_DB = {
    "Gear (Engrenagem)": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    "Linha Leve (Carro)": '<svg width="50" height="40" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle></svg>',
    "Linha Pesada (Caminhão)": '<svg width="50" height="40" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>',
    "Moto (Motocicleta)": '<svg width="50" height="40" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="16" r="3"></circle><circle cx="19" cy="16" r="3"></circle><path d="M12 17V11L8 6H4"></path><path d="M12 11h6l3-5"></path></svg>',
    "ATF (Câmbio Automático)": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>',
    "TASA (Volante/Direção)": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"></circle><path d="M12 3v18"></path><path d="M12 12l6 4"></path><path d="M12 12l-6 4"></path></svg>',
    "2 Tempos (Roçadeira/Motor)": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
    "Marítimo (Barco)": '<svg width="50" height="40" viewBox="0 0 24 24" fill="none" stroke="#1a365d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9 1.5 5.5 3.38 6"></path><path d="M12 10V4.5M12 2l3 2.5H9L12 2z"></path></svg>'
}

# --- BARRA LATERAL: CADASTRAR NOVA NORMA ---
with st.sidebar.expander("➕ Cadastrar Nova Norma no Banco"):
    cat_destino = st.selectbox("Categoria para a Nova Norma:", list(st.session_state.normas_db.keys()))
    nova_norma_input = st.text_input("Nome da Norma / Especificação (ex: ZF TE-ML 08):")
    if st.button("💾 Salvar Norma no Banco"):
        if nova_norma_input.strip() != "":
            norma_limpa = nova_norma_input.strip()
            if norma_limpa not in st.session_state.normas_db[cat_destino]:
                st.session_state.normas_db[cat_destino].append(norma_limpa)
                st.success(f"Norma '{norma_limpa}' adicionada com sucesso!")
            else:
                st.warning("Esta norma já existe nesta categoria.")
        else:
            st.error("Digite o nome da norma antes de salvar.")

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
    marca_comercial = st.text_input("Marca Comercial / Linha", "MULTI GEAR SUPER")
    viscosidade = st.selectbox("Viscosidade (SAE / ISO)", VISCOSIDADES, index=16) # 85W-140
    tipo_oleo = st.selectbox("Tipo de Base", ["Mineral", "Semissintético", "Sintético"])
    volume = st.selectbox("Volume da Embalagem", VOLUMES, index=1)
    
    linha_produto = st.selectbox("Linha / Aplicação Recomendada (Pictograma)", list(ICON_SVG_DB.keys()), index=0)
    posicao_icone = st.radio("Posição do Ícone no Rótulo:", ["Esquerda", "Centro", "Direita", "Lateral Esquerda Superior"], horizontal=True)
    
    desc_opcional = st.text_area(
        "Descrição Opcional na Frente / Aplicação", 
        "Óleo lubrificante mineral para caixas de mudança e eixos diferenciais de veículos automotores."
    )

with col2:
    st.subheader("⚙️ Especificações & Contra-Rótulo")
    
    cat_normas = st.selectbox("Categoria de Normas no Banco", list(st.session_state.normas_db.keys()), index=3)
    opcoes_disponiveis = st.session_state.normas_db[cat_normas]
    
    normas_frente = st.multiselect("Normas para aparecer na FRENTE", opcoes_disponiveis, default=[opcoes_disponiveis[1]])
    normas_costas = st.multiselect("Normas Adicionais para o CONTRA-RÓTULO", opcoes_disponiveis, default=[opcoes_disponiveis[0], opcoes_disponiveis[1]])
    
    normas_livres = st.text_input("Outras Normas / Escrever Manualmente (Separadas por vírgula):", value="ZF TE-ML 07A, ZF TE-ML 08")
    campo_aplicacao = st.text_input("Campo de Aplicação:", "Engrenagens hipóides, caixas de mudança e diferenciais")
    
    beneficios_txt = st.text_area(
        "Benefícios (Exclusivo Modelo IPA):",
        "Formulado com aditivos extrema pressão para proporcionar excelente proteção contra o desgaste das engrenagens e alta estabilidade térmica."
    )

st.subheader("🏢 Dados da Empresa (Campos Editáveis)")
col_emp1, col_emp2 = st.columns(2)

with col_emp1:
    produtor = st.text_input("Produtor", "INDUSTRIA PETROQUIMICA APOLLO")
    cnpj_produtor = st.text_input("CNPJ Produtor", "37.413.384/0001-84")
    endereco_produtor = st.text_input("Endereço", "Av. Adroaldo José Bombardelli, 1835 - Ponta Grossa/PR")
    sac_empresa = st.text_input("SAC / Contato", "+55 (42) 2702-0500 - www.ipabr.com.br")

with col_emp2:
    quimico_resp = st.text_input("Químico Responsável", "Rafael Costa da Cunha")
    crq_num = st.text_input("Nº CRQ / Região", "CRQ IX: 09303534")
    registro_anp = st.text_input("Registro ANP", "24076")

# --- LÓGICA DE COMPOSIÇÃO DE TEXTOS ---
if tipo_oleo == "Sintético":
    texto_frente_tipo = "ÓLEO LUBRIFICANTE SINTÉTICO"
    composicao_contra = "Óleo sintético com aditivos antidesgaste, antioxidante, anticorrosivo, antiespumante, detergente e melhorador de viscosidade."
elif tipo_oleo == "Mineral":
    texto_frente_tipo = "ÓLEO LUBRIFICANTE MINERAL"
    composicao_contra = "Óleo básico mineral e pacote de aditivos de alta performance (Extrema Pressão)."
else:
    texto_frente_tipo = "ÓLEO LUBRIFICANTE SEMISSINTÉTICO"
    composicao_contra = "Óleos básicos mineral e sintético com aditivos multifuncionais."

# --- BOTÃO DE GERAR PDF ---
if st.button("🚀 Gerar Croqui PDF para ANP", type="primary"):
    
    lista_normas_costas_totais = list(normas_costas)
    if normas_livres.strip():
        lista_normas_costas_totais.append(normas_livres.strip())

    str_normas_frente = " ".join(normas_frente) if normas_frente else ""
    if normas_livres.strip():
        str_normas_frente += f" {normas_livres.strip()}"

    str_normas_costas = f"{viscosidade} - {' '.join(lista_normas_costas_totais)}" if lista_normas_costas_totais else viscosidade

    # Posição do Ícone
    align_style = "text-align: center;"
    if posicao_icone == "Esquerda": align_style = "text-align: left; padding-left: 5mm;"
    elif posicao_icone == "Direita": align_style = "text-align: right; padding-right: 5mm;"
    elif posicao_icone == "Lateral Esquerda Superior": align_style = "position: absolute; top: 6mm; left: 6mm;"

    svg_icon_html = f'<div style="{align_style} margin: 3mm 0;">{ICON_SVG_DB.get(linha_produto, "")}</div>'

    # -------------------------------------------------------------
    # OPT 1: MODELO PADRÃO LUBRIFICANTES (REGULATÓRIO ANP)
    # -------------------------------------------------------------
    if modelo_selecionado == "Modelo Padrão Lubrificantes (Frente + Contra-Rótulo)":
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4 landscape; margin: 8mm; }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Helvetica', 'Arial', sans-serif; }}
                body {{ background-color: #ffffff; color: #1a202c; padding: 2mm; }}
                
                .label-table {{ width: 100%; border-collapse: separate; border-spacing: 12px 0; }}
                .label-cell {{ width: 50%; vertical-align: top; }}
                
                .label-card {{
                    border: 3px solid #1a365d; border-radius: 10px; background-color: #ffffff;
                    padding: 6mm; min-height: 175mm; position: relative;
                    display: flex; flex-direction: column; justify-content: space-between;
                }}
                
                .front-brand {{ font-size: 26pt; font-weight: 900; color: #1a365d; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; line-height: 1.1; margin-top: 1mm; }}
                .viscosity-badge {{
                    background: linear-gradient(135deg, #1a365d, #2b6cb0); color: #ffffff;
                    text-align: center; font-size: 26pt; font-weight: 900; padding: 4mm 2mm; border-radius: 8px; margin: 4mm 0; letter-spacing: 1px;
                }}
                .type-pill {{
                    background-color: #edf2f7; color: #2d3748; text-align: center; font-size: 11pt;
                    font-weight: 800; padding: 2mm; border-radius: 20px; text-transform: uppercase; margin-bottom: 4mm; border: 1px solid #cbd5e0;
                }}
                .front-desc {{ font-size: 9.5pt; text-align: center; color: #4a5568; margin-bottom: 5mm; line-height: 1.3; font-style: italic; padding: 0 2mm; }}
                
                .specs-box-front {{ 
                    border: 1px solid #cbd5e0; background-color: #f7fafc; padding: 3.5mm; border-radius: 6px; font-size: 9pt; line-height: 1.35; color: #2d3748;
                }}
                .volume-tag {{ position: absolute; bottom: 6mm; right: 6mm; font-size: 16pt; font-weight: 900; color: #1a365d; }}
                
                .back-title {{ 
                    font-size: 12pt; font-weight: 900; color: #1a365d; border-bottom: 2px solid #1a365d; 
                    padding-bottom: 1.5mm; margin-bottom: 3.5mm; text-transform: uppercase; letter-spacing: 0.5px;
                }}
                .field-group {{ margin-bottom: 2.5mm; font-size: 8.2pt; line-height: 1.25; color: #2d3748; }}
                .field-label {{ font-weight: 800; color: #1a365d; text-transform: uppercase; }}
                
                /* SEÇÃO OBRIGATÓRIA ANP / CONAMA */
                .anp-regulatory-box {{ 
                    background-color: #f8fafc; border: 1.5px solid #cbd5e1; padding: 3mm; border-radius: 6px; 
                    margin: 3mm 0; font-size: 7.2pt; color: #1e293b; line-height: 1.3;
                }}
                .anp-regulatory-box strong {{ color: #0f172a; text-transform: uppercase; }}
                
                .company-info {{ font-size: 7.2pt; color: #475569; border-top: 1px dashed #cbd5e0; padding-top: 2.5mm; margin-top: 2.5mm; line-height: 1.4; }}
                .company-info div {{ margin-bottom: 1px; }}
                
                .footer-banner {{ 
                    background-color: #1a365d; color: #ffffff; text-align: center; font-weight: 800; 
                    font-size: 7.5pt; padding: 2mm; border-radius: 4px; margin-top: 3mm; letter-spacing: 0.5px; text-transform: uppercase;
                }}
            </style>
        </head>
        <body>
            <table class="label-table">
                <tr>
                    <!-- FRENTE DO RÓTULO -->
                    <td class="label-cell">
                        <div class="label-card">
                            <div>
                                <div class="front-brand">{marca_comercial}</div>
                                {svg_icon_html}
                                <div class="viscosity-badge">{viscosidade}</div>
                                <div class="type-pill">{texto_frente_tipo}</div>
                                <div class="front-desc">{desc_opcional}</div>
                                <div class="specs-box-front">
                                    <strong style="color: #1a365d;">ESPECIFICAÇÕES:</strong><br>{str_normas_frente}
                                </div>
                            </div>
                            <div class="volume-tag">{volume}</div>
                        </div>
                    </td>
                    
                    <!-- CONTRA-RÓTULO (VERSO) -->
                    <td class="label-cell">
                        <div class="label-card">
                            <div>
                                <div class="back-title">{marca_comercial} {viscosidade}</div>
                                <div class="field-group"><span class="field-label">NATUREZA DO PRODUTO:</span> {tipo_oleo}</div>
                                <div class="field-group"><span class="field-label">CAMPO DE APLICAÇÃO:</span> {campo_aplicacao}</div>
                                <div class="field-group"><span class="field-label">ESPECIFICAÇÕES ATENDIDAS:</span> {str_normas_costas}</div>
                                <div class="field-group"><span class="field-label">COMPOSIÇÃO:</span> {composicao_contra}</div>
                                
                                <!-- BLOCO REGULATÓRIO FIXO - ANP/CONAMA -->
                                <div class="anp-regulatory-box">
                                    <p style="margin-bottom: 2mm;"><strong>ADVERTÊNCIA:</strong> Não despeje óleo em ralos, esgotos ou curso d'água. A embalagem e o lubrificante são recicláveis, destinem-os a pontos de coletas autorizados conforme resolução do CONAMA nº 362/05.</p>
                                    <p style="margin-bottom: 2mm;"><strong>PRECAUÇÃO:</strong> Em caso de contato com os olhos ou a pele, lave bem com água. Se ingerido, procure imediatamente um médico. Mantenha fora do alcance de crianças e animais domésticos. O produto pode causar irritação moderada à pele e irritação ocular grave. Evite inalar vapores, névoas ou gases.</p>
                                    <p><strong>VALIDADE:</strong> 5 anos desde que armazenado e lacrado em local seco, limpo e protegido do sol.</p>
                                </div>
                                
                                <div class="company-info">
                                    <div><strong>PRODUTOR:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                                    <div><strong>ENDEREÇO:</strong> {endereco_produtor}</div>
                                    <div><strong>RESPONSÁVEL TÉCNICO:</strong> {quimico_resp} - {crq_num}</div>
                                    <div><strong>REGISTRO ANP:</strong> {registro_anp}</div>
                                    <div><strong>SAC:</strong> {sac_empresa}</div>
                                </div>
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
    elif modelo_selecionado == "Modelo IPA / Petroquímica Apollo (Frente + Contra-Rótulo)":
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4 landscape; margin: 8mm; }}
                * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Helvetica', 'Arial', sans-serif; }}
                body {{ background-color: #ffffff; color: #ffffff; padding: 2mm; }}
                .label-table {{ width: 100%; border-collapse: separate; border-spacing: 12px 0; }}
                .label-cell {{ width: 50%; vertical-align: top; }}
                .label-card {{
                    background-color: #181b20; border: 2px solid #333945; border-radius: 10px;
                    padding: 6mm; min-height: 175mm; position: relative;
                    display: flex; flex-direction: column; justify-content: space-between;
                }}
                .header-brand {{ text-align: center; border-bottom: 2px solid #00a651; padding-bottom: 2.5mm; margin-bottom: 3mm; }}
                .company-name {{ font-size: 8.5pt; font-weight: bold; letter-spacing: 1.5px; color: #a0aec0; text-transform: uppercase; }}
                .product-line {{ font-size: 22pt; font-weight: 900; color: #ffffff; margin: 1.5mm 0; text-transform: uppercase; letter-spacing: 0.5px; }}
                .viscosity-box {{
                    background-color: #00a651; color: #ffffff; font-size: 18pt; font-weight: 900;
                    text-align: center; padding: 2.5mm; border-radius: 6px; margin: 3mm 0; line-height: 1.2;
                }}
                .type-badge {{ text-align: center; font-size: 9.5pt; font-weight: bold; color: #ffffff; margin-bottom: 3mm; text-transform: uppercase; }}
                .front-desc {{ font-size: 8.5pt; text-align: center; color: #cbd5e1; font-style: italic; margin-bottom: 4mm; line-height: 1.3; }}
                .section-title {{ font-size: 7.5pt; font-weight: bold; color: #00a651; text-transform: uppercase; margin-top: 2.5mm; border-bottom: 1px solid #2d3748; padding-bottom: 1mm; }}
                .text-body {{ font-size: 6.8pt; color: #cbd5e1; margin-top: 1.2mm; text-align: justify; line-height: 1.25; }}
                .info-grid {{ font-size: 6.8pt; margin-top: 2.5mm; background-color: #0f1115; padding: 2.5mm; border-radius: 4px; border: 1px solid #2d3748; color: #e2e8f0; }}
                .info-grid div {{ margin-bottom: 1.5px; }}
                .footer-ipa {{ text-align: center; font-size: 6.5pt; color: #a0aec0; border-top: 1px solid #2d3748; padding-top: 2mm; margin-top: 2.5mm; }}
                .volume-badge {{ position: absolute; bottom: 6mm; right: 6mm; font-size: 13pt; font-weight: 900; color: #00a651; }}
            </style>
        </head>
        <body>
            <table class="label-table">
                <tr>
                    <td class="label-cell">
                        <div class="label-card">
                            <div>
                                <div class="header-brand">
                                    <div class="company-name">{produtor}</div>
                                    <div class="product-line">{marca_comercial}</div>
                                </div>
                                {svg_icon_html}
                                <div class="viscosity-box">
                                    {viscosidade}<br>
                                    <span style="font-size: 13pt; font-weight: bold;">{str_normas_frente}</span>
                                </div>
                                <div class="type-badge">{texto_frente_tipo}</div>
                                <div class="front-desc">{desc_opcional}</div>
                            </div>
                            <div class="volume-badge">Conteúdo {volume}</div>
                        </div>
                    </td>
                    <td class="label-cell">
                        <div class="label-card">
                            <div>
                                <div class="header-brand">
                                    <div class="company-name">{produtor}</div>
                                    <div class="product-line" style="font-size: 13pt;">{marca_comercial} {viscosidade}</div>
                                </div>
                                <div class="section-title">BENEFÍCIOS:</div>
                                <div class="text-body">{beneficios_txt}</div>
                                <div class="section-title">COMPOSIÇÃO:</div>
                                <div class="text-body">{composicao_contra}</div>
                                
                                <div class="section-title">ADVERTÊNCIA:</div>
                                <div class="text-body">Não despeje óleo em ralos, esgotos ou curso d'água. A embalagem e o lubrificante são recicláveis, destinem-os a pontos de coletas autorizados conforme resolução do CONAMA nº 362/05.</div>
                                
                                <div class="section-title">PRECAUÇÃO:</div>
                                <div class="text-body">Em caso de contato com os olhos ou a pele, lave bem com água. Se ingerido, procure imediatamente um médico. Mantenha fora do alcance de crianças e animais domésticos. O produto pode causar irritação moderada à pele e irritação ocular grave. Evite inalar vapores, névoas ou gases.</div>
                                
                                <div class="section-title">VALIDADE:</div>
                                <div class="text-body">5 anos desde que armazenado e lacrado em local seco, limpo e protegido do sol.</div>

                                <div class="info-grid">
                                    <div><strong>NATUREZA DO PRODUTO:</strong> {tipo_oleo} | <strong>REGISTRO ANP:</strong> {registro_anp}</div>
                                    <div><strong>ESPECIFICAÇÕES ATENDIDAS:</strong> {str_normas_costas}</div>
                                    <div><strong>CAMPO DE APLICAÇÃO:</strong> {campo_aplicacao}</div>
                                    <div><strong>PRODUTOR:</strong> {produtor} - CNPJ: {cnpj_produtor}</div>
                                    <div><strong>ENDEREÇO:</strong> {endereco_produtor}</div>
                                    <div><strong>RESPONSÁVEL TÉCNICO:</strong> {quimico_resp} - {crq_num}</div>
                                </div>
                            </div>
                            <div class="footer-ipa">
                                SAC: {sac_empresa} | Indústria Brasileira
                            </div>
                        </div>
                    </td>
                </tr>
            </table>
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
    
    st.success("✅ Croqui para ANP gerado com sucesso!")
    with open(output_pdf, "rb") as file:
        st.download_button(
            label="📥 Baixar Croqui em PDF (Enviar ANP)",
            data=file,
            file_name=f"croqui_anp_{marca_comercial.lower().replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
