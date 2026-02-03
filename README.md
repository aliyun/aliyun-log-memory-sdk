# SLS Memory SDK

阿里云 SLS Memory 客户端 SDK。

## 安装

```bash
pip install sls-memory
```

## 快速开始

```python
from sls_memory import Config, SLSMemoryClient

# 初始化客户端
config = Config(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    endpoint="cn-hangzhou.log.aliyuncs.com"
)
client = SLSMemoryClient(
    config, 
    project="my-project", 
    memory_store="my-store"
)

# 添加记忆
client.add("我喜欢打网球", user_id="user123")

# 搜索记忆
results = client.search("网球", user_id="user123")
print(results)
```

## 主要功能

- ✅ 兼容 mem0 SDK 接口
- ✅ 支持同步和异步客户端
- ✅ 支持记忆的增删改查
- ✅ 支持语义搜索和过滤
- ✅ 支持 Memory Store 管理

## 文档

详细使用文档请查看 [usage.md](https://github.com/aliyun/aliyun-log-memory-sdk/blob/master/usage.md)

