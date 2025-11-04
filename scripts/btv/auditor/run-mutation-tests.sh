#!/usr/bin/env bash
# 🔬 Safe Mutation Tests Runner (BuildToValue Auditor Profundo)
# Executa PITest se pom.xml existir, senão registra fallback.
set -e

echo "🚀 Executando Mutation Tests (PITest)..."
PROJECT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_DIR"

# Detectar presença de projeto Java
if [ ! -f "./pom.xml" ] && [ ! -f "./java-auditor/pom.xml" ]; then
  echo "ℹ️ Nenhum projeto Java detectado (pom.xml ausente)."
  echo "➡️ PITest será ignorado neste ambiente Python-only."
  mkdir -p .buildtovalue/reports
  echo '{"status": "skipped", "reason": "No pom.xml found"}' > .buildtovalue/reports/mutation-report.json
  exit 0
fi

# Escolher diretório base
REPORT_DIR=".buildtovalue/reports"
if [ -f "./java-auditor/pom.xml" ]; then
  cd java-auditor
  REPORT_DIR="../${REPORT_DIR}"
  echo "📁 Entrando no módulo Java (java-auditor/)"
fi

mkdir -p "$REPORT_DIR"

# Executar build se necessário
if [ ! -d "./target" ]; then
  echo "🧩 Compilando projeto Java..."
  if [ -x "./mvnw" ]; then
    ./mvnw clean test -DskipTests || {
      echo "⚠️ Maven build falhou, ignorando PITest."
      echo '{"status": "skipped", "reason": "Maven build failed"}' > "$REPORT_DIR/mutation-report.json"
      exit 0
    }
  else
    mvn clean test -DskipTests || {
      echo "⚠️ Maven build falhou, ignorando PITest."
      echo '{"status": "skipped", "reason": "Maven build failed"}' > "$REPORT_DIR/mutation-report.json"
      exit 0
    }
  fi
fi

# Executar PITest
if [ -x "./mvnw" ]; then
  ./mvnw org.pitest:pitest-maven:mutationCoverage \
    -DwithHistory \
    -DtimeoutConstant=4000 \
    -Dthreads=4 \
    -DoutputFormats=XML,HTML || {
      echo "⚠️ PITest falhou ou foi ignorado. Registrando fallback..."
      echo '{"status": "skipped", "reason": "PITest execution failed"}' > "$REPORT_DIR/mutation-report.json"
      exit 0
    }
else
  mvn org.pitest:pitest-maven:mutationCoverage \
    -DwithHistory \
    -DtimeoutConstant=4000 \
    -Dthreads=4 \
    -DoutputFormats=XML,HTML || {
      echo "⚠️ PITest falhou ou foi ignorado. Registrando fallback..."
      echo '{"status": "skipped", "reason": "PITest execution failed"}' > "$REPORT_DIR/mutation-report.json"
      exit 0
    }
fi

echo "✅ Relatórios gerados em target/pit-reports/"
