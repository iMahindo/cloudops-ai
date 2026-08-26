#github federate credentials
resource "azurerm_federated_identity_credential" "github_acr_publisher_main" { #Only the main branch in the repo can publish images in acr
  name                      = "github_main_acr_publisher"
  user_assigned_identity_id = azurerm_user_assigned_identity.github_acr_publisher.id

  audience = ["api://AzureADTokenExchange"]                                       #azure doc
  issuer   = "https://token.actions.githubusercontent.com"                        #github doc
  subject  = "repo:iMahindo@309682860/cloudops-ai@1315907876:ref:refs/heads/main" #github repo
}