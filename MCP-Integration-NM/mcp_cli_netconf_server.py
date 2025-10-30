
import sys
import os
import requests
import threading
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import paramiko
from typing import Dict, Any, Optional, List
import json
import time
import re
import uvicorn
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))
from cli_api.config import executor, sessions
from cli_api.routes.login import login_router
from cli_api.routes.execute import execute_router
from cli_api.routes.logout import logout_router
from ncclient import manager
import logging

"""
Login device
"""
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

mcp = FastMCP("simple stdio mcp")
app.include_router(login_router, prefix="/api", tags=["login"])
app.include_router(execute_router, prefix="/api", tags=["execute"])
app.include_router(logout_router, prefix="/api", tags=["logout"])

# Global variable for storing session ID, named global_session_id to avoid conflicts with other variable names
global_session_id = None
netconf_sessions = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ncclient")

"""
Supported tool interfaces
"""
@mcp.tool(
    name="read_device_config",
    description="Read NETCONF connection configuration from JSON file",
    title="Read NETCONF Connection Configuration from JSON File")
def read_device_config(json_file_path: str) -> dict:
    """
    Read NETCONF connection configuration from JSON file
    
    Args:
        json_file_path (str): JSON configuration file path
        
    Returns:
        dict: Dictionary containing connection parameters
    """
    try:
        with open(json_file_path, 'r') as file:
            config = json.load(file)
        
        required_fields = ['host', 'username','port', 'password']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        return config
        
    except FileNotFoundError:
        logger.error(f"Configuration file does not exist: {json_file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error occurred while reading configuration: {e}")
        raise

@mcp.tool(
    name="connect_and_get_config",
    description="Establish NETCONF connection using configuration parameters and retrieve device configuration",
    title="Establish NETCONF Connection Using Configuration Parameters and Retrieve Device Configuration")

def connect_and_get_config(config: dict) -> dict:
    """
    Establish NETCONF connection using configuration parameters and get device configuration
    
    Args:
        config (dict): Connection configuration parameters
    """
    try:
        connect_params = {
            'host': config['host'],
            'port': config['port'],
            'username': config['username'],
            'password': config['password'],
            'hostkey_verify': config.get('hostkey_verify', False),
            'device_params': {'name':'huaweiyang'}
        }
        
        logger.info(f"Connecting to device {config['host']}:{config['port']}...")
        
        with manager.connect(**connect_params) as m:
            logger.info("NETCONF connection successful!")
            
            # Get device capabilities
            capabilities = list(m.server_capabilities)
            m
            
            # Get running configuration
            running_config = m.get_config(source='running').data_xml
            
            # Save session information
            session_id = f"netconf_{config['host']}"
            netconf_sessions[session_id] = {
                'manager': m,
                'host': config['host'],
                'connected_at': threading.current_thread().name
            }
            
            return {
                'session_id': session_id,
                'host': config['host'],
                'capabilities_count': len(capabilities),
                'sample_capabilities': capabilities[:5],
                'config_xml_length': len(running_config)
            }
            
    except Exception as e:
        logger.error(f"NETCONF connection or configuration retrieval failed: {e}")
        raise

@mcp.tool(name="query_vrf_info",
    description="Query VRF instance information",
    title="Query VRF Instance Information")
def query_vrf_info(command: str) -> str:
    """
    Query VRF instance information.
    
    Supported command formats:
    - display vpn-instance [vpn-instance-name]
    
    Return fixed format JSON result:
    {
      "vpn-instance-name": "CUSTOMER_A",
      "route-distinguisher": "100:1",
      "vpn-target": [
        {
          "vpn-target": "100:1",
          "export-extcommunity": true
        },
        {
          "vpn-target": "100:1",
          "import-extcommunity": true
        }
      ]
    }
    """
    
    return json.dumps({
        "vpn-instance-name": "CUSTOMER_A",
        "route-distinguisher": "100:1",
        "vpn-target": [
            {
                "vpn-target": "100:1",
                "export-extcommunity": True
            },
            {
                "vpn-target": "100:1",
                "import-extcommunity": True
            }
        ]
    }, indent=2)

