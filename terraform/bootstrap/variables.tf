variable "subscription_id" {
  description = "Azure subscription ID where resources will be managed"
  type        = string
  nullable    = false
}

variable "location" {
  description = "Azure region used by the Terraform backend resources"
  type        = string
  default     = "Spain Central"
  nullable    = false
}

variable "budget_amount" {
  description = "Monthly subscription budget amount in the billing currency"
  type        = number
  default     = 10
  nullable    = false

  validation {
    condition     = var.budget_amount > 0
    error_message = "The budget amount must be greater than zero"
  }
}