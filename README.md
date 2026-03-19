# Generador y Validador de Gramáticas Formales

Este proyecto es una herramienta educativa desarrollada en **Python** con una interfaz gráfica basada en **Tkinter**. Permite la definición, clasificación y validación de gramáticas formales (Tipo 2 y Tipo 3) siguiendo la jerarquía de Chomsky.

## 🚀 Características Principales

-   **Definición Dinámica:** Interfaz amigable para ingresar símbolos iniciales, terminales, no terminales y reglas de producción.
-   **Clasificación de Gramáticas:** Identificación automática de gramáticas como **Regulares (Tipo 3)** o **Libres de Contexto (Tipo 2)**.
-   **Validación de Cadenas:**
    -   **Algoritmo CYK:** Para comprobar la pertenencia de cadenas en gramáticas de Tipo 2.
    -   **Simulación Directa:** Para gramáticas de Tipo 3.
-   **Derivación Paso a Paso:** Visualización del proceso de derivación por la izquierda para entender cómo se generan las cadenas.
-   **Conversión a FNC:** Transformación automática a la **Forma Normal de Chomsky**.
-   **Generador de Cadenas:** Generación aleatoria de palabras válidas de una longitud específica.
-   **Persistencia:** Guardado y carga de gramáticas en formato **JSON**.

## 📂 Estructura del Proyecto

-   `main.py`: Punto de entrada que inicializa la aplicación.
-   `GrammarApp.py`: Gestión de la interfaz gráfica y eventos de usuario.
-   `GrammarLogic.py`: Núcleo lógico con los algoritmos de validación y transformación.
-   `Constants.py`: Definiciones globales y constantes del sistema.

## 🛠️ Requisitos e Instalación

1.  Asegúrate de tener **Python 3.x** instalado.
2.  Clona este repositorio:
    ```bash
    git clone https://github.com/TuUsuario/GramaticsGenerator.git
    ```
3.  Ejecuta la aplicación:
    ```bash
    python main.py
    ```

## 📖 Uso

1.  Define los **Terminales** y **No Terminales** separados por comas.
2.  Establece el **Símbolo Inicial**.
3.  Añade las **Producciones** (usa `->` para separar el lado izquierdo del derecho).
4.  Haz clic en **Validar Tipo** para clasificar la gramática.
5.  Prueba cadenas específicas en la sección de **Validación** o genera cadenas aleatorias.

---
Desarrollado como herramienta de apoyo para el estudio de **Lenguajes Formales y Autómatas**.