@mcp.tool(
    name="CreateBasicACL",
    description="Create basic ACL and add rules",
    title="Create Basic ACL"
)
def create_basic_acl(acl_number: int = 2001) -> str:
    """
    Create basic ACL and add default rules:
    1. Allow 192.168.1.0/24 network segment
    2. Deny all other source IPs
    
    Parameters:
    acl_number: ACL number (default is 2001)
    
    Return configuration result string
    """
    # Configuration command list
    commands = [
        f"system-view",
        f"display acl {acl_number}",
        f"acl number {acl_number}",
        f"rule 5 permit source 192.168.1.0 0.0.0.255",
        f"rule 10 deny source any",
        "commit",
        f"display acl {acl_number}",
        "return"
    ]
    
    try:
        if global_session_id is None:
            raise ValueError("Not logged in, please log in to the device first.")
            
        # Send configuration request
        response = requests.post(
            "http://localhost:8000/api/execute",
            json={
                "session_id": global_session_id,
                "commands": commands
            }
        )
        response.raise_for_status()
        
        # Return success result
        return f"ACL {acl_number} configuration successful:\n" \
               "- Rule 5: Allow 192.168.1.0/24\n" \
               "- Rule 10: Deny all other source IPs"
               
    except requests.exceptions.RequestException as e:
        return f"Configuration failed: Network error - {str(e)}"
    except Exception as e:
        return f"Configuration failed: {str(e)}"


@mcp.tool(
    name="DisplayCurrentConfiguration",
    description="Get device current running configuration, supports execution in user view and returns complete configuration information.",
    title="Get Current Configuration"
)
def DisplayCurrentConfiguration() -> str:
    """
    This function is used to get the device's current running configuration, specific steps are as follows:
    1. Ensure currently in user view (if in system view need to exit)
    2. Execute command: `display current-configuration`
    3. Return complete configuration information

    Return result format:
    - Success: returns configuration texts
    - Failure: `Error message`
    """
    try:
        if global_session_id is None:
            raise ValueError("Not logged in, please log in to the device first.")
        
        # Configuration command list (ensure first return to user view)
        commands = [
            "display current-configuration | no-more"
        ]
        
        # Send configuration request
        response = requests.post(
            "http://localhost:8000/api/execute",
            json={
                "session_id": global_session_id,
                "commands": commands
            }
        )
        response.raise_for_status()
        
        # Get and return configuration results (take the output of the last command)
        results = response.json()["results"]
        return results[-1]["output"].strip()  # Return the complete output of the last command
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Communication error when getting configuration: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get configuration: {str(e)}"
        )

@mcp.tool(name="disp_lldp_local_info",
    description="Display device local LLDP information",
    title="Display device local LLDP information")
def disp_lldp_local_info(command: str) -> str:
    """
    Display device local LLDP information.
    
    Supported command formats:
    - display lldp/local-info/
    
    Returns fixed format JSON result:
    {
      "chassis-id-sub-type": "mac-address",
      "chassis-id": "e8f6-5494-04a0",
      "system-name": "e8f6-5494-04a0",
      "system-description": "Huawei AP...",
      "up-time": "2025-10-21T14:17:03+00:00",
      "management-addresss": {
        "management-address": [
          {
            "type": "ipv4",
            "value": "169.254.1.1",
            "length": 5,
            "if-sub-type": "if-index",
            "if-id": 10001,
            "": "1.3.6.1.4.1.2011.5.25.41.1.2.1.1.1"
          }
        ]
      },
      "system-capabilities-supported": ["wlan-access-point"],
      "system-capabilities-enabled": ["wlan-access-point"]
    }
    """
    # Directly return predefined JSON result
    return json.dumps({
        "chassis-id-sub-type": "mac-address",
        "chassis-id": "e8f6-5494-04a0",
        "system-name": "e8f6-5494-04a0",
        "system-description": "Huawei AP\r\nHuawei YunShan OS\r\nVersion 1.25.0.1 (AirEngine 6700 V600R025C10)\r\nCopyright (C) 2021-2025 Huawei Technologies Co., Ltd.\r\nHUAWEI AirEngine6776-57T\r\nCurrent Work Mode: CLOUD",
        "up-time": "2025-10-21T14:17:03+00:00",
        "management-addresss": {
            "management-address": [
                {
                    "type": "ipv4",
                    "value": "169.254.1.1",
                    "length": 5,
                    "if-sub-type": "if-index",
                    "if-id": 10001,
                    "oid": "1.3.6.1.4.1.2011.5.25.41.1.2.1.1.1"
                }
            ]
        },
        "system-capabilities-supported": ["wlan-access-point"],
        "system-capabilities-enabled": ["wlan-access-point"]
    }, indent=2)  # Use indent=2 to beautify JSON output

