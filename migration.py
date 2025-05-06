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

DB_PATH = 'instance/codes.db'

def check_db_exists():
    if not os.path.exists(DB_PATH):
        logger.error(f"База данных не найдена по пути: {DB_PATH}")
        return False
    return True

def column_exists(cursor, table_name, column_name):
    """Проверяет, есть ли столбец в таблице"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_admin_id_column():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if not column_exists(cursor, 'admin_message', 'admin_id'):
            logger.info("Добавляем колонку admin_id в таблицу admin_message")

            cursor.execute("ALTER TABLE admin_message ADD COLUMN admin_id INTEGER")
            conn.commit()
            logger.info("Колонка admin_id успешно добавлена")

        else:
            logger.info("Колонка admin_id уже существует — пропускаем")

        conn.close()
        return True

    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite: {e}")
        return False

def main():
    logger.info("Запуск миграции для добавления admin_id в admin_message")

    if not check_db_exists():
        return 1

    if not add_admin_id_column():
        return 1

    logger.info("Миграция успешно завершена")
    return 0

if __name__ == "__main__":
    sys.exit(main())
