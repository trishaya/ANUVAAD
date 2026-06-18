import sqlite3
from datetime import datetime


class ErrorLogger:

    def __init__(self):

        self.db_name = "errors.db"

        self.create_table()

    def connect(self):

        return sqlite3.connect(
            self.db_name
        )

    def create_table(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS errors (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT,

                endpoint TEXT,

                error_message TEXT

            )

        """)

        conn.commit()

        conn.close()

        print(
            "✅ Error logging ready"
        )

    def log_error(

        self,

        endpoint,

        error_message
    ):

        try:

            conn = self.connect()

            cursor = conn.cursor()

            cursor.execute("""

                INSERT INTO errors (

                    timestamp,

                    endpoint,

                    error_message

                )

                VALUES (?, ?, ?)

            """, (

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                endpoint,

                error_message
            ))

            conn.commit()

            conn.close()

            print(
                "Error logged"
            )

        except Exception as error:

            print(
                "Error Logger Failed:",
                str(error)
            )

    def get_errors(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                timestamp,
                endpoint,
                error_message

            FROM errors

            ORDER BY id DESC

        """)

        rows = cursor.fetchall()

        conn.close()

        results = []

        for row in rows:

            results.append({

                "timestamp":
                    row[0],

                "endpoint":
                    row[1],

                "error":
                    row[2]
            })

        return results