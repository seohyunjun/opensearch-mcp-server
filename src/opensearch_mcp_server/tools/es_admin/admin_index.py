import logging
from typing import Dict, Any
from ...es_client import OpensearchClient
from mcp.types import TextContent

class AdminIndexTools(OpensearchClient):
    def register_tools(self, mcp: Any):
        """Register administrative index-related tools."""
        
        @mcp.tool(description="Get ISM policies and their configurations")
        async def get_ism_policies() -> list[TextContent]:
            """
            Get Index State Management policies and their configurations.
            Returns policy IDs, descriptions, states, and index patterns.
            This result should be useful in determining index lifecycle management configurations such as index size limits, index rollover policy
            and retention policy.
            """
            self.logger.info("Fetching ISM policies...")
            try:
                response = self.es_client.transport.perform_request(
                    'GET',
                    '/_plugins/_ism/policies',
                    params={'filter_path': 'policies.policy.policy_id,policies.policy.description,policies.policy.states,policies.policy.ism_template.index_patterns'}
                )
                return [TextContent(type="text", text=str(response))]
            except Exception as e:
                self.logger.error(f"Error fetching ISM policies: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get index template configurations")
        async def get_index_templates() -> list[TextContent]:
            """
            Get index templates and their configurations.
            Returns template names and their configured number of shards.
            This helps understand how new indices will be created.
            """
            self.logger.info("Fetching index templates...")
            try:
                response = self.es_client.transport.perform_request(
                    'GET',
                    '/_index_template',
                    params={'filter_path': ' _index_template?filter_path=index_templates.name,index_templates.index_template.index_patterns,index_templates.index_template.template.settings.index.number_of_shards'}
                )
                return [TextContent(type="text", text=str(response))]
            except Exception as e:
                self.logger.error(f"Error fetching index templates: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @mcp.tool(description="Get index shard allocation distribution")
        async def get_shard_allocation(latest_index: str) -> list[TextContent]:
            """
            Get the current index shard allocation distribution across nodes.
            Returns index name, shard number, primary/replica status, and node assignment.
            This helps understand how shards are distributed across the cluster.

            Args:
            latest_index: The most recent index of interest.
            """
            self.logger.info("Fetching shard allocation...")
            try:
                response = self.es_client.transport.perform_request(
                    'GET',
                    '/_cat/shards',
                    params={'h': 'index,shard,prirep,node', 'format': 'json'}
                )
                # Count shards per node
                shard_counts = {}
                for shard in response:
                    if shard['node'] not in shard_counts:
                        shard_counts[shard['node']] = 0
                    shard_counts[shard['node']] += 1
                
                # Format the response with both raw data and counts
                formatted_response = {
                    'shard_distribution': response,
                    'shards_per_node': shard_counts
                }
                return [TextContent(type="text", text=str(formatted_response))]
            except Exception as e:
                self.logger.error(f"Error fetching shard allocation: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
