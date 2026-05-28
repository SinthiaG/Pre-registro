# Pre-registro - Auditoría Inteligente de Siniestros

Proyecto de experimentación orientado a la auditoría inteligente de facturas de siniestros vehiculares utilizando Neo4j, GraphRAG, LLMs y consultas en lenguaje natural.

---

# 🚗 Descripción General

Este proyecto implementa un flujo completo de auditoría automatizada para validar facturación de siniestros vehiculares enviados por talleres hacia aseguradoras.

La solución integra:

* Grafos de conocimiento con Neo4j
* IA generativa y modelos LLM
* Consultas en lenguaje natural
* Procesamiento documental
* Detección de inconsistencias
* Análisis contextual de siniestros

El sistema permite detectar automáticamente:

✅ Sobrecostos
✅ Cobros duplicados
✅ Inconsistencias entre daños y facturación
✅ Facturación fuera de tarifario
✅ Elementos sin respaldo visual o documental

---

# 🎯 Objetivo

Construir un flujo inteligente que permita:

* Generar datos de prueba (tarifarios, órdenes y facturas XML).
* Convertir documentos de siniestro a una estructura de grafo en Neo4j.
* Consultar y auditar el grafo mediante lenguaje natural.
* Emitir reportes automáticos de hallazgos y recomendaciones.

---

# 🧠 Tecnologías Utilizadas

## Inteligencia Artificial

* OpenAI API
* Large Language Models (LLMs)
* Agentic AI
* GraphRAG

## Base de Datos

* Neo4j

## Backend y Procesamiento

* Python
* Cypher Query Language
* Pydantic
* Pandas

## Procesamiento Inteligente

* Retrieval-Augmented Generation (RAG)
* Text2Cypher
* Procesamiento documental
* Detección visual con modelos de visión

---

# 📂 Estructura Real del Proyecto

```text
Pre-registro/
├── RagModels/
│   ├── IARAG_GENERADOR_FACTURAS.ipynb
│   ├── IARAG_RETRIEVAL.ipynb
│   ├── IARAG_GENERATION.ipynb
│   └── neo_conector.py
│
├── data/
│   ├── OI-2026-1088/
│   ├── OI-2026-1089/
│   ├── OI-2026-1090/
│   └── OI-2026-1091/
│
├── Facturas/
│   ├── facturas_emitidas/
│   ├── ordenes_reparacion.json
│   └── tarifario_seguros.json
│
├── bd_aseguradora/
│   ├── ordenes_reparacion.json
│   └── tarifario_seguros.json
│
├── models/
│   └── car-parts/
│
├── auditor_siniestros.py
└── README.md
```

---

# 📘 Componentes Principales

## `IARAG_GENERADOR_FACTURAS.ipynb`

Notebook encargado de:

* Generar tarifarios sintéticos
* Crear órdenes de reparación
* Simular facturas XML
* Insertar escenarios:

  * Normales
  * Sobrecostos
  * Valores duplicados

También incluye utilidades para carga hacia Neo4j.

---

## `IARAG_RETRIEVAL.ipynb`

Implementa:

* Extracción estructurada de documentos
* Conversión de datos hacia Neo4j
* Modelo de entidades y relaciones
* Procesamiento de facturas XML
* Integración de evidencia visual

Contempla detección de partes vehiculares mediante modelos de visión.

---

## `IARAG_GENERATION.ipynb`

Implementa el flujo de auditoría en lenguaje natural:

* Conversión Text2Cypher
* Consultas inteligentes
* Análisis contextual
* Comparación contra tarifarios
* Evaluación de siniestralidad

Ejemplos de preguntas:

* ¿Existen costos duplicados?
* ¿La factura coincide con los daños reportados?
* ¿Qué items exceden el tarifario oficial?

---

## `neo_conector.py`

Conector utilitario para Neo4j que permite:

* Ejecutar consultas Cypher
* Gestionar conexiones
* Ejecutar operaciones parametrizadas

---

## `auditor_siniestros.py`

