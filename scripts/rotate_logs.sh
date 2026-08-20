#!/bin/bash

# Переменные
LOG_DIR="/Users/mezentsev_d/bystroed/logs"
ARCHIVE_DIR="/Users/mezentsev_d/bystroed/logs/archive"
DAYS_TO_KEEP=7

echo "=== Start log rotation at $(date) ==="

# Ищем файлы старше 7 дней
# -type f : только файлы
# -mtime +7 : изменённые более 7 дней назад
OLD_FILES=$(find "$LOG_DIR" -maxdepth 1 -type f -name "*.log" -mtime +$DAYS_TO_KEEP)

if [ -z "$OLD_FILES" ]; then
    echo "No old files found. Exiting."
    exit 0
fi

echo "Found old files:"
echo "$OLD_FILES"

# Создаём имя архива с текущей датой
ARCHIVE_NAME="logs_$(date +%Y%m%d_%H%M%S).tar.gz"

# Архивируем
# tar -czf : create, gzip, file
echo "Creating archive $ARCHIVE_NAME..."
tar -czf "$ARCHIVE_DIR/$ARCHIVE_NAME" -C "$LOG_DIR" $(echo "$OLD_FILES" | xargs -n 1 basename)

# Удаляем старые файлы
echo "Deleting old files..."
echo "$OLD_FILES" | xargs rm

echo "=== Rotation finished ==="
