variable "subscription_id" {
  description = "Azure subscription ID where resources will be managed"
  type        = string
  nullable    = false
}

variable "location" {
  description = "Azure region used by the CloudOps AI demo resources."
  type        = string
  default     = "Spain Central"
  nullable    = false
}

variable "key_vault_secrets_officer_object_id" {
  description = "Microsoft Entra object ID of the user allowed to manage demo secrets."
  type        = string
  nullable    = false
}

variable "container_image_tag" {
  description = "Immutable tag of the application container image, normally a Git commit SHA"
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.container_image_tag)) > 0
    error_message = "The container image tag must not be empty"
  }
}

variable "qdrant_host" {
  description = "Public hostname of the external Qdrant Cloud cluster"
  type        = string
  nullable    = false

  validation {
    condition     = length(trimspace(var.qdrant_host)) > 0
    error_message = "The Qdrant host must not be empty."
  }
}

variable "deploy_container_app" {
  description = "Whether to deploy the Container App after its image and secrets are available"
  type        = bool
  default     = false
  nullable    = false
}