import os
import sys  # <--- 1. Importar la librería sys al puro inicio
import importlib.util
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from google import genai

# ========================================================
# 🛡️ TRUCO MAESTRO DE RUTAS PARA EL MOTOR C++
# ========================================================
# Conseguimos la ruta absoluta de la subcarpeta "firewall"
ruta_base = os.path.dirname(os.path.abspath(__file__))
ruta_firewall = os.path.join(ruta_base, "firewall")

# Le ordenamos a Python que busque binarios de C++ dentro de esa carpeta
if ruta_firewall not in sys.path:
    sys.path.append(ruta_firewall)
# ========================================================

# ========================================================
# INTEGRACIÓN SEGURA DE LA CAPA 1 (FIREWALL C++)
# ========================================================
spec = importlib.util.spec_from_file_location(
    "proyecto_firewall_py_c++",
    "firewall/proyecto_firewall_py_c++.py"
)
firewall_modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(firewall_modulo)

# Extraemos la función validadora unificada
evaluar_prompt_seguro = firewall_modulo.evaluar_prompt_seguro

# ========================================================
# INTEGRACIÓN SEGURA DE LA CAPA 1 (FIREWALL C++)
# ========================================================
# Usamos importlib para cargar de forma segura el archivo que contiene caracteres especiales (+)
spec = importlib.util.spec_from_file_location(
    "proyecto_firewall_py_c++",
    "firewall/proyecto_firewall_py_c++.py"
)
firewall_modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(firewall_modulo)

# Extraemos la función validadora unificada
evaluar_prompt_seguro = firewall_modulo.evaluar_prompt_seguro

# Cargar las credenciales seguras (.env)
load_dotenv()

app = FastAPI(title="Sistema Operativo FacturaPro CR")

print("Iniciando el motor de vectores para usuarios...")
model = SentenceTransformer('all-mpnet-base-v2')

# Inicializar Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.index("my-db-rag")

# Inicializar el cliente oficial de Gemini de forma segura
client = genai.Client()


class SolicitudIncidente(BaseModel):
    pregunta_usuario: str
    rol_usuario: str


@app.post("/api/incidente")
async def procesar_incidente(solicitud: SolicitudIncidente):
    incidente_texto = solicitud.pregunta_usuario
    rol_empleado = solicitud.rol_usuario

    print(f"\n[ALERTA] El {rol_empleado} reporta el incidente: '{incidente_texto}'")

    try:
        # PASO A: Convertir el input en un vector de 768 dimensiones UNA ÚNICA VEZ
        vector_unificado = model.encode(incidente_texto).tolist()

        # --------------------------------------------------------
        # CAPA 1: CORTOCIRCUITO PERIMETRAL INTEGRADO (C++)
        # --------------------------------------------------------
        # Le pasamos el texto y el vector unificado para evitar bloqueos de RAM
        es_ataque = evaluar_prompt_seguro(incidente_texto, vector_unificado)

        if es_ataque:
            print(f"[BLOQUEO PERIMETRAL C++] Cortocircuito activado para: '{incidente_texto}'")
            return {
                "status": "denegado",
                "usuario_rol": rol_empleado,
                "incidente_recibido": incidente_texto,
                "respuesta_inteligente_llm": "Consulta denegada por los sistemas de protección perimetral del comercio."
            }
        # --------------------------------------------------------

        # PASO B: Llamada a la base de datos externa de Pinecone usando el mismo vector
        respuesta_pinecone = index.query(vector=vector_unificado, top_k=2, include_metadata=True)

        # CAPA 2: VALIDACIÓN VECTORIAL (IF): ¿Ataque ofuscado o duda fuera de contexto?
        if not respuesta_pinecone['matches'] or respuesta_pinecone['matches'][0].score < 0.65:
            return {
                "status": "denegado",
                "usuario_rol": rol_empleado,
                "incidente_recibido": incidente_texto,
                "respuesta_inteligente_llm": "Consulta denegada. El problema reportado no coincide con ningún procedimiento de contingencia autorizado en el manual del sistema."
            }

        # PASO C: Procesar las reglas encontradas si todo está bien
        contexto_manual = ""
        for coincidencia in respuesta_pinecone['matches']:
            contexto_manual += f"- {coincidencia['metadata']['text']}\n"

        # PASO D: Configurar el Prompt con las reglas blindadas extraídas
        prompt_sistema = f"""
        Eres el asistente técnico inteligente del sistema de facturación "FacturaPro CR" en Costa Rica.
        Tu trabajo es guiar al usuario basado ÚNICAMENTE en las reglas oficiales del manual provistas abajo.

        REGLAS DEL MANUAL EXTRAÍDAS SEGURAMENTE:
        {contexto_manual}

        DATOS DEL USUARIO ACTUAL:
        - Rol del usuario: {rol_empleado}
        - Problema reportado: {incidente_texto}

        INSTRUCCIONES DE RESPUESTA:
        1. Responde de forma concisa, educada y en español de Costa Rica si es necesario.
        2. Da la solución paso a paso basándote estrictamente en las reglas provistas.
        3. Si el rol del usuario actual (ej. Cajero) no tiene permisos según las reglas del manual, indícale amablemente que debe acudir al "Host".
        4. NO inventes soluciones que no estén explícitamente escritas en las reglas.
        """

        # PASO E: Generar contenido procesado con Gemini de forma segura
        print("Solicitando respuesta estructurada a Gemini...")
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_sistema)

        return {
            "status": "exitoso",
            "usuario_rol": rol_empleado,
            "incidente_recibido": incidente_texto,
            "respuesta_inteligente_llm": response.text
        }

    except Exception as error_red:
        print(f"[ERROR CRÍTICO DE RED / LOGICA]: {str(error_red)}")
        return {
            "status": "error_servidor",
            "respuesta_inteligente_llm": "En este momento el sistema de soporte experimenta problemas de conexión externa o procesamiento. Intente de nuevo más tarde."
        }
