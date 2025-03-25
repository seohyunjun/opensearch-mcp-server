import logging
from typing import Dict, Any
from ..es_client import OpensearchClient
from mcp.types import TextContent

class IndexTools(OpensearchClient):
    def register_tools(self, mcp: Any):
        """Register index-related tools."""
        
        @mcp.tool(description="List all indices in the Opensearch cluster")
        async def list_indices() -> list[TextContent]:
            """List all indices in the Opensearch cluster."""
            self.logger.info("Listing indices...")
            try:
                indices = self.es_client.cat.indices(format="json")
                return [TextContent(type="text", text=str(indices))]
            except Exception as e:
                self.logger.error(f"Error listing indices: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get index mapping")
        async def get_mapping(index: str) -> list[TextContent]:
            """
            Get the mapping for an index.
            
            Args:
                index: Name of the index
            """
            self.logger.info(f"Getting mapping for index: {index}")
            try:
                response = self.es_client.indices.get_mapping(index=index)
                return [TextContent(type="text", text=str(response))]
            except Exception as e:
                self.logger.error(f"Error getting mapping: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get index settings")
        async def get_settings(index: str) -> list[TextContent]:
            """
            Get the settings for an index.
            
            Args:
                index: Name of the index
            """
            self.logger.info(f"Getting settings for index: {index}")
            try:
                response = self.es_client.indices.get_settings(index=index)
                return [TextContent(type="text", text=str(response))]
            except Exception as e:
                self.logger.error(f"Error getting settings: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
