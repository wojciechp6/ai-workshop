#!/usr/bin/env bash

ENV_FILE=".env"

# 1) Wykryj maksymalną CUDA z nvidia-smi
CUDA_MAX="$(nvidia-smi | sed -n 's/.*CUDA Version: \([0-9]\+\.[0-9]\+\).*/\1/p' | head -n1)"
if [[ -z "${CUDA_MAX}" ]]; then
  echo "ERROR: Nie mogę wykryć CUDA Version z nvidia-smi."
  exit 1
fi

major="${CUDA_MAX%%.*}"
minor="${CUDA_MAX##*.}"

# 2) Dobierz najbliższy wspierany tag PyTorch
pick_torch_tag() {
  if [[ "$major" -lt 11 ]]; then
    echo "cu118"
  elif [[ "$major" -eq 11 ]]; then
    echo "cu118"
  else
    if [[ "$minor" -ge 6 ]]; then
      echo "cu126"
    elif [[ "$minor" -ge 4 ]]; then
      echo "cu124"
    elif [[ "$minor" -ge 1 ]]; then
      echo "cu121"
    else
      echo "cu121"
    fi
  fi
}

TORCH_CUDA_TAG="$(pick_torch_tag)"
CUDA_VERSION="${CUDA_MAX}.0"

# 3) Funkcja: ustaw lub zaktualizuj klucz w .env
set_env_var() {
  local key="$1"
  local value="$2"

  if [[ -f "$ENV_FILE" ]] && grep -qE "^${key}=" "$ENV_FILE"; then
    # podmień istniejącą wartość
    sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    # dopisz nową linię
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

# 4) Zapisz TYLKO to, co trzeba
touch "$ENV_FILE"
set_env_var "CUDA_VERSION" "${CUDA_VERSION}"
set_env_var "TORCH_CUDA_TAG" "${TORCH_CUDA_TAG}"

echo "OK: zaktualizowano .env"
echo "  CUDA_VERSION=${CUDA_VERSION}"
echo "  TORCH_CUDA_TAG=${TORCH_CUDA_TAG}"
