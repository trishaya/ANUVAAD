import sqlite3
from datetime import datetime


class AnalyticsService:

    def __init__(self):

        self.db_name = "analytics.db"

        self.create_table()

    def connect(self):

        return sqlite3.connect(
            self.db_name
        )

    def create_table(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS translations (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT,

                source_lang TEXT,

                target_lang TEXT,

                model_used TEXT,

                response_time REAL,

                text_length INTEGER,

                success INTEGER
            )

        """)

        conn.commit()

        conn.close()

        print(
            "✅ Analytics table ready"
        )

    def log_translation(

        self,

        source_lang,

        target_lang,

        model_used,

        response_time,

        text_length,

        success=True
    ):

        try:

            conn = self.connect()

            cursor = conn.cursor()

            cursor.execute("""

                INSERT INTO translations (

                    timestamp,

                    source_lang,

                    target_lang,

                    model_used,

                    response_time,

                    text_length,

                    success

                )

                VALUES (?, ?, ?, ?, ?, ?, ?)

            """, (

                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                source_lang,

                target_lang,

                model_used,

                response_time,

                text_length,

                1 if success else 0
            ))

            conn.commit()

            conn.close()

            print(
                "📊 Translation logged"
            )

        except Exception as error:

            print(
                "❌ Analytics Logging Error:",
                str(error)
            )

    def get_stats(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT COUNT(*)
            FROM translations

        """)

        total_translations = (
            cursor.fetchone()[0]
        )

        cursor.execute("""

            SELECT AVG(response_time)
            FROM translations

        """)

        avg_response_time = (
            cursor.fetchone()[0]
        )

        if avg_response_time:

            avg_response_time = round(
                avg_response_time,
                2
            )

        else:

            avg_response_time = 0

        cursor.execute("""

            SELECT AVG(text_length)
            FROM translations

        """)

        avg_text_length = (
            cursor.fetchone()[0]
        )

        if avg_text_length:

            avg_text_length = round(
                avg_text_length,
                2
            )

        else:

            avg_text_length = 0

        conn.close()

        return {

            "total_translations":
                total_translations,

            "average_response_time":
                avg_response_time,

            "average_text_length":
                avg_text_length
        }

    def get_language_stats(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                target_lang,

                COUNT(*) as total

            FROM translations

            GROUP BY target_lang

            ORDER BY total DESC

        """)

        rows = cursor.fetchall()

        conn.close()

        results = []

        for row in rows:

            results.append({

                "language":
                    row[0],

                "count":
                    row[1]
            })

        return results

    def get_model_stats(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                model_used,

                COUNT(*) as total

            FROM translations

            GROUP BY model_used

            ORDER BY total DESC

        """)

        rows = cursor.fetchall()

        conn.close()

        results = []

        for row in rows:

            results.append({

                "model":
                    row[0],

                "count":
                    row[1]
            })

        return results

    def get_daily_stats(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                DATE(timestamp),

                COUNT(*)

            FROM translations

            GROUP BY DATE(timestamp)

            ORDER BY DATE(timestamp)

        """)

        rows = cursor.fetchall()

        conn.close()

        results = []

        for row in rows:

            results.append({

                "date":
                    row[0],

                "count":
                    row[1]
            })

        return results

    def get_success_stats(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT

                success,

                COUNT(*)

            FROM translations

            GROUP BY success

        """)

        rows = cursor.fetchall()

        conn.close()

        success_count = 0
        failure_count = 0

        for row in rows:

            if row[0] == 1:

                success_count = row[1]

            else:

                failure_count = row[1]

        return {

            "success":
                success_count,

            "failure":
                failure_count
        }