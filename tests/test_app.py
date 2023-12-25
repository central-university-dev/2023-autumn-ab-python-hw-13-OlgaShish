import pytest
import hw_15.main
import hw_15.token
import hw_15.models
import hw_15.app
import hw_15.db
import asyncio
import json
import os


def test_read_body_is_none():
    async def helper():
        return {}

    v = asyncio.run(hw_15.main.read_body(helper))

    assert v is None


def test_read_body_is_not_none():
    dum = json.dumps({"login": "1", "password": "1", "is_admin": False})
    body = {"body": dum.encode("utf-8")}

    async def helper():
        return body

    v = asyncio.run(hw_15.main.read_body(helper))

    assert v == {"login": "1", "password": "1", "is_admin": False}


def test_send_response(mocker):
    async def helper_id(x):
        return x

    v = asyncio.run(hw_15.main.send_response(helper_id, {}, "", True))

    assert v is None

    v = asyncio.run(hw_15.main.send_response(helper_id, {}, "", False))

    assert v is None


def test_application_none(mocker):
    async def helper():
        return {}

    async def helper_id(x):
        return x

    v = asyncio.run(hw_15.main.application(None, helper, helper_id))

    assert v is None


def test_application_bad_path(mocker):
    async def helper_id(x):
        return x

    mocked_dict = {"body": {"login": "1", "password": "1", "is_admin": False}}
    mocker.patch.object(hw_15.main, "read_body", return_value=mocked_dict)

    scope = {
        "type": "http",
        "scheme": "http",
        "root_path": "",
        "server": ("127.0.0.1", 8000),
        "http_version": "1.1",
        "method": "",
        "path": "/add_task",
        "headers": [
            (b"host", b"127.0.0.1:8000"),
            (b"user-agent", b"curl/7.51.0"),
            (b"accept", b"*/*"),
        ],
    }
    v = asyncio.run(hw_15.main.application(scope, None, helper_id))

    assert v is None


def test_application():
    payload = {"body": {"login": "1", "password": "1", "is_admin": False}}
    dum = json.dumps(payload)
    body = {"body": dum.encode("utf-8")}

    async def helper():
        return body

    async def helper_id(x):
        return x

    scope = {
        "type": "http",
        "scheme": "http",
        "root_path": "/",
        "server": ("127.0.0.1", 8000),
        "http_version": "1.1",
        "method": "POST",
        "path": "/add_task",
        "headers": [
            (b"host", b"127.0.0.1:8000"),
            (b"user-agent", b"curl/7.51.0"),
            (b"accept", b"*/*"),
        ],
    }
    v = asyncio.run(hw_15.main.application(scope, helper, helper_id))

    assert v is None

    scope["path"] = "/add_user"

    v = asyncio.run(hw_15.main.application(scope, helper, helper_id))

    assert v is None

    scope["path"] = "/edit_task"

    v = asyncio.run(hw_15.main.application(scope, helper, helper_id))

    assert v is None

    scope["path"] = "/delete_task"

    v = asyncio.run(hw_15.main.application(scope, helper, helper_id))

    assert v is None

    scope["path"] = "/get_list_tasks"
    scope["method"] = "GET"

    v = asyncio.run(hw_15.main.application(scope, helper, helper_id))

    assert v is None


def test_read_token_is_none():
    token = b"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.\
V8ELQLA8XEwR4JDqFIM45MUzuQ75NyIjqheefo6Gmag"
    v = hw_15.token.read_token({"token": token})
    assert v == {"user_id": 123}


def test_is_token_need_refresh():
    token = b"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\
eyJ1c2VyX2lkIjoxMjMsInRpbWUiOiIyMDIzLTEyLTIzIDAwOjE0OjM5In0.\
XHQle2IuJS4C_W97OrOxgPVQJfPEtxl7_Oc8-I5cu4A"
    body = {"token": token}
    op = hw_15.token.is_token_need_refresh(body)
    assert op

    token = hw_15.token.make_token("123")
    body = {"token": token}
    op = hw_15.token.is_token_need_refresh(body)
    assert not op


def test_get_field_xss():
    with pytest.raises(hw_15.app.BadField):
        hw_15.app.get_field({"xss": "<script>alert(123)</script>"}, "xss")


