import streamlit as st
import streamlit.components.v1 as components
import cv2
import numpy as np
import base64
from datetime import datetime

st.set_page_config(page_title="Sistema de Análise Iridológica", layout="wide")

st.title("🔬 Estação de Análise e Topografia Iridológica")
st.caption("Calibração geométrica, realce de estroma, projeção polar de Daugman e laudo automatizado.")

with st.expander("📋 Dados do Avaliado (Para o Relatório)", expanded=True):
    col_p1, col_p2 = st.columns(2)
    nome_paciente = col_p1.text_input("Nome do Avaliado:", placeholder="Ex: Lavinia")
    notas_clinicas = col_p2.text_input("Queixa Principal / Observações:", placeholder="Ex: Depressão, fadiga...")

aba_od, aba_oe, aba_relatorio = st.tabs([
    "👁️ Olho Direito (OD)", 
    "👁️ Olho Esquerdo (OE)", 
    "📄 Relatório Geral"
])

def carregador_universal_android(prefixo, titulo):
    st.markdown(f"**{titulo}**")
    metodo = st.radio(
        "Método de carregamento:",
        ["⚡ Carregador Anti-Erro (Recomendado no Telemóvel)", "📸 Câmara Direta", "📁 Carregador Padrão"],
        key=f"met_{prefixo}"
    )

    if metodo == "⚡ Carregador Anti-Erro (Recomendado no Telemóvel)":
        html_code = f"""
        <div style="background:#f8fafc; padding:14px; border-radius:10px; border:2px dashed #0284c7; font-family:sans-serif;">
            <div style="font-weight:bold; font-size:14px; color:#0f172a; margin-bottom:8px;">
                1️⃣ Toque abaixo para escolher a foto da Galeria:
            </div>
            <input type="file" id="f_{prefixo}" accept="image/*" style="font-size:14px; width:100%; margin-bottom:10px;">
            <div id="msg_{prefixo}" style="font-size:13px; color:#0369a1; font-weight:bold; margin-bottom:8px;"></div>
            <button id="b_{prefixo}" onclick="copiar_{prefixo}()" style="display:none; width:100%; background:#16a34a; color:white; border:none; padding:10px; border-radius:6px; font-size:14px; font-weight:bold; cursor:pointer;">
                2️⃣ TOCAR AQUI PARA COPIAR A FOTO PRONTA
            </button>
            <textarea id="t_{prefixo}" style="width:100%; height:1px; opacity:0.01;" readonly></textarea>
        </div>
        <script>
        document.getElementById('f_{prefixo}').addEventListener('change', function(e) {{
            const file = e.target.files[0];
            if (!file) return;
            document.getElementById('msg_{prefixo}').innerText = '⏳ A preparar imagem no telemóvel...';
            const reader = new FileReader();
            reader.onload = function(ev) {{
                const img = new Image();
                img.onload = function() {{
                    const canvas = document.createElement('canvas');
                    const max_w = 700;
                    let w = img.width, h = img.height;
                    if (w > max_w) {{ h = Math.round(h * (max_w / w)); w = max_w; }}
                    canvas.width = w; canvas.height = h;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, w, h);
                    document.getElementById('t_{prefixo}').value = canvas.toDataURL('image/jpeg', 0.82);
                    document.getElementById('b_{prefixo}').style.display = 'block';
                    document.getElementById('msg_{prefixo}').innerText = '✅ Foto pronta! Toque no botão verde abaixo:';
                }};
                img.src = ev.target.result;
            }};
            reader.readAsDataURL(file);
        }});
        function copiar_{prefixo}() {{
            const t = document.getElementById('t_{prefixo}');
            t.select();
            t.setSelectionRange(0, 999999);
            navigator.clipboard.writeText(t.value).then(function() {{
                document.getElementById('msg_{prefixo}').innerText = '✅ COPIADO! Agora cole na caixa "3️⃣ Colar aqui" logo abaixo:';
                document.getElementById('b_{prefixo}').style.background = '#15803d';
                document.getElementById('b_{prefixo}').innerText = '✔ COPIADO! COLE NA CAIXA ABAIXO';
            }}).catch(function() {{
                document.execCommand('copy');
                document.getElementById('msg_{prefixo}').innerText = '✅ COPIADO! Agora cole na caixa "3️⃣ Colar aqui" logo abaixo:';
            }});
        }}
        </script>
        """
        components.html(html_code, height=165)
        b64_txt = st.text_input("3️⃣ Segure o dedo aqui, toque em COLAR e prima Enter:", key=f"in_{prefixo}", placeholder="Cole aqui o código da foto...")
        if b64_txt and len(b64_txt) > 50:
            try:
                if "," in b64_txt:
                    b64_txt = b64_txt.split(",")[1]
                img_bytes = base64.b64decode(b64_txt.strip())
                return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            except Exception as e:
                st.error(f"Erro ao descodificar imagem: {e}")
        return None

    elif metodo == "📸 Câmara Direta":
        f_cam = st.camera_input("Tirar foto da íris", key=f"cam_{prefixo}")
        if f_cam is not None:
            return cv2.imdecode(np.frombuffer(f_cam.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        return None

    else:
        f_up = st.file_uploader("Selecionar ficheiro", key=f"up_{prefixo}")
        if f_up is not None:
            return cv2.imdecode(np.frombuffer(f_up.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        return None

def processar_olho(img_bgr, prefixo, lado_str):
    if img_bgr is None:
        return None

    h_orig, w_orig = img_bgr.shape[:2]
    largura_max = 700
    if w_orig > largura_max:
        escala = largura_max / w_orig
        img_bgr = cv2.resize(img_bgr, (largura_max, int(h_orig * escala)), interpolation=cv2.INTER_AREA)

    h, w = img_bgr.shape[:2]
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    st.subheader(f"Calibração Geométrica — {lado_str}")
    c1, c2 = st.columns(2)
    cx = c1.slider("Centro X", 0, w, int(w / 2), 1, key=f"{prefixo}_cx")
    cy = c2.slider("Centro Y", 0, h, int(h / 2), 1, key=f"{prefixo}_cy")
    r_pupila = c1.slider("Raio Pupila (Interno)", 10, int(w / 3), int(w * 0.12), 1, key=f"{prefixo}_rp")
    r_iris = c2.slider("Raio Limbo (Externo)", r_pupila + 10, int(w / 2), int(w * 0.35), 1, key=f"{prefixo}_ri")

    co1, co2, co3 = st.columns(3)
    exibir_grade = co1.checkbox("Raios 30°", value=True, key=f"{prefixo}_gr")
    exibir_zonas = co2.checkbox("7 Anéis de Jensen", value=True, key=f"{prefixo}_zn")
    aplicar_clahe = co3.checkbox("Realce de Fibras", value=True, key=f"{prefixo}_cl")

    img_proc = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(img_gray) if aplicar_clahe else img_gray.copy()

    canvas = img_rgb.copy()
    cv2.circle(canvas, (cx, cy), r_pupila, (255, 220, 0), 2)
    cv2.circle(canvas, (cx, cy), r_iris, (0, 255, 120), 2)

    if exibir_zonas:
        passo_raio = (r_iris - r_pupila) / 7.0
        for z in range(1, 7):
            rz = int(r_pupila + z * passo_raio)
            cv2.circle(canvas, (cx, cy), rz, (180, 180, 255), 1, lineType=cv2.LINE_AA)

    if exibir_grade:
        for ang in range(0, 360, 30):
            rad = np.deg2rad(ang)
            x1 = int(cx + r_pupila * np.cos(rad))
            y1 = int(cy + r_pupila * np.sin(rad))
            x2 = int(cx + r_iris * np.cos(rad))
            y2 = int(cy + r_iris * np.sin(rad))
            cv2.line(canvas, (x1, y1), (x2, y2), (255, 80, 80), 1, lineType=cv2.LINE_AA)

    largura_p, altura_p = 360, 70
    tira = np.zeros((altura_p, largura_p), dtype=np.uint8)
    thetas = np.linspace(0, 2 * np.pi, largura_p, endpoint=False)
    raios = np.linspace(0, 1, altura_p)
    for i, r_ratio in enumerate(raios):
        r = r_pupila + r_ratio * (r_iris - r_pupila)
        xs = np.clip(np.round(cx + r * np.cos(thetas)).astype(int), 0, w - 1)
        ys = np.clip(np.round(cy + r * np.sin(thetas)).astype(int), 0, h - 1)
        tira[i, :] = img_proc[ys, xs]

    st.image(canvas, use_container_width=True, caption=f"{lado_str} Mapeado")
    st.image(tira, use_container_width=True, caption="Projeção Polar de Daugman (0° a 360°)")

    prop_pupila = (r_pupila / r_iris) * 100
    score_var = cv2.Laplacian(tira, cv2.CV_64F).var()
    
    if score_var < 150:
        densidade = "Grau 1 (Seda - Compacta)"
    elif score_var < 350:
        densidade = "Grau 2 (Seda/Linho - Boa)"
    elif score_var < 700:
        densidade = "Grau 3 (Linho - Comum)"
    elif score_var < 1200:
        densidade = "Grau 4 (Algodão - Aberta)"
    else:
        densidade = "Grau 5 (Rede - Fragilidade Conjuntiva)"

    tonus_sna = "Equilíbrio Autonómico"
    if prop_pupila > 33:
        tonus_sna = "Tendência Simpaticotónica (Midríase Relativa)"
    elif prop_pupila < 20:
        tonus_sna = "Tendência Parassimpaticotónica (Miose Relativa)"

    m1, m2 = st.columns(2)
    m1.metric("Relação Pupila / Íris", f"{prop_pupila:.1f}%")
    m2.metric("Índice de Trama (Laplaciano)", f"{score_var:.1f}")
    st.info(f"**Constituição Tecidual:** {densidade} | **Dinâmica Pupilar:** {tonus_sna}")

    return {
        "lado": lado_str,
        "prop_pupila": prop_pupila,
        "score_var": score_var,
        "densidade": densidade,
        "tonus_sna": tonus_sna
    }

dados_od = None
dados_oe = None

with aba_od:
    img_od = carregador_universal_android("od", "Carregar Olho Direito (OD)")
    if img_od is not None:
        dados_od = processar_olho(img_od, "od", "Olho Direito (OD)")

with aba_oe:
    img_oe = carregador_universal_android("oe", "Carregar Olho Esquerdo (OE)")
    if img_oe is not None:
        dados_oe = processar_olho(img_oe, "oe", "Olho Esquerdo (OE)")

with aba_relatorio:
    st.subheader("📑 Síntese e Relatório Iridológico")
    if not dados_od and not dados_oe:
        st.warning("Carregue pelo menos uma imagem nos separadores OD ou OE para gerar os relatórios.")
    else:
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        texto_relatorio = f"""# LAUDO DE ANÁLISE TOPOGRÁFICA IRIDOLÓGICA
**Avaliado(a):** {nome_paciente or 'Não informado'}
**Data da Análise:** {data_atual}
**Observações Iniciais:** {notas_clinicas or 'Nenhuma'}

---
"""
        for d in [dados_od, dados_oe]:
            if d:
                texto_relatorio += f"""### {d['lado']}
* **Relação Pupila / Limbo:** {d['prop_pupila']:.1f}% ({d['tonus_sna']})
* **Score Morfológico de Textura:** {d['score_var']:.1f}
* **Densidade Constitucional Estimada:** {d['densidade']}

"""
        texto_relatorio += """---
### Referência das 7 Zonas Anulares de Jensen
1. **Zona 1 (Gástrica):** Assimilação digestiva primária.
2. **Zona 2 (Intestinal):** Absorção, peristaltismo e microbiota.
3. **Zona 3 (Colarete / BPA):** Sistema Nervoso Autónomo, eixo neuroendócrino.
4. **Zona 4 (Órgãos Internos):** Glândulas e parênquimas vitais.
5. **Zona 5 (Sustentação):** Estrutura óssea, muscular e visceral.
6. **Zona 6 (Linfática e Circulatória):** Drenagem linfática e microcirculação.
7. **Zona 7 (Cutânea / Periférica):** Eliminação epitelial e metabolismo lipídico/mineral.
"""
        st.markdown(texto_relatorio)
        st.download_button(
            label="📥 Descarregar Laudo Completo (.MD)",
            data=texto_relatorio,
            file_name=f"laudo_iridologico_{nome_paciente or 'paciente'}.md",
            mime="text/markdown"
        )
