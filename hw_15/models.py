"""User and Task represantation"""
import dataclasses


@dataclasses.dataclass
class User:
    """User represantation"""

    def __init__(self, login: str, password: str, is_admin: bool) -> None:
        self.login = login
        self.password = password
        self.is_admin = is_admin


@dataclasses.dataclass
class Task:
    """Task represantation"""

    def __init__(self, task_name: str, user_id: str) -> None:
        self.task_name = task_name
        self.user_id = user_id
