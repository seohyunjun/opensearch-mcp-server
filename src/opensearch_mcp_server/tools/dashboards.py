import logging
import json
from typing import Dict, Any
from ..es_client import OpensearchClient
from mcp.types import TextContent
from urllib.parse import urlencode

class DashboardTools(OpensearchClient):
    def register_tools(self, mcp: Any):
        """Register dashboards-related tools."""


        @mcp.tool(description="List OpenSearch Dashboards index patterns2")
        async def list_index_patterns() -> list[TextContent]:
            """
            Find all index pattern IDs stored in the .kibana index. Especially useful for
            identifying the correct index pattern ID to use in the Discover view URL.
            This function queries the .kibana index for saved objects of type 'index-pattern'
            and returns a list of their titles and IDs.

            Returns:
            list[TextContent]: A list containing the found index patterns or an error message.
            """
            self.logger.info("Searching for index patterns")
            try:
                response = self.es_client.search(
                    index=".kibana",
                    body={
                        '_source': ['index-pattern.title', '_id'],
                        'query': {
                            'term': {
                                'type': 'index-pattern'
                            }
                        }
                    }
                )
                patterns = json.dumps([{hit["_source"]["index-pattern"]["title"]: hit["_id"].replace('index-pattern:', '')} 
                            for hit in response["hits"]["hits"]], indent=4)
                return [TextContent(type="text", text=(patterns))]
            except Exception as e:
                self.logger.error(f"Error finding index patterns: {e}")
                return [TextContent(type="text", text=f"Error: {(e)}")]

        @mcp.tool(description="Generate OpenSearch Dashboards Discover view URL")
        async def generate_discover_url(query: str, index_pattern_id: str, from_time: str, to_time: str) -> list[TextContent]:
            """
            Generate a URL for the OpenSearch Dashboards Discover view that will display the results of a query.
            The argument values must be compatible with the rison data format used by OpenSearch Dashboards.
            Use the list index patterns tool to determine the available index pattern IDs. 
            Index_pattern_id argument must be the ID of the index pattern to be used.
            The query arguement must be a valid OpenSearch lucene format.
            Refrain from using querying the timestamp or @timestamp fields in the query. Use from_time and to_time parameters instead
            The function constructs a URL that includes the query and index pattern as parameters.

            Args:
            query str: The query to apply in the Discover view in lucene format.
            index_pattern_id str: The index pattern ID to use in the Discover view URL.
            from_time str: The starting time for the query in the format like `now-15m`.
            to_time str: The ending time for the query in the format like `now`.

            Returns:
            list[TextContent]: A list containing the generated URL or an error message.
            """
            self.logger.info("Generating Discover view URL")
            config = self._get_es_config()
            try:
                base_url = config["dashboards_host"] + "/app/data-explorer/discover#?" #"http[s]://host[:port]/app/data-explorer/discover#? + query_params"
                query_params = {
                    "_g": "(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:'"+from_time+"',to:'"+to_time+"'))",
                    "_q": "(filters:!(),query:(language:lucene,query:\'"+query+"\'))",
                    "_a": "(discover:(columns:!(_source),isDirty:!f,sort:!()),metadata:(indexPattern:\'"+index_pattern_id+"\',view:discover))"   
                }
                url = base_url + urlencode(query_params, safe="(),:")
                return [TextContent(type="text", text=url)]
                
            except Exception as e:
                self.logger.error(f"Error generating Discover view URL: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
