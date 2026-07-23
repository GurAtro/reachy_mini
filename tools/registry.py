"""
Tool registry — defines tools for LLM function calling and dispatches execution.
"""
from tools.pc_control import (
    open_youtube,
    shutdown_pc,
    cancel_shutdown,
    restart_pc,
    get_disk_space,
    get_system_info,
    set_volume,
    open_application,
    take_screenshot,
    list_running_processes,
)

# Tool definitions in Ollama/OpenAI format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_youtube",
            "description": "Open YouTube in the browser, optionally searching for a video.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for YouTube. Leave empty to just open YouTube."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_pc",
            "description": "Shut down the PC after a delay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delay_seconds": {
                        "type": "integer",
                        "description": "Seconds before shutdown. Default is 30."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_shutdown",
            "description": "Cancel a scheduled shutdown or restart.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_pc",
            "description": "Restart the PC after a delay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delay_seconds": {
                        "type": "integer",
                        "description": "Seconds before restart. Default is 30."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_space",
            "description": "Get the disk space usage for a drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drive": {
                        "type": "string",
                        "description": "Drive letter (e.g. 'C', 'D'). Default is 'C'."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get current CPU and RAM usage.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set the system speaker volume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Volume level from 0 to 100."
                    }
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open a Windows application by name (e.g. 'notepad', 'calculator', 'chrome').",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the application to open."
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen and save it to the Desktop.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_running_processes",
            "description": "List the top running processes by CPU usage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top processes to show. Default is 10."
                    }
                },
                "required": []
            }
        }
    },
]

# Dispatch map
_TOOL_MAP = {
    "open_youtube": open_youtube,
    "shutdown_pc": shutdown_pc,
    "cancel_shutdown": cancel_shutdown,
    "restart_pc": restart_pc,
    "get_disk_space": get_disk_space,
    "get_system_info": get_system_info,
    "set_volume": set_volume,
    "open_application": open_application,
    "take_screenshot": take_screenshot,
    "list_running_processes": list_running_processes,
}


def execute_tool(name: str, args: dict) -> str:
    fn = _TOOL_MAP.get(name)
    if fn is None:
        return f"Unknown tool: {name}"
    try:
        return fn(**args)
    except Exception as e:
        return f"Tool '{name}' error: {e}"
