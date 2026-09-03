# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard SIMCE", page_icon="📊", layout="wide")

@st.cache_data

def cargar_datos():
    df = pd.read_csv("datos_simce.csv", encoding="utf-8")
    df_resultados = pd.read_csv("resultados_simce.csv", encoding="utf-8")
    return df, df_resultados

df, df_resultados = cargar_datos()

# Nombres normalizados y compatibles
columnas_ensayos = ["Simce I", "Simce II", "Simce III", "Simce IV", "Simce V", "Simce VI"]
col_ultima = "Últ. Prueba"
col_penultima = "Penúlt. Prueba"

# Conversión segura de columnas numéricas
for col in columnas_ensayos + ["Promedio", col_ultima, col_penultima]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Nivel de apoyo calculado de manera segura
def nivel_apoyo(row):
    ultimo = row.get(col_ultima)
    if pd.isna(ultimo):
        return "En seguimiento"
    if ultimo < 0.50:
        return "Prioritario"
    if ultimo < 0.75:
        return "En seguimiento"
    return "Consolidado"

# Si el CSV tuviera una clasificación incorrecta, recalcularla
df["Nivel_apoyo"] = df.apply(nivel_apoyo, axis=1)

def etiqueta_tendencia(valor):
    if pd.isna(valor):
        return "Sin dato"
    valor = str(valor).strip().lower()
    if "mejor" in valor:
        return "Mejoró"
    if "baj" in valor:
        return "Bajó"
    if "estab" in valor:
        return "Estable"
    return str(valor).title()

df["Tendencia_app"] = df["Tendencia"].apply(etiqueta_tendencia)

# Barra lateral
st.sidebar.title("📊 Dashboard SIMCE")
st.sidebar.markdown("### 6to Básico")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "📈 Comparación Cursos", "👥 Seguimiento Individual", "⚠️ Prioritarios", "📋 Ficha Estudiante"]
)

cursos = sorted(df["Curso"].dropna().unique().tolist())
seleccion_cursos = st.sidebar.multiselect("Seleccionar Curso(s)", cursos, default=cursos)

niveles = ["Prioritario", "En seguimiento", "Consolidado"]
seleccion_niveles = st.sidebar.multiselect("Nivel de Apoyo", niveles, default=niveles)

df_filtrado = df[
    df["Curso"].isin(seleccion_cursos) &
    df["Nivel_apoyo"].isin(seleccion_niveles)
].copy()

# Métricas
promedio_general = df_filtrado["Promedio"].mean() if len(df_filtrado) else None
promedio_ultimo = df_filtrado[col_ultima].mean() if len(df_filtrado) else None
mejoraron = int((df_filtrado["Tendencia_app"] == "Mejoró").sum())
bajaron = int((df_filtrado["Tendencia_app"] == "Bajó").sum())
estables = int((df_filtrado["Tendencia_app"] == "Estable").sum())
prioritarios = int((df_filtrado["Nivel_apoyo"] == "Prioritario").sum())

