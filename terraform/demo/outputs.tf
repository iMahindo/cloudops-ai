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
  value       = "https://${azurerm_container_app.demo.ingress[0].fqdn}"
}