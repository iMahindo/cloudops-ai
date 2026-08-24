resource "azurerm_container_registry" "demo" {
  name                = local.container_registry_name
  resource_group_name = local.resource_group_name
  location            = var.location

  sku           = "Basic"
  admin_enabled = false

  public_network_access_enabled = true
  role_assignment_mode          = "LegacyRegistryPermissions"

  tags = local.common_tags
}