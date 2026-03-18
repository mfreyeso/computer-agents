import json
import contextlib
from collections.abc import AsyncGenerator

from anthropic import AsyncAnthropic
from src.core.config import settings
from src.services.computer_use import tool_service


class AnthropicAgentClient:
    def __init__(self):
        api_key = settings.ANTHROPIC_API_KEY
        if api_key and api_key != "your-api-key-here":
            self.client = AsyncAnthropic(api_key=api_key)
        else:
            self.client = None
        self.model = "claude-sonnet-4-20250514"

    async def stream_agent_loop(
        self, messages: list[dict]
    ) -> AsyncGenerator[dict, None]:
        """
        Streams thoughts and tool demands dynamically from Claude.
        Auto-executes VNC tools natively and continues streaming
        until turn completes.
        """
        if not self.client:
            yield {
                "chunk_type": "text",
                "payload": "Error: ANTHROPIC_API_KEY is not configured. "
                "Please set it in your .env file and restart.",
            }
            yield {"chunk_type": "turn_complete", "payload": "end_turn"}
            return

        tools_def = tool_service.get_tool_definitions()

        while True:
            response = await self.client.beta.messages.create(
                model=self.model,
                max_tokens=4096,
                betas=["computer-use-2025-01-24"],
                system=[
                    {
                        "type": "text",
                        "text": "You are a specialized agent loop "
                        "orchestrating computer interactions. "
                        "Use the tools provided.",
                    }
                ],
                messages=messages,
                tools=tools_def,
                stream=True,
            )

            assistant_msg = {"role": "assistant", "content": []}
            current_tool_call = None
            stop_reason = None

            async for chunk in response:
                if chunk.type == "content_block_start":
                    if chunk.content_block.type == "tool_use":
                        current_tool_call = {
                            "type": "tool_use",
                            "id": chunk.content_block.id,
                            "name": chunk.content_block.name,
                            "input": ""
                        }
                        assistant_msg["content"].append(current_tool_call)

                elif chunk.type == "content_block_delta":
                    if chunk.delta.type == "text_delta":
                        # We stream thoughts natively
                        yield {"chunk_type": "text", "payload": chunk.delta.text}
                    elif chunk.delta.type == "input_json_delta":
                        if current_tool_call:
                            current_tool_call["input"] += chunk.delta.partial_json

                elif chunk.type == "message_delta":
                    stop_reason = chunk.delta.stop_reason

            # Yield the final stop reason block
            yield {"chunk_type": "turn_complete", "payload": stop_reason}

            # Post-process tool JSON
            for block in assistant_msg["content"]:
                if block["type"] == "tool_use":
                    with contextlib.suppress(Exception):
                        block["input"] = json.loads(block["input"])

            messages.append(assistant_msg)

            if stop_reason == "tool_use":
                user_msg = {"role": "user", "content": []}
                for block in assistant_msg["content"]:
                    if block["type"] == "tool_use":
                        # Stream UI that tool is executing
                        yield {"chunk_type": "tool_execution_start", "payload": {"tool": block["name"], "input": block["input"]}}

                        # Execute safely via Free-threading pool wrapper
                        tool_result_blocks = await tool_service.execute_tool(block["name"], block["input"])

                        user_msg["content"].append({
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": tool_result_blocks
                        })

                        # If a screenshot was captured, stream it to frontend
                        for r_block in tool_result_blocks:
                            if r_block.get("type") == "image":
                                yield {"chunk_type": "vnc_screenshot_result", "payload": {"base64": r_block["source"]["data"]}}

                messages.append(user_msg)
                # Loop continues back to the top querying Claude with the tool result
            else:
                break

agent_client = AnthropicAgentClient()
