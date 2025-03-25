# OpenSearch MCP Server

## Overview

 This Repository Fork of [elastic-mcp-server](https://github.com/cr7258/elasticsearch-mcp-server) and Converted to [opensearch-mcp-server](https://github.com/seohyunjun/opensearch-mcp-server) MCP Server. It is a Model Context Protocol (MCP) server implementation that provides opensearch interaction. This server enables searching documents, analyzing indices, and managing cluster through a set of tools.

A Model Context Protocol (MCP) server implementation that provides opensearch interaction. This server enables searching documents, analyzing indices, and managing cluster through a set of tools.

## Features

### Index Operations

- `list_indices`: List all indices in the Opensearch cluster.
- `get_mapping`: Retrieve the mapping configuration for a specific index.
- `get_settings`: Get the settings configuration for a specific index.

### Document Operations

- `search_documents`: Search documents in an index using Opensearch Query DSL.

### Cluster Operations

- `get_cluster_health`: Get health status of the cluster.
- `get_cluster_stats`: Get statistical information about the cluster.


## Start Opensearch Cluster

Start the Opensearch cluster using Docker Compose:

```bash
docker-compose up -d
```

This will start a 3-node Opensearch cluster and Kibana. Default Opensearch username `opensearch`, password `test123`.

You can access Kibana from http://localhost:5601.

## Usage with Claude Desktop

### Using uv with local development

Using `uv` requires cloning the repository locally and specifying the path to the source code. Add the following configuration to Claude Desktop's config file `claude_desktop_config.json`.

you need to change `path/to/src/opensearch_mcp_server` to the path where you cloned the repository.

```json
{
  "mcpServers": {
    "opensearch": {
      "command": "uv",
      "args": [
        "--directory",
        "path/to/src/opensearch_mcp_server",
        "run",
        "opensearch-mcp-server"
      ],
      "env": {
        "OPENSEARCH_HOST": "https://localhost:9200",
        "OPENSEARCH_USERNAME": "opensearch",
        "OPENSEARCH_PASSWORD": "test123"
      }
    }
  }
}
```

- On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Restart Claude Desktop to load the new MCP server.

Now you can interact with your Opensearch cluster through Claude using natural language commands like:
- "List all indices in the cluster"
- "How old is the student Bob?"
- "Show me the cluster health status"

## License

This project is licensed under the Apache License Version 2.0 - see the [LICENSE](LICENSE) file for details.