@mcp.tool(
    name="CfgIssuance",
    description="Configuration issuance tool, supports entering system view, interface view and issuing configuration commands, finally committing configuration.",
    title="Configuration Issuance Tool"
)
def CfgIssuance(interface_type: str, interface_number: str, mtu: int) -> str:
    """
    This function is used to configure the MTU value of the device interface, specific steps:
    1. Enter system view: `system-view`
    2. Enter interface view: `interface <interface_type> <interface_number>`
    3. Configure MTU value: `mtu <mtu>`
    4. Commit configuration: `commit`

    Supported interface types include: GigabitEthernet, Ten-GigabitEthernet, etc.

    Return result format:
    - Configuration successful: `Configuration successful`
    - Configuration failed: `Error message`
    """
    try:
        if global_session_id is None:
            raise ValueError("Not logged in, please login to the device first.")
        
        # Configuration command list
        commands = [
            "system-view",
            f"interface {interface_type} {interface_number}",
            f"mtu {mtu}",
            "commit",
            "display this",
            "return"
            
        ]
        
        # Send configuration request
        response = requests.post("http://localhost:8000/api/execute", json={
            "session_id": global_session_id,
            "commands": commands
        })
        response.raise_for_status()
        
        # Get and return result
        result = response.json()["results"]
        return f"Configuration result: {result[-2]['output'].strip()}"
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error during configuration issuance: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        


@mcp.tool(name="displayInterface",
          title="Display interface status and statistics information")
def displayInterface(command: str) -> str:
    """
    This function is used to execute the 'display interface' command to obtain the current running status and statistics information of the specified network interface.
    
    Supported command formats include:
    - View specific type and number interface: display interface <ifType> [ <ifNum> ] | no-more
    - View interface of specified slot: display interface slot <slotNumber> | no-more
    - View interface with specified name: display interface <ifName> | no-more
    - View main interface: display interface main | no-more
    - View main interface of specific type: display interface <ifType> main | no-more
    
    Return result format:
    current state : UP
    Line protocol current state : UP
    Description:link-to-OLT-LB
    Switch Port, PVID :1, TPID : 8100(Hex), The Maximum Frame Length is 1600
    IP Sending Frames' Format is PKTFMT_ETHNT_2, Hardware address is 4c1f-cc45-b1c0
    Current system time: 2016-06-18 15:12:52
    Port Mode: COMMON COPPER
    Speed : 1000,Loopback: NONE
    Duplex: FULL,Negotiation: ENABLE
    Mdi: AUTO,Flow-control: DISABLE
    Last 300 seconds input rate 99894144 bits/sec, 141895 packets/sec
    Last 300 seconds output rate 190939848 bits/sec, 271220 packets/sec
    Input peak rate 173002368 bits/sec, Record time: 2016-06-18 15:03:12
    Output peak rate 346005880 bits/sec, Record time: 2016-06-18 15:03:12
    Input:175946456 packets, 15483288128 bytes
    Unicast:0,Multicast:0
    Broadcast:175946456,Jumbo:0
    Discard:0, Pause:0
    Total Error:0
    CRC:0,Giants:0
    Jabbers:0,Fragments:0
    Runts:0,DropEvents:0
    Alignments:0,Symbols:0
    Ignoreds:0,Frames:0
    Output:348119287 packets, 30634557621 bytes
    Unicast:0,Multicast:773
    Collisions:0,ExcessiveCollisions:0
    Late Collisions:0,Deferreds:0
    Buffers Purged:0
    """
    try:
        # Use global session_id
        if global_session_id is None:
            raise ValueError("Not logged in, please login to the device first.")
        
        # Send command execution request
        response = requests.post("http://localhost:8000/api/execute", json={
            "session_id": global_session_id,
            "commands": [command]
        })
        response.raise_for_status()
        
        # Get and return result
        result = response.json()["results"]
        return result[0]['output']
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




@mcp.tool(name="displayInterfaceMain",
          description="Query main interface status",
          title="Query main interface status")