def test_login_user(mocker):
    body = {"body": {"login": "1", "password": "1", "is_admin": False}}
    mocker.patch.object(
        hw_15.db.db, "find_user_id_by_login_and_passwrod", return_value="123"
    )
    mocker.patch.object(hw_15.db.db, "add_user_or_admin", return_value="123")
    v = asyncio.run(hw_15.app.login_user(body, None))
    assert v is None
    v = asyncio.run(hw_15.app.login_user(body, "123"))
    assert v == "123"

    mocker.patch.object(
        hw_15.db.db, "find_user_id_by_login_and_passwrod", return_value="123"
    )
    v = asyncio.run(hw_15.app.login_user(body, "12"))
    assert v is None


def test_add_task(mocker):
    with pytest.raises(hw_15.app.BadField):
        asyncio.run(hw_15.app.add_task(None, {}))

    mocker.patch.object(hw_15.db.db, "add_task", return_value=None)
    v = asyncio.run(hw_15.app.add_task("123", {"task_name": "123"}))
    assert v is None


def test_edit_task(mocker):
    v = asyncio.run(hw_15.app.edit_task(None, {}))
    assert v is None

    mocker.patch.object(hw_15.db.db, "edit_task", return_value=None)
    tasks = [("123", "123")]
    method = "find_tasks_by_user_id"
    mocker.patch.object(hw_15.db.db, method, return_value=tasks)
    body = {"task_name": "123", "task_id": "123"}
    v = asyncio.run(hw_15.app.edit_task("123", body))
    assert v is None


def test_delete_task(mocker):
    with pytest.raises(hw_15.app.BadField):
        asyncio.run(hw_15.app.delete_task(None, {}))

    mocker.patch.object(hw_15.db.db, "delete_task", return_value=None)
    tasks = [("123", "123")]
    method = "find_tasks_by_user_id"
    mocker.patch.object(hw_15.db.db, method, return_value=tasks)
    v = asyncio.run(hw_15.app.delete_task("123", {"task_id": "123"}))
    assert v is None


def test_get_tasks_list(mocker):
    with pytest.raises(hw_15.app.BadField):
        asyncio.run(hw_15.app.get_tasks_list(None))

    tasks = [("123", "123")]
    method = "find_tasks_by_user_id"
    mocker.patch.object(hw_15.db.db, method, return_value=tasks)
    v = asyncio.run(hw_15.app.get_tasks_list("123"))
    assert v == [{"task_name": "123", "task_id": "123"}]


def test_db():
    test_db = hw_15.db.DB("test.db")
    user = hw_15.models.User("user", "user", False)
    admin = hw_15.models.User("admin", "admin", True)
    user_id = test_db.add_user_or_admin(user)
    admin_id = test_db.add_user_or_admin(admin)
    user = test_db.find_user_by_id(user_id)
    assert user.password == hash("user")
    admin = test_db.find_user_by_id(admin_id)
    assert admin.password == hash("admin")
    f_user_id = test_db.find_user_id_by_login_and_passwrod("user", "user")
    assert f_user_id == user_id
    f_admin_id = test_db.find_user_id_by_login_and_passwrod("admin", "admin")
    assert f_admin_id == admin_id
    task_id_user = test_db.add_task(hw_15.models.Task("test_user", user_id))
    task_id_admin = test_db.add_task(hw_15.models.Task("test_admin", admin_id))
    test_db.edit_task(task_id_user, "new_task_user")
    test_db.edit_task(task_id_admin, "new_task_admin")
    tasks_user = test_db.find_tasks_by_user_id(user_id)
    assert tasks_user == [(task_id_user, "new_task_user")]
    tasks_admin = test_db.find_tasks_by_user_id(admin_id)
    assert tasks_admin == [
        (task_id_user, "new_task_user"),
        (task_id_admin, "new_task_admin"),
    ]
    test_db.delete_task(task_id_user)
    tasks_admin = test_db.find_tasks_by_user_id(admin_id)
    assert tasks_admin == [(task_id_admin, "new_task_admin")]
    path = os.getcwd()
    print(path)
    os.remove(path + "/test.db")
