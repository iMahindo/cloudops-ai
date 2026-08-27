#!/usr/bin/env bash

# Stop on errors, undefined variables and failed commands inside pipelines
set -euo pipefail

PLAN_JSON_PATH="${1:?Usage: validate-terraform-deployment-plan.sh <plan-json-path>}"

# Fail clearly if the workflow did not generate the expected JSON file
if [[ ! -f "${PLAN_JSON_PATH}" ]]; then
  echo "::error::Terraform plan JSON file was not found: ${PLAN_JSON_PATH}"
  exit 1
fi

# Allow no changes or one update to the existing Container App
if ! jq --exit-status '
  [.resource_changes[] | select(.change.actions != ["no-op"])] as $changes
  |
  (($changes | length) <= 1)
  and all(
    $changes[];
    .address == "azurerm_container_app.demo[0]"
    and .change.actions == ["update"]
  )
' "${PLAN_JSON_PATH}" > /dev/null; then
  echo "::error::Deployment blocked because Terraform planned unexpected infrastructure changes."

  # Print only resource addresses and actions, without configuration values
  jq -r '
    .resource_changes[]
    | select(.change.actions != ["no-op"])
    | "\(.address): \(.change.actions | join(","))"
  ' "${PLAN_JSON_PATH}"

  exit 1
fi

echo "Terraform plan approved for application deployment."