locals {
  unique_suffix = substr(md5(var.subscription_id), 0, 6) #Convert to unique hex number 

  state_resource_group_name = "cloudopsai-tfstate"
  storage_account_name      = "stcloudopsaistate${local.unique_suffix}"
  state_container_name      = "tfstate"
  budget_name               = "budget-cloudopsai-monthly"

  commons_tags = {
    project     = "cloudops-ai"
    environment = "bootstrap"
    managed_by  = "terraform"
    purpose     = "terraform-state"
  }
}