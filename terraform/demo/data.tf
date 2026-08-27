data "azurerm_client_config" "current" {} #Get the current config info: tenanID...

data "azurerm_storage_account" "tfstate" {
  name                = local.tfstate_storage_account_name
  resource_group_name = local.tfstate_resource_group_name
}

data "azurerm_storage_container" "tfstate" {
  name               = local.tfstate_container_name
  storage_account_id = data.azurerm_storage_account.tfstate.id
}