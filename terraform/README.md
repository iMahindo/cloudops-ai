# Terraform Azure infrastructure

Terraform defines the minimal Azure infrastructure required by the CloudOps AI public demo.

The infrastructure is split into two root configurations:

- `bootstrap`: manages the remote Terraform state infrastructure and the subscription budget.
- `demo`: manages the resources required by the public CloudOps AI demo.

## State layout

Both configurations use the same private Azure Blob container with different state keys:

```text
tfstate/
├── bootstrap.tfstate
└── demo.tfstate
```

The state storage infrastructure belongs to the `cloudopsai-tfstate` resource group.

The public demo infrastructure belongs to the `cloudopsai-demo` resource group.

Terraform state may contain sensitive infrastructure information. State files, saved plans and real `.tfvars` files must never be committed.

## Prerequisites

- Terraform 1.15.x.
- Azure CLI.
- An active Azure subscription.
- An authenticated Azure CLI session.
- Local `terraform.tfvars` files created from the provided examples.

Authenticate explicitly against the project tenant:

```powershell
az login --tenant 134d5c33-62d3-4f87-8048-ff5206daa5df
az account set --subscription "<subscription-id>"
az account show --query "{subscription:name, subscriptionId:id, tenantId:tenantId}" -o table
```

The final command verifies which subscription and tenant are active before Terraform accesses Azure.

## Configuration files

Create local variable files from the provided examples:

```text
terraform/bootstrap/terraform.tfvars.example
    ↓
terraform/bootstrap/terraform.tfvars

terraform/demo/terraform.tfvars.example
    ↓
terraform/demo/terraform.tfvars
```

The real `terraform.tfvars` files are ignored by Git.

Do not place API keys, tokens or passwords in these files. Application secrets are stored in Azure Key Vault and referenced by Azure Container Apps.

## Safe validation workflow

### Bootstrap

Initialize the bootstrap configuration:

```powershell
terraform "-chdir=terraform/bootstrap" init
```

Check its formatting:

```powershell
terraform "-chdir=terraform/bootstrap" fmt -check
```

Validate its syntax and internal references:

```powershell
terraform "-chdir=terraform/bootstrap" validate
```

Generate a plan:

```powershell
terraform "-chdir=terraform/bootstrap" plan
```

### Demo

Initialize the demo configuration:

```powershell
terraform "-chdir=terraform/demo" init
```

Check its formatting:

```powershell
terraform "-chdir=terraform/demo" fmt -check
```

Validate its syntax and internal references:

```powershell
terraform "-chdir=terraform/demo" validate
```

Generate a plan:

```powershell
terraform "-chdir=terraform/demo" plan
```

## Command safety

`terraform fmt -check` verifies formatting without modifying files.

`terraform validate` verifies Terraform syntax, provider schemas and internal references. It does not create or modify Azure resources.

`terraform plan` compares:

- The Terraform configuration.
- The remote Terraform state.
- The resources currently present in Azure.

It displays the changes Terraform proposes but does not perform them.

`terraform apply` creates or modifies real Azure resources and may generate cost. Never run it without reviewing the complete plan first.

`terraform destroy` deletes resources managed by the selected Terraform configuration. Always confirm the active directory, subscription, state and destruction plan before approving it.

## Deployment boundary

The complete demo infrastructure is defined in Terraform, but it must not be applied until all deployment prerequisites are available.

The Container App depends on:

- A real CloudOps AI image published in Azure Container Registry.
- The Groq API key stored in Azure Key Vault.
- The Gemini API key stored in Azure Key Vault.
- The Qdrant API key stored in Azure Key Vault.
- Application support for authenticated Qdrant Cloud connections.
- Optional handling of integrations that are not enabled in the public demo.

Until those prerequisites exist, the demo configuration is validated using `terraform plan` only.

The placeholder image tag exists solely to allow Terraform to build and validate the planned Container App configuration. It must be replaced by an immutable image tag, normally a Git commit SHA, before deployment.

## Infrastructure summary

The bootstrap configuration manages:

- The Terraform state resource group.
- The Azure Storage account used by the remote backend.
- The private Blob container used for state files.
- The current operator’s Blob data access.
- The subscription-level cost budget and notifications.

The demo configuration defines:

- The demo resource group.
- Azure Container Registry Basic.
- A user-assigned managed identity.
- Azure Key Vault Standard.
- RBAC assignments for image pulls and secret access.
- A Log Analytics workspace with limited ingestion and retention.
- An Azure Container Apps Environment.
- An Azure Container App using the Consumption workload profile.
- Public HTTPS ingress.
- Scale-to-zero with a maximum of one replica.
- Startup, readiness and liveness probes using `/health`.
- Non-sensitive application configuration.
- Versionless Key Vault secret references.
- Useful deployment outputs.

The local Docker Compose observability stack and local Qdrant container are not deployed to Azure.

## Complete teardown

The demo and bootstrap configurations must be destroyed in the correct order.

The demo state is stored inside the Storage account managed by bootstrap. Never destroy bootstrap before destroying the demo.

The required order is:

