from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from app.core.config import settings
from app.core.security import verify_github_signature

router = APIRouter(prefix="/webhooks")


@router.post("/github", status_code=202)
async def github_webhook(
    request: Request,
    background: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    body = await request.body()
    if not verify_github_signature(settings.github_webhook_secret, body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="invalid signature")
    if x_github_event == "pull_request":
        pass  # TODO: background.add_task(run_scan, payload)
    return {"accepted": True}