Script principal de auditoría automática.

Responsabilidades:

* Obtener contexto desde Neo4j
* Cruzar información:

  * Facturas
  * Vehículos
  * Accidentes
  * Evidencia visual
  * Tarifario oficial
* Generar informes inteligentes usando OpenAI

---

# ⚙️ Flujo Funcional del Proyecto

## 1. Generación de Datos

Se generan:

* Tarifarios
* Órdenes de reparación
* Facturas XML
* Casos sintéticos de auditoría

---

## 2. Ingesta y Modelado en Neo4j

Se crean nodos y relaciones para:

* Vehículos
* Accidentes
* Daños
* Facturas
* Talleres
* Órdenes de ingreso
* Repuestos

---

## 3. Enriquecimiento con Evidencia

Se integran:

* Documentos
* Imágenes
* Detecciones visuales
* Hallazgos automáticos

---

## 4. Consulta y Auditoría Inteligente

El usuario puede realizar preguntas en lenguaje natural.

El sistema:

1. Interpreta la intención
2. Genera consultas Cypher
3. Recupera contexto desde el grafo
4. Analiza inconsistencias

---

## 5. Generación de Reporte Final

El LLM produce:

* Conclusión de auditoría
* Riesgos detectados
* Recomendaciones
* Sugerencia de Aprobación o Rechazo

---

# 🔗 Modelo Basado en Grafos

La solución utiliza Neo4j y GraphRAG para conectar:

* Vehículos
* Accidentes
* Facturas
* Repuestos
* Propietario
* Talleres
* Evidencia visual
* Tarifarios

Esto permite:

✅ Trazabilidad contextual
✅ Consultas semánticas avanzadas
✅ Reducción de alucinaciones
✅ Relación directa daño-costo
✅ Auditorías explicables

---

# 📊 Casos de Auditoría Cubiertos

* Detección de sobrecostos frente al tarifario.
* Validación entre daños reportados y factura.
* Revisión de respaldo visual para items facturados.
* Detección de duplicidades.
* Identificación de inconsistencias estructurales.

---

# 🔐 Variables de Entorno

Crear un archivo `.env`:

```env
NEO4J_URI=neo4j+s://tu-instancia.databases.neo4j.io
NEO4J_USERNAME=usuario
NEO4J_PASSWORD=contrasena
OPENAI_API_KEY=tu_api_key
```

---

# ▶️ Ejecución Rápida

## 1. Generar o cargar datos

Ejecutar notebooks dentro de:

```bash
RagModels/
```

---

## 2. Verificar Neo4j

Confirmar que existan:

* Nodos
* Relaciones
* Facturas
* Órdenes
* Evidencia

---

## 3. Ejecutar auditoría

```bash
python auditor_siniestros.py
```

Por defecto se audita el siniestro en funcion del nodod procioan l que al oriden d eignreso.:

```text
Texto: Orden de ingreso OI-2026-1088
Python: ID_ORDEN_INGRESO = OI-2026-1088
DB: Nodo OrdenIngreso(:order_id)
LLM: orderId
```

---

# 📦 Dependencias Observadas

El proyecto actualmente no posee un `requirements.txt` consolidado.

Dependencias identificadas:

* neo4j
* openai
* pandas
* pydantic
* python-dotenv
* tiktoken
* ultralytics

---

# 🚧 Estado del Proyecto

Proyecto en desarrollo orientado a:

* Experimentación técnica
* Validación funcional
* Investigación aplicada con IA agéntica
* Auditoría inteligente basada en grafos

---

# 👥 Equipo

## Miguel Ponce

MSc. en Inteligencia Artificial y MSc. en Ciencia de Datos.

## Sinthia Guaigua

MSc. en Ciencia de Datos.

## Ing. Luis Pumisacho

Estudiante de la Maestría en Inteligencia Artificial.

---

# 📚 Referencias

* Essential GraphRAG — O’Reilly Media
* Neo4j Graph Database
* OpenAI API
* Retrieval-Augmented Generation (RAG)

---
