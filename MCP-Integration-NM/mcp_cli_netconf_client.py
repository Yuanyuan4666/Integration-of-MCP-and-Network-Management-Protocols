import json
import asyncio
import requests

from typing import Optional
from contextlib import AsyncExitStack
from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
OLLAMA_MODEL = "ollama.rnd.huawei.com/library/qwen3:4b"
MCP_BASE = "http://localhost:8000"
DEBUG_FLAG = False
DEBUG_LEVEL = 1

def trace_log(head, data, format):
    if DEBUG_FLAG is False:
        return
    else:
        if format is True:
            formatted_json = json.dumps(
                data,
                indent=4,                # Indentation spaces
                ensure_ascii=False,      # Disable ASCII escape (display original Chinese)
                sort_keys=True           # Sort by key
            )
            print(f"\n[{head} {formatted_json}]\n")
        else:
            print(f"\n{head} {data}\n")

# Call tools
class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command="C:\\Users\\y00931291\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
            args=["./ifm_server.py"],
            env=None,  # Optional environment variables
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params))
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write))

        await self.session.initialize()

    async def proc_call_tools(self, messages, tools_info) -> str:
        for tool_call in tools_info["message"]["tool_calls"]:
            name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])

            # 如果是 connect_and_get_config 工具，确保提供完整参数
            if name == "connect_and_get_config":
                # 检查参数是否完整，如果不完整则补充
                if "config" not in args or not args["config"]:
                    args["config"] = {
                        "host": "192.168.45.11",
                        "port": 22,
                        "username": "Rfvbgt#123",        # 修改为正确的用户名
                        "password": "Chasdfgh_123",      # 修改为正确的密码
                        "hostkey_verify": False
                    }
                else:
                    # 确保必需的字段都存在
                    required_fields = ['host', 'port', 'username', 'password']
                    for field in required_fields:
                        if field not in args["config"]:
                            if field == 'host':
                                args["config"][field] = "192.168.45.11"
                            elif field == 'port':
                                args["config"][field] = 22
                            elif field == 'username':
                                args["config"][field] = "Rfvbgt#123"      # 修改为正确的用户名
                            elif field == 'password':
                                args["config"][field] = "Chasdfgh_123"    # 修改为正确的密码

            try:
                result = await self.session.call_tool(name, args)
                trace_log("Calling tool", f"{name} with args {args}", False)

                # Build messages for second call
                messages.append({
                    "role": "assistant",
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "content": result.content[0].text
                })
            except Exception as e:
                # 如果工具调用失败，将错误信息添加到消息中
                error_message = f"Error executing tool {name}: {str(e)}"
                messages.append({
                    "role": "assistant",
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "content": error_message
                })

        trace_log("request answer messages", messages, True)
        # Second call, generate final answer
        try:
            result = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "messages": messages}).json()
            trace_log("result", result, True)
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating final response: {str(e)}"

    async def add_tools_message(self, messages):
        # Get tool list information
        response = await self.session.list_tools()
        trace_log("tools list:", f"[ {response} ]\n", False)
        # Generate function call description information
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

        # Request LLM, function call description information passed through tools parameter
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "tools": available_tools,
            "tool_choice": "required"
        }
        return payload

    async def get_prompt_message(self, user_input):
        try:
            prompt = await self.session.get_prompt("cmd_prompts", None)
            trace_log("Command_prompts: ", prompt.messages[0].content.text, False)
            return prompt.messages[0].content.text
        except Exception as e:
            trace_log("Error getting prompt", str(e), False)
            return None

    async def process_query(self, user_input: str) -> str:
        user_prompt = await self.get_prompt_message(user_input)
        system_prompt = (
            "You are a network device command execution assistant. "
            "Your only task is to: "
            "1. Understand the user's operation intent "
            "2. Call appropriate tools to execute corresponding device commands "
            "3. Return the complete command execution results to the user "
            ""
            "Important rules: "
            "- Execute commands only, do not analyze or explain "
            "- Do not provide any operation suggestions or optimization opinions "
            "- Do not add any additional explanatory text "
            "- Do not fabricate or modify command execution results "
            "- Directly return the original command output content "
            "- Always respond in English, regardless of the user's language "
            "- When calling tools that require parameters, ensure all required parameters are provided "
            ""
            "Command execution process: "
            "Identify user needs → Call corresponding tools → Return complete results "
            ""
            "If the user asks in Chinese or any other language, still respond in English."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ]
        
        language_instruction = (
            "Please respond in English only. "
            "If the user's query is in Chinese, translate it to English internally but respond in English. "
            "Do not include any Chinese characters in your response."
        )
        messages.append({"role": "user", "content": language_instruction})

        if user_prompt is not None:
           messages.append({"role": "user", "content": user_prompt})
        trace_log("query request messages", messages, False)

        payload = await self.add_tools_message(messages)

        # Send to large model, get whether tool call is needed
        try:
            result = requests.post(OLLAMA_URL, json=payload)
            trace_log("query request", result, False)
            res = result.json()
        except json.JSONDecodeError as e:
            trace_log("query request", result, False)
            print(f"JSON parsing error: {e}")
            return f"Error: Failed to parse response from LLM - {str(e)}"
        except Exception as e:
            trace_log("query request error", str(e), False)
            return f"Error: Failed to communicate with LLM - {str(e)}"
            上
        trace_log("tools chose result", res, True)
        
        if "choices" not in res or len(res["choices"]) == 0:
            return "Error: No response from LLM"
            
        choice = res["choices"][0]

        # If there are tool calls
        if "tool_calls" in choice["message"]:
            return await self.proc_call_tools(messages, choice)
        else:
            return choice["message"]["content"]

    async def chat_loop(self):
        while True:
            try:
                query = input("\nInput: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error in chat loop: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        print("Connected to MCP server successfully!")
        await client.chat_loop()
    except Exception as e:
        print(f"Failed to connect to MCP server: {str(e)}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    args = sys.argv[0:]
    if "-d" in args:
        DEBUG_FLAG = True

    asyncio.run(main())

