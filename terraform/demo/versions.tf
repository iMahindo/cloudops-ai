terraform {
  required_version = "~> 1.15.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "cloudopsai-tfstate"
    storage_account_name = "stcloudopsaistated6eda8"
    container_name       = "tfstate"
    key                  = "demo.tfstate"

    use_azuread_auth = true
    use_cli          = true
  }
}