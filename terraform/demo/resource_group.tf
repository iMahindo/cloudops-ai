resource "azurerm_resource_group" "demo" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.common_tags
}