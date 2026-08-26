resource "azurerm_role_assignment" "app_acr_pull" {
  scope                = azurerm_container_registry.demo.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.app.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "app_key_vault_secrets_user" {
  scope                = azurerm_key_vault.demo.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.app.principal_id
  principal_type       = "ServicePrincipal"
}

resource "azurerm_role_assignment" "current_user_key_Vault_secrets_officer" {
  scope                = azurerm_key_vault.demo.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = var.key_vault_secrets_officer_object_id
  principal_type       = "User"
}

resource "azurerm_role_assignment" "github_acr_publisher_push" {
  scope                = azurerm_container_registry.demo.id
  role_definition_name = "AcrPush"
  principal_id         = azurerm_user_assigned_identity.github_acr_publisher.principal_id
  principal_type       = "ServicePrincipal"
}