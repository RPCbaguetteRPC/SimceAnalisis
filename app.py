# -*- coding: utf-8 -*-
"""
Dashboard SIMCE 6to Básico - Aplicativo Web
Desarrollado para visualizacion de resultados de ensayos SIMCE
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuracion de la pagina
st.set_page_config(
    page_title="Dashboard SIMCE 6to Básico",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv('datos_simce.csv')
    df_resultados = pd.read_csv('resultados_simce.csv')
    return df, df_resultados

df, df_resultados = cargar_datos()

# Convertir valores numericos
for col in ['Simce I', 'Simce II', 'Simce III', 'Simce IV', 'Simce V', 'Simce VI', 
            'Promedio', 'Úıt. Prueba', 'Pen últ. Prueba']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Barra lateral
st.sidebar.title("📊 Dashboard SIMCE")
st.sidebar.markdown("---")
st.sidebar.image("https://img.icons8.com/color/96/school.png", width=80)
st.sidebar.markdown("### 6to Básico")
st.sidebar.markdown("---")

# Menu de navegacion
menu = st.sidebar.radio(
    "Navegacion",
    ["🏠 Inicio", "📈 Comparacion Cursos", "👥 Seguimiento Individual", 
     "⚠️ Prioritarios", "📋 Ficha Estudiante"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros")

# Filtro por curso
curso_filter = st.sidebar.multiselect(
    "Seleccionar Curso(s)",
    options=df['Curso'].unique(),
    default=df['Curso'].unique()
)

# Filtro por nivel de apoyo
apoyo_filter = st.sidebar.multiselect(
    "Nivel de Apoyo",
    options=df['Nivel_apoyo'].unique(),
    default=df['Nivel_apoyo'].unique()
)

# Filtrar datos
df_filtrado = df[
    (df['Curso'].isin(curso_filter)) & 
    (df['Nivel_apoyo'].isin(apoyo_filter))
].copy()

# ============================================
# PAGINA DE INICIO
# ============================================
if menu == "🏠 Inicio":
    st.title("🏠 Panel General - SIMCE 6to Básico")
    st.markdown("---")
    
    # Indicadores principales
    total_estudiantes = len(df_filtrado)
    
    # Calcular promedio general (excluyendo ausentes)
    promedios_validos = df_filtrado['Promedio'].dropna()
    promedio_general = promedios_validos.mean() if len(promedios_validos) > 0 else 0
    
    # Calcular promedio ultima prueba
    ultimos_validos = df_filtrado['Úıt. Prueba'].dropna()
    promedio_ultimo = ultimos_validos.mean() if len(ultimos_validos) > 0 else 0
    
    # Estudiantes que mejoraron
    mejoraron = len(df_filtrado[df_filtrado['Tendencia'] == 'Mejoró···'])
    bajaron = len(df_filtrado[df_filtrado['Tendencia'] == 'Bajó···'])
    estables = len(df_filtrado[df_filtrado['Tendencia'] == 'Estable'] | 
                   (df_filtrado['Tendencia'].isna()))
    
    # Prioritarios
    prioritarios = len(df_filtrado[df_filtrado['Nivel_apoyo'] == 'Prioritario'])
    consolidados = len(df_filtrado[df_filtrado['Nivel_apoyo'] == 'Consolidado'])
    
    # Mostrar indicadores en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👨‍🎓 Total Estudiantes", total_estudiantes)
    with col2:
        st.metric("📊 Promedio General", f"{promedio_general:.2%}" if promedio_general > 0 else "N/A")
    with col3:
        st.metric("📈 Última Prueba", f"{promedio_ultimo:.2%}" if promedio_ultimo > 0 else "N/A")
    with col4:
        st.metric("⚠️ Prioritarios", prioritarios)
    
    st.markdown("---")
    
    # Fila 2 de indicadores
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("▲ Mejoraron", mejoraron)
    with col6:
        st.metric("▼ Bajaron", bajaron)
    with col7:
        st.metric("→ Estables", estables)
    
    st.markdown("---")
    
    # Graficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribucion por Nivel de Apoyo")
        
        # Datos para el grafico
        nivel_counts = df_filtrado['Nivel_apoyo'].value_counts().reset_index()
        nivel_counts.columns = ['Nivel', 'Cantidad']
        
        fig_pie = px.pie(
            nivel_counts, 
            values='Cantidad', 
            names='Nivel',
            color='Nivel',
            color_discrete_map={
                'Consolidado': '#2ecc71',
                'En seguimiento': '#f39c12',
                'Prioritario': '#e74c3c'
            },
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📈 Tendencia de Estudiantes")
        
        tendencia_data = {
            'Tendencia': ['Mejoró···', 'Bajó···', 'Estable'],
            'Cantidad': [mejoraron, bajaron, estables]
        }
        fig_bar = px.bar(
            pd.DataFrame(tendencia_data),
            x='Tendencia',
            y='Cantidad',
            color='Tendencia',
            color_discrete_map={
                'Mejoró···': '#2ecc71',
                'Bajó···': '#e74c3c',
                'Estable': '#95a5a6'
            },
            text='Cantidad'
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Cantidad")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla resumen por curso
    st.subheader("📋 Resumen por Curso")
    
    resumen_curso = df_filtrado.groupby('Curso').agg({
        'Estudiante': 'count',
        'Promedio': 'mean',
        'Úıt. Prueba': 'mean',
        'Nivel_apoyo': lambda x: (x == 'Prioritario').sum()
    }).reset_index()
    
    resumen_curso.columns = ['Curso', 'Total Estudiantes', 'Promedio Curso', 
                             'Promedio Últ. Prueba', 'Prioritarios']
    
    resumen_curso['Promedio Curso'] = resumen_curso['Promedio Curso'].apply(
        lambda x: f"{x:.2%}" if pd.notna(x) else "N/A"
    )
    resumen_curso['Promedio Últ. Prueba'] = resumen_curso['Promedio Últ. Prueba'].apply(
        lambda x: f"{x:.2%}" if pd.notna(x) else "N/A"
    )
    
    st.dataframe(resumen_curso, use_container_width=True, hide_index=True)

# ============================================
# PAGINA COMPARACION DE CURSOS
# ============================================
elif menu == "📈 Comparacion Cursos":
    st.title("📈 Comparacion de Cursos")
    st.markdown("---")
    
    # Preparar datos para comparacion
    ensayos = ['Simce I', 'Simce II', 'Simce III', 'Simce IV', 'Simce V', 'Simce VI']
    
    # Promedio por curso y ensayo
    datos_comparacion = []
    for curso in df_filtrado['Curso'].unique():
        df_curso = df_filtrado[df_filtrado['Curso'] == curso]
        for ensayo in ensayos:
            if ensayo in df_curso.columns:
                promedio = df_curso[ensayo].mean()
                if pd.notna(promedio):
                    datos_comparacion.append({
                        'Curso': curso,
                        'Ensayo': ensayo,
                        'Promedio': promedio
                    })
    
    df_comparacion = pd.DataFrame(datos_comparacion)
    
    # Grafico de lineas comparativo
    st.subheader("📊 Evolucion de Promedios por Curso")
    
    fig_lineas = px.line(
        df_comparacion,
        x='Ensayo',
        y='Promedio',
        color='Curso',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['#3498db', '#e74c3c', '#2ecc71']
    )
    fig_lineas.update_traces(line=dict(width=3))
    fig_lineas.update_layout(
        height=500,
        xaxis_title="Ensayo",
        yaxis_title="Promedio del Curso",
        yaxis=dict(tickformat='.0%'),
        hovermode='x unified'
    )
    st.plotly_chart(fig_lineas, use_container_width=True)
    
    st.markdown("---")
    
    # Comparacion lado a lado
    st.subheader("📊 Comparacion Directa por Ensayo")
    
    # Crear tabla dinamica para heatmap
    pivot_comparacion = df_comparacion.pivot(
        index='Curso', 
        columns='Ensayo', 
        values='Promedio'
    )
    
    fig_heatmap = px.imshow(
        pivot_comparacion,
        text_auto='.1%',
        aspect='auto',
        color_continuous_scale='RdYlGn',
        range_color=[0, 1]
    )
    fig_heatmap.update_layout(
        height=400,
        xaxis_title="Ensayo",
        yaxis_title="Curso"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Estadisticas por curso
    st.subheader("📋 Estadisticas Detalladas por Curso")
    
    stats_curso = df_filtrado.groupby('Curso').agg({
        'Promedio': ['mean', 'std', 'min', 'max'],
        'Úıt. Prueba': 'mean',
        'Estudiante': 'count'
    }).round(3)
    
    st.dataframe(stats_curso, use_container_width=True)

# ============================================
# PAGINA SEGUIMIENTO INDIVIDUAL
# ============================================
elif menu == "👥 Seguimiento Individual":
    st.title("👥 Seguimiento Individual de Estudiantes")
    st.markdown("---")
    
    # Buscador de estudiantes
    search_term = st.text_input(
        "🔍 Buscar estudiante por nombre:",
        placeholder="Escribe el nombre del estudiante..."
    )
    
    if search_term:
        df_busqueda = df_filtrado[
            df_filtrado['Estudiante'].str.contains(search_term, case=False, na=False)
        ]
    else:
        df_busqueda = df_filtrado
    
    # Selector de estudiante
    if len(df_busqueda) > 0:
        estudiante_seleccionado = st.selectbox(
            "Seleccionar Estudiante:",
            options=df_busqueda['Estudiante'].unique()
        )
        
        # Filtrar datos del estudiante
        df_estudiante = df_filtrado[df_filtrado['Estudiante'] == estudiante_seleccionado]
        
        if len(df_estudiante) > 0:
            row = df_estudiante.iloc[0]
            
            # Mostrar informacion del estudiante
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👨‍🎓 Estudiante", row['Estudiante'])
            with col2:
                st.metric("🏫 Curso", row['Curso'])
            with col3:
                st.metric("📊 Promedio", f"{row['Promedio']:.2%}" if pd.notna(row['Promedio']) else "N/A")
            with col4:
                st.metric("⚠️ Nivel", row['Nivel_apoyo'])
            
            st.markdown("---")
            
            # Grafico de evolucion del estudiante
            st.subheader(f"📈 Evolucion de {row['Estudiante']}")
            
            ensayos_data = []
            for i, ensayo in enumerate(ensayos, 1):
                if ensayo in row and pd.notna(row[ensayo]):
                    ensayos_data.append({
                        'Ensayo': f'Ensayo {i}',
                        'Puntaje': row[ensayo]
                    })
            
            if len(ensayos_data) > 0:
                df_ensayos = pd.DataFrame(ensayos_data)
                
                fig_evolucion = px.line(
                    df_ensayos,
                    x='Ensayo',
                    y='Puntaje',
                    markers=True,
                    line_shape='linear'
                )
                fig_evolucion.update_traces(
                    line=dict(width=3, color='#3498db'),
                    marker=dict(size=10)
                )
                fig_evolucion.update_layout(
                    height=400,
                    xaxis_title="Ensayo",
                    yaxis_title="Puntaje",
                    yaxis=dict(tickformat='.0%', range=[0, 1]),
                    showlegend=False
                )
                st.plotly_chart(fig_evolucion, use_container_width=True)
            
            st.markdown("---")
            
            # Detalles adicionales
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Detalles")
                st.write(f"**Úıtima prueba:** {row['Úıt. Prueba']:.2%}" if pd.notna(row.get('Úıt. Prueba')) else "**Úıtima prueba:** N/A")
                st.write(f"**Pen últ. prueba:** {row['Pen últ. Prueba']:.2%}" if pd.notna(row.get('Pen últ. Prueba')) else "**Pen últ. prueba:** N/A")
                st.write(f"**Tendencia:** {row.get('Tendencia', 'N/A')}")
            
            with col2:
                st.subheader("📋 Recomendacion")
                if row['Nivel_apoyo'] == 'Prioritario':
                    st.error("⚠️ **Requiere atención prioritaria** - Reforzar contenidos basicos")
                elif row['Nivel_apoyo'] == 'En seguimiento':
                    st.warning("⚠️ **Mantener acompañamiento** - Monitorear proximo ensayo")
                else:
                    st.success("✅ **Buen desempeño** - Continuar con el trabajo actual")
            
            st.markdown("---")
            
            # Tabla completa del estudiante
            st.subheader("📋 Datos Completos")
            
            datos_completos = {
                'Campo': ['Estudiante', 'Curso', 'Simce I', 'Simce II', 'Simce III', 
                         'Simce IV', 'Simce V', 'Simce VI', 'Promedio', 
                         'Úıtima Prueba', 'Tendencia', 'Nivel de Apoyo'],
                'Valor': [
                    row['Estudiante'], row['Curso'],
                    f"{row['Simce I']:.2%}" if pd.notna(row.get('Simce I')) else 'Ausente',
                    f"{row['Simce II']:.2%}" if pd.notna(row.get('Simce II')) else 'Ausente',
                    f"{row['Simce III']:.2%}" if pd.notna(row.get('Simce III')) else 'Ausente',
                    f"{row['Simce IV']:.2%}" if pd.notna(row.get('Simce IV')) else 'Ausente',
                    f"{row['Simce V']:.2%}" if pd.notna(row.get('Simce V')) else 'Ausente',
                    f"{row['Simce VI']:.2%}" if pd.notna(row.get('Simce VI')) else 'Ausente',
                    f"{row['Promedio']:.2%}" if pd.notna(row.get('Promedio')) else 'N/A',
                    f"{row['Úıt. Prueba']:.2%}" if pd.notna(row.get('Úıt. Prueba')) else 'N/A',
                    row.get('Tendencia', 'N/A'),
                    row['Nivel_apoyo']
                ]
            }
            
            st.dataframe(pd.DataFrame(datos_completos), use_container_width=True, hide_index=True)
    
    else:
        st.info("No se encontraron estudiantes que coincidan con la busqueda.")

# ============================================
# PAGINA ESTUDIANTES PRIORITARIOS
# ============================================
elif menu == "⚠️ Prioritarios":
    st.title("⚠️ Estudiantes Prioritarios")
    st.markdown("---")
    
    # Filtrar estudiantes prioritarios
    df_prioritarios = df_filtrado[df_filtrado['Nivel_apoyo'] == 'Prioritario'].copy()
    
    if len(df_prioritarios) > 0:
        st.warning(f"🔴 **{len(df_prioritarios)} estudiantes requieren atención prioritaria**")
        
        st.markdown("---")
        
        # Mostrar tabla de prioritarios
        st.subheader("📋 Lista de Estudiantes Prioritarios")
        
        columnas_mostrar = ['Estudiante', 'Curso', 'Promedio', 'Úıt. Prueba', 'Tendencia']
        df_mostrar = df_prioritarios[columnas_mostrar].copy()
        
        # Formatear porcentajes
        for col in ['Promedio', 'Úıt. Prueba']:
            if col in df_mostrar.columns:
                df_mostrar[col] = df_mostrar[col].apply(
                    lambda x: f"{x:.2%}" if pd.notna(x) else "N/A"
                )
        
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Grafico de distribucion por curso
        st.subheader("📊 Distribucion de Prioritarios por Curso")
        
        prioritarios_por_curso = df_prioritarios.groupby('Curso').size().reset_index(name='Cantidad')
        
        fig_barras = px.bar(
            prioritarios_por_curso,
            x='Curso',
            y='Cantidad',
            color='Cantidad',
            color_continuous_scale='Reds',
            text='Cantidad'
        )
        fig_barras.update_traces(textposition='outside')
        fig_barras.update_layout(
            height=400,
            xaxis_title="Curso",
            yaxis_title="Cantidad de Prioritarios",
            showlegend=False
        )
        st.plotly_chart(fig_barras, use_container_width=True)
        
    else:
        st.success("✅ No hay estudiantes prioritarios en este momento.")

# ============================================
# PAGINA FICHA DEL ESTUDIANTE
# ============================================
elif menu == "📋 Ficha Estudiante":
    st.title("📋 Ficha Individual del Estudiante")
    st.markdown("---")
    
    # Selector de estudiante
    estudiante_seleccionado = st.selectbox(
        "Seleccionar Estudiante:",
        options=df_filtrado['Estudiante'].unique()
    )
    
    # Filtrar datos del estudiante
    df_estudiante = df_filtrado[df_filtrado['Estudiante'] == estudiante_seleccionado]
    
    if len(df_estudiante) > 0:
        row = df_estudiante.iloc[0]
        
        # Encabezado de la ficha
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"👨‍🎓 {row['Estudiante']}")
            st.write(f"**Curso:** {row['Curso']}")
            st.write(f"**ID:** {row['ID_alumno']}")
        
        with col2:
            st.metric("📊 Promedio", f"{row['Promedio']:.2%}" if pd.notna(row['Promedio']) else "N/A")
            st.metric("⚠️ Nivel", row['Nivel_apoyo'])
        
        st.markdown("---")
        
        # Grafico de radar con todos los ensayos
        st.subheader("📊 Perfil de Rendimiento")
        
        ensayos_valores = []
        ensayos_nombres = []
        
        for ensayo in ensayos:
            if ensayo in row and pd.notna(row[ensayo]):
                ensayos_valores.append(row[ensayo])
                ensayos_nombres.append(ensayo.replace('Simce ', 'E'))
        
        if len(ensayos_valores) > 0:
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=ensayos_valores,
                theta=ensayos_nombres,
                fill='toself',
                line=dict(color='#3498db', width=3),
                marker=dict(size=10, color='#3498db')
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        tickformat='.0%',
                        range=[0, 1]
                    )
                ),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        st.markdown("---")
        
        # Informacion detallada
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Resultados por Ensayo")
            
            resultados_data = []
            for i, ensayo in enumerate(ensayos, 1):
                if ensayo in row:
                    valor = row[ensayo]
                    if pd.notna(valor):
                        resultados_data.append({
                            'Ensayo': f'Ensayo {i}',
                            'Puntaje': f"{valor:.2%}",
                            'Estado': 'Presente'
                        })
                    else:
                        resultados_data.append({
                            'Ensayo': f'Ensayo {i}',
                            'Puntaje': 'Ausente',
                            'Estado': 'Ausente'
                        })
            
            if len(resultados_data) > 0:
                st.dataframe(pd.DataFrame(resultados_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("📋 Analisis")
            
            # Calcular variacion
            if pd.notna(row.get('Úıt. Prueba')) and pd.notna(row.get('Pen últ. Prueba')):
                variacion = row['Úıt. Prueba'] - row['Pen últ. Prueba']
                if variacion > 0:
                    st.success(f"▲ Mejoro en {variacion:.2%} respecto a la prueba anterior")
                elif variacion < 0:
                    st.error(f"▼ Bajo en {abs(variacion):.2%} respecto a la prueba anterior")
                else:
                    st.info("→ Se mantuvo estable respecto a la prueba anterior")
            
            # Recomendacion
            st.markdown("**Recomendacion:**")
            if row['Nivel_apoyo'] == 'Prioritario':
                st.error("⚠️ Reforzar contenidos basicos de manera urgente")
            elif row['Nivel_apoyo'] == 'En seguimiento':
                st.warning("⚠️ Mantener acompañamiento y monitorear proximo ensayo")
            else:
                st.success("✅ Continuar con el trabajo actual")
        
        st.markdown("---")
        
        # Historial completo
        st.subheader("📋 Historial Academico")
        
        historial = {
            'Indicador': ['Promedio General', 'Úıtima Prueba', 'Pen últ. Prueba', 
                         'Tendencia', 'Nivel de Apoyo', 'Total Ensayos Rendidos'],
            'Valor': [
                f"{row['Promedio']:.2%}" if pd.notna(row.get('Promedio')) else "N/A",
                f"{row['Úıt. Prueba']:.2%}" if pd.notna(row.get('Úıt. Prueba')) else "N/A",
                f"{row['Pen últ. Prueba']:.2%}" if pd.notna(row.get('Pen últ. Prueba')) else "N/A",
                row.get('Tendencia', 'N/A'),
                row['Nivel_apoyo'],
                len([e for e in ensayos if pd.notna(row.get(e))])
            ]
        }
        
        st.dataframe(pd.DataFrame(historial), use_container_width=True, hide_index=True)

# ============================================
# PIE DE PAGINA
# ============================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Acerca de")
st.sidebar.markdown("""
Dashboard desarrollado para el 
seguimiento de ensayos SIMCE 6to Básico.

**Ultima actualizacion:** Datos cargados 
desde archivo Excel.
""")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Dashboard SIMCE 6to Básico | Desarrollado con Streamlit
    </div>
    """,
    unsafe_allow_html=True
)