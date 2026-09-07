# CloudOps AI

[Español](README.md) | English

This English version was translated from the original Spanish README using AI.

A cloud-ready AI assistant that turns operational documentation into answers with references to their sources.

The project covers the full development, validation, deployment, and operations lifecycle: a RAG application, containerization, observability, infrastructure as code, and automated CI/CD on Azure using GitHub Actions and OIDC federated authentication.

## Overview

CloudOps AI is an engineering project that combines a RAG application with the practices needed to run, deploy, and operate it. It supports document ingestion, semantic similarity search, and context-aware answers with references to the sources used.

The project includes a complete local environment with Docker Compose and observability, alongside a minimal demo deployed on Azure using Terraform and GitHub Actions. The two architectures serve different purposes: the local environment acts as a technical lab, while Azure prioritizes low cost, security, and scaling to zero.

## Main features

- Knowledge ingestion from files, local directories, and Notion pages.
- Document chunking, embedding generation, and storage in Qdrant.
- Semantic search with content and metadata retrieval.
- A RAG workflow orchestrated with LangGraph to classify each question, determine whether it needs context from Qdrant, and retrieve that context when necessary before generating and validating the answer.
- A FastAPI backend and a simple web interface.
- A reproducible local environment using Docker Compose.
- Local metrics, logs, and traces with Prometheus, Grafana, Loki, Tempo, and Alloy.
- Azure infrastructure managed with Terraform.
- Automated image publication and deployment using GitHub Actions and OIDC authentication.

## How it works

CloudOps AI separates knowledge ingestion and query processing into two related workflows.

### Knowledge ingestion

The application receives content from files, local directories, or Notion pages and converts it into a common document format. It then splits each document into chunks, adds the required metadata, and generates vector representations (embeddings) before storing them in Qdrant.

When a document with the same identifier is processed again, its previous chunks are replaced to avoid retaining duplicate or outdated information.

![Knowledge ingestion workflow](diagramas_arquitectura/ingestion_pipeline.png)

### Query processing and answer generation

When the API receives a question, LangGraph coordinates the workflow. It first classifies the query and determines whether it can be answered directly or requires information from Qdrant.

When context is required, the question is converted into a vector and used to search for the most relevant chunks. The retrieved content and metadata are added to the workflow state to generate a context-aware answer, validate it, and return the sources used.

When a query is classified as conversational or does not require consulting documentation, the workflow skips context retrieval and generates the answer directly with the LLM.

The final validation checks that the answer is not empty and that context exists when retrieval is required. It does not verify the accuracy of the answer.

![LangGraph node workflow](diagramas_arquitectura/langGraph_nodes.png)

## Architecture

CloudOps AI uses two environments: a local lab for development and observability, and a public Azure demo with a smaller infrastructure footprint.

This separation keeps cloud costs low. The local environment retains all features and the complete observability stack, while the Azure demo supports queries and answer generation with ingestion and public metrics access disabled.

![Local and Azure architecture](diagramas_arquitectura/Arquitectura_local_cloud.png)

### Local environment

Docker Compose brings together the FastAPI application, Qdrant, and the observability services:

- **Prometheus:** collects and stores metrics.
- **Loki and Alloy:** support log collection and querying.
- **Tempo:** stores traces generated through OpenTelemetry.
- **Grafana:** provides a way to explore metrics, logs, and traces.

This environment supports development, testing, and inspection of application behavior, with the lab configuration versioned in the repository.

![Local observability: metrics, logs, and traces](diagramas_arquitectura/Metrics_logging_tracing.png)

### Azure demo

The application runs on Azure Container Apps using the Consumption plan, scaling between zero and one replica. Qdrant Cloud stores the vectorized knowledge, and AI providers are accessed as external services.

The infrastructure includes a private image registry in Azure Container Registry, Key Vault for secrets, and a managed identity with permissions to access the required resources. Environment logs are collected in Log Analytics.

### Design decisions

Scaling to zero reduces resource consumption while the application is idle, although it can add startup time to the first request. Using external services for Qdrant and AI models simplifies deployment, at the cost of depending on their availability and usage limits.

## Infrastructure and CI/CD

### Infrastructure as code

Azure resources are managed with Terraform through two separate configurations:

- **Bootstrap:** creates the storage needed to keep Terraform state in Azure.
- **Demo:** creates and manages the application infrastructure.

The initial bootstrap runs with locally stored state because the remote storage does not exist yet. Once the storage has been created, that state is migrated to Azure Blob Storage, and the demo infrastructure is configured to use the same storage.

Each configuration maintains its own state file. Terraform uses these files to map resources defined in code to those that exist in Azure and calculate the required changes:

- `bootstrap.tfstate`: tracks the setup resources, including the state resource group, storage account, blob container, associated permissions, and budget.
- `demo.tfstate`: tracks the application infrastructure, including Container Apps, the image registry, Key Vault, Log Analytics, and identities and their permissions.

