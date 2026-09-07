# CloudOps AI

Español | [English](README_en.md)

Asistente de IA diseñado para la nube que transforma documentación operativa en respuestas consultables y respaldadas por sus fuentes.

El proyecto cubre el ciclo completo de desarrollo, validación, despliegue y operación: aplicación RAG, contenerización, observabilidad, infraestructura como código y CI/CD automatizado en Azure mediante GitHub Actions y autenticación federada OIDC.

## Descripción

CloudOps AI es un proyecto de ingeniería que combina una aplicación RAG con las prácticas necesarias para ejecutarla, desplegarla y operarla. Permite incorporar documentación, buscar información mediante similitud semántica y generar respuestas contextualizadas con referencias a las fuentes utilizadas.

El proyecto incluye un entorno local completo con Docker Compose y observabilidad, además de una demo mínima desplegada en Azure mediante Terraform y GitHub Actions. Ambas arquitecturas tienen objetivos diferentes: el entorno local funciona como laboratorio técnico, mientras que Azure prioriza un coste reducido, seguridad y escalado a cero.

## Funcionalidades principales

- Ingestión de conocimiento desde archivos, directorios locales y páginas de Notion.
- División de documentos en fragmentos, generación de embeddings y almacenamiento en Qdrant.
- Búsqueda semántica con recuperación de contenido y metadatos.
- Flujo RAG orquestado con LangGraph para clasificar cada pregunta, decidir si requiere contexto de Qdrant y, cuando es necesario, recuperarlo antes de generar y validar la respuesta.
- API desarrollada con FastAPI y una interfaz web sencilla.
- Entorno local reproducible mediante Docker Compose.
- Métricas, logs y trazas en local con Prometheus, Grafana, Loki, Tempo y Alloy.
- Infraestructura Azure gestionada con Terraform.
- Publicación y despliegue automatizados mediante GitHub Actions y autenticación OIDC.


## Cómo funciona

CloudOps AI separa la incorporación del conocimiento y la resolución de consultas en dos flujos relacionados.

### Ingesta de conocimiento

La aplicación recibe contenido desde archivos, directorios locales o páginas de Notion y lo transforma en un formato documental común. Después, divide cada documento en fragmentos, añade los metadatos necesarios y genera sus representaciones vectoriales (embeddings) antes de almacenarlas en Qdrant.

Cuando se vuelve a procesar un documento con el mismo identificador, sus fragmentos anteriores se sustituyen para evitar mantener información duplicada o desactualizada.

![Flujo de ingesta de conocimiento](diagramas_arquitectura/ingestion_pipeline.png)

### Consulta y generación de respuestas

Cuando la API recibe una pregunta, LangGraph coordina el flujo de ejecución. Primero clasifica la consulta y determina si puede responderse directamente o si necesita recuperar información de Qdrant.

Cuando se requiere contexto, la pregunta se convierte en un vector y se utiliza para buscar los fragmentos más relevantes. El contenido recuperado y sus metadatos se incorporan al estado del flujo para generar una respuesta contextualizada, validarla y devolver las fuentes utilizadas.

Cuando la consulta se clasifica como conversacional o no requiere consultar documentación, el flujo omite la recuperación de contexto y genera la respuesta directamente con el LLM.

La validación final comprueba que la respuesta no esté vacía y que exista contexto cuando la consulta requiere recuperación. No verifica la exactitud de la respuesta.

![Flujo de nodos con LangGraph](diagramas_arquitectura/langGraph_nodes.png)

## Arquitectura

CloudOps AI utiliza dos entornos: un laboratorio local para desarrollo y observabilidad, y una demo pública en Azure con una infraestructura reducida.

Esta separación responde al objetivo de mantener un coste reducido en la nube. El entorno local conserva todas las funcionalidades y el stack completo de observabilidad, mientras que la demo en Azure permite probar el flujo de consulta y generación de respuestas, con la ingesta y la exposición pública de métricas deshabilitadas.

![Arquitectura local y Azure](diagramas_arquitectura/Arquitectura_local_cloud.png)

