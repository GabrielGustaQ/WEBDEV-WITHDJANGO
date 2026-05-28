#!/bin/sh

set -e

echo "Aguardando banco de dados..."

while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
  sleep 1
done

echo "Banco disponível."

echo "Aplicando migrations..."
python manage.py migrate

if [ "$SEED_DB" = "True" ]; then
  echo "Executando seed..."
  python manage.py seed
fi

echo "Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000