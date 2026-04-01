# Binaryformatter 解析

Binaryformatter 解析初版实现。

## 构建

```
go build -o binaryformatter_parser main.go
```

## 命令行使用

```
./binaryformatter_parser --path example/MS-NRBF_example.ser
```

## MCP 服务

本项目提供了 MCP (Model Context Protocol) 服务，可在 AI 助手中直接调用解析功能。

### 环境要求

- Python 3.10+
- mcp 包 (`pip install mcp`)

### 配置

1. 复制 `mcp/mcp_config.json` 中的配置到你的 MCP 客户端配置文件中
2. 修改路径为你的实际路径

配置示例：
```json
{
  "mcpServers": {
    "binaryformatter-parser": {
      "command": "/path/to/python",
      "args": ["/path/to/mcp/mcp_server.py"],
      "env": {
        "BINARYFORMATTER_PARSER_PATH": "/path/to/binaryformatter_parser"
      }
    }
  }
}
```

### 可用工具

1. **parse_binaryformatter**: 解析序列化数据
   - `data`: 序列化数据（原始内容）

2. **parse_binaryformatter_file**: 解析文件
   - `path`: .ser 文件路径

### 运行测试

```bash
cd mcp && python -m unittest test_mcp_server -v
```

## 解析结果示例

```
SerializedStreamHeader:
    RootId: 1
    HeaderId: -1
    MajorVersion: 1
    MinorVersion: 0
MethodCall:
    MessageEnum: 20
    MethodName:
        ObjectId: 18
        Value: SendAddress
    TypeName:
        ObjectId: 18
        Value: DOJRemotingMetadata.MyServer, DOJRemotingMetadata, Version=1.0.2622.31326, Culture=neutral, PublicKeyToken=null
    CallContext:
        ObjectId: 0
        Value:
    Args:
        Length: 0
        ListOfValueWithCode:
ArraySingleObject:
    ArrayInfo:
        ObjectId: 1
        Length: 1
MemberReference:
    IdRef: 2
BinaryLibrary:
    LibraryId: 3
    LibraryName: DOJRemotingMetadata, Version=1.0.2622.31326, Culture=neutral, PublicKeyToken=null
ClassWithMembersAndTypes:
    ClassInfo:
        ObjectId: 2
        Name: DOJRemotingMetadata.Address
        MemberCount: 4
        MemberNames:
            - Street
            - City
            - State
            - Zip
BinaryObjectString:
    ObjectId: 4
    Value: One Microsoft Way
BinaryObjectString:
    ObjectId: 5
    Value: Redmond
BinaryObjectString:
    ObjectId: 6
    Value: WA
BinaryObjectString:
    ObjectId: 7
    Value: 98054
MessageEnd
```

## 注意事项

还存在很多已知和未知的问题待解决