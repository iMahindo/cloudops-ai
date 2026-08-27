#!/usr/bin/env bash

# Stop on errors, undefined variables and failed commands inside pipelines
set -euo pipefail

ACR_NAME="${1:?Usage: cleanup-acr-images.sh <acr-name> <repository> <current-tag> <previous-tag>}"
REPOSITORY="${2:?Usage: cleanup-acr-images.sh <acr-name> <repository> <current-tag> <previous-tag>}"
CURRENT_TAG="${3:?Usage: cleanup-acr-images.sh <acr-name> <repository> <current-tag> <previous-tag>}"
PREVIOUS_TAG="${4:?Usage: cleanup-acr-images.sh <acr-name> <repository> <current-tag> <previous-tag>}"

SHA_PATTERN='^[0-9a-f]{40}$'

# Refuse to delete anything if either protected tag is malformed
if [[ ! "${CURRENT_TAG}" =~ ${SHA_PATTERN} ]]; then
  echo "::error::Current image tag is not a full Git commit SHA."
  exit 1
fi

if [[ ! "${PREVIOUS_TAG}" =~ ${SHA_PATTERN} ]]; then
  echo "::error::Previous image tag is not a full Git commit SHA."
  exit 1
fi

# A repeated deployment has no new previous version, so cleanup is skipped
if [[ "${CURRENT_TAG}" == "${PREVIOUS_TAG}" ]]; then
  echo "Current and previous image tags are identical. Skipping cleanup."
  exit 0
fi

TAGS_OUTPUT="$(az acr repository show-tags \
  --name "${ACR_NAME}" \
  --repository "${REPOSITORY}" \
  --output tsv)"

if [[ -z "${TAGS_OUTPUT}" ]]; then
  echo "::error::No image tags were returned by Azure Container Registry."
  exit 1
fi

mapfile -t TAGS <<< "${TAGS_OUTPUT}"

for TAG in "${TAGS[@]}"; do
  if [[ "${TAG}" == "${CURRENT_TAG}" || "${TAG}" == "${PREVIOUS_TAG}" ]]; then
    echo "Keeping protected image: ${REPOSITORY}:${TAG}"
    continue
  fi

  # Never delete tags that do not follow the immutable Git SHA convention
  if [[ ! "${TAG}" =~ ${SHA_PATTERN} ]]; then
    echo "Skipping non-SHA tag: ${REPOSITORY}:${TAG}"
    continue
  fi

  echo "Deleting old image: ${REPOSITORY}:${TAG}"

  az acr repository delete \
    --name "${ACR_NAME}" \
    --image "${REPOSITORY}:${TAG}" \
    --yes \
    --output none
done