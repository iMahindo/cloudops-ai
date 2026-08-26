output "resource_group_name" {
  description = "Name of the resource group containing the public demo"
  value       = azurerm_resource_group.demo.name
}

output "container_registry_login_server" {
  description = "Login server used to publish and pull application images"
  value       = azurerm_container_registry.demo.login_server
}

output "key_vault_name" {
  description = "Name of the Key Vault containing the application secrets"
  value       = azurerm_key_vault.demo.name
}

output "key_vault_uri" {
  description = "URI of the Key Vault containing the application secrets"
  value       = azurerm_key_vault.demo.vault_uri
}

output "container_app_url" {
  description = "Public HTTPS URL of the CloudOps AI demo"
  value = var.deploy_container_app ? (
    "https://${azurerm_container_app.demo[0].ingress[0].fqdn}"
  ) : null
}

output "github_acr_publisher_client_id" {
  description = "Client ID of the managed identity used by GitHub Actions to publish images"
  value       = azurerm_user_assigned_identity.github_acr_publisher.client_id
  sensitive   = true
}

output "azure_tenant_id" {
  description = "Microsoft Entra tenant ID used by GitHub Actions authentication"
  value       = data.azurerm_client_config.current.tenant_id
  sensitive   = true
}

output "azure_subscription_id" {
  description = "Azure subscription ID used by GitHub Actions authentication"
  value       = data.azurerm_client_config.current.subscription_id
  sensitive   = true
}