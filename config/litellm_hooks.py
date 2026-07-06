"""Codex 0.142+ responses 载荷携带内置非 function 工具(type=namespace/web_search 等),
DeepSeek/Moonshot 反序列化直接 400。上游不认的工具类型在代理层剥离,只放行 function。
(codex 已移除 wire_api="chat",无法从客户端侧规避,只能在此过滤。)
"""
from litellm.integrations.custom_logger import CustomLogger


class ToolSanitizer(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        tools = data.get("tools")
        if isinstance(tools, list):
            kept = [
                t for t in tools
                if not isinstance(t, dict) or t.get("type") in (None, "function")
            ]
            if kept:
                data["tools"] = kept
            else:
                # 全被过滤时连 tool_choice 一起清掉,防上游报"tool_choice 但无 tools"
                data.pop("tools", None)
                data.pop("tool_choice", None)
        return data


proxy_handler_instance = ToolSanitizer()