```text
1. Destroy demo
2. Verify that demo state contains no managed resources
3. Migrate bootstrap state from Azure Blob Storage to local state
4. Verify the local bootstrap state
5. Destroy bootstrap
```

Do not delete the resource groups manually from the Azure portal. Terraform should perform the destruction so that its state remains consistent with Azure.

### 1. Destroy the demo

Generate a dedicated destruction plan:

```powershell
terraform "-chdir=terraform/demo" plan -destroy "-out=demo-destroy.tfplan"
```

Review the saved plan:

```powershell
terraform "-chdir=terraform/demo" show demo-destroy.tfplan
```

Only after confirming that the plan exclusively deletes the expected demo resources, apply it:

```powershell
terraform "-chdir=terraform/demo" apply demo-destroy.tfplan
```

Inspect the remaining demo state:

```powershell
terraform "-chdir=terraform/demo" state list
```

The state must not contain managed Azure resources. Read-only data sources such as `data.azurerm_client_config.current` may still appear and do not represent deployed infrastructure.

Do not continue if the demo destruction fails or its state still contains managed resources.

### 2. Migrate bootstrap state to local storage

The bootstrap state must be moved out of the Storage account before that account can be destroyed.

Temporarily remove the following backend block from `terraform/bootstrap/versions.tf`:

```hcl
backend "azurerm" {
  resource_group_name  = "cloudopsai-tfstate"
  storage_account_name = "stcloudopsaistated6eda8"
  container_name       = "tfstate"
  key                  = "bootstrap.tfstate"
  use_azuread_auth     = true
  use_cli              = true
}
```

This is a temporary operational change. Do not commit the removal.

Initialize Terraform and request state migration:

```powershell
terraform "-chdir=terraform/bootstrap" init -migrate-state
```

Terraform will ask whether the existing remote state should be copied to the local backend. Review the prompt and approve the copy.

Verify that the expected bootstrap resources are present in the migrated state:

```powershell
terraform "-chdir=terraform/bootstrap" state list
```

Verify that the migrated state still matches Azure:

```powershell
terraform "-chdir=terraform/bootstrap" plan
```

The expected result before destruction is:

```text
No changes. Your infrastructure matches the configuration.
```

A local `terraform/bootstrap/terraform.tfstate` file should now exist. It is ignored by Git and must never be committed.

### 3. Destroy bootstrap

Generate a dedicated bootstrap destruction plan:

```powershell
terraform "-chdir=terraform/bootstrap" plan -destroy "-out=bootstrap-destroy.tfplan"
```

Review it:

```powershell
terraform "-chdir=terraform/bootstrap" show bootstrap-destroy.tfplan
```

Only after confirming that the plan exclusively deletes the expected bootstrap resources, apply it:

```powershell
terraform "-chdir=terraform/bootstrap" apply bootstrap-destroy.tfplan
```

Inspect the remaining bootstrap state:

```powershell
terraform "-chdir=terraform/bootstrap" state list
```

The state must not contain managed Azure resources. Read-only data sources such as `data.azurerm_client_config.current` may still appear and do not represent deployed infrastructure.

Restore the Azure backend block in `terraform/bootstrap/versions.tf` so that the committed configuration continues to describe the normal remote-state architecture.

Do not run `terraform init` against the restored remote backend after complete destruction because the Storage account no longer exists.

Azure soft-delete may retain recoverable Storage or Key Vault data for the configured retention period. Recoverable data is not an active deployment, but globally unique names may remain temporarily reserved.

## Rebuild after complete teardown

To recreate the infrastructure after a complete teardown, bootstrap must initially run with local state because its remote backend does not exist yet.

Temporarily remove the Azure backend block from `terraform/bootstrap/versions.tf`. Do not commit this temporary removal.

Initialize bootstrap with the local backend:

```powershell
terraform "-chdir=terraform/bootstrap" init -reconfigure
```

Validate and review the bootstrap plan:

```powershell
terraform "-chdir=terraform/bootstrap" fmt -check
terraform "-chdir=terraform/bootstrap" validate
terraform "-chdir=terraform/bootstrap" plan "-out=bootstrap.tfplan"
terraform "-chdir=terraform/bootstrap" show bootstrap.tfplan
```

After explicit approval, create the bootstrap resources:

```powershell
terraform "-chdir=terraform/bootstrap" apply bootstrap.tfplan
```

Restore the Azure backend block in `terraform/bootstrap/versions.tf`.

Migrate the newly created bootstrap state from local storage to Azure Blob Storage:

```powershell
terraform "-chdir=terraform/bootstrap" init -migrate-state
```

Verify the migrated remote state:

```powershell
terraform "-chdir=terraform/bootstrap" state list
terraform "-chdir=terraform/bootstrap" plan
```

Initialize the demo configuration against its recreated remote backend:

```powershell
terraform "-chdir=terraform/demo" init -reconfigure
terraform "-chdir=terraform/demo" validate
terraform "-chdir=terraform/demo" plan
```

The demo must only be applied after its image, Key Vault secrets and application deployment prerequisites are available.