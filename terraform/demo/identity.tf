resource "azurerm_user_assigned_identity" "app" {
  name                = local.managed_identity_name
  resource_group_name = local.resource_group_name
  location            = var.location

  tags = local.common_tags
}