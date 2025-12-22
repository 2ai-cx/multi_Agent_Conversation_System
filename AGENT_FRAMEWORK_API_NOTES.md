# Microsoft Agent Framework - API Structure Notes

**Package Version:** `1.0.0b251218` (Public Preview)

## Actual API Structure

The Agent Framework has a different API structure than initially expected. Here's what's actually available:

### Main Imports Available:
```python
from agent_framework import (
    # Agents
    BaseAgent,
    ChatAgent,
    WorkflowAgent,
    
    # Chat
    BaseChatClient,
    ChatMessage,
    ChatResponse,
    ChatContext,
    ChatOptions,
    
    # Content Types
    TextContent,
    DataContent,
    FunctionCallContent,
    FunctionResultContent,
    
    # Middleware
    Middleware,
    AgentMiddleware,
    ChatMiddleware,
    FunctionMiddleware,
    
    # Context
    ContextProvider,
    Context,
    
    # Workflows
    Workflow,
    WorkflowBuilder,
    WorkflowContext,
    
    # Tools
    ToolProtocol,
    MCPStdioTool,
    MCPWebsocketTool,
    
    # Threads
    AgentThread,
    
    # And many more...
)
```

### Key Differences from Expected:

1. **No `agent_framework.core` module** - Everything is in `agent_framework` directly
2. **BaseChatClient instead of ModelClient** - Chat client interface is different
3. **ChatResponse instead of ChatCompletion** - Response format is different
4. **Context handling** - Uses ChatContext, not AgentContext
5. **Middleware** - Available but structure is different

### Working Implementation Pattern:

```python
from agent_framework import BaseChatClient, ChatMessage, ChatResponse, ChatContext, TextContent

class CustomLLM(BaseChatClient):
    async def create(self, messages: List[ChatMessage], context: ChatContext, **kwargs) -> ChatResponse:
        # Implementation
        response_text = await self.custom_client.generate_async(...)
        return ChatResponse(
            messages=[
                ChatMessage(
                    role="assistant",
                    content=[TextContent(text=response_text)]
                )
            ]
        )
```

## Issues Encountered:

1. **Import Errors** - Initial implementation used non-existent `agent_framework.core`
2. **Type Mismatches** - Expected types don't match actual API
3. **Method Signatures** - `create()` instead of `create_chat_completion()`
4. **Content Format** - Messages use content arrays with TextContent objects

## Next Steps:

1. Align all implementations with actual API
2. Update tests to use correct types
3. Verify MCP integration works with actual API
4. Test workflow capabilities
5. Compare with LangChain implementation

## Resources:

- GitHub: https://github.com/microsoft/agent-framework
- Docs: https://learn.microsoft.com/en-us/agent-framework/
- Package is in **public preview** - API may change
