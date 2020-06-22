import sqlite3


class SqliteConnection:

    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_channel_table()

    def _create_channel_table(self):
        with self.connection:
            self.connection.execute("""CREATE TABLE IF NOT EXISTS guilds 
                (id string,
                webhook_id integer NOT NULL,
                user_id text,
                name text,
                CONSTRAINT user_unique UNIQUE (id, webhook_id, user_id)
                )""")

    def select_records_by_id(self, id: str):
        with self.connection:
            c = self.connection.execute("SELECT * FROM guilds WHERE id=(?)", [id])
            return c.fetchall()

    def select_records_by_user_id(self, user_id: str):
        with self.connection:
            c = self.connection.execute("SELECT * FROM guilds WHERE user_id=(?)", [user_id])
            return c.fetchall()

    def select_record(self, id: str, webhook_id: str, user_id: str):
        with self.connection:
            c = self.connection.execute("SELECT * FROM guilds WHERE id=(?) AND webhook_id=(?) AND user_id=(?)",
                                        [id, webhook_id, user_id])
            return c.fetchone()

    def delete_record(self, id: str, user_id: str):
        with self.connection:
            c = self.connection.execute("DELETE FROM guilds WHERE id=(?) AND user_id=(?)",
                                        [id, user_id])
            return c.fetchone()

    def insert_record(self, id: str, webhook_id: str, user_id: str, name: str):
        with self.connection:
            c = self.connection.execute("INSERT INTO guilds VALUES (?, ?, ?, ?)",
                                        [id, webhook_id, user_id, name])
            return c.fetchone()

    def update_name_of_record(self, user_id: str, name: str):
        with self.connection:
            c = self.connection.execute("UPDATE guilds SET name = (?) WHERE user_id = (?)",
                                        [name, user_id])

    def update_webhook_id_of_record(self, id: str, webhook_id: str):
        with self.connection:
            c = self.conneciton.execute("UPDATE guilds SET webhook_id = (?) WHERE id = (?)",
                                        [webhook_id, id])