### Entorno local

Docker Compose agrupa la aplicación FastAPI, Qdrant y los servicios de observabilidad:

- **Prometheus:** recopila y almacena métricas.
- **Loki y Alloy:** permiten recoger y consultar los logs.
- **Tempo:** almacena las trazas generadas mediante OpenTelemetry.
- **Grafana:** permite explorar las métricas, los logs y las trazas.

Este entorno permite desarrollar, probar y observar el comportamiento de la aplicación con la configuración del laboratorio versionada en el repositorio.

![Observabilidad local: métricas, logs y trazas](diagramas_arquitectura/Metrics_logging_tracing.png)

### Demo en Azure

La aplicación se ejecuta en Azure Container Apps con el plan Consumption y un escalado de cero a una réplica. Qdrant Cloud almacena el conocimiento vectorizado y los proveedores de IA se consumen como servicios externos.

La infraestructura incluye un registro privado de imágenes en Azure Container Registry, Key Vault para almacenar secretos y una identidad administrada con permisos para acceder a los recursos necesarios. Los logs del entorno se recogen en Log Analytics.

### Decisiones de diseño

El escalado a cero reduce el consumo cuando la aplicación está inactiva, aunque puede añadir tiempo de arranque a la primera petición. Utilizar servicios externos para Qdrant y los modelos de IA simplifica el despliegue, a cambio de depender de su disponibilidad y sus límites de uso.

## Infraestructura y CI/CD

### Infraestructura como código

Los recursos de Azure se gestionan con Terraform, con dos configuraciones separadas:

- **Bootstrap:** crea el almacenamiento necesario para guardar el estado de Terraform en Azure.
- **Demo:** crea y gestiona la infraestructura de la aplicación.

El primer arranque se realiza con el estado de bootstrap guardado localmente, porque el almacenamiento remoto todavía no existe. Una vez creado, ese estado se migra a Azure Blob Storage y se configura la infraestructura de la demo para utilizar también este almacenamiento.

Cada configuración mantiene su propio archivo de estado. Terraform utiliza estos archivos para relacionar los recursos definidos en el código con los que existen en Azure y calcular los cambios necesarios:

- `bootstrap.tfstate`: registra los recursos de preparación, como el grupo de recursos del estado, la cuenta de almacenamiento, el contenedor de blobs, los permisos asociados y el presupuesto.
- `demo.tfstate`: registra la infraestructura de la aplicación, como Container Apps, el registro de imágenes, Key Vault, Log Analytics y las identidades y sus permisos.

Ambos estados se guardan en el mismo contenedor de Azure Blob Storage, pero en archivos separados. Así, los cambios en la aplicación se gestionan desde `demo` sin incluir los recursos de preparación gestionados por `bootstrap`. El acceso al almacenamiento se autentica mediante Microsoft Entra ID.

![Organización de los recursos en Azure](diagramas_arquitectura/Resources_groups.png)

### Validación, publicación y despliegue

GitHub Actions automatiza las comprobaciones del proyecto y la entrega de nuevas versiones:

1. **Validación:** ejecuta las comprobaciones de código con Ruff, las pruebas con pytest y las validaciones de Terraform, workflows y scripts. También comprueba el arranque con Docker Compose y el estado de salud de la API. Estas comprobaciones no necesitan secretos ni llamadas reales a proveedores de IA.
2. **Publicación:** cuando hay cambios relevantes, construye la imagen Docker y la publica en Azure Container Registry. Cada imagen se etiqueta con el SHA completo del commit para relacionarla con el código que la generó y desplegar esa versión concreta.
3. **Despliegue:** tras una publicación correcta, el workflow prepara un plan de Terraform para desplegar la nueva versión. Antes de aplicarlo, un script comprueba que los cambios se limitan a actualizar la Container App existente. Si el plan incluye crear, eliminar o sustituir recursos, o modificar otros componentes de la infraestructura, el despliegue se detiene para revisarlo.
4. **Verificación:** se comprueba la salud de la aplicación y se ejecuta un plan final para confirmar que no quedan diferencias pendientes entre la infraestructura y su configuración.

