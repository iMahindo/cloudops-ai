resource "azurerm_log_analytics_workspace" "demo" {
  name                = local.log_analytics_workspace_name
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location

  sku               = "PerGB2018"
  retention_in_days = 30
  daily_quota_gb    = 0.1

  internet_ingestion_access_type = "Enabled"
  internet_query_access_type     = "Enabled"

  tags = local.common_tags
}