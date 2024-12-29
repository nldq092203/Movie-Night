#!/bin/bash
############################################################################
# run.sh
# Script for managing Django application environments (development, reset)
# Usage: ./infrastructure/scripts/run.sh [COMMAND]
############################################################################

# Constants
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
SERVICES=("web" "db" "redis" "celery" "celery-beat" "nginx") 

# Set dynamic paths and configurations
SCRIPT_DIR="$(dirname "$0")"
cd "${SCRIPT_DIR}/../.." || exit 1
ROOT_PROJECT="$(pwd)"
export ROOT_PROJECT

export NGINX_CONTAINER="nginx"
export BACKEND_CONTAINER="api_backend"
export CELERY_WORKER_CONTAINER="celery_worker"
export CELERY_BEAT_CONTAINER="celery_beat"
export DATABASE_CONTAINER="postgres_db"
export REDIS_CONTAINER="redis"

TLS_DIR="${ROOT_PROJECT}/infrastructure/nginx_reverse_proxy/tls"
NGINX_DEV="${ROOT_PROJECT}/infrastructure/nginx_reverse_proxy/nginx/nginx-dev.conf"
NGINX_DEV_TEMPLATE="${ROOT_PROJECT}/infrastructure/nginx_reverse_proxy/nginx/nginx-dev.template.conf"
DOCKER_COMPOSE_DEV="${ROOT_PROJECT}/infrastructure/docker/docker-compose.yml"
DOCKERFILE_DEV="${ROOT_PROJECT}/infrastructure/docker/Dockerfile.dev"
export DOCKERFILE_DEV

export TLS_DIR
export NGINX_DEV
CERT_FILE="certificate.crt"
KEY_FILE="private.key"

export DOCKER_UID=$(id -u)
export DOCKER_GID=$(id -g)

cd "${ROOT_PROJECT}"

# Prevent running as root
if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}Error: Do not run this script as root or with sudo.${NC}"
  exit 1
fi

# Display help
display_help() {
  cat <<EOF
Usage: ./infrastructure/scripts/run.sh [COMMAND]

Commands:
  help                 Display this help message and exit
  prerequisite         Check if required tools are installed
  create-tls-certs     Create TLS certificates (for local dev environment)
  dev                  Run the application in the development environment
  logs                 View logs for a specific service
  status               Check the status of all services
  stop                 Stop all running services
  reset                Stop and clean all containers, volumes, and temporary files
  clean                Clean up generated files and volumes
  exec                 Run a command in a specific service
  add-trusted-cert     Add the generated TLS certificate to the trusted certificates store, avoiding "Not Secure" warnings


Important Notes: Don't run run.sh with 'sudo'

Examples:
  ./infrastructure/scripts/run.sh dev          Start the app in development mode
  ./infrastructure/scripts/run.sh logs         View logs for a specific service
  ./infrastructure/scripts/run.sh reset        Clean the environment
  ./infrastructure/scripts/run.sh clean        Remove build artifacts and volumes
EOF
}

