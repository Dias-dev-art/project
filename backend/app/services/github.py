import httpx

API = "https://api.github.com"


async def fetch_pr_diff(token: str, repo: str, pr_number: int) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{API}/repos/{repo}/pulls/{pr_number}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.diff"},
        )
        r.raise_for_status()
        return r.text
