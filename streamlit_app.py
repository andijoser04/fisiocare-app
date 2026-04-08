import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURACIÓN DE PÁGINA DE ALTA GAMA
st.set_page_config(
    page_title="FISIOCARE - Portal Médica Premium",
    page_icon="🏥",
    layout="wide"
)

# --- EL MOTOR DE ESTILO (CSS AVANZADO) ---
# He diseñado este CSS para imitar la limpieza y fluidez de Antares, 
# adaptándolo a los colores de sanación de Fisiocare.
st.markdown("""
    <style>
    /* 1. Fondo Calido y Fuente Limpia */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    .main {
        background-color: #f4f7f6;
        font-family: 'Poppins', sans-serif;
    }
    
    /* 2. Cabeceras Centradas y Elegantes (Como Antares) */
    h1 {
        text-align: center;
        color: #028090;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 2rem !important;
    }
    h2, h3 {
        color: #00a896;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }

    /* 3. Tarjetas Elevadas para Contenido (Cards) */
    .stForm, div[data-testid="stDataFrameContainer"], .stAlert {
        background-color: #ffffff;
        padding: 2.5rem !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
        border: none !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    div[data-testid="stDataFrameContainer"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.08) !important;
    }

    /* 4. Botones de Acción Modernos (Degradado y Animación) */
    .stButton>button {
        width: 100%;
        border-radius: 25px !important;
        background: linear-gradient(135deg, #00a896 0%, #028090 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,123,123,0.2) !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 20px rgba(0,123,123,0.3) !important;
        background: linear-gradient(135deg, #028090 0%, #00a896 100%) !important;
    }

    /* 5. Inputs y Selects más limpios */
    .stDateInput div, .stSelectbox div {
        border-radius: 12px !important;
    }

    /* 6. Sidebar Premium */
    [data-testid="stSidebar"] {
        background-color: #028090;
        color: white;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Fondo para secciones específicas si subimos imágenes */
    .hero-bg {
        background-color: rgba(255,255,255,0.7);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN (Mantenemos la lógica intacta)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

def save_data(sheet_name, new_row_df):
    try:
        existing_data = load_data(sheet_name)
        updated_df = pd.concat([existing_data, new_row_df], ignore_index=True)
        conn.update(worksheet=sheet_name, data=updated_df)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# 3. INTERFAZ MODERNA

# SIDEBAR LIMPIO
LOGO_URL = "logo.png" # Asumimos que subiste logo.png a tu GitHub
if LOGO_URL:
    st.sidebar.image(LOGO_URL, width=150)
else:
    st.sidebar.markdown("# 🏥 FISIOCARE")

st.sidebar.title("Navegación Portal")
st.sidebar.markdown("*Gestión Terapéutica Integral*")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Ir a:",
    ["🏠 Dashboard", "📅 Agenda Diaria", "👤 Pacientes"]
)

# --- SECCIONES REDISEÑADAS ---

if menu == "🏠 Dashboard":
    # Cabecera Hero (Como Antares Salud)
    st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
    st.title("Atención de Excelencia a tu Alcance")
    st.markdown("##### Gestión Integral para una Recuperación Exitosa y Sostenible")
    st.markdown("Aquí puedes ver el resumen de actividades de FISIOCARE para hoy.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Métricas en Cards Modernos
    df_agenda = load_data("Agenda")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Citas Hoy", len(df_agenda) if not df_agenda.empty else 0, "+2")
    with col2:
        st.metric("Nuevos Pacientes (Mes)", "+15", "8%")
    with col3:
        st.metric("Terapeutas Activos", "5 / 8")
        
    st.markdown("---")
    
    # Vista rápida de la Agenda Elevada
    st.subheader("📌 Próximos Turnos")
    if not df_agenda.empty:
        st.dataframe(df_agenda.head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No hay citas registradas. ¡Portal listo para operar!")

elif menu == "📅 Agenda Diaria":
    st.header("📅 Control de Agenda y Cupos")
    df_agenda = load_data("Agenda")
    
    # Usamos Tabs modernos para separar la vista del ingreso
    tab_view, tab_add = st.tabs(["👁️ Ver Citas", "➕ Agendar Turno"])
    
    with tab_view:
        if not df_agenda.empty:
            st.dataframe(df_agenda, use_container_width=True, hide_index=True)
        else:
            st.info("No hay citas programadas para hoy.")
            
    with tab_add:
        st.subheader("Registrar Nueva Cita")
        with st.form("form_agenda", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f = col1.date_input("Fecha de la cita", datetime.now())
            h = col2.selectbox("Hora de la cita", ["08:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "17:00"])
            pac = st.text_input("Nombre Completo del Paciente")
            ter = st.selectbox("Terapia Solicitada", ["Convencional", "Integral/Inductivo", "Evaluación"])
            
            # Lógica de colores (Regla de Oro)
            col_val = "Amarillo" if "Integral" in ter else "Rojo" if "Evaluación" in ter else "Verde"
            
            # Botón moderno
            if st.form_submit_button("Confirmar Turno en Agenda"):
                nueva_fila = pd.DataFrame([{
                    "Fecha": str(f),
                    "Hora": h,
                    "Paciente": pac,
                    "Terapia": ter,
                    "Color": col_val
                }])
                
                # EFECTO DE ANIMACIÓN DE ÉXITO
                st.snow() # Lanza copos de nieve (o globos con st.balloons())
                if save_data("Agenda", nueva_fila):
                    st.success(f"✅ ¡Cita para {pac} agendada correctamente como {color_val}!")
                    # Espera un momento y refresca para mostrar los datos nuevos
                    st.rerun()

elif menu == "👤 Pacientes":
    st.header("👤 Base de Datos de Pacientes")
    df_pacientes = load_data("Pacientes")
    
    with st.expander("➕ Registrar Nuevo Paciente en FISIOCARE", expanded=True):
        with st.form("form_paciente", clear_on_submit=True):
            c1, c2 = st.columns(2)
            dni = c1.text_input("DNI / CE")
            nom = c1.text_input("Nombre y Apellido Completos")
            cel = c2.text_input("Celular (Ej: +51...)")
            
            if st.form_submit_button("Añadir Paciente"):
                nueva_p = pd.DataFrame([{"DNI": dni, "Nombre": nom, "Celular": cel}])
                if save_data("Pacientes", nueva_p):
                    st.success(f"✅ Paciente {nom} registrado en FISIOCARE.")
                    st.rerun()

    if not df_pacientes.empty:
        st.dataframe(df_pacientes, use_container_width=True, hide_index=True)
