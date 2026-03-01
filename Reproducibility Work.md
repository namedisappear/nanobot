# Reproducibility Work

***Name: Shaoxuan Ma                            Student ID:1155251596***

## Project summary

Nanobot is a versatile, lightweight AI assistant framework designed for extensibility and ease of use. It serves as a bridge between Large Language Models (LLMs) and various communication platforms. Key features include:

* **Multi-Provider Support:** Seamless integration with major LLM providers such as OpenAI, Anthropic, DeepSeek, Gemini, and local models via vLLM.
* **Omnichannel Presence:** Connects with popular messaging apps including Feishu (Lark), WeChat (via Mochat), QQ, Telegram, Discord, and Slack.
* **Skill System:** Extensible tool-use capabilities allowing the bot to perform tasks like web searching, GitHub interactions, and scheduling.
* **Configuration-Driven:** Centralized JSON configuration for easy management of agents, channels, and tools.

## Setup notes (env, data, keys, compute)

To reproduce the environment and run the project, follow these steps:

* **Environment:**

  * Requires Python 3.10 or higher.
  * Install dependencies using `pip install -e .` in the project root.
* **Configuration & Data:**

  * Run `python -m nanobot onboard` to initialize the configuration directory.
  * The main configuration file is located at `~/.nanobot/config.json`.
  * A workspace directory `~/.nanobot/workspace` is created for the agent's file operations.
* **Keys & Credentials:**

  * **LLM Providers:** Obtain API keys for your preferred provider (e.g., `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`) and configure them in the `providers` section of `config.json`.
  * **Channels:** For platform integration (e.g., Feishu), configure the necessary `app_id`, `app_secret`, and `verification_token` in the `channels` section.
* **Compute:**

  * **Inference:** Heavy computation is offloaded to remote API providers, making the local resource footprint minimal.
  * **Local Models:** If using local models (e.g., via vLLM), a GPU with sufficient VRAM (e.g., NVIDIA RTX 3090/4090) is recommended.

## Detailed Usage Steps

Follow these instructions to configure and run the project:

### 1. Installation

Open a terminal in the project root directory and install the package in editable mode:

```bash
pip install -e .
```

### 2. Initialization

Initialize the default configuration and workspace structure:

```bash
python -m nanobot onboard
```

### 3. Configuration

Locate the configuration file at `~/.nanobot/config.json` (on Windows: `C:\Users\<User>\.nanobot\config.json`). Open it with a text editor and modify the following sections:

**a. Configure LLM Provider (e.g., DeepSeek):**

Update the `agents` and `providers` sections to use your desired model and API key:

```json
{
  "agents": {
    "defaults": {
      "provider": "deepseek",
      "model": "deepseek-chat"
    }
  },
  "providers": {
    "deepseek": {
      "api_key": "sk-YOUR_API_KEY_HERE",
      "api_base": "https://api.deepseek.com"
    }
  }
}
```

**b. Configure Channel (e.g., Feishu/Lark):**

Update the `channels` section with your Feishu App credentials (obtained from the Feishu Open Platform):

```json
  "channels": {
    "feishu": {
      "enabled": true,
      "app_id": "cli_xxxxx",
      "app_secret": "xxxxxxx",
      "encrypt_key": "",
      "verification_token": ""
    }
  }
}
```

![image-20260301184910131](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301184910131.png)

![image-20260301184924055](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301184924055.png)

### 4.Permission Management

Add permission to the robot

![image-20260301185215813](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301185215813.png)

### 5. Running the Bot

Start the gateway service to listen for incoming messages:

```bash
python -m nanobot gateway
```

If configured correctly, you will see logs indicating that the bot has started and connected to the enabled channels (e.g., `Feishu bot started with WebSocket long connection`).

### 6. Verification

1. Open your messaging app (e.g., Feishu).
2. Find the bot you created.
3. Send a test message (e.g., "Hello").
4. The bot should respond using the configured LLM.

## New function

### Enhanced Channel Robustness & Cross-Channel Logic

Implemented intelligent filtering mechanisms across multiple communication channels to support stable agent-to-agent communication.

*   **Internal ID Filtering:** Updated `EmailChannel`, `MochatChannel`, `QQChannel`, and `FeishuChannel` to recognize and safely ignore "internal" or virtual chat IDs. This prevents runtime errors when an agent on one channel (e.g., Feishu) attempts to communicate with a virtual agent identity on another channel, ensuring that system-internal messages don't trigger invalid external API calls.
*   **Agent Loop Integration:** Enhanced the core `AgentLoop` to register and support new cross-channel tools by default, enabling seamless message routing between different platform adapters (e.g., bridging Feishu instructions to Email actions).

### 1. CrossChannelTool (`send_to_channel_agent`)

*   **Location:** `nanobot/agent/tools/channel.py`
*   **Description:** A powerful infrastructure tool that allows an agent to send messages or instructions to agents operating on other channels.
*   **Functionality:** It constructs an `InboundMessage` and injects it directly into the system's `MessageBus`. This simulates an incoming user message on the target channel, triggering the target agent to wake up and process the instruction.
*   **Use Case:** Enables complex workflows like "Feishu Agent asks Email Agent to check for new emails" or "Telegram Agent asks Slack Agent to post an update".

### 2. SendEmailTool (`send_email`)

*   **Location:** `nanobot/agent/tools/email.py`
*   **Description:** A dedicated tool that provides agents with the capability to proactively send emails via SMTP.
*   **Functionality:** Uses the configured SMTP settings (host, port, credentials) to dispatch emails. It supports specifying the recipient (`to`), subject (`subject`), and body (`body`) directly from the agent's reasoning process.
*   **Use Case:** Allows the agent to perform actions like "Send a meeting summary to the client" or "Notify the admin about a system alert" directly, without needing to draft a file or rely on external triggers.

## Reproduction results

![image-20260301185415166](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301185415166.png)

### Send email through Feishu

![image-20260301203653784](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301203653784.png)

![image-20260301203709926](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301203709926.png)

![image-20260301203724381](C:\Users\pc\AppData\Roaming\Typora\typora-user-images\image-20260301203724381.png)
