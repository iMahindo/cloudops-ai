locals {
  unique_suffix = substr(md5(var.subscription_id), 0, 6) #unique suffix for general names

  resource_group_name             = "cloudopsai-demo"
  container_registry_name         = "crcloudopsaidemo${local.unique_suffix}" #ACR unique name
  managed_identity_name           = "id-cloudopsai-demo"
  key_vault_name                  = "kv-cloudopsai-${local.unique_suffix}" #Key vault unique name
  log_analytics_workspace_name    = "log-cloudopsai-demo"
  container_apps_environment_name = "cae-cloudopsai-demo"
  container_image_repository      = "cloudops-ai"
  container_app_name              = "ca-cloudopsai-demo"
  container_name                  = "cloudops-ai"

  github_acr_publisher_identity_name = "id-github-cloudopsai-publisher" #identity used to publish images in acr by github actions
  github_deployer_identity_name      = "id-github-cloudopsai-deployer"  #identity used to deploy the images in container app

  tfstate_resource_group_name  = "cloudopsai-tfstate"
  tfstate_storage_account_name = "stcloudopsaistated6eda8"
  tfstate_container_name       = "tfstate"

  groq_api_key_secret_name   = "groq-api-key"
  gemini_api_key_secret_name = "gemini-api-key"
  qdrant_api_key_secret_name = "qdrant-api-key"

  common_tags = {
    project     = "cloudops-ai"
    environment = "demo"
    managed_by  = "terraform"
  }
}