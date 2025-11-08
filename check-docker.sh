#!/bin/bash

# Скрипт проверки Docker окружения для Telegram бота

echo "🐳 Проверка Docker окружения для Telegram бота"
echo "=============================================="

# Проверка установки Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
else
    echo "✅ Docker установлен: $(docker --version)"
fi

# Проверка установки Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose не установлен"
    exit 1
else
    echo "✅ Docker Compose установлен: $(docker compose version)"
fi

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден"
    echo "📝 Создайте .env файл из примера:"
    echo "   make env"
    echo "   cp .env.example .env"
else
    echo "✅ Файл .env найден"
fi

# Проверка обязательных переменных в .env
if [ -f .env ]; then
    echo ""
    echo "🔍 Проверка переменных окружения:"
    
    required_vars=("BOT_TOKEN" "YOOKASSA_SHOP_ID" "YOOKASSA_API_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "^${var}=your_" .env && ! grep -q "^${var}=$" .env; then
            echo "✅ $var установлен"
        else
            echo "❌ $var не установлен или имеет значение по умолчанию"
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  Установите следующие переменные в .env:"
        printf '   %s\n' "${missing_vars[@]}"
    fi
fi

# Проверка наличия необходимых файлов
echo ""
echo "📁 Проверка файлов проекта:"
files=("Dockerfile" "docker-compose.yml" "requirements.txt" "Makefile" ".env.example")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file не найден"
    fi
done

# Проверка структуры директорий
echo ""
echo "📂 Проверка директорий:"
dirs=("src" "migrations" "tests")

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ не найдена"
    fi
done

# Проверка синтаксиса Python файлов
echo ""
echo "🐍 Проверка синтаксиса Python файлов:"
python_files=("src/main.py" "src/config.py" "src/services/scenario_service.py" "src/handlers/commands.py")

for file in "${python_files[@]}"; do
    if [ -f "$file" ]; then
        if python -m py_compile "$file" 2>/dev/null; then
            echo "✅ $file - синтаксис корректен"
        else
            echo "❌ $file - ошибка синтаксиса"
        fi
    fi
done

# Проверка Docker файлов
echo ""
echo "🐳 Проверка Docker конфигурации:"
if docker compose config >/dev/null 2>&1; then
    echo "✅ docker-compose.yml - конфигурация корректна"
else
    echo "❌ docker-compose.yml - ошибка в конфигурации"
fi

# Проверка доступности Docker образов
echo ""
echo "📦 Проверка доступности Docker образов:"
images=("python:3.10-slim" "postgres:15-alpine" "redis:7-alpine")

for image in "${images[@]}"; do
    if docker pull "$image" --dry-run >/dev/null 2>&1 || docker images | grep -q "$image"; then
        echo "✅ $image - доступен"
    else
        echo "⚠️  $image - может потребоваться загрузка"
    fi
done

echo ""
echo "🚀 Команды для запуска:"
echo "   make env          # Создать .env файл"
echo "   make build        # Собрать образы"
echo "   make up           # Запустить сервисы"
echo "   make migrate      # Применить миграции"
echo "   make logs         # Просмотр логов"
echo "   make status       # Проверка статуса"

echo ""
echo "=============================================="
echo "✅ Проверка завершена!"