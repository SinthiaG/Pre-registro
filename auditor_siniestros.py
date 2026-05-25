import os
import logging
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class AuditorSiniestros:
    def __init__(self, uri, user, password):
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("Conexión exitosa con Neo4j.")
        except Exception as e:
            logger.error(f"Error al conectar con Neo4j: {e}")
            raise

    def close(self):
        self.driver.close()

    def auditar_factura(self, fac_id):
        with self.driver.session() as session:
            # Obtener datos generales del vehículo
            query_info = """
            MATCH (f:Factura {facId: $fid})-[:PARA_VEHICULO]->(v:Vehiculo)
            RETURN v.marca as marca, v.modelo as modelo, v.placa as placa
            """
            info = session.run(query_info, fid=fac_id).single()
            
            print(f"\n====================================================")
            print(f"--- AUDITANDO FACTURA: {fac_id} ---")
            if info:
                print(f"Vehículo: {info['marca']} {info['modelo']} (Placa: {info['placa']})")
            print(f"====================================================\n")

            # 1. Sobrecargos de Precio
            self._check_sobrecargos(session, fac_id)
            
            # 2. Ítems No Detectados en Imágenes
            self._check_detecciones(session, fac_id)
            
            # 3. Ítems Duplicados
            self._check_duplicados(session, fac_id)
            
            # 4. Ítems No Autorizados para el Tipo de Siniestro
            self._check_autorizacion_siniestro(session, fac_id)

    def _check_sobrecargos(self, session, fac_id):
        print("\nA) Verificando Sobrecargos de Precio...")
        query = """
        MATCH (f:Factura {facId: $fid})-[:CONTIENE]->(df:DetalleFactura)
        MATCH (f)-[:PARA_VEHICULO]->(v:Vehiculo)
        MATCH (f)-[:BASADA_EN]->(oi:OrdenIngreso)-[:REGISTRA]->(acc:Accidente)
        MATCH (ma:Marca {nombre: v.marca})-[:TIENE_MODELO]->(mo:Modelo {nombre: v.modelo, anio: v.anio})
        MATCH (mo)-[:SUFRE]->(s:Siniestro {tipo: acc.tipoAccidente})
        MATCH (s)-[rel:INCLUYE]->(i:Item {nombre: df.desc})
        WHERE df.p > (rel.precio + 0.01)
        RETURN df.desc as item, df.p as cobrado, rel.precio as acordado
        """
        results = session.run(query, fid=fac_id)
        found = False
        for record in results:
            found = True
            print(f"  [ALERTA] '{record['item']}' tiene sobrecargo: Cobrado ${record['cobrado']} | Acordado ${record['acordado']}")
        if not found:
            print("  ✓ Todos los precios cumplen con el tarifario.")

    def _check_detecciones(self, session, fac_id):
        print("\nB) Verificando Detecciones en Imágenes...")
        query = """
        MATCH (f:Factura {facId: $fid})-[:CONTIENE]->(df:DetalleFactura)
        MATCH (f)-[:BASADA_EN]->(oi:OrdenIngreso)-[:REGISTRA]->(acc:Accidente)
        OPTIONAL MATCH (acc)-[:TIENE_IMAGEN]->(img:Imagen)-[:TIENE_DETECCION]->(d:Deteccion)
        WHERE toLower(d.descripcion) = toLower(df.desc)
        WITH df, count(d) as num_detecciones
        WHERE num_detecciones = 0
        RETURN df.desc as item
        """
        results = session.run(query, fid=fac_id)
        found = False
        for record in results:
            found = True
            print(f"  [ALERTA] '{record['item']}' facturado pero NO detectado en las imágenes del siniestro.")
        if not found:
            print("  ✓ Todos los ítems facturados tienen evidencia visual detectada.")

    def _check_duplicados(self, session, fac_id):
        print("\nC) Verificando Ítems Duplicados por Orden de Ingreso...")
        query = """
        MATCH (f1:Factura)-[:CONTIENE]->(d1:DetalleFactura)
        MATCH (f2:Factura)-[:CONTIENE]->(d2:DetalleFactura)
        WHERE d1.desc = d2.desc AND elementId(d1) < elementId(d2)
        MATCH (f1)-[:BASADA_EN]->(oi:OrdenIngreso)
        MATCH (f2)-[:BASADA_EN]->(oi)
        WHERE f1.facId = $fid OR f2.facId = $fid
        RETURN d1.desc as item, f1.facId as f1, f2.facId as f2
        """
        results = session.run(query, fid=fac_id)
        found = False
        for record in results:
            found = True
            if record['f1'] == record['f2']:
                print(f"  [ALERTA] '{record['item']}' duplicado dentro de la misma factura.")
            else:
                otra = record['f2'] if record['f1'] == fac_id else record['f1']
                print(f"  [ALERTA] '{record['item']}' ya fue cobrado en la factura {otra}.")
        if not found:
            print("  ✓ No se detectaron ítems duplicados.")

    def _check_autorizacion_siniestro(self, session, fac_id):
        print("\nD) Verificando Autorización por Tipo de Siniestro...")
        query = """
        MATCH (f:Factura {facId: $fid})-[:CONTIENE]->(df:DetalleFactura)
        MATCH (f)-[:PARA_VEHICULO]->(v:Vehiculo)
        MATCH (f)-[:BASADA_EN]->(oi:OrdenIngreso)-[:REGISTRA]->(acc:Accidente)
        MATCH (ma:Marca {nombre: v.marca})-[:TIENE_MODELO]->(mo:Modelo {nombre: v.modelo, anio: v.anio})
        MATCH (mo)-[:SUFRE]->(s:Siniestro {tipo: acc.tipoAccidente})
        WHERE NOT (s)-[:INCLUYE]->(:Item {nombre: df.desc})
        RETURN df.desc as item, s.tipo as tipo_siniestro
        """
        results = session.run(query, fid=fac_id)
        found = False
        for record in results:
            found = True
            print(f"  [ALERTA] '{record['item']}' no es un ítem autorizado para un siniestro tipo '{record['tipo_siniestro']}'.")
        if not found:
            print("  ✓ Todos los ítems son consistentes con el tipo de siniestro.")

    def procesar_consulta_ln(self, mensaje):
        """
        Interfaz de lenguaje natural para procesar consultas.
        Busca patrones de IDs de facturas (ej: FAC001) o palabras clave.
        """
        import re
        print(f"\n> Procesando consulta: '{mensaje}'")
        
        # Buscar IDs de factura con patrón FAC + números
        facturas_encontradas = re.findall(r'FAC\d+', mensaje.upper())
        
        if facturas_encontradas:
            for fid in facturas_encontradas:
                self.auditar_factura(fid)
        elif "TODO" in mensaje.upper() or "TODAS" in mensaje.upper() or "SINIESTRO" in mensaje.upper():
            print("Identificada solicitud global. Auditando últimas facturas...")
            with self.driver.session() as session:
                res = session.run("MATCH (f:Factura) RETURN f.facId as id ORDER BY f.facId DESC LIMIT 5")
                for r in res:
                    self.auditar_factura(r['id'])
        else:
            print("No pude identificar una factura específica. Intenta con algo como: 'Verifica la factura FAC001'")

if __name__ == "__main__":
    # Inicializar auditor
    auditor = AuditorSiniestros(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    # Ejemplo de uso con lenguaje natural
    consultas_ejemplo = [
        "¿Hay alguna alerta en la factura FAC001?",
        "Verifica si el siniestro tiene alertas de auditoria (revisar todas)",
    ]
    
    for consulta in consultas_ejemplo:
        auditor.procesar_consulta_ln(consulta)
        
    auditor.close()
