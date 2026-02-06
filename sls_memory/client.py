# -*- coding: utf-8 -*-
"""
SLS Memory Client - A mem0-compatible memory client powered by Alibaba Cloud SLS.

This module provides synchronous and asynchronous clients that wrap the SLS SDK
to provide an interface compatible with mem0 SDK.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from alibabacloud_sls20201230.client import Client as SLSClient
from alibabacloud_sls20201230 import models as sls_models
from alibabacloud_tea_openapi import utils_models as openapi_models

from sls_memory.exceptions import ValidationError


class SLSMemoryClient:
    """Synchronous client for interacting with SLS Memory service.

    This class provides methods compatible with mem0 SDK to create, retrieve,
    search, and delete memories using the SLS Memory service.

    Example:
        >>> from sls_memory import SLSMemoryClient
        >>> from alibabacloud_tea_openapi.utils_models import Config
        >>> 
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
    """

    def __init__(
        self,
        config: openapi_models.Config,
        project: str,
        memory_store: str,
    ):
        """Initialize the SLSMemoryClient.

        Args:
            config: The SLS SDK configuration object. Supports multiple authentication
                   methods including AK/SK, STS Token, Bearer Token, and Credential.
            project: The SLS project name.
            memory_store: The Memory Store name within the project.

        Raises:
            ValidationError: If required parameters are missing.
        """
        if not project:
            raise ValidationError("project is required")
        if not memory_store:
            raise ValidationError("memory_store is required")

        self._client = SLSClient(config)
        self._project = project
        self._memory_store = memory_store

    @property
    def project(self) -> str:
        """Get the SLS project name."""
        return self._project

    @property
    def memory_store(self) -> str:
        """Get the Memory Store name."""
        return self._memory_store

    def _prepare_messages(
        self, messages: Union[str, Dict[str, str], List[Dict[str, str]]]
    ) -> List[sls_models.AddMemoriesRequestMessages]:
        """Convert messages to SLS request format.

        Args:
            messages: A string, single message dict, or list of message dicts.
                     If a string is provided, it will be converted to a user message.

        Returns:
            A list of AddMemoriesRequestMessages objects.
        """
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, dict):
            messages = [messages]
        elif not isinstance(messages, list):
            raise ValidationError(
                f"messages must be str, dict, or list[dict], got {type(messages).__name__}"
            )

        result = []
        for msg in messages:
            result.append(sls_models.AddMemoriesRequestMessages(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
            ))
        return result

    def _convert_memory_result(self, result: Any) -> Dict[str, Any]:
        """Convert SLS memory result to dict format."""
        if hasattr(result, 'to_map'):
            return result.to_map()
        return dict(result) if result else {}

    def _convert_results_list(self, results: List[Any]) -> List[Dict[str, Any]]:
        """Convert a list of SLS results to dict format."""
        return [self._convert_memory_result(r) for r in results] if results else []

    def add(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        infer: bool = True,
        async_mode: bool = True,
    ) -> Dict[str, Any]:
        """Add a new memory.

        Args:
            messages: A list of message dictionaries, a single message dictionary,
                     or a string. If a string is provided, it will be converted to
                     a user message.
            user_id: The user ID to associate with the memory.
            agent_id: The agent ID to associate with the memory.
            app_id: The application ID to associate with the memory.
            run_id: The run ID to associate with the memory.
            metadata: Optional metadata to attach to the memory (any key-value pairs).
            infer: Whether to enable inference mode. Defaults to True.
            async_mode: Whether to process asynchronously. Defaults to True.

        Returns:
            A dictionary containing the API response in format:
            {"results": [{"message": "...", "status": "PENDING", "event_id": "..."}]}

        Example:
            >>> client.add("I love playing tennis", user_id="user123")
            >>> client.add(
            ...     messages=[{"role": "user", "content": "I love tennis"}],
            ...     user_id="user123",
            ...     agent_id="agent_001",
            ...     metadata={"source": "chat", "importance": "high"}
            ... )
        """
        sls_messages = self._prepare_messages(messages)

        request = sls_models.AddMemoriesRequest(
            messages=sls_messages,
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            metadata=metadata,
            infer=infer,
            async_mode=async_mode,
        )

        response = self._client.add_memories(
            self._project,
            self._memory_store,
            request,
        )

        # Return the response body (async mode format)
        if response.body:
            return self._convert_memory_result(response.body)
        return {"results": []}

    def get(self, memory_id: str) -> Dict[str, Any]:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: The ID of the memory to retrieve.

        Returns:
            A dictionary containing the memory data.

        Example:
            >>> memory = client.get("mem_123")
            >>> print(memory["memory"])
        """
        if not memory_id:
            raise ValidationError("memory_id is required")

        response = self._client.get_memory(
            self._project,
            self._memory_store,
            memory_id,
        )

        if response.body:
            return self._convert_memory_result(response.body)
        return {}

    def get_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve all memories, with optional filtering.

        Args:
            user_id: Optional user ID to filter memories.
            agent_id: Optional agent ID to filter memories.
            app_id: Optional application ID to filter memories.
            run_id: Optional run ID to filter memories.
            limit: Maximum number of memories to retrieve.

        Returns:
            A dictionary containing memories in format: {"results": [...]}

        Example:
            >>> memories = client.get_all(user_id="user123", limit=10)
            >>> for mem in memories["results"]:
            ...     print(mem["memory"])
        """
        request = sls_models.GetMemoriesRequest(
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            limit=limit,
        )

        response = self._client.get_memories(
            self._project,
            self._memory_store,
            request,
        )

        result = {"results": []}
        if response.body and response.body.results:
            result["results"] = self._convert_results_list(response.body.results)

        return result

    def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        top_k: Optional[int] = None,
        rerank: bool = False,
    ) -> Dict[str, Any]:
        """Search memories based on a query.

        Args:
            query: The search query string.
            user_id: Optional user ID to filter results.
            agent_id: Optional agent ID to filter results.
            app_id: Optional application ID to filter results.
            run_id: Optional run ID to filter results.
            top_k: Maximum number of top results to return.
            rerank: Whether to enable reranking. Defaults to False.

        Returns:
            A dictionary containing search results in format: {"results": [...]}

        Example:
            >>> results = client.search("tennis", user_id="user123", top_k=5)
            >>> results = client.search(
            ...     query="preferences",
            ...     agent_id="agent_001",
            ...     rerank=True,
            ... )
            >>> for mem in results["results"]:
            ...     print(f"{mem['memory']} (score: {mem.get('score', 'N/A')})")
        """
        if not query:
            raise ValidationError("query is required")

        request = sls_models.SearchMemoriesRequest(
            query=query,
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            top_k=top_k,
            rerank=rerank,
        )

        response = self._client.search_memories(
            self._project,
            self._memory_store,
            request,
        )

        result = {"results": []}
        if response.body and response.body.results:
                result["results"] = self._convert_results_list(response.body.results)

        return result

    def update(
        self,
        memory_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update a memory by ID.

        Args:
            memory_id: The ID of the memory to update.
            text: New content to update the memory with.
            metadata: Metadata to update in the memory (any key-value pairs).

        Returns:
            A dictionary containing the API response.

        Example:
            >>> client.update("mem_123", text="I love playing tennis on weekends")
            >>> client.update(
            ...     memory_id="mem_123",
            ...     metadata={"updated_by": "user", "importance": "high"}
            ... )
        """
        if not memory_id:
            raise ValidationError("memory_id is required")
        if text is None and metadata is None:
            raise ValidationError("Either text or metadata must be provided for update.")

        request = sls_models.UpdateMemoryRequest(
            text=text,
            metadata=metadata,
        )

        response = self._client.update_memory(
            self._project,
            self._memory_store,
            memory_id,
            request,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    def delete(self, memory_id: str) -> Dict[str, Any]:
        """Delete a specific memory by ID.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            A dictionary containing the API response.

        Example:
            >>> client.delete("mem_123")
        """
        if not memory_id:
            raise ValidationError("memory_id is required")

        response = self._client.delete_memory(
            self._project,
            self._memory_store,
            memory_id,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    def delete_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delete all memories with optional filtering.

        Args:
            user_id: Optional user ID to filter which memories to delete.
            agent_id: Optional agent ID to filter which memories to delete.
            app_id: Optional application ID to filter which memories to delete.
            run_id: Optional run ID to filter which memories to delete.

        Returns:
            A dictionary containing the API response.

        Warning:
            If no filters are provided, this will delete ALL memories in the memory store!

        Example:
            >>> client.delete_all(user_id="user123")  # Delete only user123's memories
        """
        request = sls_models.DeleteMemoriesRequest(
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
        )

        response = self._client.delete_memories(
            self._project,
            self._memory_store,
            request,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    def history(self, memory_id: str) -> List[Dict[str, Any]]:
        """Retrieve the history of a specific memory.

        Args:
            memory_id: The ID of the memory to retrieve history for.

        Returns:
            A list of dictionaries containing the memory history.

        Example:
            >>> history = client.history("mem_123")
            >>> for entry in history:
            ...     print(f"{entry['event']}: {entry.get('new_memory', 'N/A')}")
        """
        if not memory_id:
            raise ValidationError("memory_id is required")

        response = self._client.get_memory_history(
            self._project,
            self._memory_store,
            memory_id,
        )

        if response.body:
            return self._convert_results_list(response.body)
        return []

    # Memory Store Management Methods

    def create_memory_store(
        self,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        enable_graph: bool = False,
        strategy: str = "default",
        short_term_ttl: int = 7,
    ) -> Dict[str, Any]:
        """Create the Memory Store bound to this client.

        Creates the memory store specified during client initialization.
        If the project does not exist, creates the project first then retries.

        Args:
            description: Description of the memory store.
            custom_instructions: Custom instructions for the memory store.
            enable_graph: Whether to enable knowledge graph. Defaults to False.
            strategy: Memory processing strategy. Defaults to "default".
            short_term_ttl: TTL for short-term memories in days. Defaults to 7.

        Returns:
            A dictionary containing the API response.

        Example:
            >>> client.create_memory_store(
            ...     description="Store for user memories",
            ...     enable_graph=True
            ... )
        """
        store_name = self._memory_store
        
        request = sls_models.CreateMemoryStoreRequest(
            name=store_name,
            description=description,
            custom_instructions=custom_instructions,
            enable_graph=enable_graph,
            strategy=strategy,
            short_term_ttl=short_term_ttl,
        )

        try:
            response = self._client.create_memory_store(
                self._project,
                request,
            )
        except Exception as e:
            if "ProjectNotExist" not in str(e):
                raise
            self._client.create_project(
                sls_models.CreateProjectRequest(
                    project_name=self._project,
                    description="Auto-created by SLS Memory SDK",
                )
            )
            response = self._client.create_memory_store(
                self._project,
                request,
            )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    def describe_memory_store(self) -> Dict[str, Any]:
        """Get detailed information about the current Memory Store.

        Returns:
            A dictionary containing memory store details including:
            - name: Memory Store name
            - description: Description
            - custom_instructions: Custom instructions
            - enable_graph: Whether graph is enabled
            - strategy: Processing strategy
            - short_term_ttl: Short-term memory TTL
            - create_time: Creation timestamp
            - update_time: Last update timestamp

        Example:
            >>> info = client.describe_memory_store()
            >>> print(f"Store: {info['name']}, Created: {info['create_time']}")
        """
        response = self._client.get_memory_store(
            self._project,
            self._memory_store,
        )

        if response.body:
            return self._convert_memory_result(response.body)
        return {}

    def update_memory_store(
        self,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        enable_graph: Optional[bool] = None,
        strategy: Optional[str] = None,
        short_term_ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update the configuration of the current Memory Store.

        Args:
            description: New description.
            custom_instructions: New custom instructions.
            enable_graph: Whether to enable knowledge graph.
            strategy: New memory processing strategy.
            short_term_ttl: New TTL for short-term memories in seconds.

        Returns:
            A dictionary containing the API response.

        Example:
            >>> client.update_memory_store(
            ...     description="Updated description",
            ...     enable_graph=True,
            ...     short_term_ttl=3600
            ... )
        """
        request = sls_models.UpdateMemoryStoreRequest(
            description=description,
            custom_instructions=custom_instructions,
            enable_graph=enable_graph,
            strategy=strategy,
            short_term_ttl=short_term_ttl,
        )

        response = self._client.update_memory_store(
            self._project,
            self._memory_store,
            request,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    def delete_memory_store(self) -> Dict[str, Any]:
        """Delete the current Memory Store.

        Warning:
            This will permanently delete the memory store and all its memories!

        Returns:
            A dictionary containing the API response.

        Example:
            >>> client.delete_memory_store()
        """
        response = self._client.delete_memory_store(
            self._project,
            self._memory_store,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }


class AsyncSLSMemoryClient:
    """Asynchronous client for interacting with SLS Memory service.

    This class provides async versions of all SLSMemoryClient methods.
    It uses the SLS SDK's async methods for non-blocking API requests.

    Example:
        >>> import asyncio
        >>> from sls_memory import AsyncSLSMemoryClient
        >>> from alibabacloud_tea_openapi.utils_models import Config
        >>> 
        >>> async def main():
        ...     config = Config(
        ...         access_key_id="your_access_key_id",
        ...         access_key_secret="your_access_key_secret",
        ...         endpoint="cn-hangzhou.log.aliyuncs.com"
        ...     )
        ...     async with AsyncSLSMemoryClient(config, "my-project", "my-store") as client:
        ...         await client.add("I love tennis", user_id="user123")
        ...         results = await client.search("tennis", user_id="user123")
        ...         print(results)
        >>> 
        >>> asyncio.run(main())
    """

    def __init__(
        self,
        config: openapi_models.Config,
        project: str,
        memory_store: str,
    ):
        """Initialize the AsyncSLSMemoryClient.

        Args:
            config: The SLS SDK configuration object. Supports multiple authentication
                   methods including AK/SK, STS Token, Bearer Token, and Credential.
            project: The SLS project name.
            memory_store: The Memory Store name within the project.

        Raises:
            ValidationError: If required parameters are missing.
        """
        if not project:
            raise ValidationError("project is required")
        if not memory_store:
            raise ValidationError("memory_store is required")

        self._client = SLSClient(config)
        self._project = project
        self._memory_store = memory_store

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def project(self) -> str:
        """Get the SLS project name."""
        return self._project

    @property
    def memory_store(self) -> str:
        """Get the Memory Store name."""
        return self._memory_store

    def _prepare_messages(
        self, messages: Union[str, Dict[str, str], List[Dict[str, str]]]
    ) -> List[sls_models.AddMemoriesRequestMessages]:
        """Convert messages to SLS request format."""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, dict):
            messages = [messages]
        elif not isinstance(messages, list):
            raise ValidationError(
                f"messages must be str, dict, or list[dict], got {type(messages).__name__}"
            )

        result = []
        for msg in messages:
            result.append(sls_models.AddMemoriesRequestMessages(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
            ))
        return result

    def _convert_memory_result(self, result: Any) -> Dict[str, Any]:
        """Convert SLS memory result to dict format."""
        if hasattr(result, 'to_map'):
            return result.to_map()
        return dict(result) if result else {}

    def _convert_results_list(self, results: List[Any]) -> List[Dict[str, Any]]:
        """Convert a list of SLS results to dict format."""
        return [self._convert_memory_result(r) for r in results] if results else []

    async def add(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]],
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        infer: bool = True,
        custom_instructions: Optional[str] = None,
        async_mode: bool = True,
    ) -> Dict[str, Any]:
        """Add a new memory (async version).

        Args:
            messages: A list of message dictionaries, a single message dictionary,
                     or a string. If a string is provided, it will be converted to
                     a user message.
            user_id: The user ID to associate with the memory.
            agent_id: The agent ID to associate with the memory.
            app_id: The application ID to associate with the memory.
            run_id: The run ID to associate with the memory.
            metadata: Optional metadata to attach to the memory (any key-value pairs).
            infer: Whether to enable inference mode. Defaults to True.
            custom_instructions: Custom instructions for memory processing.
            async_mode: Whether to process asynchronously. Defaults to True.

        Returns:
            A dictionary containing the API response in format:
            {"results": [{"message": "...", "status": "PENDING", "event_id": "..."}]}
        """
        sls_messages = self._prepare_messages(messages)

        request = sls_models.AddMemoriesRequest(
            messages=sls_messages,
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            metadata=metadata,
            infer=infer,
            custom_instructions=custom_instructions,
            async_mode=async_mode,
        )

        response = await self._client.add_memories_async(
            self._project,
            self._memory_store,
            request,
        )

        # Return the response body (async mode format)
        if response.body:
            return self._convert_memory_result(response.body)
        return {"results": []}

    async def get(self, memory_id: str) -> Dict[str, Any]:
        """Retrieve a specific memory by ID (async version).

        Args:
            memory_id: The ID of the memory to retrieve.

        Returns:
            A dictionary containing the memory data.
        """
        if not memory_id:
            raise ValidationError("memory_id is required")

        response = await self._client.get_memory_async(
            self._project,
            self._memory_store,
            memory_id,
        )

        if response.body:
            return self._convert_memory_result(response.body)
        return {}

    async def get_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Retrieve all memories, with optional filtering (async version).

        Args:
            user_id: Optional user ID to filter memories.
            agent_id: Optional agent ID to filter memories.
            app_id: Optional application ID to filter memories.
            run_id: Optional run ID to filter memories.
            limit: Maximum number of memories to retrieve.

        Returns:
            A dictionary containing memories in format: {"results": [...]}
        """
        request = sls_models.GetMemoriesRequest(
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            limit=limit,
        )

        response = await self._client.get_memories_async(
            self._project,
            self._memory_store,
            request,
        )

        result = {"results": []}
        if response.body and response.body.results:
            result["results"] = self._convert_results_list(response.body.results)

        return result

    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
        top_k: Optional[int] = None,
        rerank: bool = False,
    ) -> Dict[str, Any]:
        """Search memories based on a query (async version).

        Args:
            query: The search query string.
            user_id: Optional user ID to filter results.
            agent_id: Optional agent ID to filter results.
            app_id: Optional application ID to filter results.
            run_id: Optional run ID to filter results.
            top_k: Maximum number of top results to return.
            rerank: Whether to enable reranking. Defaults to False.

        Returns:
            A dictionary containing search results in format: {"results": [...]}
        """
        if not query:
            raise ValidationError("query is required")

        request = sls_models.SearchMemoriesRequest(
            query=query,
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
            top_k=top_k,
            rerank=rerank,
        )

        response = await self._client.search_memories_async(
            self._project,
            self._memory_store,
            request,
        )

        result = {"results": []}
        if response.body and response.body.results:
            result["results"] = self._convert_results_list(response.body.results)

        return result

    async def update(
        self,
        memory_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update a memory by ID (async version).

        Args:
            memory_id: The ID of the memory to update.
            text: New content to update the memory with.
            metadata: Metadata to update in the memory (any key-value pairs).

        Returns:
            A dictionary containing the API response.
        """
        if not memory_id:
            raise ValidationError("memory_id is required")
        if text is None and metadata is None:
            raise ValidationError("Either text or metadata must be provided for update.")

        request = sls_models.UpdateMemoryRequest(
            text=text,
            metadata=metadata,
        )

        response = await self._client.update_memory_async(
            self._project,
            self._memory_store,
            memory_id,
            request,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    async def delete(self, memory_id: str) -> Dict[str, Any]:
        """Delete a specific memory by ID (async version).

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            A dictionary containing the API response.
        """
        if not memory_id:
            raise ValidationError("memory_id is required")

        response = await self._client.delete_memory_async(
            self._project,
            self._memory_store,
            memory_id,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    async def delete_all(
        self,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        app_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete all memories with optional filtering (async version).

        Args:
            user_id: Optional user ID to filter which memories to delete.
            agent_id: Optional agent ID to filter which memories to delete.
            app_id: Optional application ID to filter which memories to delete.
            run_id: Optional run ID to filter which memories to delete.

        Returns:
            A dictionary containing the API response.

        Warning:
            If no filters are provided, this will delete ALL memories in the memory store!
        """
        request = sls_models.DeleteMemoriesRequest(
            user_id=user_id,
            agent_id=agent_id,
            app_id=app_id,
            run_id=run_id,
        )

        response = await self._client.delete_memories_async(
            self._project,
            self._memory_store,
            request,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    async def history(self, memory_id: str) -> List[Dict[str, Any]]:
        """Retrieve the history of a specific memory (async version).

        Args:
            memory_id: The ID of the memory to retrieve history for.

        Returns:
            A list of dictionaries containing the memory history.
        """
        if not memory_id:
            raise ValidationError("memory_id is required")

        response = await self._client.get_memory_history_async(
            self._project,
            self._memory_store,
            memory_id,
        )

        if response.body:
            return self._convert_results_list(response.body)
        return []

    # Memory Store Management Methods (Async)

    async def create_memory_store(
        self,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        enable_graph: bool = False,
        strategy: str = "default",
        short_term_ttl: int = 7,
    ) -> Dict[str, Any]:
        """Create the Memory Store bound to this client (async version).

        Creates the memory store specified during client initialization.
        If the project does not exist, creates the project first then retries.

        Args:
            description: Description of the memory store.
            custom_instructions: Custom instructions for the memory store.
            enable_graph: Whether to enable knowledge graph. Defaults to False.
            strategy: Memory processing strategy. Defaults to "default".
            short_term_ttl: TTL for short-term memories in days. Defaults to 7.

        Returns:
            A dictionary containing the API response.
        """
        store_name = self._memory_store
        
        request = sls_models.CreateMemoryStoreRequest(
            name=store_name,
            description=description,
            custom_instructions=custom_instructions,
            enable_graph=enable_graph,
            strategy=strategy,
            short_term_ttl=short_term_ttl,
        )

        try:
            response = await self._client.create_memory_store_async(
                self._project,
                request,
            )
        except Exception as e:
            if "ProjectNotExist" not in str(e):
                raise
            await self._client.create_project_async(
                sls_models.CreateProjectRequest(
                    project_name=self._project,
                    description="Auto-created by SLS Memory SDK",
                )
            )
            response = await self._client.create_memory_store_async(
                self._project,
                request,
            )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    async def describe_memory_store(self) -> Dict[str, Any]:
        """Get detailed information about the current Memory Store (async version).

        Returns:
            A dictionary containing memory store details including:
            - name: Memory Store name
            - description: Description
            - custom_instructions: Custom instructions
            - enable_graph: Whether graph is enabled
            - strategy: Processing strategy
            - short_term_ttl: Short-term memory TTL
            - create_time: Creation timestamp
            - update_time: Last update timestamp
        """
        response = await self._client.get_memory_store_async(
            self._project,
            self._memory_store,
        )

        if response.body:
            return self._convert_memory_result(response.body)
        return {}

    async def update_memory_store(
        self,
        description: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        enable_graph: Optional[bool] = None,
        strategy: Optional[str] = None,
        short_term_ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update the configuration of the current Memory Store (async version).

        Args:
            description: New description.
            custom_instructions: New custom instructions.
            enable_graph: Whether to enable knowledge graph.
            strategy: New memory processing strategy.
            short_term_ttl: New TTL for short-term memories in seconds.

        Returns:
            A dictionary containing the API response.
        """
        request = sls_models.UpdateMemoryStoreRequest(
            description=description,
            custom_instructions=custom_instructions,
            enable_graph=enable_graph,
            strategy=strategy,
            short_term_ttl=short_term_ttl,
        )

        response = await self._client.update_memory_store_async(
            self._project,
            self._memory_store,
            request,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }

    async def delete_memory_store(self) -> Dict[str, Any]:
        """Delete the current Memory Store (async version).

        Warning:
            This will permanently delete the memory store and all its memories!

        Returns:
            A dictionary containing the API response.
        """
        response = await self._client.delete_memory_store_async(
            self._project,
            self._memory_store,
        )

        return {
            "status_code": response.status_code,
            "headers": response.headers,
        }
