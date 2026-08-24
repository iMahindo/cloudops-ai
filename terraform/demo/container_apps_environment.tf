resource "azurerm_container_app_environment" "demo" {
  name                = local.container_apps_environment_name
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location

  logs_destination           = "log-analytics"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.demo.id

  tags = local.common_tags
}