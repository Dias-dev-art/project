from anthropic import AsyncAnthropic

from app.core.config import settings


async def explain_finding(rule_id: str, message: str, snippet: str) -> str:
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    prompt = (
        "Explain this security finding and suggest a fix.\n"
        f"Rule: {rule_id}\n{message}\n\n```\n{snippet}\n```"
    )
    resp = await client.messages.create(
        model=settings.claude_model,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text
