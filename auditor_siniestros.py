import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv
from openai import OpenAI

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AuditorSiniestros:
    def __init__(self, uri, user, password, openai_key=None):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("Conexión exitosa con Neo4j.")
            self.llm_client = OpenAI(api_key=openai_key) if openai_key else None
        except Exception as e:
            logger.error(f"Error al conectar con Neo4j: {e}")
            raise

    def close(self):
        self.driver.close()

    def auditar_con_llm(self, fac_id):
        """
        Realiza una auditoría avanzada usando el LLM (GPT-4o), extrayendo el contexto del grafo
        y utilizando el archivo JSON del tarifario como fuente oficial de precios.
        """
        if not self.llm_client:
            print("[ERROR] No se ha configurado la API Key de OpenAI para auditoría LLM.")
            return

        import json
        print(f"\n[LLM] Iniciando Auditoría Inteligente para Factura: {fac_id}...")
        
        # 1. Cargar Tarifario Oficial desde JSON
        try:
            with open("bd_aseguradora/tarifario_seguros.json", "r", encoding="utf-8") as f:
                tarifario_completo = json.load(f)
        except Exception as e:
            print(f"[ERROR] No se pudo cargar el tarifario JSON: {e}")
            return

        with self.driver.session() as session:
            # 2. Extraer Contexto del Grafo
            contexto_query = """
            MATCH (f:Factura)
            WHERE f.FactId = $fid OR f.facId = $fid
            OPTIONAL MATCH (f)-[:PARA_VEHICULO]->(v:Vehiculo)
            OPTIONAL MATCH (f)-[:BASADA_EN]->(oi:OrdenIngreso)-[:REGISTRA]->(acc:Accidente)
            OPTIONAL MATCH (f)-[:CONTIENE]->(df:DetalleFactura)
            OPTIONAL MATCH (acc)-[:TIENE_IMAGEN]->(img:Imagen)-[:TIENE_DETECCION]->(det:Deteccion)

            WITH f, v, acc, 
                 collect(distinct {item: df.desc, precio_cobrado: df.p}) as detalles,
                 collect(distinct {descripcion: det.descripcion, confianza: det.confianza}) as detecciones
            
            RETURN {
                factura: {id: coalesce(f.FactId, f.facId)},
                vehiculo: {marca: v.marca, modelo: v.modelo, anio: v.anio, placa: v.placa},
                accidente: {tipo: acc.tipoAccidente, descripcion: acc.descripcion, gravedad: acc.gravedad},
                detalles_factura: detalles,
                detecciones_ia: detecciones
            } as contexto
            """
            
            res = session.run(contexto_query, fid=fac_id).single()
            if not res or not res['contexto']['factura']['id']:
                print(f"No se encontró información suficiente en Neo4j para la factura {fac_id}.")
                return
                
            contexto = res['contexto']
            
            # 3. Filtrar Tarifario para el vehículo y siniestro específico (Lógica Robusta)
            marca_f = str(contexto['vehiculo'].get('marca') or "").strip().lower()
            modelo_f = str(contexto['vehiculo'].get('modelo') or "").strip().lower()
            anio_f = contexto['vehiculo'].get('anio')
            tipo_siniestro_f = str(contexto['accidente'].get('tipo') or "").strip().lower()
            
            print(f"[DEBUG] Buscando tarifario para: {marca_f} {modelo_f} ({anio_f})")

            # Intento 1: Match por Marca y Modelo (Independiente del año/siniestro para dar contexto al LLM)
            tarifario_relevante = [
                item for item in tarifario_completo 
                if str(item.get('marca')).strip().lower() == marca_f 
                and str(item.get('modelo')).strip().lower() == modelo_f
            ]

            # Intento 2: Si no hay match exacto de modelo, buscar por marca para al menos dar una idea de precios
            if not tarifario_relevante:
                print(f"[DEBUG] No hay match exacto para {modelo_f}. Buscando por marca {marca_f}...")
                tarifario_relevante = [
                    item for item in tarifario_completo 
                    if str(item.get('marca')).strip().lower() == marca_f
                ]

            print(f"[DEBUG] Se encontraron {len(tarifario_relevante)} items de referencia en el tarifario.")

            # 4. Construir Prompt para el LLM
            prompt = f"""
            Eres un experto auditor de siniestros vehiculares. Tu objetivo es detectar anomalías, fraudes o inconsistencias.
            
            --- CONTEXTO DEL SINIESTRO (Desde Neo4j) ---
            - Vehículo: {contexto['vehiculo']}
            - Accidente Reportado: {contexto['accidente']}
            
            --- DATOS DE FACTURACIÓN (Desde Neo4j) ---
            - Items Facturados: {contexto['detalles_factura']}
            
            --- TARIFARIO OFICIAL DE REFERENCIA (Desde JSON) ---
            - Precios Acordados: {tarifario_relevante}
            
            --- EVIDENCIA VISUAL (Desde Neo4j - IA) ---
            - Detecciones encontradas en fotos: {contexto['detecciones_ia']}
            
            --- TAREAS DE AUDITORÍA ---
            1. SOBRECARGOS: Compara 'precio_cobrado' en la factura vs 'precio_acordado' en el tarifario JSON. Señala cualquier exceso.
            2. EVIDENCIA VISUAL: Señala si un ítem facturado NO tiene una detección de la IA que lo respalde.
            3. COHERENCIA DEL SINIESTRO: ¿Tienen sentido las piezas cambiadas dada la descripción del accidente?
            4. INTEGRIDAD: Busca ítems duplicados o errores en la identidad del vehículo (Placa/Modelo).
            
            Responde con un informe profesional en formato Markdown. 
            Finaliza con una recomendación clara: [APROBADA], [RECHAZADA] o [REVISIÓN MANUAL].
            """
            
            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Eres un auditor de seguros de alta precisión especializado en cruce de datos documentales, visuales y financieros."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                
                reporte = response.choices[0].message.content
                print("\n" + "="*50)
                print(f"REPORTE DE AUDITORÍA INTELIGENTE: {fac_id}")
                print("="*50)
                print(reporte)
                print("="*50 + "\n")
            except Exception as e:
                print(f"Error al llamar a la API de OpenAI: {e}")

if __name__ == "__main__":
    # Inicializar auditor con credenciales
    auditor = AuditorSiniestros(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_API_KEY)
    
    # Ejemplo de ejecución: Auditar la factura deseada
    # Nota: Asegúrate de que el facId exista en tu base de datos Neo4j
    fac_id_test = "FAC088" 
    auditor.auditar_con_llm(fac_id_test)
        
    auditor.close()
