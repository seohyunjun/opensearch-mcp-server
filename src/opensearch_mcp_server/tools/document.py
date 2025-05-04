import logging
import json
from typing import Dict, Any
from ..es_client import OpensearchClient
from mcp.types import TextContent

class DocumentTools(OpensearchClient):
    def register_tools(self, mcp: Any):
        """Register document-related tools."""

        @mcp.tool(description="Search documents in an opensearch index with a custom query")
        async def search_documents(index: str, body: dict) -> list[TextContent]:
            """
            Search documents in a specified opensearch index using a custom query.
            
            Args:
                index: Name of the index to search
                body: Opensearch query DSL. If size is not specified, defaults to 20 results.
            """
            # Ensure reasonable default size limit is set
            if 'size' not in body:
                body['size'] = 20
            self.logger.info(f"Searching in index: {index} with query: {body}")
            try:
                response = self.es_client.search(index=index, body=body)
                # Extract and format relevant information
                formatted_response = {
                    'total_hits': response['hits']['total']['value'],
                    'max_score': response['hits']['max_score'],
                    'hits': []
                }

                # Process each hit
                for hit in response['hits']['hits']:
                    hit_data = {
                        '_id': hit['_id'],
                        '_score': hit['_score'],
                        'source': hit['_source']
                    }
                    formatted_response['hits'].append(hit_data)

                # Include aggregations if present
                if 'aggregations' in response:
                    formatted_response['aggregations'] = response['aggregations']

                return [TextContent(type="text", text=json.dumps(formatted_response, indent=2))]
            except Exception as e:
                self.logger.error(f"Error searching documents: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
