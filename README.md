# Brainee ByteTutor  
*(Temas Selectos de Análisis de Datos ITAM – Primavera 2025)*  

![Logo](imgs/Brainee_ByteTutor.png)

Repositorio de un asistente de estudio inteligente que permite al usuario cargar material en PDF/TXT y, mediante LLMs y búsqueda vectorial, generar automáticamente preguntas de comprensión, resúmenes y estrategias de estudio adaptadas a su estilo de aprendizaje y nivel de conocimiento.

---

## Autor

| Nombre                    | CU     | Correo Electrónico          | Usuario GitHub |
|---------------------------|--------|-----------------------------|----------------|
| Yuneri Pérez Arellano     | 199813 | yperezar@itam.mx            | YunPerez       |

---

## Contexto 🧠

- En el marco del curso **Temas Selectos de Análisis de Datos**, necesitamos prototipar un asistente que ayude a estudiantes a digerir material de estudio (artículos, apuntes, PDFs) de forma interactiva y personalizada.  
- El asistente debe:  
  1. Leer y limpiar texto de PDFs/TXT.  
  2. Generar preguntas de comprensión con opciones múltiples.  
  3. Ofrecer resúmenes breves.  
  4. Proponer estrategias de estudio y actividades prácticas según el estilo de aprendizaje (visual, auditivo, kinestésico, lectura/escritura) y nivel de conocimiento (principiante, intermedio, avanzado).  
  5. Permitir consultas específicas al contenido mediante RAG (búsqueda vectorial + LLM).  
  6. Llevar un seguimiento de progreso de uso.

---

## Objetivo del proyecto 🎯

Desarrollar un prototipo en Python que integre:  
1. **Ingestión de material** (PDF/TXT).  
2. **Generación de preguntas** de comprensión con 3 opciones y respuesta correcta.  
3. **Resumen automático** del texto.  
4. **Adaptación personalizada**: diagramas, podcasts, role-plays o flashcards según el estilo del estudiante.  
5. **Búsqueda de respuestas** a consultas puntuales vía vector search.  
6. **Seguimiento de progreso** de uso.

---

## Infraestructura y Ejecución ⚙

### Requisitos de software

- Github
- VSCode u otro IDE
- Python 3.9+  
- Conda (opcional pero recomendado) 

### Instalación

```bash
git clone https://github.com/YunPerez/Studio_Assistant_Agent.git
cd Studio_Assistant_Agent

# Crear entorno y activar
conda env create --file environments.yml
conda activate studio_assistant-env

# Instalar requisitos pip
pip install -r requirements.txt
```
### Ejecución

```bash
streamlit run app.py
```
### Estructura del repositorio

```bash
.
├── README.md
├── app.py
├── docs
│   ├── Qué es una IA conversacional.pdf
│   ├── Qué es una IA conversacional.txt
│   ├── Qué son los modelos de lenguaje de gran tamaño.pdf
│   ├── Qué son los modelos de lenguaje de gran tamaño.txt
│   ├── llm_ai_agents.pdf
│   └── llm_ai_agents.txt
├── environments.yml
├── exports
├── imgs
│   └── Brainee_ByteTutor.png
├── progress.json
├── requirements.txt
└── src
    ├── study_agent.py
    └── user_model.py
```

### Pantallas
![ejemplo_inicio](imgs/inicio.png)
![ejemplo_preguntas](imgs/preguntas.png)
![ejemplo_resumen](imgs/resumen.png)
![ejemplo_estilo](imgs/estilo.png)

### Diagrama de arquitectura
![Diagrama de arquitectura](imgs/arquitectura.png)