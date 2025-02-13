from typing import Optional

from langchain_openai.chat_models import ChatOpenAI

from config.types import ServerConfig
from network import NetworkException, post, set_headers

# ==================== Auth ====================


async def auth_signin(config: ServerConfig) -> Optional[str]:

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


async def generate_openai_api_key(config: ServerConfig, token: str) -> Optional[str]:
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

# ==================== Chat ====================


async def chat_completions(
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    base_url: str,
    timeout: float = 600.0,
):
    """Chat with OpenAI API

    Args:
        model (str): model name
        system_prompt (str): System sentence
        user_prompt (str): User sentence
        api_key (str): OpenAI API key
        base_url (str): OpenAI API base URL
        timeout (float, optional): Timeout. Defaults to 600.0.
    """

    print(f"Using model: {model}")
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=None,
        timeout=timeout,
        max_retries=2,
        api_key=api_key,
        base_url=base_url,
    )

    messages = [
        ("system", system_prompt),
        ("human", user_prompt),
    ]

    for chunk in llm.stream(messages):
        yield chunk
