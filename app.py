# -*- coding: utf-8 -*-
"""
🕯️ EL ORÁCULO DEL MICTLÁN: CHATBOT DE DÍA DE MUERTOS (Versión Streamlit) 💀
--------------------------------------------------------------------------
Chatbot web interactivo para estudiantes de secundaria (12-15 años) con Gemini.
"""

import os
import random
import time

import streamlit as st
from google import genai
from google.genai import types

# ============================================================
# 1. CONFIGURACIÓN Y PARÁMETROS
# ============================================================

MODELO = "gemini-3.8-flash"
MAX_MENSAJES_POR_SESION = 15
MAX_REINTENTOS = 4

# Preguntas clave y retos creativos de la barra lateral (Sidebar)
PREGUNTAS_RAPIDAS = [
    "¿Qué es el Día de Muertos y de dónde viene?",
    "¿Para qué sirve la flor de cempasúchil?",
    "¿Qué significa el pan de muerto?",
    "¿Qué lleva una ofrenda tradicional?",
    "¿Qué es el Mictlán y sus niveles?",
    "¿Cómo ayuda el Xoloitzcuintle a las almas?",
    "¿Qué diferencia hay entre Halloween y Día de Muertos?",
    "🎮 ¿Cómo armar una ofrenda friki o gamer?",
    "✍️ Rífate una calaverita literaria para un profe",
    "🐾 ¿Qué animal místico sería mi guía al Mictlán?",
]

# Título creativo superior y mensaje de bienvenida actualizado
TITULO_SUPERIOR = "🏛️ CÓDICES SAGRADOS DEL MICTLÁN 💀"

BIENVENIDA = (
    "🕯️ **¡Bienvenido, alma viajera!** Soy **El Oráculo del Mictlán**. "
    "He abierto el portal para guiarte a través de los misterios, ofrendas "
    "y tradiciones del Día de Muertos. Toca una pregunta de la barra lateral "
    "o escribe tu duda con confianza (aunque te comas acentos o letras, aquí te entiendo). 💀 ¡Empieza tu travesía!"
)

# ============================================================
# 2. PROMPT DE SISTEMA (Personalidad y Base de Conocimiento)
# ============================================================

PROMPT_SISTEMA = """
Eres "El Oráculo del Mictlán", un guardián místico, sabio, amigable y sumamente creativo 
que conoce todos los secretos del Día de Muertos. Hablas con estudiantes de secundaria (12 a 15 años).

PERSONALIDAD Y ESTILO
- Responde SIEMPRE en español, con un tono místico, respetuoso de las tradiciones mexicanas, 
  pero fresco y juvenil (puedes usar modismos ligeros como '¡Qué onda!', 'chido', 'rifarse').
- Usa emojis alusivos con elegancia (🕯️💀🌼🍂 Cempasúchil, Copal, Papel picado, Xolos).
- Respuestas claras, educativas y directas: de 3 a 6 oraciones, cerrando a veces con una pregunta curiosa.
- Si te piden recomendaciones o retos creativos (ofrenda gamer, calaverita literaria para un maestro, 
  descubrir su animal guía), ¡ponte súper creativo! Inventa versos divertidos e ideas originales.

TOLERANCIA A ERRORES
- Los adolescentes pueden escribir con faltas de ortografía, sin tildes, abreviaturas (q, xk, tmb) o con errores de dedo.
- NUNCA corrijas ni regañes por la ortografía. Interpreta la intención y responde directo.

REGLAS DE SEGURIDAD
- Todo apto para 12-15 años. Mantén siempre el enfoque en el Día de Muertos, la cultura y la memoria de los seres queridos.
"""

# ============================================================
# 3. CONFIGURACIÓN DE LA PÁGINA Y ESTILO CSS UNIFORME
# ============================================================

st.set_page_config(
    page_title="El Oráculo del Mictlán 🕯️💀", page_icon="🕯️", layout="centered"
)

