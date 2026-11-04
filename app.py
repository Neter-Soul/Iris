import pathlib
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Íris Touch", layout="wide")

html_file = pathlib.Path(__file__).parent / "index.html"
if html_file.exists():
  components.html(
      html_file.read_text(encoding="utf-8"), height=950, scrolling=True
  )
else:
  st.warning("Arquivo index.html não encontrado.")
