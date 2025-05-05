import os
import sys
import sqlite3
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Путь к базе данных
DB_PATH = 'instance/codes.db'  # Измените путь, если ваша БД находится в другом месте


def check_db_exists():
    """Проверка существования файла базы данных"""
    if not os.path.exists(DB_PATH):
        logger.error(f"База данных не найдена по пути: {DB_PATH}")
        return False
    return True


def create_admin_messages_table():
    """Создание таблицы для сообщений админу"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем существование таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_message'")
        if cursor.fetchone():
            logger.info("Таблица admin_message уже существует")
            conn.close()
            return True

        # Создаем таблицу
        cursor.execute('''
        CREATE TABLE admin_message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            code_id INTEGER NOT NULL,
            created_at TIMESTAMP NOT NULL,
            read BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (code_id) REFERENCES code_status(id)
        )
        ''')

        conn.commit()
        logger.info("Таблица admin_message успешно создана")
        conn.close()
        return True

    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite при создании таблицы: {e}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return False


def main():
    """Основная функция миграции"""
    logger.info("Начало процесса миграции базы данных")

    if not check_db_exists():
        return 1

    if not create_admin_messages_table():
        return 1

    logger.info("Миграция базы данных успешно завершена")
    return 0


if __name__ == "__main__":
    sys.exit(main())