Both state files are stored in the same Azure Blob Storage container as separate files. Application changes are therefore managed through `demo` without including the setup resources managed by `bootstrap`. Storage access is authenticated through Microsoft Entra ID.

![Azure resource organization](diagramas_arquitectura/Resources_groups.png)

### Validation, image publication, and deployment

GitHub Actions automates project checks and the delivery of new versions:

1. **Validation:** runs Ruff code checks, pytest tests, and validation for Terraform, workflows, and scripts. It also checks Docker Compose startup and API health. These checks require no secrets or real calls to AI providers.
2. **Image publication:** when relevant changes occur, it builds the Docker image and publishes it to Azure Container Registry. Each image is tagged with the full commit SHA to link it to the code that produced it and deploy that specific version.
3. **Deployment:** after successful publication, the workflow prepares a Terraform plan to deploy the new version. Before applying it, a script checks that changes are limited to updating the existing Container App. If the plan includes creating, deleting, or replacing resources, or modifying other infrastructure components, deployment is stopped for review.
4. **Verification:** checks application health and runs a final plan to confirm that no pending differences remain between the infrastructure and its configuration.

After a successful deployment, the current image and the previous image verified as healthy are retained. This limits registry storage usage while keeping an earlier version available. Automatic rollback is outside the current scope.

### Authentication and permissions

Terraform creates three managed identities in Azure and assigns each the permissions required for its role:

- **Publisher:** used by GitHub Actions to push images to Azure Container Registry and delete older versions during cleanup.
- **Deployer:** used by GitHub Actions to inspect infrastructure, access remote Terraform state, and update the Container App.
- **Runtime:** assigned to the Container App to pull the image from the private registry and access secrets in Key Vault.

Terraform also configures trust between GitHub Actions and the publisher and deployer identities through OIDC. This allows workflows to obtain temporary access to Azure without storing a long-lived Azure password in GitHub.

The runtime identity is used by the Container App itself. Credentials for external services, such as AI providers, are stored in Key Vault.

## Running locally

### Requirements and configuration

Docker with Linux container support and Docker Compose are required. Python does not need to be installed on the host: the application and its dependencies run inside the container.

From the repository root, create a `.env` file by copying `.env.example`. If one already exists, keep your current configuration.

To use the AI features, configure these variables in `.env`:

- `GROQ_API_KEY`: query classification and answer generation.
- `GEMINI_API_KEY`: embedding generation for ingestion and search.
- `NOTION_API_KEY`: optional; only required to import Notion pages.

The example values support CI checks but cannot be used to access the real providers. The `.env` file is excluded from Git and must not be published.

Keep `QDRANT_HOST=qdrant` to use the instance included in Docker Compose.

### Startup

Build the image and start the services:

```bash
docker compose up -d --build
```

Check their status:

```bash
docker compose ps --all
```

Once the application has started, you can access:

