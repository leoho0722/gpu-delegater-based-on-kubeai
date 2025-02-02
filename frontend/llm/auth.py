from shared.config.types import Config
from shared.utils.network import NetworkException, post, set_headers


async def auth_signin(config: Config):

    try:
        response = await post(
            url=f"{config.webui_url}/auths/signin",
            json={
                "email": config.user.get("email"),
                "password": config.user.get("password"),
            },
            timeout=config.timeout,
        )
        print(f"POST /api/v1/auths/signin: {response}")
        return response.get("token")
    except NetworkException as e:
        print(f"Network Exception: {e}")


async def generate_openai_api_key(config: Config, token: str):
    try:
        response = await post(
            url=f"{config.webui_url}/auths/api_key",
            json={},
            headers=set_headers([
                {"Authorization": f"Bearer {token}"}
            ]),
            timeout=config.timeout,
        )
        print(f"POST /api/v1/auths/api_key: {response}")
        return response.get("api_key")
    except NetworkException as e:
        print(f"Network Exception: {e}")
