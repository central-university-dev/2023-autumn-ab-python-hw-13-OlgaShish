"""functions for application, working when the endpoint is called"""


from typing import Any, Optional
import html
from hw_15.models import User, Task
from hw_15.db import db


class BadField(Exception):
    """Exception for bad filed in body"""


def get_field(body: dict, name: str) -> Any:
    """helper function for get field from body"""
    val = body.get(name, None)
    if val is not None and (isinstance(val, str) and html.escape(val) != val):
        raise BadField
    return val


async def login_user(body: dict, op_user_id: Optional[Any]) -> Optional[Any]:
    """login user or add into db"""
    login = get_field(body, "login")
    password = get_field(body, "password")
    is_admin = get_field(body, "is_admin")

    user_id = db.find_user_id_by_login_and_passwrod(login, password)
    print(user_id, op_user_id)
    if user_id is not None:
        if op_user_id is not None and op_user_id == user_id:
            return user_id
        return None
    user_id = db.add_user_or_admin(User(login, password, is_admin))
    return user_id


async def add_task(user_id: Optional[Any], body: dict) -> None:
    """add task by user id"""
    if user_id is None:
        raise BadField

    task_name = get_field(body, "task_name")
    db.add_task(Task(task_name, user_id))


async def edit_task(user_id: Optional[Any], body: dict) -> None:
    """edit task by user id"""
    if user_id is None:
        return None

    task_name = get_field(body, "task_name")
    task_id = get_field(body, "task_id")

    task_names = db.find_tasks_by_user_id(user_id)
    if (task_id, task_name) in task_names:
        db.edit_task(task_id, task_name)


async def delete_task(user_id: Optional[Any], body: dict) -> None:
    """delete task by user id"""
    if user_id is None:
        raise BadField

    task_id = get_field(body, "task_id")

    tasks = db.find_tasks_by_user_id(user_id)
    task_ids = list(map(lambda task: task[0], tasks))
    if task_id in task_ids:
        db.delete_task(task_id)


async def get_tasks_list(user_id: Optional[Any]) -> list[dict[str, str]]:
    """get list of tasks by user id"""
    if user_id is None:
        raise BadField

    tasks = db.find_tasks_by_user_id(user_id)
    res = []
    for task in tasks:
        res.append({"task_name": task[0], "task_id": task[1]})
    return res
