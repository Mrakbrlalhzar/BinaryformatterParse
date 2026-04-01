#!/usr/bin/env python3
"""
BinaryFormatter Parser MCP Server

MCP服务用于解析 .NET BinaryFormatter 序列化数据。

环境变量:
    BINARYFORMATTER_PARSER_PATH: binaryformatter_parser 可执行文件路径
"""

import asyncio
import os
import subprocess
import tempfile
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 创建 MCP 服务实例
server = Server("binaryformatter-parser")

# 从环境变量获取 binaryformatter_parser 路径
BINARYFORMATTER_PARSER_PATH = os.environ.get(
    "BINARYFORMATTER_PARSER_PATH",
    "./binaryformatter_parser"
)


def parse_binaryformatter(data: str) -> str:
    """
    使用 binaryformatter_parser 解析 BinaryFormatter 数据

    Args:
        data: BinaryFormatter 序列化数据（原始内容）

    Returns:
        解析结果字符串
    """
    # 创建临时文件存储数据
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ser', delete=False) as f:
        f.write(data)
        temp_path = f.name

    try:
        # 调用 binaryformatter_parser
        result = subprocess.run(
            [BINARYFORMATTER_PARSER_PATH, "--path", temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return f"解析错误: {result.stderr}"

        return result.stdout
    except subprocess.TimeoutExpired:
        return "解析超时"
    except FileNotFoundError:
        return f"找不到 binaryformatter_parser: {BINARYFORMATTER_PARSER_PATH}"
    finally:
        # 清理临时文件
        os.unlink(temp_path)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="parse_binaryformatter",
            description="解析 .NET BinaryFormatter 序列化数据。输入原始序列化数据，返回解析结果。",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "BinaryFormatter 序列化数据（原始内容）"
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="parse_binaryformatter_file",
            description="解析 .NET BinaryFormatter 序列化文件。输入文件路径，返回解析结果。",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "BinaryFormatter 序列化文件路径（.ser 文件）"
                    }
                },
                "required": ["path"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    if name == "parse_binaryformatter":
        data = arguments.get("data", "")

        try:
            result = parse_binaryformatter(data)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            return [TextContent(type="text", text=f"错误: {str(e)}")]

    elif name == "parse_binaryformatter_file":
        file_path = arguments.get("path", "")

        try:
            # 调用 binaryformatter_parser 直接解析文件
            result = subprocess.run(
                [BINARYFORMATTER_PARSER_PATH, "--path", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return [TextContent(
                    type="text",
                    text=f"解析错误: {result.stderr}"
                )]

            return [TextContent(type="text", text=result.stdout)]

        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text="解析超时")]
        except FileNotFoundError:
            return [TextContent(
                type="text",
                text=f"找不到 binaryformatter_parser: {BINARYFORMATTER_PARSER_PATH}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"错误: {str(e)}")]

    return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    """启动 MCP 服务"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
