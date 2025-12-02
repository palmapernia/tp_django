#!/bin/bash
# Script para exportar datos de desarrollo a producción

echo "Exportando datos de desarrollo..."
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude=contenttypes --exclude=auth.permission \
    --exclude=sessions.session --exclude=admin.logentry \
    > production_data.json

echo "Datos exportados a production_data.json"
echo "En producción ejecuta: python manage.py loaddata production_data.json"