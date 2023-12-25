"""main application module"""

from typing import Any, Optional
import json
from hw_15.token import read_token, make_token, is_token_need_refresh

from hw_15 import app


class RequestTypeError(Exception):
    """Error for type error in request"""


class EndpointError(Exception):
    """Error for bad endpoint"""


async def read_body(receive: Any) -> Optional[Any]:
    """
    Read and return the entire body from an incoming ASGI message.
    """
    body = b""
    more_body = True

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)
    if body != b"":
        res_body = json.loads(body)
        return res_body
    return None


async def send_response(
    send: Any, body: Optional[dict], new_token: Optional[str], update: bool
) -> None:
    """
    Send response if token is fresh
    """
    if update:
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    [b"content-type", b"text/plain"],
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "response": "pls, relogin",
            }
        )
        return

    if body is not None or new_token is not None:
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"Access-Control-Allow-Origin", b"*"],
                    [b"Content-Type", b"application/json"],
                ],
            }
        )

        response: dict[str, Any] = {}
        if new_token is not None:
            response["token"] = new_token

        if body is not None:
            response["body"] = body
        await send(
            {
                "type": "http.response.body",
                "response": response,
            }
        )


async def application(scope, receive, send):
    """
    ASGI application.
    """
    body = await read_body(receive)
    if body is not None:
        body = body["body"]
        user_id = read_token(body)
        need_update = is_token_need_refresh(body)
        res = None
        new_token = None
        try:
            match (scope["path"], scope["method"]):
                case ("/add_user", "POST"):
                    if need_update:
                        new_token = make_token(user_id)
                    else:
                        user_id = await app.login_user(body, user_id)
                        new_token = make_token(user_id)
                case ("/add_task", "POST"):
                    await app.add_task(user_id, body)
                case ("/edit_task", "POST"):
                    await app.edit_task(user_id, body)
                case ("/delete_task", "POST"):
                    await app.delete_task(user_id, body)
                case ("/get_list_tasks", "GET"):
                    res = await app.delete_task(user_id, body)
                case _:
                    raise EndpointError(f"body: {body}")
        except (app.BadField, EndpointError):
            await send(
                {
                    "type": "http.response.start",
                    "status": 400,
                    "headers": [
                        [b"Access-Control-Allow-Origin", b"*"],
                        [b"content-type", b"text/plain"],
                    ],
                }
            )

            await send(
                {
                    "type": "http.response.body",
                    "response": "bad request",
                }
            )

        await send_response(send, res, new_token, need_update)
    else:
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    [b"Content-type", b"application/json"],
                    [b"access-control-allow-origin", b"*"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": '{"field" : "success"}'.encode("utf-8"),
            }
        )
