#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
  echo "Running all tests..."
  # Instalación de las dependencias por seguridad
  pip install --quiet pytest pandas numpy scikit-learn --break-system-packages 2>/dev/null || true

  # Cambiamos al directorio de los tests
  cd /app/tests
  
  # Ejecutamos pytest, se asume que las variables de entorno lo redirigen
  pytest test_main.py -v --tb=short
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
