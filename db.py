import os
import psycopg2
from psycopg2.extras import RealDictCursor

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
cursor = conn.cursor(cursor_factory=RealDictCursor)

class DBQuery:
    def __init__(self, table):
        self.table = table
        self.action = "select"
        self.columns = "*"
        self.conditions = []
        self.joins = []
        self.data = {}

        # Определение связей между таблицами
        self.foreign_keys = {
            "cards": {"owner": ("clients", "dsc_id")},
            "invoice": {"own_number": ("cards", "number")},
        }

    def select(self, *columns):
        expanded_columns = set()  # Используем `set`, чтобы убрать дубликаты

        # Если columns передан как одна строка, разбиваем её по запятым
        if len(columns) == 1 and isinstance(columns[0], str):
            columns = [col.strip() for col in columns[0].split(",")]

        print(f"test1   columns: {columns}")  # Проверяем входные данные после обработки

        for col in columns:
            col = col.strip()
            
            # Если колонка относится к clients, добавляем её в expanded_columns и добавляем JOIN
            if col.startswith("clients."):
                expanded_columns.add(col)

                # Автоматически добавляем JOIN на основе foreign_keys, если связь с clients существует
                if "cards" in self.foreign_keys and "owner" in self.foreign_keys["cards"]:
                    fk_table, fk_column = self.foreign_keys["cards"]["owner"]
                    join_condition = f"cards.owner = {fk_table}.{fk_column}"
                    join_statement = f"JOIN {fk_table} ON {join_condition}"
                    if join_statement not in self.joins:  # Добавляем JOIN только один раз
                        self.joins.append(join_statement)
            else:
                expanded_columns.add(f"{self.table}.{col}")  # Добавляем таблицу к колонке, если это не сложное поле

        # Собираем итоговые колонки для запроса
        self.columns = ", ".join(expanded_columns) if expanded_columns else "*"
        
        print(f"test5   final_columns: {self.columns}")  # Проверяем итоговый список колонок
        print(f"test6   final_joins: {self.joins}")  # Проверяем итоговые JOIN'ы
        
        # Формируем SQL запрос
        joins_clause = " ".join(self.joins)
        where_clause = " AND ".join([f"{col} = %s" for col, _ in self.conditions])
        sql = f"SELECT {self.columns} FROM {self.table} {joins_clause} " + (f"WHERE {where_clause}" if where_clause else "")
        
        print(f"Executing SQL: {sql}")  # Выводим итоговый запрос
        cursor.execute(sql, tuple(val for _, val in self.conditions))
        self.data = cursor.fetchall()
        return self


    def eq(self, column, value):
        self.conditions.append((column, value))
        return self

    def execute(self):
        where_clause = " AND ".join([f"{col} = %s" for col, _ in self.conditions])
        joins_clause = " ".join(self.joins)
        sql = f"SELECT {self.columns} FROM {self.table} {joins_clause} " + (f"WHERE {where_clause}" if where_clause else "")
        print(f"Executing SQL: {sql}")  # <-- Добавь это перед cursor.execute()
        cursor.execute(sql, tuple(val for _, val in self.conditions))
        self.data = cursor.fetchall()
        return self



class DBRPC:
    def __init__(self, function_name, params):
        self.function_name = function_name
        self.params = params
        self.data = self.execute()

    def execute(self):
        placeholders = ", ".join(["%s"] * len(self.params))
        sql = f"SELECT * FROM {self.function_name}({placeholders})"
        cursor.execute(sql, tuple(self.params.values()))
        return cursor.fetchall()

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
