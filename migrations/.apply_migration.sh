#!/bin/bash
# Скрипт для применения миграций базы данных
# Использование: ./migrations/.apply_migration.sh [migration_file]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo -e "${RED}Ошибка: Файл .env не найден${NC}"
    echo "Создайте файл .env на основе .env.example"
    exit 1
fi

# Загрузка переменных окружения
export $(grep -v '^#' .env | xargs)

# Проверка наличия DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Ошибка: DATABASE_URL не установлен в .env${NC}"
    exit 1
fi

# Файл миграции
MIGRATION_FILE=${1:-"migrations/0001_init.sql"}

# Проверка наличия файла миграции
if [ ! -f "$MIGRATION_FILE" ]; then
    echo -e "${RED}Ошибка: Файл миграции $MIGRATION_FILE не найден${NC}"
    exit 1
fi

echo -e "${YELLOW}Применение миграции: $MIGRATION_FILE${NC}"
echo "База данных: $DATABASE_URL"
echo ""

# Применение миграции
if psql "$DATABASE_URL" -f "$MIGRATION_FILE"; then
    echo ""
    echo -e "${GREEN}✓ Миграция успешно применена${NC}"
    echo ""
    echo "Проверка результата:"
    psql "$DATABASE_URL" -c "\dt"
else
    echo ""
    echo -e "${RED}✗ Ошибка при применении миграции${NC}"
    exit 1
fi
