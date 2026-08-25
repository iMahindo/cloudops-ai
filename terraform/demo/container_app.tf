resource "azurerm_container_app" "demo" {
  name                         = local.container_app_name
  container_app_environment_id = azurerm_container_app_environment.demo.id
  resource_group_name          = azurerm_resource_group.demo.name
  revision_mode                = "Single" #Only able one version

  count = var.deploy_container_app ? 1 : 0

  identity {
    type = "UserAssigned"

    identity_ids = [
      azurerm_user_assigned_identity.app.id
    ]
  }

  registry { #ACR server and identity used to download the image
    server   = azurerm_container_registry.demo.login_server
    identity = azurerm_user_assigned_identity.app.id
  }

  secret {
    name     = local.groq_api_key_secret_name
    identity = azurerm_user_assigned_identity.app.id

    key_vault_secret_id = "${azurerm_key_vault.demo.vault_uri}secrets/${local.groq_api_key_secret_name}"
  }
  secret {
    name     = local.gemini_api_key_secret_name
    identity = azurerm_user_assigned_identity.app.id

    key_vault_secret_id = "${azurerm_key_vault.demo.vault_uri}secrets/${local.gemini_api_key_secret_name}"
  }

  secret {
    name     = local.qdrant_api_key_secret_name
    identity = azurerm_user_assigned_identity.app.id

    key_vault_secret_id = "${azurerm_key_vault.demo.vault_uri}secrets/${local.qdrant_api_key_secret_name}"
  }

  ingress {
    external_enabled           = true
    target_port                = 8000
    transport                  = "auto"
    allow_insecure_connections = false

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    min_replicas = 0
    max_replicas = 1

    container {
      name = local.container_name

      image = "${azurerm_container_registry.demo.login_server}/${local.container_image_repository}:${var.container_image_tag}"

      cpu    = 0.5
      memory = "1Gi"

      startup_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/health"

        initial_delay           = 0
        interval_seconds        = 5
        timeout                 = 3
        failure_count_threshold = 30
      }

      readiness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/health"

        initial_delay           = 0
        interval_seconds        = 10
        timeout                 = 3
        failure_count_threshold = 3
        success_count_threshold = 1
      }

      liveness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/health"

        initial_delay           = 10
        interval_seconds        = 30
        timeout                 = 3
        failure_count_threshold = 3
      }

      env {
        name  = "METRICS_ENABLED"
        value = "false"
      }

      env {
        name  = "ENVIRONMENT"
        value = "production"
      }

      env {
        name  = "DEBUG"
        value = "false"
      }

      env {
        name  = "QDRANT_HOST"
        value = var.qdrant_host
      }

      env {
        name  = "QDRANT_PORT"
        value = "6333"
      }

      env {
        name  = "QDRANT_COLLECTION"
        value = "cloudops_knowledge"
      }

      env {
        name  = "QDRANT_HTTPS"
        value = "true"
      }

      env {
        name  = "QDRANT_CREATE_COLLECTION_ON_STARTUP"
        value = "false"
      }

      env {
        name  = "INGESTION_ENABLED"
        value = "false"
      }

      env {
        name        = "GROQ_API_KEY"
        secret_name = local.groq_api_key_secret_name
      }
      env {
        name        = "GEMINI_API_KEY"
        secret_name = local.gemini_api_key_secret_name
      }

      env {
        name        = "QDRANT_API_KEY"
        secret_name = local.qdrant_api_key_secret_name
      }
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_role_assignment.app_acr_pull,
    azurerm_role_assignment.app_key_vault_secrets_user
  ]
}