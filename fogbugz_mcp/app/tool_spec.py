from typing import Type, Callable, Any, Dict, List
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """Base class for all tool inputs."""
    pass


class ToolSpec(BaseModel):
    """
    Declarative description of an MCP tool.
    """
    name: str
    description: str
    input_model: Type[ToolInput]
    returns: str

    class Config:
        arbitrary_types_allowed = True

    def to_mcp_tool(self) -> Dict[str, Any]:
        schema = self.input_model.model_json_schema()

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            },
        }
