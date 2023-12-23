"""Module providing a fwt token functions with user id and time for sessions"""

from typing import Any, Optional
from datetime import datetime, timedelta
import json
import jwt  # type: ignore


def read_token(body: dict) -> Optional[Any]:
    """read token from dict by config key_word"""
    with open("config.json", encoding="utf-8") as config:
        key_word = json.load(config)["key_word"]
    token = body.get("token", None)
    if token is None:
        return None
    jwt_token = jwt.decode(token, key_word, algorithms=["HS256"])
    return jwt_token


def make_token(user_id: Any) -> str:
    """make token by config key_word and user_id"""
    with open("config.json", encoding="utf-8") as config:
        key_word = json.load(config)["key_word"]
    json_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = {"user_id": str(user_id), "time": str(json_time)}
    token = jwt.encode(body, key_word, algorithm="HS256")
    return token


def is_token_need_refresh(body: dict) -> bool:
    """check if token isn't fresh and need refresh"""
    jwt_token = read_token(body)
    if jwt_token is None:
        return False
    time = datetime.strptime(jwt_token["time"], "%Y-%m-%d %H:%M:%S")
    return datetime.now() - time > timedelta(hours=1)
