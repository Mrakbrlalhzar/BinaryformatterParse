#!/usr/bin/env python3
"""
Unit tests for BinaryFormatter Parser MCP Server
"""

import asyncio
import os
import sys
import unittest

# 添加 mcp 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mcp_server


class TestParseBinaryFormatter(unittest.TestCase):
    """测试 parse_binaryformatter 函数"""

    def setUp(self):
        """设置测试环境"""
        self.original_path = os.environ.get('BINARYFORMATTER_PARSER_PATH')
        # 使用项目根目录的 binaryformatter_parser
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ['BINARYFORMATTER_PARSER_PATH'] = os.path.join(project_root, 'binaryformatter_parser')
        mcp_server.BINARYFORMATTER_PARSER_PATH = os.environ['BINARYFORMATTER_PARSER_PATH']

    def tearDown(self):
        """恢复环境"""
        if self.original_path:
            os.environ['BINARYFORMATTER_PARSER_PATH'] = self.original_path
        else:
            os.environ.pop('BINARYFORMATTER_PARSER_PATH', None)

    def test_parse_valid_data(self):
        """测试解析有效数据"""
        # 读取测试文件
        test_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'example', 'MS-NRBF_example.ser'
        )
        with open(test_file, 'r') as f:
            data = f.read()

        result = mcp_server.parse_binaryformatter(data)

        self.assertIn('SerializedStreamHeader', result)
        self.assertIn('RootId', result)
        self.assertIn('MethodCall', result)

    def test_parse_invalid_parser_path(self):
        """测试无效的解析器路径"""
        mcp_server.BINARYFORMATTER_PARSER_PATH = '/nonexistent/parser'
        data = 'test data'

        result = mcp_server.parse_binaryformatter(data)
        self.assertIn('找不到', result)

    def test_parse_empty_data(self):
        """测试空数据"""
        data = ''
        result = mcp_server.parse_binaryformatter(data)
        # 应该返回某种错误或空结果
        self.assertIsInstance(result, str)


class TestCallTool(unittest.TestCase):
    """测试 call_tool 函数"""

    def setUp(self):
        """设置测试环境"""
        self.original_path = os.environ.get('BINARYFORMATTER_PARSER_PATH')
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ['BINARYFORMATTER_PARSER_PATH'] = os.path.join(project_root, 'binaryformatter_parser')
        mcp_server.BINARYFORMATTER_PARSER_PATH = os.environ['BINARYFORMATTER_PARSER_PATH']

    def tearDown(self):
        """恢复环境"""
        if self.original_path:
            os.environ['BINARYFORMATTER_PARSER_PATH'] = self.original_path

    def test_parse_binaryformatter_raw(self):
        """测试原始数据解析"""
        test_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'example', 'MS-NRBF_example.ser'
        )
        with open(test_file, 'r') as f:
            data = f.read()

        result = asyncio.run(mcp_server.call_tool(
            'parse_binaryformatter',
            {'data': data}
        ))

        self.assertEqual(len(result), 1)
        self.assertIn('SerializedStreamHeader', result[0].text)

    def test_parse_binaryformatter_file(self):
        """测试文件解析"""
        test_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'example', 'MS-NRBF_example.ser'
        )

        result = asyncio.run(mcp_server.call_tool(
            'parse_binaryformatter_file',
            {'path': test_file}
        ))

        self.assertEqual(len(result), 1)
        self.assertIn('SerializedStreamHeader', result[0].text)

    def test_parse_binaryformatter_file_not_found(self):
        """测试文件不存在"""
        result = asyncio.run(mcp_server.call_tool(
            'parse_binaryformatter_file',
            {'path': '/nonexistent/file.ser'}
        ))

        self.assertEqual(len(result), 1)
        self.assertIn('解析错误', result[0].text)

    def test_unknown_tool(self):
        """测试未知工具"""
        result = asyncio.run(mcp_server.call_tool(
            'unknown_tool',
            {}
        ))

        self.assertEqual(len(result), 1)
        self.assertIn('未知工具', result[0].text)


class TestListTools(unittest.TestCase):
    """测试 list_tools 函数"""

    def test_list_tools(self):
        """测试列出工具"""
        tools = asyncio.run(mcp_server.list_tools())

        self.assertEqual(len(tools), 2)
        tool_names = [t.name for t in tools]
        self.assertIn('parse_binaryformatter', tool_names)
        self.assertIn('parse_binaryformatter_file', tool_names)

    def test_tool_schemas(self):
        """测试工具 Schema"""
        tools = asyncio.run(mcp_server.list_tools())

        for tool in tools:
            self.assertIsNotNone(tool.name)
            self.assertIsNotNone(tool.description)
            self.assertIsNotNone(tool.inputSchema)
            self.assertEqual(tool.inputSchema['type'], 'object')
            self.assertIn('properties', tool.inputSchema)


if __name__ == '__main__':
    unittest.main()
