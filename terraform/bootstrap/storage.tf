resource "azurerm_resource_group" "terraform_state" {
  name     = local.state_resource_group_name
  location = var.location
  tags     = local.commons_tags
}

resource "azurerm_storage_account" "terraform_state" {
  name                = local.storage_account_name
  resource_group_name = local.state_resource_group_name
  location            = var.location

  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS" #only copies in the data center

  https_traffic_only_enabled       = true
  min_tls_version                  = "TLS1_2"
  public_network_access_enabled    = true
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  default_to_oauth_authentication  = true  #entry ID auth
  shared_access_key_enabled        = false #Deactivate shared keys

  blob_properties { #Soft delete
    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = local.commons_tags
}

resource "azurerm_storage_container" "terraform_state" {
  name                  = local.state_container_name
  storage_account_id    = azurerm_storage_account.terraform_state.id
  container_access_type = "private"

  depends_on = [
    azurerm_role_assignment.terraform_state_blob_contributor
  ]
}