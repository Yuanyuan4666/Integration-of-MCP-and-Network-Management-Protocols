# MCP Network Device Management Tool

## Project Overview

This project consists of two main files that implement an MCP (Model Context Protocol) based network device management tool:

1. **mcp_cli_netconf_client.py** - MCP client responsible for communicating with Ollama large language model and MCP server
2. **mcp_cli_netconf_server.py** - MCP server providing network device configuration and query tools

## Features

- Support for managing network devices (Huawei-router as an example)via CLI and NETCONF protocols
- Integration with Ollama large language model for intelligent tool calling
- Rich set of network device operation tools
- Support for real-time device configuration and status queries

## Environment Requirements

### Required Software
1. **ENSP Network Simulator** (requires Virtual Box virtual machine)
   - Reference: [ENSP Installation Guide](https://support.huawei.com/enterprise/zh/management-system/ensp-pid-9017384/bulletins)
   - Obtain device IP addresses from routers

2. **Ollama**
   - Download: https://ollama.com/download/windows

3. **Anaconda**
   - Download: https://www.anaconda.com/products/distribution

## Installation Steps

### 1. Create Virtual Environment
bash
conda create -n test python=3.11
conda activate test
### 2. Install Dependencies
bash
pip install mcp
pip install FastMCP
pip install fastapi>=0.68.0
pip install uvicorn>=0.15.0
pip install openai>=1.108
pip install paramiko>=2.7.2
pip install pydantic>=1.8.2
pip install requests
pip install ncclient
## Running Methods

### 1. Start MCP Server
bash
python mcp_cli_netconf_server.py
### 2. Start MCP Client
bash
python mcp_client.py
### Debug Mode
bash
python mcp_client.py -d
## Tool Function Description

### Configuration Management Tools

#### 1. read_device_config
**Function**: Read NETCONF connection configuration from JSON file

**Parameters**: json_file_path - JSON configuration file path

**Returns**: Dictionary containing connection parameters

#### 2. connect_and_get_config
**Function**: Establish NETCONF connection and retrieve device configuration

**Parameters**: config - Connection configuration parameter dictionary

**Returns**: Session information and device configuration

#### 3. DisplayCurrentConfiguration
**Function**: Get device current running configuration

**Returns**: Complete configuration text information

### Interface Management Tools

#### 4. displayInterface
**Function**: Display interface status and statistical information

**Parameters**: command - Interface display command

**Returns**: Detailed interface status information

#### 5. displayInterfaceMain
**Function**: Query main interface status

**Parameters**: ifType - Interface type (optional)

**Returns**: Main interface status summary

#### 6. displayIfBrief
**Function**: Display brief information for all interfaces

**Parameters**: command - Interface brief information command

**Returns**: Interface brief status table

#### 7. DisMethSts
**Function**: View MEth management port status

**Parameters**: command - MEth status display command

**Returns**: Management interface status information

#### 8. disp_port_loopback
**Function**: Display port loopback mode

**Parameters**: command - Loopback mode display command

**Returns**: Port loopback configuration information

### Configuration Deployment Tools

#### 9. CfgIssuance
**Function**: Configuration deployment tool supporting system view and interface view configuration

**Parameters**:
- interface_type - Interface type
- interface_number - Interface number
- mtu - MTU value

**Returns**: Configuration execution result

#### 10. CreateBasicACL
**Function**: Create basic ACL and add rules

**Parameters**: acl_number - ACL number (default 2001)

**Returns**: ACL configuration result

### Information Query Tools

#### 11. query_vrf_info
**Function**: Query VRF instance information

**Parameters**: command - VRF query command

**Returns**: VRF information in JSON format

#### 12. disp_lldp_local_info
**Function**: Display device local LLDP information

**Parameters**: command - LLDP information display command

**Returns**: LLDP information in JSON format

## Usage Examples

After startup, enter commands in the client, and the system will automatically select appropriate tools to execute:
Input: display interface GigabitEthernet0/0/0
The system will call the corresponding tool function and return device interface information.

## Precautions

- Ensure network devices (ENSP routers) are started and configured with correct IP addresses
- Configure correct device login credentials before first run
- Ensure Ollama service is running normally and required models are downloaded
- Debug mode will display detailed request and response information

## Troubleshooting

- Check network connectivity and device reachability
- Verify login credentials are correct
- Confirm if Ollama models are properly loaded
- Check debug logs for detailed error information
