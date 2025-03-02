import os
import psycopg2
import logging
import json
from psycopg2.extras import RealDictCursor

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger()

# Подключение к локальной БД PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "your_database")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
# Включение автофиксации для транзакций
conn.autocommit = True

cursor = conn.cursor(cursor_factory=RealDictCursor)

class DBQuery:
    def __init__(self, table):
        self.table = table
        self.action = "select"
        self.columns = "*"
        self.conditions = []
        self.joins = []
        self.data = []
        self.error = None
        self.values = None  # Для хранения значений в update и insert

        # Список всех возможных связей между таблицами
        self.foreign_keys = {
            "invoice": {"own_number": ("cards", "number")},
            "cards": {"owner": ("clients", "dsc_id")},
        }

        self._build_joins()

    def _build_joins(self):
        # Построение всех необходимых JOIN'ов для текущей таблицы
        if self.table == "invoice":
            self.joins.append("JOIN cards ON invoice.own_number = cards.number")
            self.joins.append("JOIN clients ON cards.owner = clients.dsc_id")
        elif self.table == "cards":
            self.joins.append("JOIN clients ON cards.owner = clients.dsc_id")

    def select(self, *columns):
        expanded_columns = set()

        if len(columns) == 1 and isinstance(columns[0], str):
            columns = [col.strip() for col in columns[0].split(",")]

        for col in columns:
            col = col.strip()

            if col.startswith("clients.") or col.startswith("cards."):
                expanded_columns.add(col)
            else:
                expanded_columns.add(f"{self.table}.{col}")

        self.columns = ", ".join(expanded_columns) if expanded_columns else "*"
        self.action = "select"
        return self

    def update(self, values):
        self.values = self._convert_jsonb(values)
        self.action = "update"
        return self

    def insert(self, values):
        self.values = self._convert_jsonb(values)
        self.action = "insert"
        return self

    def delete(self):
        self.action = "delete"
        return self

    def eq(self, column, value):
        self.conditions.append((column, value))
        return self

    def _convert_jsonb(self, values):
        """Преобразует `dict` в JSON-строку для PostgreSQL JSONB."""
        return {k: json.dumps(v) if isinstance(v, dict) else v for k, v in values.items()}

    def execute(self):
        if self.action == "select":
            # Формируем SQL для SELECT
            where_clause = " AND ".join([f"{col} = %s" for col, _ in self.conditions])
            joins_clause = " ".join(self.joins)
            sql = f"SELECT {self.columns} FROM {self.table} {joins_clause} " + (f"WHERE {where_clause}" if where_clause else "")
            params = tuple(val for _, val in self.conditions)

            cursor.execute(sql, params)
            self.data = [dict(row) for row in cursor.fetchall()]
        
        elif self.action == "update":
            # Формируем SQL для UPDATE
            set_clause = ", ".join([f"{col} = %s" for col in self.values.keys()])
            where_clause = " AND ".join([f"{col} = %s" for col, _ in self.conditions])
            sql = f"UPDATE {self.table} SET {set_clause} WHERE {where_clause}"

            params = list(self.values.values()) + [val for _, val in self.conditions]
            cursor.execute(sql, params)
            conn.commit()
        
        elif self.action == "insert":
            # Формируем SQL для INSERT
            columns = ", ".join(self.values.keys())
            placeholders = ", ".join(["%s"] * len(self.values))
            sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders}) RETURNING *"

            cursor.execute(sql, tuple(self.values.values()))
            conn.commit()
            self.data = [dict(cursor.fetchone())]  # Сохраняем вставленные данные


        elif self.action == "delete":
            # Формируем SQL для DELETE
            where_clause = " AND ".join([f"{col} = %s" for col, _ in self.conditions])
            sql = f"DELETE FROM {self.table} WHERE {where_clause}" if where_clause else f"DELETE FROM {self.table}"

            params = tuple(val for _, val in self.conditions)
            cursor.execute(sql, params)
            conn.commit()

        # Логируем запрос
        logger.info(f"📋 DB Request - {sql} | Params: {params if 'params' in locals() else 'N/A'}")

        return self

    def __str__(self):
        return f"{{'data': {self.data}, 'error': {self.error}}}"


class DBRPC:
    def __init__(self, function_name, params):
        self.function_name = function_name
        self.params = params
        self.data = []
        self.error = None

    def execute(self):
        # Формируем строку с параметрами, которые будут переданы в SQL
        if self.params:
            placeholders = ", ".join(["%s"] * len(self.params))
            sql = f"SELECT * FROM {self.function_name}({placeholders})"
        else:
            # Если params пуст, просто вызываем функцию без параметров
            sql = f"SELECT * FROM {self.function_name}()"

        try:
            # Выполнение запроса
            cursor.execute(sql, tuple(self.params.values()))

            logger.info(f"📋 DB Request - SQL: {sql} | Params: {self.params}")

            # Если возвращаемое значение - это список
            if isinstance(cursor, list):
                self.data = [cursor]
            else:
                self.data = cursor.fetchall()
            
        except Exception as e:
            # В случае ошибки логируем информацию об ошибке
            self.error = str(e)
            logger.error(f"❌ DB Error - SQL: {sql} | Error: {self.error}")

        return self

    def __str__(self):
        # Форматируем вывод в нужный вид
        return f"{{'data': {self.data}, 'error': {self.error}}}"



def db_cursor(table_name):
    return DBQuery(table_name)

def db_rpc(function_name, params):
    return DBRPC(function_name, params)

# Пример использования
# result = db_cursor("users").select("*").eq("id", 1).execute()
# print(result.data)

# Пример вызова хранимой функции
# rpc_result = db_rpc("get_user_cards_demote", {"user_id": 12345})
# print(rpc_result.data)
