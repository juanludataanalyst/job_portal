import streamlit as st
import pandas as pd
import json

# Configuración de la página
st.set_page_config(
    page_title="Portal de Empleos",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("Portal de Empleos")
st.write("Explora ofertas de trabajo disponibles en el sector tecnológico.")

# Cargar datos desde el archivo JSON
@st.cache_data
def load_data():
    try:
        with open("joined_data_standar.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        
        # Extraer solo los campos requeridos
        filtered_data = []
        for job in data:
            filtered_data.append({
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "date": job.get("date", ""),
                "location": job.get("location", ""),
                "source": job.get("source", ""),
                "link": job.get("link", "")
            })
        
        return pd.DataFrame(filtered_data)
    except Exception as e:
        st.error(f"Error al cargar el archivo JSON: {e}")
        return pd.DataFrame()

# Cargar los datos
jobs_df = load_data()

if not jobs_df.empty:
    # Añadir filtros en la barra lateral
    st.sidebar.header("Filtros")
    
    # Filtro de empresa
    companies = ["Todas"] + sorted(jobs_df["company"].unique().tolist())
    selected_company = st.sidebar.selectbox("Empresa", companies)
    
    # Filtro de ubicación
    locations = ["Todas"] + sorted(jobs_df["location"].unique().tolist())
    selected_location = st.sidebar.selectbox("Ubicación", locations)
    
    # Filtro de fuente
    sources = ["Todas"] + sorted(jobs_df["source"].unique().tolist())
    selected_source = st.sidebar.selectbox("Fuente", sources)
    
    # Aplicar filtros
    filtered_df = jobs_df.copy()
    
    if selected_company != "Todas":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]
    
    if selected_location != "Todas":
        filtered_df = filtered_df[filtered_df["location"] == selected_location]
    
    if selected_source != "Todas":
        filtered_df = filtered_df[filtered_df["source"] == selected_source]
    
    # Mostrar número de resultados
    st.write(f"Mostrando {len(filtered_df)} de {len(jobs_df)} ofertas de trabajo")
    
    # Mostrar como dataframe interactivo con selección
    job_selection = st.dataframe(
        filtered_df,
        column_config={
            "title": st.column_config.TextColumn("Título del Puesto", width="large"),
            "company": st.column_config.TextColumn("Empresa", width="medium"),
            "date": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY", width="small"),
            "location": st.column_config.TextColumn("Ubicación", width="medium"),
            "source": st.column_config.TextColumn("Fuente", width="small"),
            "link": st.column_config.LinkColumn("Enlace", width="small"),
        },
        use_container_width=True,
        hide_index=True,
        selection_mode="multi-row",
        on_select="rerun"
    )
    
    # Mostrar trabajos seleccionados
    if hasattr(job_selection, 'selection') and job_selection.selection.rows:
        st.header("Ofertas Seleccionadas")
        selected_indices = job_selection.selection.rows
        selected_jobs = filtered_df.iloc[selected_indices]
        
        st.dataframe(
            selected_jobs,
            use_container_width=True,
            hide_index=True
        )
        
        # Añadir botón de aplicación para trabajos seleccionados
        if st.button("Aplicar a las Ofertas Seleccionadas"):
            st.success(f"¡Solicitud enviada para {len(selected_indices)} ofertas!")
            
            # Mostrar formulario de solicitud
            with st.expander("Detalles de la Aplicación", expanded=True):
                st.text_input("Nombre Completo")
                st.text_input("Email")
                st.text_input("Teléfono")
                st.file_uploader("Subir CV (PDF)", type=["pdf"])
                st.text_area("Carta de Presentación")
                if st.button("Enviar Solicitud"):
                    st.success("¡Tu solicitud ha sido enviada correctamente!")
    else:
        st.info("Selecciona las ofertas que te interesen haciendo clic en las filas de la tabla.")
else:
    st.error("No se pudieron cargar los datos. Verifica que el archivo 'joined_data_standar.json' exista y tenga el formato correcto.")

# Añadir pie de página
st.markdown("---")
st.caption("Portal de Empleos - Construido con Streamlit")