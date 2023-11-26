import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

# Función para calcular los pesos a partir de la matriz de comparación
def calcular_pesos(matriz):
    cant = matriz.shape[0]
    productos = np.prod(matriz, axis=1)
    raices = productos ** (1 / cant)
    pesos = raices / raices.sum()
    return pesos

# Función principal de la app de Streamlit
def app():
    #  Imágenes
    logoUPME = Image.open('img/UPME.png')
    logoUdeA = Image.open('img/UdeA.png')

    # Layout imágenes
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(logoUPME)
    with col2:
        st.image(logoUdeA)
    
    # HTML para título y subtítulos
    st.markdown("""
    <h1 style='text-align: center; font-size: 36px;'>Modelo de Conflictividad Socio-Ambiental</h1>
    <h3 style='text-align: center; font-size: 30px;'>Ponderación de Variables <br> Analytic Hierarchy Process - AHP</h3>
    """, unsafe_allow_html=True)

    # Captura número de criterios
    cant = st.number_input("¿CUÁNTOS CRITERIOS DESEA EVALUAR?", min_value=2, max_value=15, step=1)

    # Si se ha establecido un número de criterios, solicitar sus nombres
    if cant > 0:
        criterios = [st.text_input(f"Nombre del criterio {i+1}:", key=f"criterio_{i}") for i in range(cant)]
    
    if all(criterios):
        # Crear una matriz de comparación
        matriz = np.ones((cant, cant))
        
        with st.form("matriz_comparacion"):
            st.subheader("Matriz de Comparación")
            # Crear campos de entrada para comparaciones
            opciones = [
                ("Igualmente importante", 1),
                ("Ligeramente más importante", 3),
                ("Bastante más importante", 5),
                ("Considerablemente más importante", 7),
                ("Absolutamente más importante", 9),
            ]
            for i in range(cant):
                for j in range(i+1, cant):
                    # Usar un selectbox con texto en lugar de números
                    opcion = st.selectbox(f"Cómo definirías la comparación entre {criterios[i]} y {criterios[j]}:", 
                                          options=[o[0] for o in opciones], 
                                          format_func=lambda x: x,
                                          key=f"select_{i}_{j}")
                    # Encontrar el valor numérico correspondiente a la opción de texto
                    valor = next(val for text, val in opciones if text == opcion)
                    matriz[i, j] = valor
                    matriz[j, i] = 1 / valor
            
            # Botón de envío
            submitted = st.form_submit_button("Calcular pesos")
            if submitted:
                # Calcular pesos
                pesos = calcular_pesos(matriz)
                # Mostrar pesos en formato de porcentaje
                st.subheader("Pesos calculados:")
                pesos_porcentaje = pd.Series(pesos * 100, index=criterios)
                st.dataframe(pesos_porcentaje.to_frame(name="Peso (%)"))

if __name__ == "__main__":
    app()


       # Agregar los créditos e la parte inferior
    st.markdown("""
        <style>
        .credits {
            font-size: 10pt;
            color: gray;
            align: right;
        }
        </style>
        <p class="credits">Developed by: Julián Darío Giraldo Ocampo | ingenieria@juliangiraldo.co</p>
        """, unsafe_allow_html=True)