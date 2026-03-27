# Personal Finance MCP Server

This module acts as a bridge between the user and the `personal-finance-service` backend. It uses the `fastmcp` library to expose the backend's API as a set of tools that can be used in a conversational AI environment.

## Getting Started

### Prerequisites
- Python 3.9+

### Installation
To install the required dependencies, run the following command in this directory:
```bash
sh scripts/install-mcp.sh
```

### Running the Server
To start the MCP server, run the following command:
```bash
sh scripts/start-mcp.sh
```
The server will be available at `http://localhost:8000`.

## Scripts

- `scripts/install-mcp.sh`: Installs the Python dependencies for the MCP server.
- `scripts/start-mcp.sh`: Starts the Uvicorn server for the MCP application.
