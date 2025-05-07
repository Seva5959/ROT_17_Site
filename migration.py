import os
import sys
import sqlite3
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_PATH = 'instance/codes.db'  # Проверь путь к БД

def check_db_exists():
    if not os.path.exists(DB_PATH):
        logger.error(f"База данных не найдена по пути: {DB_PATH}")
        return False
    return True

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_column_if_missing(cursor, table, column, column_type, default_value):
    if not column_exists(cursor, table, column):
        logger.info(f"Добавляем колонку {column} в таблицу {table}")
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type} DEFAULT {default_value}")
    else:
        logger.info(f"Колонка {column} уже существует")

def apply_migration():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        add_column_if_missing(cursor, 'admin_message', 'read_by_user', 'BOOLEAN', 0)
        add_column_if_missing(cursor, 'admin_message', 'read_by_admin', 'BOOLEAN', 0)

        conn.commit()
        conn.close()
        logger.info("Миграция успешно завершена")
        return True
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite: {e}")
        return False

def main():
    logger.info("Запуск миграции: добавление read_by_user и read_by_admin")
    if not check_db_exists():
        return 1
    if not apply_migration():
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