# Validate environment variables
validate_env() {
  local required_vars=(
    "DEBUG" "SECRET_KEY" "ALLOWED_HOSTS" "DATABASE_NAME" "DATABASE_USER"
    "DATABASE_PASSWORD" "DATABASE_HOST" "DATABASE_PORT" "REDIS_HOST"
    "REDIS_PORT" "SOCIAL_CLIENT_SECRET" "GOOGLE_CLIENT_ID" "BASE_URL"
    "USE_SQLITE_FOR_TESTS" "ABLY_API_KEY" "FIREBASE_ADMINSDK_KEY" "OMDB_KEY"
  )

  if [[ ! -f "${ROOT_PROJECT}/.env" ]]; then
    echo -e "${RED}Error: .env file is missing in the project root.${NC}"
    exit 1
  fi

  local missing_vars=()
  for var in "${required_vars[@]}"; do
    if ! grep -qE "^${var}=" "${ROOT_PROJECT}/.env"; then
      missing_vars+=("$var")
    fi
  done

  if [[ ${#missing_vars[@]} -gt 0 ]]; then
    echo -e "${RED}Error: Missing environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
      echo "  - $var"
    done
    exit 1
  fi

  echo -e "${GREEN}✓ All required environment variables are set.${NC}"
}

# Check prerequisites
check_prerequisite() {
  echo "Checking prerequisites..."

  command -v docker >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
  }
  echo -e "${GREEN}✓ Docker is installed.${NC}"

  docker compose version >/dev/null 2>&1 || {
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    exit 1
  }
  echo -e "${GREEN}✓ Docker Compose is installed.${NC}"

  validate_env

  if [[ ! -f "${TLS_DIR}/${CERT_FILE}" || ! -f "${TLS_DIR}/${KEY_FILE}" ]]; then
    echo -e "${RED}Error: TLS certificates are missing. Run 'create-tls-certs' command.${NC}"
    exit 1
  fi
  echo -e "${GREEN}✓ TLS certificates are present.${NC}"
}

# Create TLS Certificates
create_tls_certificates() {
  mkdir -p "${TLS_DIR}"

  if [[ -f "${TLS_DIR}/${CERT_FILE}" && -f "${TLS_DIR}/${KEY_FILE}" ]]; then
    # Check if the existing certificate is still valid
    if openssl x509 -checkend 86400 -noout -in "${TLS_DIR}/${CERT_FILE}"; then
      echo -e "${YELLOW}TLS certificates are valid and already exist. Skipping creation.${NC}"
      return
    else
      echo -e "${RED}Existing TLS certificates have expired. Regenerating...${NC}"
    fi
  fi

  # Use dynamic hostname if provided, default to localhost
  HOSTNAME=${1:-localhost}

  # Generate the certificate with Subject Alternative Name (SAN)
  openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${TLS_DIR}/${KEY_FILE}" -out "${TLS_DIR}/${CERT_FILE}" \
    -subj "/CN=${HOSTNAME}" \
    -addext "subjectAltName=DNS:${HOSTNAME}"

  echo -e "${GREEN}✓ TLS certificates with SAN created successfully. Adding to trusted store...${NC}"

  # Automatically add the newly created certificate to the trusted store
  add_trusted_cert
}



# Choose a service to display logs
choose_service() {
  echo "Available services:"
  for i in "${!SERVICES[@]}"; do
    echo "$((i + 1)). ${SERVICES[i]}"
  done

  echo -n "Enter the number corresponding to the service: "
  read -r service_number

  if [[ "$service_number" =~ ^[0-9]+$ ]] && (( service_number > 0 && service_number <= ${#SERVICES[@]} )); then
    CHOSEN_SERVICE="${SERVICES[service_number - 1]}"
  else
    echo -e "${RED}Invalid choice. Please select a valid service.${NC}"
    exit 1
  fi
}

# View logs for a specific service
view_logs() {
  choose_service
  echo -e "${GREEN}Displaying logs for service: ${CHOSEN_SERVICE}${NC}"
  docker compose -f "${DOCKER_COMPOSE_DEV}" logs -f "${CHOSEN_SERVICE}"
}

# Start development environment
run_dev() {
  echo -e "${GREEN}Starting development environment...${NC}"

  if [[ -f "${NGINX_DEV_TEMPLATE}" ]]; then
    envsubst '${BACKEND_CONTAINER}' < "${NGINX_DEV_TEMPLATE}" > "${NGINX_DEV}"
    echo -e "${GREEN}✓ NGINX configuration generated.${NC}"
  else
    echo -e "${RED}Error: NGINX_DEV_TEMPLATE not found.${NC}"
    exit 1
  fi

  docker compose -f "${DOCKER_COMPOSE_DEV}" --env-file "${ROOT_PROJECT}/.env" up --build -d
  docker compose -f "${DOCKER_COMPOSE_DEV}" ps
  echo -e "${GREEN}Development environment is running!${NC}"
  echo "Access the app at https://localhost"
}

# Check status of all services
check_status() {
  echo -e "${YELLOW}Checking the status of all services...${NC}"
  docker compose -f "${DOCKER_COMPOSE_DEV}" ps
}

# Stop all running services
stop_services() {
  echo -e "${YELLOW}Stopping all running services...${NC}"
  docker compose -f "${DOCKER_COMPOSE_DEV}" down
  echo -e "${GREEN}✓ Services stopped.${NC}"
}

# Reset environment
reset_environment() {
  echo -e "${YELLOW}Stopping and cleaning up environment...${NC}"
  docker compose -f "${DOCKER_COMPOSE_DEV}" down -v
  echo -e "${GREEN}✓ Environment reset complete.${NC}"
}

# Clean up environment
clean_environment() {
  echo -e "${YELLOW}Cleaning environment...${NC}"
  docker compose -f "${DOCKER_COMPOSE_DEV}" down -v
  rm -rf "${TLS_DIR}/${CERT_FILE}" "${TLS_DIR}/${KEY_FILE}" "${NGINX_DEV}"
  echo -e "${GREEN}✓ Environment cleaned.${NC}"
}

# Run a command in a specific service
exec_service() {
  # List available services
  echo "Available services:"
  for i in "${!SERVICES[@]}"; do
    echo "$((i + 1)). ${SERVICES[i]}"
  done

  # Prompt the user to select a service
  echo -n "Enter the number corresponding to the service: "
  read -r service_number

  # Validate input
  if [[ "$service_number" =~ ^[0-9]+$ ]] && (( service_number > 0 && service_number <= ${#SERVICES[@]} )); then
    local service="${SERVICES[service_number - 1]}"
    echo "Executing command in service: $service"
  else
    echo -e "${RED}Invalid choice. Please select a valid service.${NC}"
    exit 1
  fi

  # Prompt the user for the command to execute
  echo -n "Enter the command to execute in the $service container: "
  read -r cmd

  # Execute the command in the selected service
  docker compose -f "${DOCKER_COMPOSE_DEV}" exec "$service" bash -c "$cmd"
}

# Add TLS certificate to the trusted certificates store
add_trusted_cert() {
  echo -e "${YELLOW}Adding TLS certificate to the trusted certificates store...${NC}"

  if [[ ! -f "${TLS_DIR}/${CERT_FILE}" ]]; then
    echo -e "${RED}Error: TLS certificate not found at ${TLS_DIR}/${CERT_FILE}.${NC}"
    exit 1
  fi

  # Detect OS and add the certificate accordingly
  case "$(uname -s)" in
    Linux)
      if [[ -d /usr/local/share/ca-certificates ]]; then
        sudo cp "${TLS_DIR}/${CERT_FILE}" /usr/local/share/ca-certificates/localhost.crt
        sudo update-ca-certificates
        echo -e "${GREEN}✓ TLS certificate added to Linux trusted store.${NC}"
      else
        echo -e "${RED}Error: Unable to locate CA certificates directory. Ensure you have permissions.${NC}"
      fi
      ;;
    Darwin)
      sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "${TLS_DIR}/${CERT_FILE}"
      echo -e "${GREEN}✓ TLS certificate added to macOS trusted store.${NC}"
      ;;
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
      echo -e "${RED}Adding trusted certificates is not automated for Windows. Please add it manually.${NC}"
      echo -e "Steps for Windows:"
      echo -e "1. Open 'certlm.msc' (Certificates Management for Local Machine)."
      echo -e "2. Import '${TLS_DIR}/${CERT_FILE}' into the 'Trusted Root Certification Authorities' store."
      ;;
    *)
      echo -e "${RED}Error: Unsupported operating system for adding trusted certificates.${NC}"
      exit 1
      ;;
  esac
}

# Main logic
case "$1" in
  help) display_help ;;
  prerequisite) check_prerequisite ;;
  create-tls-certs) create_tls_certificates ;;
  dev) 
    check_prerequisite
    run_dev
    ;;
  logs)
    view_logs
    ;;
  status) check_status ;;
  stop) stop_services ;;
  exec) exec_service ;;
  reset) reset_environment ;;
  clean) clean_environment ;;
  add-trusted-cert) add_trusted_cert ;;  
  *)
    echo -e "${RED}Invalid command.${NC}"
    display_help
    exit 1
    ;;
esac
