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

# --- BANCO DE NORMAS NA SESSÃO ---
if "normas_db" not in st.session_state:
    st.session_state.normas_db = {
        "Linha Leve & Ciclo Otto (Gasolina/Flex/GNV)": [
            "API SP", "API SN Plus", "API SN", "API SM", "API SL",
            "ACEA A3/B4", "ACEA A5/B5", "ACEA C2", "ACEA C3", "ACEA C5", "ACEA C6",
            "VW 502 00 / 505 00", "VW 508 00 / 509 00", "GM Dexos 1 Gen 3", "GM Dexos 2",
            "MB 229.3", "MB 229.5", "MB 229.51", "BMW Longlife-01", "BMW Longlife-04"
        ],
        "Linha Pesada (Diesel)": [
            "API CK-4", "API CJ-4", "API CI-4 / SL", "API CH-4",
            "ACEA E4", "ACEA E6", "ACEA E7", "ACEA E9", "ACEA E11",
            "MB 228.31", "MB 228.51", "Volvo VDS-4.5", "MAN M 3775", "Cummins CES 20086"
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

# --- DICIONÁRIO DE ÍCONES VETORIAIS REALISTAS E EXPANDIDOS ---
ICON_SVG_DB = {
    "Gear (Engrenagem Dupla Realista)": '''<svg width="85" height="85" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 35C41.7157 35 35 41.7157 35 50C35 58.2843 41.7157 65 50 65C58.2843 65 65 58.2843 65 50C65 41.7157 58.2843 35 50 35ZM50 58C45.5817 58 42 54.4183 42 50C42 45.5817 45.5817 42 50 42C54.4183 42 58 45.5817 58 50C58 54.4183 54.4183 58 50 58Z" fill="#1A365D"/>
        <path d="M92 46H83.82C83.13 42.84 81.82 39.87 80.01 37.19L85.8 31.4C86.58 30.62 86.58 29.35 85.8 28.57L71.43 14.2C70.65 13.42 69.38 13.42 68.6 14.2L62.81 19.99C60.13 18.18 57.16 16.87 54 16.18V8C54 6.9 53.1 6 52 6H31.6C30.5 6 29.6 6.9 29.6 8V16.18C26.44 16.87 23.47 18.18 20.79 19.99L15 14.2C14.22 13.42 12.95 13.42 12.17 14.2L2.8 23.57C2.02 24.35 2.02 25.62 2.8 26.4L8.59 32.19C6.78 34.87 5.47 37.84 4.78 41H0V62H4.78C5.47 65.16 6.78 68.13 8.59 70.81L2.8 76.6C2.02 77.38 2.02 78.65 2.8 79.43L17.17 93.8C17.95 94.58 19.22 94.58 20 93.8L25.79 88.01C28.47 89.82 31.44 91.13 34.6 91.82V100H56V91.82C59.16 91.13 62.13 89.82 64.81 88.01L70.6 93.8C71.38 94.58 72.65 94.58 73.43 93.8L87.8 79.43C88.58 78.65 88.58 77.38 87.8 76.6L82.01 70.81C83.82 68.13 85.13 65.16 85.82 62H92V46Z" stroke="#1A365D" stroke-width="3" stroke-linejoin="round"/>
    </svg>''',
    
    "Linha Leve (Carro Esporte)": '''<svg width="90" height="60" viewBox="0 0 24 24" fill="none" stroke="#1A365D" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path>
        <circle cx="7" cy="17" r="2.5" fill="#1A365D"></circle>
        <circle cx="17" cy="17" r="2.5" fill="#1A365D"></circle>
        <path d="M5 10l1.5-3.5h7L15 10"></path>
    </svg>''',
    
    "Linha Pesada (Caminhão Robusto)": '''<svg width="90" height="60" viewBox="0 0 24 24" fill="none" stroke="#1A365D" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <rect x="1" y="3" width="14" height="13" rx="1"></rect>
        <polygon points="15 8 19 8 22 11 22 16 15 16 15 8"></polygon>
        <circle cx="5.5" cy="18.5" r="2.5" fill="#1A365D"></circle>
        <circle cx="12.5" cy="18.5" r="2.5" fill="#1A365D"></circle>
        <circle cx="18.5" cy="18.5" r="2.5" fill="#1A365D"></circle>
        <line x1="3" y1="6" x2="10" y2="6"></line>
    </svg>''',
    
    "Moto (Motocicleta 4T/2T)": '''<svg width="85" height="60" viewBox="0 0 24 24" fill="none" stroke="#1A365D" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="5" cy="16" r="3.5"></circle>
        <circle cx="19" cy="16" r="3.5"></circle>
        <path d="M12 17V11L8 6H3"></path>
        <path d="M12 11h5.5l3.5-5"></path>
        <path d="M9 11l3-4h4"></path>
    </svg>''',
    
    "ATF (Transmissão & Engrenagem Hidráulica)": '''<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#1A365D" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="9"></circle>
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M12 3v6M12 15v6M3 12h6M15 12h6"></path>
    </svg>''',
    
    "TASA (Direção Hidráulica / Volante)": '''<svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#1A365D" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="9"></circle>
        <circle cx="12" cy="12" r="2" fill="#1A365D"></circle>
        <path d="M12 14v7M5 8.5l6 4.5M19 8.5l-6 4.5"></path>
    </svg>'''
}

FONTS_DB = {
    "Helvetica / Arial (Moderna Clássica)": "'Helvetica Neue', Helvetica, Arial, sans-serif",
    "Roboto / Trebuchet (Limpa e Industrial)": "'Trebuchet MS', 'Roboto', sans-serif",
    "Impact / Bold (Destaque de Impacto)": "Impact, 'Arial Black', sans-serif",
    "Georgia / Times (Serifada Elegante)": "Georgia, 'Times New Roman', serif",
    "Courier / Monospace (Técnica / Laboratório)": "'Courier New', Courier, monospace"
}

# --- CADASTRO DE NORMA NO BANCO ---
with st.sidebar.expander("➕ Cadastrar Nova Norma no Banco"):
    cat_destino = st.selectbox("Categoria para a Nova Norma:", list(st.session_state.normas_db.keys()))
    nova_norma_input = st.text_input("Nome da Norma / Especificação:")
    if st.button("💾 Salvar Norma no Banco"):
        if nova_norma_input.strip() != "":
            norma_limpa = nova_norma_input.strip()
            if norma_limpa not in st.session_state.normas_db[cat_destino]:
                st.session_state.normas_db[cat_destino].append(norma_limpa)
                st.success(f"Norma '{norma_limpa}' adicionada!")
            else:
                st.warning("Esta norma já existe.")

VISCOSIDADES = [
    "SAE 0W-16", "SAE 0W-20", "SAE 0W-30", "SAE 5W-20", "SAE 5W-30", "SAE 5W-40",
    "SAE 10W-30", "SAE 10W-40", "SAE 15W-40", "SAE 20W-50",
    "SAE 30", "SAE 40", "SAE 50",
    "SAE 75W-80", "SAE 75W-90", "SAE 80W-90", "SAE 85W-140", "ISO VG 68", "ISO VG 100"
]

VOLUMES = ["500 mL", "1 Litro", "4 Litros", "5 Litros", "20 Litros", "200 Litros"]

# --- ENTRADA DE DADOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Personalização Visual & Marca")
    
    nome_topo_empresa = st.text_input("Nome / Sigla no Topo (ex: IPA, APOLLO, PETRO):", "IPA")
    fonte_selecionada = st.selectbox("Fonte do Título / Marca:", list(FONTS_DB.keys()), index=0)
    
    marca_comercial = st.text_input("Marca Comercial / Linha do Produto", "MULTI GEAR SUPER")
    viscosidade = st.selectbox("Viscosidade (SAE / ISO)", VISCOSIDADES, index=16)
    tipo_oleo = st.selectbox("Tipo de Base", ["Mineral", "Semissintético", "Sintético"])
    volume = st.selectbox("Volume da Embalagem", VOLUMES, index=1)
    
    linha_produto = st.selectbox("Pictograma / Ícone Realista", list(ICON_SVG_DB.keys()), index=0)
    posicao_icone = st.radio("Posição do Ícone:", ["Centralizado", "Esquerda", "Direita"], horizontal=True)
    
    desc_opcional = st.text_area(
        "Descrição Comercial na Frente", 
        "Óleo lubrificante mineral para caixas de mudança e eixos diferenciais de veículos automotores."
    )

with col2:
    st.subheader("⚙️ Especificações & Contra-Rótulo")
    
    cat_normas = st.selectbox("Categoria de Normas no Banco", list(st.session_state.normas_db.keys()), index=3)
    opcoes_disponiveis = st.session_state.normas_db[cat_normas]
    
    normas_frente = st.multiselect("Normas na FRENTE", opcoes_disponiveis, default=[opcoes_disponiveis[1]])
    normas_costas = st.multiselect("Normas no CONTRA-RÓTULO", opcoes_disponiveis, default=[opcoes_disponiveis[0], opcoes_disponiveis[1]])
    
    normas_livres = st.text_input("Outras Normas / Texto Livre:", value="ZF TE-ML 07A, ZF TE-ML 08")
    campo_aplicacao = st.text_input("Campo de Aplicação:", "Engrenagens hipóides, caixas de mudança e diferenciais")
    
    beneficios_txt = st.text_area(
        "Benefícios (Modelo IPA):",
        "Formulado com aditivos extrema pressão para proporcionar excelente proteção contra o desgaste das engrenagens e alta estabilidade térmica."
    )

st.subheader("🏢 Dados do Produtor (ANP)")
col_emp1, col_emp2 = st.columns(2)

with col_emp1:
    produtor = st.text_input("Razão Social Produtor", "INDUSTRIA PETROQUIMICA APOLLO")
    cnpj_produtor = st.text_input("CNPJ", "37.413.384/0001-84")
    endereco_produtor = st.text_input("Endereço Completo", "Av. Adroaldo José Bombardelli, 1835 - Ponta Grossa/PR")
    sac_empresa = st.text_input("SAC / Atendimento", "+55 (42) 2702-0500 - www.ipabr.com.br")

with col_emp2:
    quimico_resp = st.text_input("Químico Responsável", "Rafael Costa da Cunha")
    crq_num = st.text_input("Nº CRQ / Região", "CRQ IX: 09303534")
    registro_anp = st.text_input("Registro ANP", "24076")

# Lógica de Textos
if tipo_oleo == "Sintético":
    texto_frente_tipo = "ÓLEO LUBRIFICANTE SINTÉTICO"
    composicao_contra = "Óleo sintético com aditivos antidesgaste, antioxidante, anticorrosivo, antiespumante e melhorador de viscosidade."
elif tipo_oleo == "Mineral":
    texto_frente_tipo = "ÓLEO LUBRIFICANTE MINERAL"
    composicao_contra = "Óleo básico mineral e pacote de aditivos de alta performance (Extrema Pressão)."
else:
    texto_frente_tipo = "ÓLEO LUBRIFICANTE SEMISSINTÉTICO"
    composicao_contra = "Óleos básicos mineral e sintético com aditivos multifuncionais."

# CSS da Fonte Selecionada
font_css_family = FONTS_DB[fonte_selecionada]

# Botão de Geração
if st.button("🚀 Gerar Croqui PDF para ANP", type="primary"):
    
    lista_normas_costas_totais = list(normas_costas)
    if normas_livres.strip():
        lista_normas_costas_totais.append(normas_livres.strip())

    str_normas_frente = " ".join(normas_frente) if normas_frente else ""
    if normas_livres.strip():
        str_normas_frente += f" {normas_livres.strip()}"

    str_normas_costas = f"{viscosidade} - {' '.join(lista_normas_costas_totais)}" if lista_normas_costas_totais else viscosidade

    # Alinhamento do Ícone
    align_style = "text-align: center;"
    if posicao_icone == "Esquerda": align_style = "text-align: left; padding-left: 10mm;"
    elif posicao_icone == "Direita": align_style = "text-align: right; padding-right: 10mm;"

    svg_icon_html = f'<div style="{align_style} margin: 4mm 0;">{ICON_SVG_DB.get(linha_produto, "")}</div>'

    # HTML / CSS
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4 landscape; margin: 8mm; }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background-color: #ffffff; color: #1a202c; padding: 2mm; font-family: {font_css_family}; }}
            
            .label-table {{ width: 100%; border-collapse: separate; border-spacing: 12px 0; }}
            .label-cell {{ width: 50%; vertical-align: top; }}
            
            .label-card {{
                border: 3px solid #1a365d; border-radius: 10px; background-color: #ffffff;
                padding: 6mm; min-height: 175mm; position: relative;
                display: flex; flex-direction: column; justify-content: space-between;
            }}
            
            .top-header-brand {{
                text-align: center; font-size: 14pt; font-weight: 900; color: #1a365d;
                letter-spacing: 3px; text-transform: uppercase; margin-bottom: 1mm;
            }}
            
            .front-brand {{ font-size: 26pt; font-weight: 900; color: #1a365d; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; line-height: 1.1; }}
            
            .viscosity-badge {{
                background: linear-gradient(135deg, #1a365d, #2b6cb0); color: #ffffff;
                text-align: center; font-size: 26pt; font-weight: 900; padding: 4mm 2mm; border-radius: 8px; margin: 3mm 0; letter-spacing: 1px;
            }}
            .type-pill {{
                background-color: #edf2f7; color: #2d3748; text-align: center; font-size: 11pt;
                font-weight: 800; padding: 2mm; border-radius: 20px; text-transform: uppercase; margin-bottom: 3mm; border: 1px solid #cbd5e0;
            }}
            .front-desc {{ font-size: 9pt; text-align: center; color: #4a5568; margin-bottom: 4mm; line-height: 1.3; font-style: italic; padding: 0 2mm; }}
            
            .specs-box-front {{ 
                border: 1px solid #cbd5e0; background-color: #f7fafc; padding: 3mm; border-radius: 6px; font-size: 9pt; line-height: 1.35; color: #2d3748;
            }}
            .volume-tag {{ position: absolute; bottom: 6mm; right: 6mm; font-size: 15pt; font-weight: 900; color: #1a365d; }}
            
            .back-title {{ 
                font-size: 12pt; font-weight: 900; color: #1a365d; border-bottom: 2px solid #1a365d; 
                padding-bottom: 1.5mm; margin-bottom: 3mm; text-transform: uppercase; letter-spacing: 0.5px;
            }}
            .field-group {{ margin-bottom: 2mm; font-size: 8pt; line-height: 1.25; color: #2d3748; }}
            .field-label {{ font-weight: 800; color: #1a365d; text-transform: uppercase; }}
            
            /* BLOCO OBRIGATÓRIO ANP / CONAMA */
            .anp-regulatory-box {{ 
                background-color: #f8fafc; border: 1.5px solid #cbd5e1; padding: 2.5mm; border-radius: 6px; 
                margin: 2.5mm 0; font-size: 7pt; color: #1e293b; line-height: 1.25;
            }}
            .anp-regulatory-box strong {{ color: #0f172a; text-transform: uppercase; }}
            
            .company-info {{ font-size: 7pt; color: #475569; border-top: 1px dashed #cbd5e0; padding-top: 2mm; margin-top: 2mm; line-height: 1.35; }}
            
            .footer-banner {{ 
                background-color: #1a365d; color: #ffffff; text-align: center; font-weight: 800; 
                font-size: 7.5pt; padding: 2mm; border-radius: 4px; margin-top: 2.5mm; letter-spacing: 0.5px; text-transform: uppercase;
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
                            <div class="top-header-brand">{nome_topo_empresa}</div>
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
                            <div class="top-header-brand" style="text-align: left;">{nome_topo_empresa}</div>
                            <div class="back-title">{marca_comercial} {viscosidade}</div>
                            <div class="field-group"><span class="field-label">NATUREZA DO PRODUTO:</span> {tipo_oleo}</div>
                            <div class="field-group"><span class="field-label">CAMPO DE APLICAÇÃO:</span> {campo_aplicacao}</div>
                            <div class="field-group"><span class="field-label">ESPECIFICAÇÕES ATENDIDAS:</span> {str_normas_costas}</div>
                            <div class="field-group"><span class="field-label">COMPOSIÇÃO:</span> {composicao_contra}</div>
                            
                            <!-- BLOCO FIXO ANP / CONAMA -->
                            <div class="anp-regulatory-box">
                                <p style="margin-bottom: 1.5mm;"><strong>ADVERTÊNCIA:</strong> Não despeje óleo em ralos, esgotos ou curso d'água. A embalagem e o lubrificante são recicláveis, destinem-os a pontos de coletas autorizados conforme resolução do CONAMA nº 362/05.</p>
                                <p style="margin-bottom: 1.5mm;"><strong>PRECAUÇÃO:</strong> Em caso de contato com os olhos ou a pele, lave bem com água. Se ingerido, procure imediatamente um médico. Mantenha fora do alcance de crianças e animais domésticos. O produto pode causar irritação moderada à pele e irritação ocular grave. Evite inalar vapores, névoas ou gases.</p>
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

    output_pdf = "rotulo_gerado.pdf"
    HTML(string=html_template).write_pdf(output_pdf)
    
    st.success("✅ Croqui PDF gerado com o novo cabeçalho e ícones expansivos!")
    with open(output_pdf, "rb") as file:
        st.download_button(
            label="📥 Baixar Croqui Atualizado em PDF",
            data=file,
            file_name=f"croqui_anp_{nome_topo_empresa.lower()}{marca_comercial.lower().replace(' ', '')}.pdf",
            mime="application/pdf"
        )