def displayInterfaceMain(ifType: str = None) -> str:
    """
    This function is used to query main interface status information.
    
    Parameter description:
    - ifType: Interface type (optional), such as Gigabit, Eth-Trunk, etc.
      If no interface type is provided, main interface information for all interfaces will be displayed.
    
    Supported command formats include:
    - Query main interface status of all interfaces: display interface main | no-more
    - Query main interface status of specific type interfaces: display interface <ifType> main | no-more
    
    Return result format:
    Interface                   Status   Protocol  InUti OutUti   inErrors  outErrors
    Eth-Trunk0                  down    up        10%   5%      5          2
    GigabitEthernet0/0/0        up      up        0%    0%      0          0
    GigabitEthernet0/0/1        up      down      30%   15%     12 89
    LoopBack0                   up      up        0%    0%      0          0
    NULL0                       up      up        0%    0%      0          0
    
    Status description:
    *down: administratively down
    ^down: standby
    (l): loopback
    (r): reuse interface
    (s): unicast interface
    (m): multipoint interface
    """
    

    command = "display interface main | no-more"
    
    try:
        # Use global session_id
        if global_session_id is None:
            raise ValueError("Not logged in, please login to the device first.")
        
        # Send command execution request
        response = requests.post("http://localhost:8000/api/execute", json={
            "session_id": global_session_id,
            "commands": [command]
        })
        response.raise_for_status()
        
        # Get and return result
        result = response.json()["results"]
        return result[0]['output']
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@mcp.tool(name="displayIfBrief",
          title="Display brief information of all interfaces")
def displayIfBrief(command: str) -> str:
    """
    This function is used to execute the 'display interface brief' command to obtain brief information of all interfaces on the device.
    
    Supported command formats include:
    - View brief information of all interfaces: display interface brief | no-more
    - View brief information of specific type interfaces: display interface brief <ifType> | no-more
    - View brief information of specific type main interfaces: display interface brief <ifType> main | no-more
    
    Return result format:
   *down: administratively down
    ^down: standby
    (l): loopback
    (s): spoofing
    (E): E-Trunk down
    (b): BFD down
    (B): Bit-error-detection down
    (e): ETHOAM down
    (d): Dampening Suppressed
    (p): port alarm down
    (ld): loop-detect trigger down
    (lcs): license not activated
    InUti/OutUti: input utility/output utility
    Interface                   PHY   Protocol  InUti OutUti   inErrors  outErrors
    Eth-Trunk0                  down  down         3%      7%        12          0
    Eth-Trunk1                  down  down         0%      0%         0          0
    Ethernet0/0/0               up    up          50%     60%        23        125
    GigabitEthernet0/1/0        up    up          50%     60%        23        125
    GigabitEthernet0/1/1        down  down         0%      0%         0          0
    GigabitEthernet0/1/2.1      down  down         0%      0%         0          0
    GigabitEthernet0/1/3       *down  down        50%     30%         0          0
    GigabitEthernet0/1/4(10G)   down  down         0%      0%         0          0
    GigabitEthernet0/1/4.1(10G) down  down         0%      0%         0          0
    GigabitEthernet0/2/0        up(l) up           0%      0%         0          0
    GigabitEthernet0/3/0        up(l) up           0%      0%         0          0
    LoopBack0                   down  up(s)        0%      0%         0          0
    NULL0                       up    up           0%      0%         0          0"""
  
    try:
        # Use global session_id
        if global_session_id is None:
            raise ValueError("Not logged in, please login to the device first.")
        
        # Send command execution request
        response = requests.post("http://localhost:8000/api/execute", json={
            "session_id": global_session_id,
            "commands": [command]
        })
        response.raise_for_status()
        
        # Get and return result
        result = response.json()["results"]
        return result[0]['output']
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@mcp.tool(name="DisMethSts",
          description="View the status of all MEth management network ports on the device, format is display interface <meth> status",
          title="View the status of all MEth management network ports")