# Inicio
if menu == "🏠 Inicio":
    st.title("🏠 Panel General - SIMCE 6to Básico")
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👨‍🎓 Total Estudiantes", len(df_filtrado))
    c2.metric("📊 Promedio General", f"{promedio_general:.2%}" if pd.notna(promedio_general) else "N/A")
    c3.metric("📈 Última Prueba", f"{promedio_ultimo:.2%}" if pd.notna(promedio_ultimo) else "N/A")
    c4.metric("⚠️ Prioritarios", prioritarios)

    c5, c6, c7 = st.columns(3)
    c5.metric("▲ Mejoraron", mejoraron)
    c6.metric("▼ Bajaron", bajaron)
    c7.metric("→ Estables", estables)

    st.markdown("---")
    a, b = st.columns(2)
    with a:
        st.subheader("📊 Distribución por Nivel de Apoyo")
        niveles_df = df_filtrado["Nivel_apoyo"].value_counts().rename_axis("Nivel").reset_index(name="Cantidad")
        fig = px.pie(niveles_df, names="Nivel", values="Cantidad", hole=0.4,
                     color="Nivel", color_discrete_map={"Consolidado":"#2ecc71", "En seguimiento":"#f39c12", "Prioritario":"#e74c3c"})
        st.plotly_chart(fig, use_container_width=True)
    with b:
        st.subheader("📈 Tendencia de Estudiantes")
        tendencia_df = pd.DataFrame({"Tendencia":["Mejoró","Bajó","Estable"], "Cantidad":[mejoraron,bajaron,estables]})
        fig = px.bar(tendencia_df, x="Tendencia", y="Cantidad", text="Cantidad", color="Tendencia",
                     color_discrete_map={"Mejoró":"#2ecc71", "Bajó":"#e74c3c", "Estable":"#95a5a6"})
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Resumen por Curso")
    if len(df_filtrado):
        resumen = df_filtrado.groupby("Curso").agg(
            Estudiantes=("Estudiante", "count"),
            Promedio=("Promedio", "mean"),
            Ultima_prueba=(col_ultima, "mean"),
            Prioritarios=("Nivel_apoyo", lambda x: (x == "Prioritario").sum())
        ).reset_index()
        resumen["Promedio"] = resumen["Promedio"].map(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
        resumen["Ultima_prueba"] = resumen["Ultima_prueba"].map(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
        st.dataframe(resumen, use_container_width=True, hide_index=True)

# Comparación
elif menu == "📈 Comparación Cursos":
    st.title("📈 Comparación de Cursos")
    st.markdown("---")
    registros = []
    for curso in seleccion_cursos:
        tmp = df_filtrado[df_filtrado["Curso"] == curso]
        for ensayo in columnas_ensayos:
            if ensayo in tmp.columns:
                valor = tmp[ensayo].mean()
                if pd.notna(valor):
                    registros.append({"Curso": curso, "Ensayo": ensayo.replace("Simce ", "Ensayo "), "Promedio": valor})
    comp = pd.DataFrame(registros)
    if len(comp):
        st.subheader("📊 Evolución de Promedios por Curso")
        fig = px.line(comp, x="Ensayo", y="Promedio", color="Curso", markers=True)
        fig.update_layout(yaxis_tickformat=".0%", height=500, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Comparación Directa")
        pivot = comp.pivot(index="Curso", columns="Ensayo", values="Promedio")
        fig = px.imshow(pivot, text_auto=".1%", aspect="auto", color_continuous_scale="RdYlGn", range_color=[0,1])
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Estadísticas por Curso")
        stats = df_filtrado.groupby("Curso").agg(
            Estudiantes=("Estudiante", "count"),
            Promedio=("Promedio", "mean"),
            Ultima_prueba=(col_ultima, "mean"),
            Minimo=("Promedio", "min"),
            Maximo=("Promedio", "max")
        ).reset_index()
        st.dataframe(stats.style.format({"Promedio":"{:.2%}", "Ultima_prueba":"{:.2%}", "Minimo":"{:.2%}", "Maximo":"{:.2%}"}), use_container_width=True, hide_index=True)

# Seguimiento
elif menu == "👥 Seguimiento Individual":
    st.title("👥 Seguimiento Individual")
    st.markdown("---")
    buscar = st.text_input("🔍 Buscar estudiante", "")
    candidatos = df_filtrado[df_filtrado["Estudiante"].str.contains(buscar, case=False, na=False)] if buscar else df_filtrado
    if len(candidatos):
        seleccionado = st.selectbox("Seleccionar Estudiante", candidatos["ID_alumno"].tolist())
        row = candidatos[candidatos["ID_alumno"] == seleccionado].iloc[0]
        st.subheader(f"👨‍🎓 {row['Estudiante']} - {row['Curso']}")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Promedio", f"{row['Promedio']:.2%}" if pd.notna(row["Promedio"]) else "N/A")
        c2.metric("Última prueba", f"{row[col_ultima]:.2%}" if pd.notna(row[col_ultima]) else "N/A")
        c3.metric("Tendencia", row["Tendencia_app"])
        c4.metric("Nivel", row["Nivel_apoyo"])
        registros = [{"Ensayo": e.replace("Simce ", "Ensayo "), "Puntaje": row[e]} for e in columnas_ensayos if e in row.index and pd.notna(row[e])]
        if registros:
            fig = px.line(pd.DataFrame(registros), x="Ensayo", y="Puntaje", markers=True)
            fig.update_layout(yaxis_tickformat=".0%", yaxis_range=[0,1])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No se encontraron estudiantes.")

# Prioritarios
elif menu == "⚠️ Prioritarios":
    st.title("⚠️ Estudiantes Prioritarios")
    st.markdown("---")
    pri = df_filtrado[df_filtrado["Nivel_apoyo"] == "Prioritario"].copy()
    st.warning(f"🔴 {len(pri)} estudiantes requieren atención prioritaria")
    if len(pri):
        vista = pri[["Estudiante", "Curso", "Promedio", col_ultima, "Tendencia_app"]].copy()
        for c in ["Promedio", col_ultima]:
            vista[c] = vista[c].map(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
        vista = vista.rename(columns={"Tendencia_app":"Tendencia"})
        st.dataframe(vista, use_container_width=True, hide_index=True)
        conteo = pri.groupby("Curso").size().reset_index(name="Cantidad")
        fig = px.bar(conteo, x="Curso", y="Cantidad", color="Cantidad", text="Cantidad", color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

# Ficha
else:
    st.title("📋 Ficha Individual del Estudiante")
    st.markdown("---")
    if len(df_filtrado):
        seleccionado = st.selectbox("Seleccionar Estudiante", df_filtrado["ID_alumno"].tolist())
        row = df_filtrado[df_filtrado["ID_alumno"] == seleccionado].iloc[0]
        c1,c2,c3 = st.columns(3)
        c1.metric("Estudiante", row["Estudiante"])
        c2.metric("Curso", row["Curso"])
        c3.metric("Nivel", row["Nivel_apoyo"])
        nombres, valores = [], []
        for e in columnas_ensayos:
            if e in row.index and pd.notna(row[e]):
                nombres.append(e.replace("Simce ", "Ensayo "))
                valores.append(row[e])
        if valores:
            fig = go.Figure(go.Scatterpolar(r=valores, theta=nombres, fill="toself", line=dict(width=3)))
            fig.update_layout(polar=dict(radialaxis=dict(range=[0,1], tickformat=".0%")), height=450)
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Resultados por Ensayo")
        tabla = pd.DataFrame({"Ensayo": nombres, "Puntaje": [f"{v:.2%}" for v in valores]})
        st.dataframe(tabla, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos para los filtros seleccionados.")
