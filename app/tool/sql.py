import mysql.connector

from app.tool import extractor


def execute_sql_to_csv(sql: str, file_path: str, db_config: dict) -> str:
    conn = mysql.connector.connect(**db_config)
    results = extractor.execute_mysql_and_save_to_csv(sql, conn, file_path)
    conn.close()
    return results