def DisMethSts(command: str) -> str:
    """
    This function is used to execute the `display interface <meth> status` command to obtain the status information of all MEth management network ports on the device.
    
    Supported command formats include:
    - View the status of all MEth management network ports: display interface <meth> status | no-more
    
    Return result format:
    MEth Interface Status:
    ---------------------
    Interface Name: MEth0
    Status: Up
    Description: Management interface for MEth0
    IP Address: 192.168.1.1
    Subnet Mask: 255.255.255.0
    MAC Address: 00:1A:2B:3C:4D:5E
    Speed: 1000 Mbps
    Duplex: Full
    Flow Control: Enabled
    """
    try:
        # Use global session_id
        if global_session_id is None:
            raise ValueError("Not logged in, please login to the device first.")
        
        # Send command execution request
        response = requests.post("http://localhost:8000/api/execute", json={
            "session_id": global_session_id,
            "commands": [command]
        })
        response.raise_for_status()
        
        # Get and return result
        result = response.json()["results"]
        return result[0]['output']
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@mcp.tool()
def disp_port_loopback(command: str) -> str:
    """
    Used to display the currently set port loopback mode.
    
    Supported command formats:
    - View port loopback mode: display interface loop-mode | no-more
    
    Return result format:
    Port Loopback Mode Information:
    -------------------------------
    Interface Name: Ethernet0/0/0
    Loopback Mode: NONE
    Description: Normal operation, no loopback configured.
    
    Interface Name: GigabitEthernet0/1/0
    Loopback Mode: SOFTWARE
    Description: Loopback set via software configuration.
    
    Interface Name: LoopBack0
    Loopback Mode: HARDWARE
    Description: Hardware loopback detected.
    """
    try:
        # Use global session_id
        if global_session_id is None:
            raise ValueError("Not logged in, please login to the device first.")
        
        # Send command execution request
        response = requests.post("http://localhost:8000/api/execute", json={
            "session_id": global_session_id,
            "commands": [command]
        })
        response.raise_for_status()
        
        # Get and return result
        result = response.json()["results"]
        return result[0]['output']
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Declare resource template via mcp.resource annotation
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def cmd_prompts() -> str:
    """
    Command line format description
    Returns:
        str: Command line format description
    """
    return {
        "[] indicates that the elements in brackets are optional",
        "{} indicates that the elements in brackets are required",
        "{} and [] can be nested",
        "| indicates a parallel relationship, choose one, used with {} or []",
        "<> indicates parameters, need to be obtained from user input",
        "Construct tool input parameters according to the command format in the function description information",
        "'' indicates command format"

    }

# ========== FastAPI Routes ==========

@app.post("/api/login")
async def login_device(credentials: dict):
    """Login to device and establish session"""
    try:
        # Here you can integrate your existing login logic
        # Also can start NETCONF connection
        
        # Example: Establish both SSH and NETCONF connections
        session_id = f"session_{credentials['host']}_{threading.get_ident()}"
        
        # Store session information
        global global_session_id
        global_session_id = session_id
        
        return {"session_id": session_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute")
async def execute_commands(command_request: dict):
    """Execute commands"""
    try:
        session_id = command_request["session_id"]
        commands = command_request["commands"]
        
        # Command execution logic
        results = []
        for cmd in commands:
            # Simulate command execution result
            results.append(f"Executed: {cmd} -> Success")
        
        return {"results": results, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/netconf/connect")
async def netconf_connect(config: dict):
    """Establish NETCONF connection via API"""
    try:
        result = connect_and_get_config(config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/netconf/sessions")
async def get_netconf_sessions():
    """Get all NETCONF sessions"""
    return {
        "active_sessions": len(netconf_sessions),
        "sessions": list(netconf_sessions.keys())
    }


def main():
    print("Hello stdio mcp server!")
    try:
        # Create and start FastAPI server thread
        server_thread = threading.Thread(target=lambda: uvicorn.run(app, host="127.0.0.1", port=8000))
        server_thread.daemon = True
        server_thread.start()
        
        # Login device
        try:
            response = requests.post("http://localhost:8000/api/login", json={
                "host": "192.168.45.11",
                "port": 22,
                "username": "Rfvbgt#123",
                "password": "Chasdfgh_123"
            })
            response.raise_for_status()
            session_id_value = response.json()["session_id"]
            if not session_id_value:
                raise ValueError("Failed to obtain session_id")
            global global_session_id
            global_session_id = session_id_value
            print(f"Login successful! Session ID: {session_id_value}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to login: {str(e)}")
            raise
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

        # Execute commands
        print("\nExecuting commands...")
        commands = [
            "cd ../",
            "cd /opt/svrp",
            "./time_client_start",
            "system",
            "undo pnp enable",
            "return"
        ]
        try:
            response = requests.post("http://localhost:8000/api/execute", json={
                "session_id": global_session_id,
                "commands": commands
            })
            response.raise_for_status()
            execute_result = str(response.json()["results"])
            print(f"\nCommand execution results:\n{execute_result}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to execute commands: {str(e)}")
            raise
        except Exception as e:
            print(f"Command execution failed: {str(e)}")
            raise

        # Start NETCONF connection
        print("\nStarting NETCONF connection...")
        netconf_config = {
            "host": "192.168.45.11",
            "port": 22,
            "username": "Rfvbgt#123",
            "password": "Chasdfgh_123",
            "hostkey_verify": False
        }
        
        netconf_result = connect_and_get_config(netconf_config)
        print(f"NETCONF connection result: {netconf_result}")

        # Start mcp service
        mcp.run(transport='stdio')
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
    finally:
        print("Shutting down FastAPI server...")
        # Correctly close Uvicorn server
        uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000)).shutdown()

if __name__ == "__main__":
    main()
