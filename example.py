from sls_memory import Config
from sls_memory.client import SLSMemoryClient
import os
import time

def main():
    # 1. init memory store client
    config = Config(
        access_key_id=os.getenv("ALIYUN_LOG_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIYUN_LOG_ACCESS_KEY_SECRET"),
        endpoint=os.getenv("ALIYUN_LOG_ENDPOINT")
    )
    client = SLSMemoryClient(config, project=os.getenv("ALIYUN_LOG_PROJECT"), memory_store=os.getenv("ALIYUN_LOG_MEMORY_STORE"))

    # 2. create memory store
    result = client.create_memory_store()
    print(result)

    time.sleep(1)

    # 3. add memory
    result = client.add(
        messages="我住在杭州，喜欢杭州的风景，经常会去西湖玩",
        user_id="user123",
    )

    print(result)

    time.sleep(120)

    # 4. search memory
    result = client.search(
        query="我住在哪里？",
        user_id="user123",
    )
    print(result)

    # 5. get all memory
    result = client.get_all(
        user_id="user123",
    )
    print(result)

if __name__ == "__main__":
    main()