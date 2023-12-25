"""Module providing a db funtions for sqlite3."""

import sqlite3
from typing import Any, Optional
import uuid

from hw_15.models import User, Task


class DB:
    """Class for db functions"""

    def __init__(self, db_name: str) -> None:
        """init db"""
        self.db_name = db_name
        self.create_tables()

    def connection(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        """connection db"""
        con = sqlite3.connect(self.db_name)
        return con, con.cursor()

    def create_tables(self):
        """create tables"""
        con, cur = self.connection()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS \
                    Users(id primary key, login, password, is_admin)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS \
                    Tasks(id primary key, name, by_user)"
        )
        con.close()

    def add_user_or_admin(self, user: User) -> Any:
        """add user or admin"""
        con, cur = self.connection()
        user_id = uuid.uuid4().hex
        data = user_id, user.login, hash(user.password), user.is_admin
        cur.execute("INSERT INTO Users VALUES(?, ?, ?, ?)", data)
        con.commit()
        con.close()
        return user_id

    def add_task(self, task: Task) -> Any:
        """add task"""
        con, cur = self.connection()
        task_id = uuid.uuid4().hex
        data = (task_id, task.task_name, task.user_id)
        cur.execute("INSERT INTO Tasks VALUES(?, ?, ?)", data)
        con.commit()
        con.close()
        return task_id

    def edit_task(self, task_id: str, new_task_name: str) -> None:
        """edit task"""
        con, cur = self.connection()
        data = (new_task_name, task_id)
        cur.execute(
            """ UPDATE Tasks
                        SET name = ?
                        WHERE id = ?""",
            data,
        )
        con.commit()
        cur.close()

    def delete_task(self, task_id: str) -> None:
        """delete task"""
        con, cur = self.connection()
        cur.execute(
            """ DELETE FROM Tasks
                        WHERE id = ?""",
            (task_id,),
        )
        con.commit()
        con.close()

    def find_user_by_id(self, user_id: Any) -> Optional[User]:
        """find user by id"""
        con, cur = self.connection()
        cur.execute("SELECT * FROM Users WHERE id = ?", (user_id,))

        row = cur.fetchone()
        con.close()
        if row is not None:
            _, login, password, is_admin = row
            return User(login, password, is_admin)
        return None

    def find_user_id_by_login_and_passwrod(
        self, login: str, password: str
    ) -> Optional[Any]:
        """find user id by login and passwrod"""
        con, cur = self.connection()
        cur.execute("SELECT * FROM Users WHERE login = ?", (login,))

        rows = cur.fetchall()
        con.close()
        for row in rows:
            if row is not None and row[2] == hash(password):
                return row[0]
        return None

    def find_tasks_by_user_id(self, user_id: Any) -> list[tuple[Any, str]]:
        """find tasks by user id"""
        user = self.find_user_by_id(user_id)
        if user is None:
            return []

        con, cur = self.connection()

        if user.is_admin:
            cur.execute("SELECT * FROM Tasks")
        else:
            cur.execute("SELECT * FROM Tasks WHERE by_user = ?", (user_id,))
        rows = cur.fetchall()
        con.close()
        print(rows)
        res = []
        for row in rows:
            res.append((row[0], row[1]))
        return res


db = DB("hw_15.db")
