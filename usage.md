# SLS Memory SDK 使用文档

## 快速开始

### 基本使用

```python
from sls_memory import Config, SLSMemoryClient

# 1. 初始化客户端
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

# 2. 添加记忆
client.add("我喜欢打网球", user_id="user123")

# 3. 搜索记忆
results = client.search("网球", user_id="user123")
print(results)

# 4. 获取所有记忆
memories = client.get_all(user_id="user123")
print(memories)
```

## API 参考

### 初始化

#### SLSMemoryClient

```python
client = SLSMemoryClient(config, project, memory_store)
```

**参数：**
- `config` (Config): SLS SDK 配置对象
- `project` (str): SLS 项目名称
- `memory_store` (str): Memory Store 名称

---

### 记忆操作

#### add() - 添加记忆

```python
client.add(messages, user_id=None, agent_id=None, app_id=None, 
          metadata=None, infer=True, async_mode=True)
```

**参数：**
- `messages` (str|dict|list): 消息内容
- `user_id` (str): 用户 ID
- `agent_id` (str): Agent ID
- `app_id` (str): 应用 ID
- `metadata` (dict): 自定义元数据
- `infer` (bool): 是否启用推理，默认 True
- `async_mode` (bool): 是否异步处理，默认 True

**返回：** `{"results": [{"message": "...", "status": "PENDING", "event_id": "..."}]}`

---

#### search() - 搜索记忆

```python
client.search(query, user_id=None, agent_id=None, top_k=None, 
             rerank=False, metadata=None)
```

**参数：**
- `query` (str): 搜索查询
- `user_id` (str): 过滤用户 ID
- `top_k` (int): 返回结果数量
- `rerank` (bool): 是否重排序
- `metadata` (dict): 元数据过滤

**返回：** `{"results": [...], "relations": [...]}`

---

#### get() - 获取单个记忆

```python
client.get(memory_id)
```

**参数：**
- `memory_id` (str): 记忆 ID

**返回：** 记忆详情字典

---

#### get_all() - 获取所有记忆

```python
client.get_all(user_id=None, agent_id=None, limit=None, 
              page=None, page_size=None, metadata=None)
```

**参数：**
- `user_id` (str): 过滤用户 ID
- `limit` (int): 最大返回数量
- `page` (int): 页码
- `page_size` (int): 每页大小
- `metadata` (dict): 元数据过滤

**返回：** `{"results": [...], "relations": [...]}`

---

#### update() - 更新记忆

```python
client.update(memory_id, text=None, metadata=None)
```

**参数：**
- `memory_id` (str): 记忆 ID
- `text` (str): 新的内容
- `metadata` (dict): 更新的元数据

**返回：** API 响应状态

---

#### delete() - 删除记忆

```python
client.delete(memory_id)
```

**参数：**
- `memory_id` (str): 记忆 ID

---

#### delete_all() - 批量删除记忆

```python
client.delete_all(user_id=None, agent_id=None, metadata=None)
```

**参数：**
- `user_id` (str): 过滤用户 ID
- `agent_id` (str): 过滤 Agent ID
- `metadata` (dict): 元数据过滤

⚠️ **警告：** 不带过滤条件将删除所有记忆！

---

#### history() - 获取记忆历史

```python
client.history(memory_id)
```

**参数：**
- `memory_id` (str): 记忆 ID

**返回：** 历史记录列表

---

### Memory Store 管理

#### create_memory_store() - 创建 Memory Store

创建当前 client 绑定的 Memory Store（初始化时指定的 memory_store）。

```python
client.create_memory_store(description="用户记忆存储")
```

**参数：**
- `description` (str): Store 描述
- `custom_instructions` (str): 自定义指令
- `strategy` (str): 处理策略，默认 "default"
- `short_term_ttl` (int): 短期记忆 TTL（天），默认 7

---

#### describe_memory_store() - 获取 Store 信息

```python
info = client.describe_memory_store()
```

**返回：** Store 详细信息字典

---

#### update_memory_store() - 更新 Store 配置

```python
client.update_memory_store(
    description="更新的描述",
    short_term_ttl=14
)
```

**参数：**
- `description` (str): 新的描述
- `custom_instructions` (str): 新的自定义指令
- `strategy` (str): 处理策略
- `short_term_ttl` (int): 短期记忆 TTL（天）

---

#### delete_memory_store() - 删除 Store

```python
client.delete_memory_store()
```

⚠️ **警告：** 将永久删除 Store 及其所有记忆！

---

## 完整示例

### 同步客户端示例

```python
from sls_memory import Config, SLSMemoryClient
import os

# 初始化
config = Config(
    access_key_id=os.getenv("ALIYUN_LOG_ACCESS_KEY_ID"),
    access_key_secret=os.getenv("ALIYUN_LOG_ACCESS_KEY_SECRET"),
    endpoint=os.getenv("ALIYUN_LOG_ENDPOINT")
)
client = SLSMemoryClient(
    config,
    project=os.getenv("ALIYUN_LOG_PROJECT"),
    memory_store=os.getenv("ALIYUN_LOG_MEMORY_STORE")
)

# 创建 Memory Store
client.create_memory_store()

# 添加记忆
result = client.add(
    messages="我住在杭州，喜欢杭州的风景，经常会去西湖玩",
    user_id="user123",
    metadata={"source": "chat", "importance": "high"}
)
print(f"添加结果: {result}")

# 搜索记忆
results = client.search(
    query="我住在哪里？",
    user_id="user123",
    top_k=5
)
for mem in results["results"]:
    print(f"记忆: {mem.get('memory')}")

# 获取所有记忆
all_memories = client.get_all(user_id="user123", limit=10)
print(f"共找到 {len(all_memories['results'])} 条记忆")

# 更新记忆
memory_id = results["results"][0]["id"]
client.update(memory_id, text="我住在杭州西湖区")

# 查看历史
history = client.history(memory_id)
for entry in history:
    print(f"操作: {entry.get('event')}")

# 删除记忆
client.delete(memory_id)
```

### 异步客户端示例

```python
import asyncio
from sls_memory import Config, AsyncSLSMemoryClient

async def main():
    config = Config(
        access_key_id="your_access_key_id",
        access_key_secret="your_access_key_secret",
        endpoint="cn-hangzhou.log.aliyuncs.com"
    )
    
    async with AsyncSLSMemoryClient(config, "my-project", "my-store") as client:
        # 添加记忆
        await client.add("我喜欢打篮球", user_id="user123")
        
        # 搜索记忆
        results = await client.search("篮球", user_id="user123")
        print(results)

asyncio.run(main())
```

## 认证方式

支持多种认证方式：

```python
# 1. AK/SK
config = Config(
    access_key_id="your_ak",
    access_key_secret="your_sk",
    endpoint="cn-hangzhou.log.aliyuncs.com"
)

# 2. STS Token
config = Config(
    access_key_id="your_ak",
    access_key_secret="your_sk",
    security_token="your_sts_token",
    endpoint="cn-hangzhou.log.aliyuncs.com"
)

```