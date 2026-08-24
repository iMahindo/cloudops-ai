resource "azurerm_key_vault" "demo" {
  name                = local.key_vault_name
  resource_group_name = local.resource_group_name
  location            = var.location

  tenant_id = data.azurerm_client_config.current.tenant_id
  sku_name  = "standard"

  rbac_authorization_enabled = true

  soft_delete_retention_days = 7
  purge_protection_enabled   = false #we will be able to delete 

  public_network_access_enabled = true

  tags = local.common_tags
}