st.markdown(
    """
    <style>
    /* 1. Fondo general de la aplicación, header y elementos principales */
    .stApp, [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: linear-gradient(135deg, #0b0714 0%, #1a0b2e 100%) !important;
        color: #ffffff !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 2. Títulos principales */
    h1 {
        color: #ff9f1c !important;
        text-align: center;
        font-family: 'Cinzel', serif, sans-serif;
        text-shadow: 2px 2px 10px rgba(255, 159, 28, 0.4);
    }
    
    .subtitulo {
        text-align: center; 
        color: #ffbf69; 
        font-style: italic;
        margin-top: -10px; 
        margin-bottom: 20px;
        font-size: 1.15em;
    }
    
    /* 3. Texto blanco brillante en los mensajes */
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #ffffff !important;
        font-size: 1.05rem;
    }
    
    /* 4. ELIMINAR EL BLANCO DE LA CLASE ESPECÍFICA Y CONTENEDORES INFERIORES */
    .st-emotion-cache-128upt6,
    .st-emotion-cache-6mn6c9,
    .st-emotion-cache-1wp6n47,
    div[data-testid="stBottomBlockContainer"], 
    div[data-testid="stBottom"], 
    .stChatFloatingInputContainer {
        background: linear-gradient(135deg, #0b0714 0%, #1a0b2e 100%) !important;
        background-color: transparent !important;
    }
    
    /* 5. Estilo místico del recuadro central donde escribes */
    div[data-testid="stChatInput"] {
        background-color: #12061f !important;
        border: 2px solid #ff9f1c !important;
        border-radius: 14px !important;
        box-shadow: 0 0 15px rgba(255, 159, 28, 0.4) !important;
    }
    
    /* Área de texto interna del input */
    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    /* 6. Barra lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #12061f !important;
        border-right: 1px solid rgba(255, 159, 28, 0.2);
    }
    
    section[data-testid="stSidebar"] button {
        border: 1px solid #ff9f1c55;
        text-align: left;
        background-color: rgba(255, 159, 28, 0.05);
        color: #ffffff !important;
        border-radius: 8px;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: #ff9f1c !important; 
        color: #0b0714 !important; 
        border-color: #ff9f1c;
        font-weight: bold;
    }
    
    /* 7. Burbujas de chat */
    .stChatMessage {
        background-color: rgba(30, 15, 50, 0.85);
        border: 1px solid rgba(255, 159, 28, 0.3);
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 4. CONEXIÓN CON GEMINI
# ============================================================


def obtener_api_key():
  try:
    if "GEMINI_API_KEY" in st.secrets:
      return st.secrets["GEMINI_API_KEY"]
  except Exception:
    pass
  return os.environ.get("GEMINI_API_KEY", "")




cliente = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def generar_respuesta(historial):
  contenidos = [
      types.Content(
          role="user" if m["role"] == "user" else "model",
          parts=[types.Part.from_text(text=m["content"])],
      )
      for m in historial
  ]
  config = types.GenerateContentConfig(
      system_instruction=PROMPT_SISTEMA,
      temperature=0.8,
      max_output_tokens=2048,
  )

  for intento in range(1, MAX_REINTENTOS + 1):
    ya_respondio = False
    try:
      for fragmento in cliente.models.generate_content_stream(
          model=MODELO, contents=contenidos, config=config
      ):
        if fragmento.text:
          ya_respondio = True
          yield fragmento.text
      return
    except Exception as e:
      saturado = "503" in str(e) or "UNAVAILABLE" in str(e)
      if saturado and not ya_respondio and intento < MAX_REINTENTOS:
        time.sleep(2 * intento)
        continue
      raise


def mensaje_de_error(e):
  msg = str(e)
  if "429" in msg or "quota" in msg.lower() or "RESOURCE_EXHAUSTED" in msg:
    return (
        "Las ánimas están muy ocupadas cruzando el río (límite gratuito"
        " alcanzado). Espera un minuto e inténtalo de nuevo. ⏳"
    )
  if "503" in msg or "UNAVAILABLE" in msg:
    return (
        "Hay mucha fila de almas intentando conectar con el Mictlán en este"
        " momento. 👻 Intenta de nuevo en unos segundos."
    )
  if "API key" in msg or "401" in msg or "403" in msg:
    return (
        "La llave del portal (API Key) no es válida. Revisa tu configuración."
        " 🔑"
    )
  if "404" in msg or "NOT_FOUND" in msg:
    return "El modelo de Gemini necesita actualización. 🧙"
  return f"Un hechizo falló en el inframundo: {msg}"


# ============================================================
# 5. ESTADO DE LA SESIÓN Y BARRA LATERAL (SIDEBAR)
# ============================================================

if "mensajes" not in st.session_state:
  st.session_state.mensajes = []

with st.sidebar:
  st.header("🔮 Retos y Preguntas Místicas")
  st.markdown(
      "<i>Toca una opción para invocar una respuesta automática:</i>",
      unsafe_allow_html=True,
  )

  for i, pregunta in enumerate(PREGUNTAS_RAPIDAS):
    if st.button(pregunta, key=f"preg_{i}", use_container_width=True):
      st.session_state.pendiente = pregunta

  st.divider()
  if st.button("🧹 Limpiar Altar (Reiniciar)", use_container_width=True):
    st.session_state.mensajes = []
    st.rerun()

# ============================================================
# 6. MOSTRAR EL HISTORIAL DEL CHAT (Con el título creativo arriba)
# ============================================================

# Título creativo arriba del cuadro de bienvenida / mensajes
st.markdown(
    f"<h3 style='text-align: center; color: #ffbf69; font-family: Cinzel, serif;"
    f" text-shadow: 1px 1px 5px rgba(255,191,105,0.3);'>{TITULO_SUPERIOR}</h3>",
    unsafe_allow_html=True,
)

with st.chat_message("assistant", avatar="💀"):
  st.markdown(BIENVENIDA)

for m in st.session_state.mensajes:
  avatar = "🧑‍🎓" if m["role"] == "user" else "💀"
  with st.chat_message(m["role"], avatar=avatar):
    st.markdown(m["content"])

# ============================================================
# 7. ENTRADA DEL USUARIO (Escrita o por Botón Rápido)
# ============================================================

texto_escrito = st.chat_input("Escribe tu pregunta al Oráculo... 🕯️")
texto = texto_escrito or st.session_state.pop("pendiente", None)

if texto:
  enviados = sum(1 for m in st.session_state.mensajes if m["role"] == "user")
  if enviados >= MAX_MENSAJES_POR_SESION:
    st.warning(
        "¡Has completado tu ofrenda de preguntas por esta sesión! 🕯️ Pulsa"
        " «Limpiar Altar» en la barra lateral para iniciar una nueva travesía."
    )
  else:
    # Guardar y mostrar mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": texto})
    with st.chat_message("user", avatar="🧑‍🎓"):
      st.markdown(texto)

    # Frases dinámicas y creativas mientras piensa
    frases_pensando = [
        "🐾 Cruzando el río Apanohuaya con la ayuda de un Xoloitzcuintle...",
        "🕯️ Encendiendo las veladoras del altar para invocar la respuesta...",
        "🍂 Deshojando pétalos de cempasúchil para consultar a los ancestros...",
        "🍞 Horneando el pan de muerto de la sabiduría...",
        "💀 Desenterrando los antiguos códices del inframundo...",
    ]
    frase_magica = random.choice(frases_pensando)

    # Generar respuesta de la IA en streaming
    with st.chat_message("assistant", avatar="💀"):
      try:
        with st.spinner(f"{frase_magica}"):
          flujo = generar_respuesta(st.session_state.mensajes)
          respuesta = st.write_stream(flujo)
        st.session_state.mensajes.append(
            {"role": "assistant", "content": respuesta}
        )
      except Exception as e:
        st.session_state.mensajes.pop()
        st.error(mensaje_de_error(e))
