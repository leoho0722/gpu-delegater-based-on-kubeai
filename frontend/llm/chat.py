from langchain_openai.chat_models import ChatOpenAI


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
