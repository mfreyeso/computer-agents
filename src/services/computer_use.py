import httpx
from src.database.session import AsyncSessionLocal
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database.models import Session
import uuid

class ToolExecutorService:
    def __init__(self):
        self._cached_tools: list[dict] | None = None

    async def _resolve_container_url(self, session_id: str | uuid.UUID) -> str:
        container_name = "vnc_target"  # fallback
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Session).options(selectinload(Session.vnc_environment)).where(Session.id == uuid.UUID(str(session_id)))
                )
                sess = result.scalar_one_or_none()
                if sess and sess.vnc_environment:
                    container_name = sess.vnc_environment.host
        except Exception:
            pass
        return f"http://{container_name}:8888"

    async def get_tool_definitions(self, session_id: str | uuid.UUID) -> list[dict]:
        if self._cached_tools is not None:
            return self._cached_tools

        tool_server_url = await self._resolve_container_url(session_id)
        import asyncio
        for _ in range(10):
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"{tool_server_url}/tools", timeout=5)
                    self._cached_tools = resp.json()
                    return self._cached_tools
            except Exception:
                await asyncio.sleep(2)
        return []

    async def execute_tool(
        self, name: str, input_params: dict, session_id: str | uuid.UUID
    ) -> list[dict]:
        tool_server_url = await self._resolve_container_url(session_id)
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{tool_server_url}/execute",
                    json={"name": name, "input": input_params},
                    timeout=60,
                )
                result = resp.json()
        except Exception as e:
            return [{"type": "text", "text": f"Tool error: {e}"}]

        blocks: list[dict] = []
        if result.get("output"):
            blocks.append({"type": "text", "text": result["output"]})
        if result.get("error"):
            blocks.append(
                {"type": "text", "text": f"Error: {result['error']}"}
            )
        if result.get("base64_image"):
            blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": result["base64_image"],
                },
            })
        if result.get("system"):
            blocks.append(
                {"type": "text", "text": f"System: {result['system']}"}
            )
        return blocks

tool_service = ToolExecutorService()
