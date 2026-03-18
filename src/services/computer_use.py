import httpx


TOOL_SERVER = "http://vnc_target:8888"


class ToolExecutorService:
    def __init__(self):
        self._cached_tools: list[dict] | None = None

    def get_tool_definitions(self) -> list[dict]:
        if self._cached_tools is not None:
            return self._cached_tools
        try:
            resp = httpx.get(
                f"{TOOL_SERVER}/tools", timeout=10
            )
            self._cached_tools = resp.json()
            return self._cached_tools
        except Exception:
            return []

    async def execute_tool(
        self, name: str, input_params: dict
    ) -> list[dict]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{TOOL_SERVER}/execute",
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
