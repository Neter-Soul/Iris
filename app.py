import cv2
import numpy as np
from PIL import Image
import streamlit as st

st.set_page_config(page_title="Análise Iridológica", layout="wide")

st.title("🔬 Análise e Topografia Iridológica")
st.caption(
    "Calibração geométrica, realce de estroma e projeção polar de Daugman."
)

olho_lado = st.radio(
    "Selecione o olho:",
    ("Olho Direito (OD)", "Olho Esquerdo (OE)"),
    horizontal=True,
)
arquivo_foto = st.file_uploader(
    "Carregar foto da íris (Câmera ou Galeria)", type=["jpg", "jpeg", "png"]
)

if arquivo_foto is not None:
  img_bytes = arquivo_foto.read()
  img_bgr = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
  h_orig, w_orig = img_bgr.shape[:2]

  largura_max = 800
  if w_orig > largura_max:
    escala = largura_max / w_orig
    img_bgr = cv2.resize(
        img_bgr,
        (largura_max, int(h_orig * escala)),
        interpolation=cv2.INTER_AREA,
    )

  h, w = img_bgr.shape[:2]
  img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
  img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

  st.subheader("Calibração Geométrica")
  cx = st.slider("Centro X", 0, w, int(w / 2), 1)
  cy = st.slider("Centro Y", 0, h, int(h / 2), 1)
  r_pupila = st.slider(
      "Raio Pupila (Interno)", 10, int(w / 3), int(w * 0.12), 1
  )
  r_iris = st.slider(
      "Raio Limbo (Externo)", r_pupila + 10, int(w / 2), int(w * 0.35), 1
  )

  col_opt1, col_opt2 = st.columns(2)
  with col_opt1:
    exibir_grade = st.checkbox("Raios de 30°", value=True)
    exibir_zonas = st.checkbox("7 Anéis de Jensen", value=True)
  with col_opt2:
    aplicar_clahe = st.checkbox("Realce de Fibras (CLAHE)", value=True)

  def normalizacao_polar(
      img_base, cx, cy, r_in, r_out, largura=360, altura=70
  ):
    tira = np.zeros((altura, largura), dtype=np.uint8)
    thetas = np.linspace(0, 2 * np.pi, largura, endpoint=False)
    raios = np.linspace(0, 1, altura)
    for i, r_ratio in enumerate(raios):
      r = r_in + r_ratio * (r_out - r_in)
      xs = np.clip(np.round(cx + r * np.cos(thetas)).astype(int), 0, w - 1)
      ys = np.clip(np.round(cy + r * np.sin(thetas)).astype(int), 0, h - 1)
      tira[i, :] = img_base[ys, xs]
    return tira

  img_processamento = (
      cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(img_gray)
      if aplicar_clahe
      else img_gray.copy()
  )

  canvas = img_rgb.copy()
  cv2.circle(canvas, (cx, cy), r_pupila, (255, 220, 0), 2)
  cv2.circle(canvas, (cx, cy), r_iris, (0, 255, 120), 2)

  if exibir_zonas:
    passo_raio = (r_iris - r_pupila) / 7.0
    for zona_idx in range(1, 7):
      rz = int(r_pupila + zona_idx * passo_raio)
      cv2.circle(canvas, (cx, cy), rz, (180, 180, 255), 1, lineType=cv2.LINE_AA)

  if exibir_grade:
    for ang in range(0, 360, 30):
      rad = np.deg2rad(ang)
      x1 = int(cx + r_pupila * np.cos(rad))
      y1 = int(cy + r_pupila * np.sin(rad))
      x2 = int(cx + r_iris * np.cos(rad))
      y2 = int(cy + r_iris * np.sin(rad))
      cv2.line(
          canvas, (x1, y1), (x2, y2), (255, 80, 80), 1, lineType=cv2.LINE_AA
      )
      cv2.putText(
          canvas,
          f"{ang}°",
          (x2 + 2, y2 + 2),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.35,
          (255, 255, 255),
          1,
      )

  tira_polar = normalizacao_polar(img_processamento, cx, cy, r_pupila, r_iris)

  st.image(canvas, use_container_width=True, caption=f"{olho_lado} calibrado")
  st.subheader("Íris Retificada (Projeção Polar)")
  st.image(
      tira_polar,
      use_container_width=True,
      caption="Eixo X: 0° a 360° | Eixo Y: Pupila até Limbo",
  )

  st.subheader("Indicadores")
  col_m1, col_m2 = st.columns(2)
  prop_pupila = (r_pupila / r_iris) * 100
  col_m1.metric("Pupila / Íris", f"{prop_pupila:.1f}%")
  score_var = cv2.Laplacian(tira_polar, cv2.CV_64F).var()
  col_m2.metric("Trama de Fibras", f"{score_var:.1f}")
else:
  st.info(
      "Envie uma foto da íris para calibrar os anéis e gerar a projeção polar."
  )
