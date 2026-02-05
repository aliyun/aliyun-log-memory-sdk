# -*- coding: utf-8 -*-
"""
SLS Memory SDK - A mem0-compatible memory SDK powered by Alibaba Cloud SLS.

This SDK provides an interface compatible with mem0 SDK, allowing users to
seamlessly migrate from mem0 to SLS Memory service.

Note:
    Some mem0 parameters are not yet supported by SLS API. See COMPATIBILITY.md
    for detailed differences between SLS Memory SDK and mem0 SDK.

Example:
    >>> from sls_memory import SLSMemoryClient, Config
    >>> 
    >>> # Initialize with AK/SK
    >>> config = Config(
    ...     access_key_id="your_access_key_id",
    ...     access_key_secret="your_access_key_secret",
    ...     endpoint="cn-hangzhou.log.aliyuncs.com"
    ... )
    >>> client = SLSMemoryClient(config, project="my-project", memory_store="my-store")
    >>> 
    >>> # Add a memory
    >>> client.add("I love playing tennis", user_id="user123")
    >>> 
    >>> # Search memories
    >>> results = client.search("tennis", user_id="user123")
    >>> print(results)
"""

from sls_memory.client import SLSMemoryClient, AsyncSLSMemoryClient
from sls_memory.exceptions import ValidationError

# Re-export Config from alibabacloud_tea_openapi for convenience
from alibabacloud_tea_openapi.utils_models import Config

__all__ = [
    # Clients
    "SLSMemoryClient",
    "AsyncSLSMemoryClient",
    # Config
    "Config",
    # Exceptions (only for SDK internal validation)
    "ValidationError",
]

__version__ = "0.1.0"
