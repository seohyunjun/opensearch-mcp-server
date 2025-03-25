# Generated by https://smithery.ai. See: https://smithery.ai/docs/config#dockerfile
# Start with a Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY . .

# Install hatch to handle the build
RUN pip install hatch

# Clean dist directory before build
RUN rm -rf dist/*

# Use hatch to build the package and install it
RUN hatch build && pip install dist/*.whl

# Set environment variables required for the MCP server
# These can be overridden at runtime with docker run --env
ENV OPENSEARCH_HOST="https://localhost:9200"
ENV OPENSEARCH_USERNAME="opensearch"
ENV OPENSEARCH_PASSWORD="test123"

# Expose the port the server is running on (if applicable)
EXPOSE 8000

# Command to run the server
ENTRYPOINT ["opensearch-mcp-server"]