Tras un despliegue correcto, se conservan la imagen actual y la anterior verificada como saludable. Esta retención limita el almacenamiento ocupado en el registro y mantiene disponible una versión anterior. El rollback automático queda fuera del alcance actual.

### Autenticación y permisos

Terraform crea tres identidades administradas en Azure y asigna a cada una los permisos necesarios para su función:

- **Publicación:** GitHub Actions la utiliza para subir imágenes a Azure Container Registry y eliminar las versiones antiguas durante la limpieza.
- **Despliegue:** GitHub Actions la utiliza para consultar la infraestructura, acceder al estado remoto de Terraform y actualizar la Container App.
- **Ejecución:** se asigna a la Container App para descargar la imagen del registro privado y acceder a los secretos de Key Vault.

Terraform también configura la confianza entre GitHub Actions y las identidades de publicación y despliegue mediante OIDC. Esto permite que los workflows obtengan acceso temporal a Azure sin guardar una contraseña permanente de Azure en GitHub.

La identidad de ejecución se utiliza desde la propia Container App. Las credenciales de los servicios externos, como los proveedores de IA, se almacenan en Key Vault.

## Ejecución local

### Requisitos y configuración

Se necesita Docker con soporte para contenedores Linux y Docker Compose. No es necesario instalar Python en el equipo: la aplicación y sus dependencias se ejecutan dentro del contenedor.

Desde la raíz del repositorio, crea un archivo `.env` copiando `.env.example`. Si ya existe, conserva tu configuración.

Para utilizar las funciones de IA, configura estas variables en `.env`:

- `GROQ_API_KEY`: clasificación de consultas y generación de respuestas.
- `GEMINI_API_KEY`: generación de embeddings para ingesta y búsqueda.
- `NOTION_API_KEY`: opcional, necesaria únicamente para importar páginas de Notion.

Los valores de ejemplo permiten realizar las comprobaciones de CI, pero no utilizar los proveedores reales. El archivo `.env` está excluido de Git y no debe publicarse.

Mantén `QDRANT_HOST=qdrant` para utilizar la instancia incluida en Docker Compose.

### Arranque

Construye la imagen e inicia los servicios:

```bash
docker compose up -d --build
```

Comprueba su estado:

```bash
docker compose ps --all
```

Una vez iniciada la aplicación, puedes acceder a:

