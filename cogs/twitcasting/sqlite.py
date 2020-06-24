import sqlite3


class SqliteConnection:

    def __init__(self, db_path: str):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._create_channel_table()

    def _create_channel_table(self):
        sql = """CREATE TABLE IF NOT EXISTS guilds 
                (channel_id string,
                webhook_id integer NOT NULL,
                user_id text,
                name text,
                CONSTRAINT user_unique UNIQUE (id, webhook_id, user_id)
                )"""
        with self.connection:
            self.connection.execute(sql)

    def select_records_by_id(self, channel_id: str):
        sql = "SELECT * FROM guilds WHERE channel_id = (?)"
        with self.connection:
            c = self.connection.execute(sql, [channel_id])
            return c.fetchall()

    def select_records_by_user_id(self, user_id: str):
        sql = "SELECT * FROM guilds WHERE user_id = (?)"
        with self.connection:
            c = self.connection.execute(sql, [user_id])
            return c.fetchall()

    def select_record(self, channel_id: str, webhook_id: str, user_id: str):
        sql = "SELECT * FROM guilds WHERE channel_id = (?) AND webhook_id = (?) AND user_id = (?)"
        with self.connection:
            c = self.connection.execute(sql, [channel_id, webhook_id, user_id])
            return c.fetchone()

    def delete_all_records(self, channel_id: str):
        sql = "DELETE FROM guilds where channel_id = (?)"
        with self.connection:
            self.connection.execute(sql, [channel_id])

    def delete_record(self, channel_id: str, user_id: str):
        sql = "DELETE FROM guilds WHERE channel_id = (?) AND user_id = (?)"
        with self.connection:
            self.connection.execute(sql, [channel_id, user_id])

    def insert_record(self, channel_id: str, webhook_id: str, user_id: str, name: str):
        sql = "INSERT INTO guilds VALUES (?, ?, ?, ?)"
        with self.connection:
            c = self.connection.execute(sql, [channel_id, webhook_id, user_id, name])
            return c.fetchone()

    def update_name_of_record(self, user_id: str, name: str):
        sql = "UPDATE guilds SET name = (?) WHERE user_id = (?)"
        with self.connection:
            c = self.connection.execute(sql, [name, user_id])

    def update_webhook_id_of_record(self, channel_id: str, webhook_id: str):
        sql = "UPDATE guilds SET webhook_id = (?) WHERE channel_id = (?)"
        with self.connection:
            c = self.connection.execute(sql, [webhook_id, channel_id])
