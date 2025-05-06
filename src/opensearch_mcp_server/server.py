#!/usr/bin/env python3
import logging
from fastmcp import FastMCP
from .tools.index import IndexTools
from .tools.document import DocumentTools
from .tools.cluster import ClusterTools
from .tools.dashboards import DashboardTools
from .tools.es_admin.admin_index import AdminIndexTools
from .tools.es_admin.admin_cluster import AdminClusterTools
class OpensearchMCPServer:
    def __init__(self):
        self.name = "opensearch_mcp_server"
        self.mcp = FastMCP(self.name)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        # Initialize tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        # Initialize tool classes
        index_tools = IndexTools(self.logger)
        document_tools = DocumentTools(self.logger)
        cluster_tools = ClusterTools(self.logger)
        dashboard_tools = DashboardTools(self.logger)
        admin_index_tools = AdminIndexTools(self.logger)
        admin_cluster_tools = AdminClusterTools(self.logger)

        # Register tools from each module
        index_tools.register_tools(self.mcp)
        document_tools.register_tools(self.mcp)
        cluster_tools.register_tools(self.mcp)
        dashboard_tools.register_tools(self.mcp)
        admin_index_tools.register_tools(self.mcp)
        admin_cluster_tools.register_tools(self.mcp)

    def run(self):
        """Run the MCP server."""
        self.mcp.run()

def main():
    server = OpensearchMCPServer()
    server.run()