- [Web interface](http://localhost:8000)
- [Interactive API documentation](http://localhost:8000/docs)
- [Health endpoint](http://localhost:8000/health)
- [Grafana](http://localhost:3000)
  - Grafana requires manual configuration of data sources and dashboards.
- [Prometheus](http://localhost:9090)

To view application logs:

```bash
docker compose logs --tail=100 app
```

To stop the environment:

```bash
docker compose down
```

Data stored in volumes is preserved between runs.

### Adding knowledge

The Qdrant collection is created at startup if it does not exist. A fresh installation starts with an empty collection, so documents must be added before querying your own knowledge.

**Markdown files**

You can upload a file using the **Upload** button in the web interface, which is enabled locally. Alternatively, use `POST /knowledge/upload` through the interactive API documentation.

**Notion pages**

Set `NOTION_API_KEY` in `.env` and grant the integration access to the page you want to import. If you changed `.env` while the application was running, apply the updated configuration:

```bash
docker compose up -d app
```

Open the [interactive API documentation](http://localhost:8000/docs), select `POST /knowledge/notion`, and click **Try it out**. Enter the page identifier:

```json
{
  "page_id": "your-page-id"
}
```

Click **Execute** to import its content. The response includes the page identifier and the number of chunks stored.

Notion imports are performed through the API; they are not available in the web interface.

## Testing and validation

With the environment running, execute the code checks and tests inside the container:

```bash
docker compose exec -T app python -m ruff check --no-cache app
docker compose exec -T app python -m pytest -p no:cacheprovider
```

These are the same commands used in CI. Tests use substitutes for external services and require neither real API keys nor calls to AI providers.

These checks validate code behavior. Systematic evaluation of RAG answer quality is planned for future work.

### Running tests in a virtual environment

You can also run the tests directly on your machine. This requires Python 3.13 and the project dependencies.

Keep the `.env` file configured as described in the initial setup. Tests do not need real credentials, but the application requires mandatory variables to be defined; you can use the values from `.env.example`.

If you do not already have a virtual environment, create one from the repository root:

```bash
python -m venv .venv
```

Activate it for your operating system:

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux or macOS:**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

With the virtual environment activated, run the tests and code checks:

```bash
python -m pytest
python -m ruff check app
```

If your virtual environment is already set up, activate it and run these last two commands. The tests are the same as those run inside the container; only the execution environment changes.

## Current limitations

The Azure installation is a demo with a maximum of one replica. Scaling to zero can introduce a delay on the first request, and availability also depends on Qdrant Cloud and the AI providers.

Answers depend on the ingested knowledge, the retrieved chunks, and the model used. Including source references does not guarantee that an answer is correct. Systematic quality evaluation and performance testing are still pending.

Deployment includes health checks and retains the previous image, but does not provide automatic rollback.

## Planned improvements

- **MCP integration:** build an internal server with read-only tools to query operational information about CloudOps AI, such as its health, deployed version, or non-sensitive configuration. The application will include an MCP client to discover and invoke these tools and use their results when answering operational questions. The specific tools will be defined during the sprint. The integration will run locally and on Azure without exposing the MCP server publicly.
- **Answer evaluation and LLMOps:** create a reference set of questions and answers to evaluate context retrieval and answer quality. MLflow will track experiments and compare changes to models, prompts, and RAG configuration, with the aim of detecting regressions and supporting improvements with measured results.
- **Performance and costs:** use Locust to study application behavior under different loads, measure latency and concurrency, and analyze the effect of cold starts. These measurements will help identify bottlenecks and assess optimizations based on their impact on performance and cost.
- **WhatsApp as a conversation channel:** allow users to query CloudOps AI through WhatsApp. The application will receive messages through a webhook, process them using the assistant logic, and send responses through the WhatsApp API.
- **GitHub task queries through MCP:** extend the CloudOps AI MCP client to connect to a GitHub MCP server and query repository issues. This will support questions about which tasks are open, the status of a specific task, or tasks assigned to a person. The initial scope will be read-only, with access limited to authorized repositories.

These improvements are part of the roadmap and have not yet been implemented.

## Future vision

CloudOps AI starts with a RAG assistant for querying operational documentation. This use case could have been addressed with a simpler implementation, but the project was also intended from the outset as an opportunity to learn and apply development, infrastructure, deployment, and operations practices.

Docker, Terraform, CI/CD, and observability support that full lifecycle and demonstrate it in a technical portfolio. They also provide a foundation for adding capabilities and observing their behavior as the project evolves.

The long-term direction is to make CloudOps AI a single place to query an organization's knowledge and operational information. In that vision, RAG would be one capability among several: it would support internal documentation queries, while integrations with tools such as GitHub, Jira, or Confluence would provide information about tasks, projects, and work processes.

The goal is to let someone use the same interface to ask both how a system works and what is happening in their working environment, combining documentation with data from connected tools.

This evolution also includes user authentication and role-based access control. A project manager and a developer could access different information sources and tools according to their responsibilities. These permissions would apply within the application and its integrations, adding a layer alongside the service identities currently used in Azure and CI/CD.

In the longer term, CloudOps AI could also help when something goes wrong. For example, if the application starts responding slowly or errors appear, it could inspect metrics, logs, and traces to investigate what is happening, explain the likely cause, and suggest how to resolve it.

The next step would be to allow it to act in specific situations: run a check, apply a predefined recovery action, and verify whether the service is working correctly again. This agentic system would have clear limits on what it can do independently and what requires human approval.

This vision guides the project. The current version implements the RAG assistant and its infrastructure; additional integrations and capabilities will be introduced gradually, based on specific use cases.

## Appendix: technical diagrams

The following diagrams provide more detail about code organization and application data flows.

### General application structure

Shows the separation between the API and the web interface, and how the frontend sends requests to backend endpoints.

![General application structure](diagramas_arquitectura/APP_estructura_general.png)

### Backend modules

Shows how API routes relate to the ingestion, search, and answer generation services.

![Backend modules](diagramas_arquitectura/Modulos_backend.png)

### Knowledge search

The diagram shows knowledge search at two levels. The upper section details how `search_knowledge()` works: it converts the query into an embedding, searches Qdrant for the most similar chunks, and returns their content and metadata.

The lower section shows how those results are used within LangGraph, the tool that coordinates the RAG workflow. Its `retrieve_context()` node calls `search_knowledge()` and stores the retrieved content and source references in `RAGState`, the structure that holds query information as it passes through the different nodes. This data becomes available for answer generation in the next step.

![Knowledge search](diagramas_arquitectura/knowledge%20search%20pipeline.png)

### Schemas and data flows

Shows the relationships between requests, responses, and data structures used during ingestion and RAG execution.

![Schemas and data flows](diagramas_arquitectura/Schemas_workflow.png)

## Additional documentation

- [Demo usage guide — Spanish](docs/demo_guide.md)
- [Use of AI during development — Spanish](docs/uso_de_ia.md)