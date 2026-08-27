resource "azurerm_user_assigned_identity" "app" {
  name                = local.managed_identity_name
  resource_group_name = local.resource_group_name
  location            = var.location

  tags = local.common_tags
}

resource "azurerm_user_assigned_identity" "github_acr_publisher" {
  name                = local.github_acr_publisher_identity_name
  resource_group_name = local.resource_group_name
  location            = var.location

  tags = local.common_tags
}

resource "azurerm_user_assigned_identity" "github_deployer" {
  name                = local.github_deployer_identity_name
  resource_group_name = local.resource_group_name
  location            = var.location

  tags = local.common_tags
}