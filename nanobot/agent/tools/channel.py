"""Tool for cross-channel agent communication."""

from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.bus.events import InboundMessage
from nanobot.bus.queue import MessageBus


class CrossChannelTool(Tool):
    """Tool to send messages to the AI agent on another channel."""

    def __init__(self, bus: MessageBus):
        self.bus = bus

    @property
    def name(self) -> str:
        return "send_to_channel_agent"

    @property
    def description(self) -> str:
        return (
            "Send a message to the AI agent on another channel. "
            "Use this to delegate tasks that belong to another domain (e.g., asking the 'email' agent to send an email or check inbox). "
            "If you are on 'feishu', 'mochat', or 'qq', you MUST use this tool to delegate email tasks to the 'email' agent. "
            "NEVER use 'feishu' as the target channel if you are already on Feishu."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message content to send to the other agent"
                },
                "channel": {
                    "type": "string",
                    "description": "The target channel name. Supported values: 'email', 'feishu', 'mochat', 'qq', 'console'. For email tasks, this MUST be 'email'. Do NOT set this to your current channel."
                },
                "sender_id": {
                    "type": "string",
                    "description": "Optional: simulated sender ID (defaults to 'internal')"
                }
            },
            "required": ["content", "channel"]
        }

    async def execute(self, content: str, channel: str, sender_id: str = "internal", **kwargs: Any) -> str:
        """Execute the tool."""
        # Create an inbound message to simulate an event from that channel
        # Use a special format "source_channel:source_id" as the sender_id to allow reply routing
        # But for now, we just want to trigger the agent on the other channel.
        # The critical part is that the message appears on the target channel's bus.
        
        # If I am on 'feishu', and I send to 'email', I want the 'email' agent to see a message.
        # The 'email' agent listens to messages where channel='email'.
        
        msg = InboundMessage(
            channel=channel,
            sender_id=f"{sender_id}:delegated", # Mark as delegated to avoid loops
            chat_id=sender_id,  # Use sender_id as chat_id for 1:1 simulation
            content=content,
        )
        
        # Publish to inbound queue so the AgentLoop picks it up as a new event
        await self.bus.publish_inbound(msg)
        
        return (
            f"✅ **已委托 {channel} Agent 处理**。内容已转发。\n"
            f"请回复用户：'我已委托 {channel} Agent 发送邮件，请稍候。'"
        )
