import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Análise Iridológica Touch", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    h1 { font-size: 1.5rem !important; margin-bottom: 0.2rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔬 Estação Iridológica Touch")
st.caption("Toque e arraste os anéis diretamente com o dedo sobre a íris.")

with st.expander("📋 Dados do Avaliado (Para o Relatório)", expanded=False):
    c1, c2 = st.columns(2)
    nome_pac = c1.text_input("Nome do Avaliado:", value="Lavinia")
    queixa_pac = c2.text_input("Queixa Principal / Observações:", value="Depressão")

aba_od, aba_oe = st.tabs(["👁️ Olho Direito (OD)", "👁️ Olho Esquerdo (OE)"])

def renderizar_estacao_touch(prefixo, titulo_lado, nome, queixa):
    codigo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 4px; background: transparent; color: #1e293b; user-select: none; -webkit-user-select: none; }}
        .upload-box {{ background: #f8fafc; border: 2px dashed #0284c7; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 10px; }}
        .upload-btn {{ background: #0284c7; color: white; padding: 10px 16px; border-radius: 8px; font-weight: bold; font-size: 14px; display: inline-block; cursor: pointer; }}
        input[type="file"] {{ display: none; }}
        .toolbar {{ display: flex; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; justify-content: center; }}
        .mode-btn {{ flex: 1; min-width: 95px; padding: 10px 6px; border: 1px solid #cbd5e1; border-radius: 8px; background: #ffffff; font-weight: 600; font-size: 13px; color: #334155; cursor: pointer; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }}
        .mode-btn.active {{ background: #0284c7; color: white; border-color: #0284c7; }}
        .toggles {{ display: flex; gap: 10px; justify-content: center; margin-bottom: 8px; font-size: 13px; font-weight: 500; }}
        .canvas-wrap {{ position: relative; width: 100%; max-width: 500px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.12); background: #0f172a; touch-action: none; }}
        canvas#irisCanvas {{ width: 100%; display: block; touch-action: none; }}
        .hint {{ text-align: center; font-size: 12px; color: #64748b; margin: 6px 0 12px 0; }}
        .cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }}
        .card {{ background: #f1f5f9; padding: 10px 12px; border-radius: 10px; border-left: 4px solid #0284c7; }}
        .card-title {{ font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 700; }}
        .card-val {{ font-size: 18px; font-weight: 800; color: #0f172a; margin-top: 2px; }}
        .card-full {{ grid-column: span 2; background: #e0f2fe; border-left-color: #0369a1; font-size: 13px; line-height: 1.4; }}
        .polar-box {{ margin-top: 12px; text-align: center; }}
        canvas#polarCanvas {{ width: 100%; height: 75px; border-radius: 6px; border: 1px solid #94a3b8; display: block; }}
        .btn-dl {{ width: 100%; margin-top: 12px; padding: 12px; background: #16a34a; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 14px; cursor: pointer; }}
    </style>
    </head>
    <body>

    <div class="upload-box">
        <label class="upload-btn">
            📸 Escolher ou Tirar Foto — {titulo_lado}
            <input type="file" id="fileInput" accept="image/*">
        </label>
        <div id="fileStatus" style="font-size:12px; color:#475569; margin-top:6px;">Toque acima para abrir a Galeria ou Câmara</div>
    </div>

    <div id="workArea" style="display:none;">
        <div class="toolbar">
            <button id="btnMove" class="mode-btn active" onclick="setMode('move')">✥ Mover Conjunto</button>
            <button id="btnLimbo" class="mode-btn" onclick="setMode('limbo')">🟢 Tamanho Íris</button>
            <button id="btnPupila" class="mode-btn" onclick="setMode('pupila')">🟡 Tamanho Pupila</button>
        </div>

        <div class="toggles">
            <label><input type="checkbox" id="chkZonas" checked onchange="draw()"> 7 Anéis Jensen</label>
            <label><input type="checkbox" id="chkRaios" checked onchange="draw()"> Raios 30°</label>
            <label><input type="checkbox" id="chkZoom" onchange="toggleZoom()"> 🔍 Lupa 2x</label>
        </div>

        <div class="canvas-wrap">
            <canvas id="irisCanvas" width="600" height="600"></canvas>
        </div>
        <div class="hint" id="touchHint">👆 Arraste com 1 dedo para mover • Pinça com 2 dedos para ampliar o anel</div>

        <div class="polar-box">
            <div style="font-size:12px; font-weight:700; color:#334155; margin-bottom:4px;">Projeção Polar de Daugman (0° a 360°)</div>
            <canvas id="polarCanvas" width="360" height="70"></canvas>
        </div>

        <div class="cards">
            <div class="card">
                <div class="card-title">Relação Pupila / Íris</div>
                <div class="card-val" id="valProp">--%</div>
            </div>
            <div class="card">
                <div class="card-title">Índice de Trama (Fibras)</div>
                <div class="card-val" id="valLap">--</div>
            </div>
            <div class="card card-full" id="valDiag">
                Carregue e ajuste os anéis para ver a síntese constitucional.
            </div>
        </div>

        <button class="btn-dl" onclick="baixarLaudo()">📥 Descarregar Relatório ({titulo_lado})</button>
    </div>

    <script>
    const fileInput = document.getElementById('fileInput');
    const canvas = document.getElementById('irisCanvas');
    const ctx = canvas.getContext('2d');
    const polarCanvas = document.getElementById('polarCanvas');
    const pCtx = polarCanvas.getContext('2d');

    let img = new Image();
    let imgLoaded = false;
    let cx = 300, cy = 300, rPupila = 65, rIris = 195;
    let mode = 'move';
    let zoom2x = false;

    let isDragging = false;
    let startX = 0, startY = 0;
    let startCx = 300, startCy = 300, startRP = 65, startRI = 195;
    let initialPinchDist = null;

    function setMode(m) {{
        mode = m;
        document.getElementById('btnMove').className = 'mode-btn' + (m==='move' ? ' active' : '');
        document.getElementById('btnLimbo').className = 'mode-btn' + (m==='limbo' ? ' active' : '');
        document.getElementById('btnPupila').className = 'mode-btn' + (m==='pupila' ? ' active' : '');
        if(m === 'move') document.getElementById('touchHint').innerText = '👆 Arraste com 1 dedo para posicionar todo o conjunto (ou use 2 dedos para abrir/fechar)';
        if(m === 'limbo') document.getElementById('touchHint').innerText = '🟢 Deslize o dedo para a direita/esquerda para ampliar ou reduzir o anel verde da Íris';
        if(m === 'pupila') document.getElementById('touchHint').innerText = '🟡 Deslize o dedo para a direita/esquerda para ajustar o anel amarelo da Pupila';
    }}

    function toggleZoom() {{
        zoom2x = document.getElementById('chkZoom').checked;
        draw();
    }}

    fileInput.addEventListener('change', function(e) {{
        const file = e.target.files[0];
        if (!file) return;
        document.getElementById('fileStatus').innerText = '✅ ' + file.name;
        const reader = new FileReader();
        reader.onload = function(ev) {{
            img.onload = function() {{
                const size = 600;
                canvas.width = size;
                canvas.height = size;
                cx = size / 2;
                cy = size / 2;
                rPupila = Math.round(size * 0.11);
                rIris = Math.round(size * 0.34);
                imgLoaded = true;
                document.getElementById('workArea').style.display = 'block';
                draw();
                atualizarAnalise();
            }};
            img.src = ev.target.result;
        }};
        reader.readAsDataURL(file);
    }});

    function getTouchPos(touch) {{
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        return {{
            x: (touch.clientX - rect.left) * scaleX,
            y: (touch.clientY - rect.top) * scaleY
        }};
    }}

    canvas.addEventListener('touchstart', function(e) {{
        e.preventDefault();
        if (e.touches.length === 2) {{
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            initialPinchDist = Math.hypot(dx, dy);
            startRI = rIris;
            startRP = rPupila;
        }} else if (e.touches.length === 1) {{
            isDragging = true;
            const pos = getTouchPos(e.touches[0]);
            startX = pos.x;
            startY = pos.y;
            startCx = cx;
            startCy = cy;
            startRI = rIris;
            startRP = rPupila;
        }}
    }}, {{passive: false}});

    canvas.addEventListener('touchmove', function(e) {{
        e.preventDefault();
        if (e.touches.length === 2 && initialPinchDist) {{
            const dx = e.touches[0].clientX - e.touches[1].clientX;
            const dy = e.touches[0].clientY - e.touches[1].clientY;
            const dist = Math.hypot(dx, dy);
            const ratio = dist / initialPinchDist;
            if (mode === 'pupila') {{
                rPupila = Math.max(12, Math.min(rIris - 10, Math.round(startRP * ratio)));
            }} else {{
                rIris = Math.max(rPupila + 15, Math.min(295, Math.round(startRI * ratio)));
            }}
            draw();
        }} else if (e.touches.length === 1 && isDragging) {{
            const pos = getTouchPos(e.touches[0]);
            const dx = (pos.x - startX) / (zoom2x ? 2 : 1);
            const dy = (pos.y - startY) / (zoom2x ? 2 : 1);

            if (mode === 'move') {{
                cx = Math.max(40, Math.min(560, startCx + dx));
                cy = Math.max(40, Math.min(560, startCy + dy));
            }} else if (mode === 'limbo') {{
                rIris = Math.max(rPupila + 15, Math.min(295, Math.round(startRI + dx * 0.8)));
            }} else if (mode === 'pupila') {{
                rPupila = Math.max(12, Math.min(rIris - 10, Math.round(startRP + dx * 0.8)));
            }}
            draw();
        }}
    }}, {{passive: false}});

    canvas.addEventListener('touchend', function(e) {{
        isDragging = false;
        initialPinchDist = null;
        atualizarAnalise();
    }});

    // Suporte também para rato (caso abra no computador)
    canvas.addEventListener('mousedown', function(e) {{
        isDragging = true;
        const rect = canvas.getBoundingClientRect();
        startX = (e.clientX - rect.left) * (canvas.width / rect.width);
        startY = (e.clientY - rect.top) * (canvas.height / rect.height);
        startCx = cx; startCy = cy; startRI = rIris; startRP = rPupila;
    }});
    window.addEventListener('mousemove', function(e) {{
        if (!isDragging) return;
        const rect = canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (canvas.height / rect.height);
        const dx = (x - startX) / (zoom2x ? 2 : 1);
        const dy = (y - startY) / (zoom2x ? 2 : 1);
        if (mode === 'move') {{ cx = startCx + dx; cy = startCy + dy; }}
        else if (mode === 'limbo') {{ rIris = Math.max(rPupila + 15, Math.min(295, startRI + dx)); }}
        else if (mode === 'pupila') {{ rPupila = Math.max(12, Math.min(rIris - 10, startRP + dx)); }}
        draw();
    }});
    window.addEventListener('mouseup', function() {{
        if (isDragging) {{ isDragging = false; atualizarAnalise(); }}
    }});

    function draw() {{
        if (!imgLoaded) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();

        if (zoom2x) {{
            ctx.translate(canvas.width/2, canvas.height/2);
            ctx.scale(2, 2);
            ctx.translate(-cx, -cy);
        }}

        // Desenhar foto centralizada e proporcional
        const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
        const iw = img.width * scale;
        const ih = img.height * scale;
        const ix = (canvas.width - iw) / 2;
        const iy = (canvas.height - ih) / 2;
        ctx.drawImage(img, ix, iy, iw, ih);

        // Raios 30 graus
        if (document.getElementById('chkRaios').checked) {{
            ctx.strokeStyle = 'rgba(255, 90, 90, 0.75)';
            ctx.lineWidth = 1;
            for (let a = 0; a < 360; a += 30) {{
                let rad = a * Math.PI / 180;
                ctx.beginPath();
                ctx.moveTo(cx + rPupila * Math.cos(rad), cy + rPupila * Math.sin(rad));
                ctx.lineTo(cx + rIris * Math.cos(rad), cy + rIris * Math.sin(rad));
                ctx.stroke();
            }}
        }}

        // 7 Anéis de Jensen
        if (document.getElementById('chkZonas').checked) {{
            ctx.strokeStyle = 'rgba(200, 210, 255, 0.75)';
            ctx.lineWidth = 1;
            let step = (rIris - rPupila) / 7.0;
            for (let z = 1; z < 7; z++) {{
                ctx.beginPath();
                ctx.arc(cx, cy, rPupila + z * step, 0, 2 * Math.PI);
                ctx.stroke();
            }}
        }}

        // Anel Pupila (Amarelo)
        ctx.strokeStyle = '#facc15';
        ctx.lineWidth = (mode === 'pupila') ? 3.5 : 2;
        ctx.beginPath();
        ctx.arc(cx, cy, rPupila, 0, 2 * Math.PI);
        ctx.stroke();

        // Anel Limbo/Íris (Verde)
        ctx.strokeStyle = '#22c55e';
        ctx.lineWidth = (mode === 'limbo') ? 3.5 : 2.5;
        ctx.beginPath();
        ctx.arc(cx, cy, rIris, 0, 2 * Math.PI);
        ctx.stroke();

        // Mira central
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(cx - 6, cy); ctx.lineTo(cx + 6, cy);
        ctx.moveTo(cx, cy - 6); ctx.lineTo(cx, cy + 6);
        ctx.stroke();

        ctx.restore();
    }}

    let ultimoRelatorio = "";

    function atualizarAnalise() {{
        if (!imgLoaded) return;
        // Extrair pixels limpos da imagem base
        const off = document.createElement('canvas');
        off.width = canvas.width; off.height = canvas.height;
        const oCtx = off.getContext('2d');
        const scale = Math.max(canvas.width / img.width, canvas.height / img.height);
        const iw = img.width * scale, ih = img.height * scale;
        oCtx.drawImage(img, (canvas.width - iw)/2, (canvas.height - ih)/2, iw, ih);
        const srcData = oCtx.getImageData(0, 0, off.width, off.height).data;

        const pw = 360, ph = 70;
        const pImg = pCtx.createImageData(pw, ph);
        const gray = new Float32Array(pw * ph);

        for (let y = 0; y < ph; y++) {{
            let rRatio = y / ph;
            let r = rPupila + rRatio * (rIris - rPupila);
            for (let x = 0; x < pw; x++)