- [Interfaz web](http://localhost:8000)
- [Documentación interactiva de la API](http://localhost:8000/docs)
- [Estado de salud](http://localhost:8000/health)
- [Grafana](http://localhost:3000)
    * La configuración de Grafana se debe hacer de manera manual, creando fuentes de datos y dashboards.
- [Prometheus](http://localhost:9090)

Para consultar los logs de la aplicación:

```bash
docker compose logs --tail=100 app
```

Para detener el entorno:

```bash
docker compose down
```

Los datos almacenados en los volúmenes se conservan entre arranques.

### Incorporar conocimiento

La colección de Qdrant se crea al arrancar si no existe. En una instalación nueva estará vacía, por lo que es necesario incorporar documentos antes de realizar consultas sobre conocimiento propio.

**Archivos Markdown**

Puedes subir un archivo desde el botón **Upload** de la interfaz web, habilitado en local. También puedes utilizar `POST /knowledge/upload` desde la documentación interactiva de la API.

**Páginas de Notion**

Configura `NOTION_API_KEY` en `.env` y concede a esa integración acceso a la página que quieras importar. Si has modificado `.env` con la aplicación arrancada, aplica la nueva configuración:

```bash
docker compose up -d app
```

Abre la [documentación interactiva de la API](http://localhost:8000/docs), selecciona `POST /knowledge/notion` y pulsa **Try it out**. Introduce el identificador de la página:

```json
{
  "page_id": "identificador-de-la-pagina"
}
```

Pulsa **Execute** para importar su contenido. La respuesta indica el identificador de la página y el número de fragmentos almacenados.

La importación desde Notion se realiza mediante la API; no está disponible en la interfaz web.

## Pruebas y validación

Con el entorno iniciado, ejecuta las comprobaciones de código y las pruebas dentro del contenedor:

```bash
docker compose exec -T app python -m ruff check --no-cache app
docker compose exec -T app python -m pytest -p no:cacheprovider
```

Son los mismos comandos utilizados en CI. Las pruebas utilizan sustitutos de los servicios externos y no necesitan API keys reales ni realizan llamadas a proveedores de IA.

Estas comprobaciones validan el comportamiento del código. La evaluación sistemática de la calidad de las respuestas RAG forma parte del trabajo futuro.

### Ejecutar las pruebas desde un entorno virtual

También puedes ejecutar las pruebas directamente desde tu equipo. Para ello, necesitas Python 3.13 y las dependencias del proyecto.

Mantén el archivo `.env` preparado como se indica en la configuración inicial. Las pruebas no necesitan credenciales reales, pero la aplicación requiere que las variables obligatorias estén definidas; puedes utilizar los valores de `.env.example`.

Si todavía no tienes un entorno virtual, créalo desde la raíz del repositorio:

```bash
python -m venv .venv
```

Actívalo según tu sistema operativo:

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux o macOS:**

```bash
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

Con el entorno virtual activado, ejecuta las pruebas y las comprobaciones de código:

```bash
python -m pytest
python -m ruff check app
```

Si ya tienes el entorno virtual preparado, basta con activarlo y ejecutar estos últimos comandos. Las pruebas son las mismas que se ejecutan dentro del contenedor; cambia únicamente el entorno desde el que se lanzan.

## Limitaciones actuales

La instalación en Azure es una demo con un máximo de una réplica. El escalado a cero puede introducir una espera en la primera petición y la disponibilidad también depende de Qdrant Cloud y de los proveedores de IA.

Las respuestas dependen del conocimiento incorporado, de los fragmentos recuperados y del modelo utilizado. Incluir referencias a las fuentes no garantiza que una respuesta sea correcta. La evaluación sistemática de su calidad y las pruebas de rendimiento están pendientes.

El despliegue incluye comprobaciones de salud y conserva la imagen anterior, pero no dispone de rollback automático.

## Próximas mejoras

- **Integración con MCP:** crear un servidor interno con herramientas de solo lectura para consultar información operativa de CloudOps AI, como su estado, versión desplegada o configuración no sensible. La aplicación incorporará un cliente MCP para descubrir e invocar esas herramientas y utilizar sus resultados al responder preguntas operativas. Las herramientas concretas se definirán durante el sprint. La integración funcionará en local y en Azure, sin exponer públicamente el servidor MCP.
- **Evaluación de respuestas y LLMOps:** crear un conjunto de preguntas y respuestas de referencia para evaluar la recuperación de contexto y la calidad de las respuestas. MLflow permitirá registrar experimentos y comparar cambios en modelos, prompts y configuración del RAG, con el objetivo de detectar regresiones y justificar las mejoras con resultados medidos.
- **Rendimiento y costes:** utilizar Locust para estudiar cómo responde la aplicación ante distintas cargas, medir latencia y concurrencia, y analizar el efecto de los arranques en frío. Estas mediciones servirán para identificar cuellos de botella y valorar optimizaciones según su impacto en el rendimiento y el coste.
- **WhatsApp como canal de conversación:** permitir consultas a CloudOps AI desde WhatsApp. La aplicación recibirá los mensajes mediante un webhook, los procesará utilizando la lógica del asistente y enviará las respuestas a través de la API de WhatsApp.
- **Consulta de tareas de GitHub mediante MCP:** ampliar el cliente MCP de CloudOps AI para conectarse a un servidor MCP de GitHub y consultar issues del repositorio. Esto permitirá preguntar qué tareas están abiertas, en qué estado se encuentra una tarea o cuáles están asignadas a una persona. El alcance inicial será de solo lectura, con acceso limitado a los repositorios autorizados.

Estas mejoras forman parte del roadmap y todavía no están implementadas.

## Visión de futuro

CloudOps AI parte de un asistente RAG para consultar documentación operativa. Este caso de uso podría haberse resuelto con una implementación más sencilla, pero desde el inicio el proyecto se planteó también como una oportunidad para aprender y aplicar prácticas de desarrollo, infraestructura, despliegue y operación.

Docker, Terraform, CI/CD y observabilidad permiten trabajar ese ciclo completo y demostrarlo en un portfolio técnico. También proporcionan una base sobre la que incorporar nuevas capacidades y observar su comportamiento a medida que el proyecto evoluciona.

La dirección futura es convertir CloudOps AI en un punto de consulta para el conocimiento y la información operativa de una organización. En esa visión, el RAG sería una capacidad más: permitiría consultar documentación interna, mientras que las integraciones con herramientas como GitHub, Jira o Confluence aportarían información sobre tareas, proyectos y procesos de trabajo.

El objetivo es que una persona pueda consultar desde una misma interfaz tanto cómo funciona un sistema como qué está ocurriendo en su entorno de trabajo, combinando documentación y datos de las herramientas conectadas.

Esta evolución también contempla autenticación de usuarios y control de acceso por roles. Un responsable de proyecto y un desarrollador podrían acceder a distintas fuentes de información y herramientas según sus responsabilidades. Estos permisos se aplicarían en la aplicación y en sus integraciones, como una capa adicional a las identidades de servicio que actualmente se utilizan en Azure y CI/CD.

A largo plazo, la idea es que CloudOps AI pueda ayudar también cuando algo falla. Por ejemplo, si la aplicación empieza a responder lentamente o aparecen errores, podría consultar las métricas, los logs y las trazas para investigar qué está ocurriendo, explicar la posible causa y proponer cómo resolverla.

El siguiente paso sería permitirle actuar en situaciones concretas: ejecutar una comprobación, aplicar una medida de recuperación previamente definida y verificar si el servicio vuelve a funcionar correctamente. Este sistema agéntico tendría límites claros sobre qué puede hacer por sí solo y qué necesita aprobación de una persona.

Esta es la visión que orienta el proyecto. La versión actual implementa el asistente RAG y su infraestructura; las integraciones y capacidades adicionales se incorporarán de forma gradual, según casos de uso concretos.

## Anexo: diagramas técnicos

Los siguientes diagramas amplían el detalle sobre la organización del código y los flujos de datos de la aplicación.

### Estructura general de la aplicación

Muestra la separación entre la API y la interfaz web, y cómo el frontend realiza peticiones a los endpoints del backend.

![Estructura general de la aplicación](diagramas_arquitectura/APP_estructura_general.png)

### Módulos del backend

Muestra cómo se relacionan las rutas de la API con los servicios de ingesta, búsqueda y generación de respuestas.

![Módulos del backend](diagramas_arquitectura/Modulos_backend.png)

### Búsqueda de conocimiento

El diagrama muestra la búsqueda de conocimiento en dos niveles. La parte superior detalla el funcionamiento de `search_knowledge()`: transforma la consulta en un embedding, busca los fragmentos más similares en Qdrant y devuelve su contenido y metadatos.

La parte inferior muestra cómo se utilizan esos resultados dentro de LangGraph, la herramienta que coordina los pasos del flujo RAG. Su nodo `retrieve_context()` llama a `search_knowledge()` y guarda el contenido recuperado y las referencias a sus fuentes en `RAGState`, la estructura que mantiene la información de la consulta durante el recorrido por los distintos nodos. Estos datos quedan disponibles para generar la respuesta en el siguiente paso.

![Búsqueda de conocimiento](diagramas_arquitectura/knowledge%20search%20pipeline.png)

### Esquemas y flujos de datos

Relaciona las solicitudes, las respuestas y las estructuras de datos utilizadas durante la ingesta y la ejecución del flujo RAG.

![Esquemas y flujos de datos](diagramas_arquitectura/Schemas_workflow.png)

## Documentación adicional

- [Guía de uso de la demo](docs/demo_guide.md)
- [Uso de la IA durante el desarrollo](docs/uso_de_ia.md)