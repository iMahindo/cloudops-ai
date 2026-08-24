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

variable "budget_start_date" {
  description = "First day of the month from wich the Azure buidget starts"
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^\\d{4}-\\d{2}-01T00:00:00Z$", var.budget_start_date))
    error_message = "The budget start date must use the format YYYY-MM-01T00:00:00Z"
  }
}