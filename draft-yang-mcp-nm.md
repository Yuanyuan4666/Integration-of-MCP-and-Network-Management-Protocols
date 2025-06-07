---
title: "Applicability of MCP for the Network Management"
category: info

docname: draft-yang-mcp-nm-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: OPS and ART
workgroup: Network Management Working Group
keyword:
 - large language model
 - model context protocol

author:
 -
    fullname: Yuanyuan Yang
    organization: Huawei
    email: yangyuanyuan55@huawei.com
 -
   fullname: Qin Wu
   organization: Huawei
   email: bill.wu@huawei.com

contributor:
 -  fullname: Guanming Zeng
    organization: Huawei
    email: zengguanming@huawei.com

normative:

informative:


--- abstract

The application of MCP in the network management field is meant to develop various rich AI driven network applications, realize intent based networks management automation in the multi-vendor heterogeneous network environment. This document discusses the applicability of MCP to the network management in the IP network that utilizes IETF technologies. It explores operational aspect, key components, generic workflow and deployment scenarios. The impact of integrating MCP into the network management system is also discussed.

--- middle

# Introduction

The Model Context Protocol (MCP) provides a standardized way for LLMs to access and utilize information from different sources, interact with tools, making it easier to build AI applications that can interact with external systems.

MCP has been seen as rapid adoption technology in the consumer field. The application of MCP in the network management field is meant to develop various rich AI driven network applications, realize intent based networks management automation in the multi-vendor heterogeneous network environment. By establishing standard interfaces for tool encapsulation, intent translation, and closed-loop execution within the network management system or the network controller, MCP enables AI
Agents to have:

- Unified operation abstraction through normalized MCP tool definitions
- Seamless LLM integration via structured API contracts
- Closed-Loop Automation Execution

This document discusses the applicability of MCP to the network management plane in the IP network that utilizes IETF technologies. It explores operational aspect, key components, generic workflow and deployment scenarios. The impact of integrating MCP into the network management system will also be discussed.

# Terminology & Notation Conventions

The following terms are used throughout this document:

## MCP

- **MCP Protocol**: MCP is an open standard designed to facilitate communication between LLMs and external data sources or tools.
- **MCP Host**: The entity initiating the LLM request.
- **MCP Client**: A built-in module within a host, specifically designed for interaction with the MCP server.
- **MCP Server**: A dedicated server that interacts with MCP clients and provides MCP services.

## Others

- **LLM**: Large Language Model
- **NETCONF**: Network Configuration Protocol {{!RFC6241}}
- **RESTCONF**: RESTful Network Configuration Protocol {{!RFC8040}}
- **SNMP**: A Simple Network Management Protocol {{!RFC2576}}
- **CLI**: Command Line Interface

# Overview of key challenges for the network management

In large scale network management environment, a large number of devices from different vendors need to be uniformly managed, which can lead to the following issues or challenges:

## Inconsistent YANG Model Support

Different vendors implement different YANG models (standard or proprietary), leading to:

- Lack of uniform data structures for configuration/state retrieval.
- Requirement for vendor-specific adaptations in automation scripts.

Also IETF standard device models has slow adoption. Similar device models
are defined in Openconfig or other SDOs, therefore the current YANG device
models ecosystem is fragmented.

## Partial or Non-Standard Network management protocols Implementations

Some vendors only partially support standard Network management protocols, and proprietary extensions may break interoperability.
Other vendors might choose non-stanard network management protocol or telemetry protocol such as gnmi {{?I-D.openconfig-rtgwg-gnmi-spec}},
grpc {{?I-D.kumar-rtgwg-grpc-protocol}}. A significant number of network operators continue to rely on legacy network management mechanisms
such as SNMP and CLI.

## Lack integration with Network APIs

Today, network API has been widely adopted by the northbound interface of OSS/BSS or Network orchestrators while YANG data models have
been widely adopted by the northbound interface of the network controller or the interface between the network controller and the network devices.
However Network API ecosystem and YANG model ecosystem are both built as silo and lack integration or mapping between them.

# Operational Consideration {#ops-radiu}

This section outlines operational aspects of MCP with Network management requirements as follows:

-  *Function-Specific MCP Servers*: Deploy dedicated MCP servers tailored to different functions and domains, such as network log analysis, device configuration management, energy consumption management, and security operations.
-  *Secure and Scalable Architecture*: Implement stringent security measures to ensure only authorized AI models and users can access and control network resources via MCP.
-  *Automated Workflows*: Leverage MCP to enable LLM-coordinated multi-tool automation, supporting real-time monitoring, diagnostics, and fault remediation.

# Architecture Overview

The LLM model with MCP support and its ability to comprehend diverse complex requirements and deliver corresponding functionalities, is well- suited for large scale multi-vendor network management environments, effectively addressing the aforementioned operational challenges in {{ops-radiu}}. Therefore, we have introduced the MCP protocol in the network management environments for building an intelligent network management and control platform.

## Encapsulating Device Operations into MCP Tools

- *Objective*: Standardize heterogeneous device operations into modular, reusable tools.
- *Implementation*:
  - *Tool Abstraction*: Vendor-specific commands are wrapped into discrete MCP Tools with uniform schemas.
  - *Tool Registry*: A centralized repository hosts MCP Tools with metadata (e.g., vendor compatibility, privilege requirements).
  - *Dynamic Loading*: MCP Servers dynamically invoke required tools via network management protocol on demand, thereby decoupling
    tool lifecycle management from the server's core functionality.
- *Benefits*:
  - Eliminates manual translation of commands across vendors.
  - Enables plug-and-play integration of new device types.

## LLM APIs for Intent-to-Tool Translation

- Objective: Bridge natural language instructions to executable tool sequences.
- Workflow:
  - Command Parsing: LLM APIs (e.g., GPT-4, Claude) process user queries like "Upgrade all switches in Datacenter A during maintenance" into structured commands.
  - Toolchain Generation: The LLM selects and sequences MCP Tools (e.g., get_inventory → schedule_downtime → download_firmware → validate_upgrade).
  - Validation: Pre-execution checks verify tool compatibility with target devices.
- APIs Exposed:
  - mcp-translate: Converts intent to toolchain JSON.
  - mcp-validate: Confirms tool availability/permissions.

## Closed-Loop Automation Execution

- Objective: Achieve end-to-end automation from language input to network changes.
- Execution Flow:
  - User Input: Operator submits request via chat/voice (e.g., "Block TCP port 22 on all edge routers").
  - LLM Processing:
    - Intent → Toolchain: Identifies get_edge_routers + configure_acl tools.
    - Parameter Binding: Maps "TCP port 22" to {"protocol": "tcp", "port": 22, "action": "deny"}.
  - Orchestration: MCP Runtime schedules tools, handles dependencies (e.g., backup configs first), and enforces RBAC.
  - Feedback: Real-time logs/rollback if configure_acl fails on any device.
- Key Features:
  - Idempotency: Tools safely retry/rollback.
  - Auditability: Full traceability of LLM decisions and tool executions.

## Workflow

A general workflow is as follows:

- User Input Submission: An operator submits a natural language request (e.g., "Disable port 22 on all edge switches") to the MCP client. And The MCP client
  forwards this request to the LLM.

- LLM Intent Processing: The LLM parses the input, identifies the operational intent, and forwards a structured request to the MCP client, which queries the
  MCP Server to retrieve the available tools.

- LLM Toolchain Decision:
  - The LLM evaluates the context and if tools are required, select and sequence tools.
  - The decision is sent back to the MCP Client and then MCP Client will execute tools via server.

- Protocol Translation & Execution: The MCP Server executes the translated commands on target devices and returns results to the client.

- Result Aggregation & Feedback: The MCP Client collates tool outputs (success/failure logs) and forwards them to the LLM for summarization.

Take multi-vendor network management as an example, the MCP server is deployed locally on the network controller, and the tools are
integrated into the MCP server. The server provide the following registered tool descriptor information:

Tools description: it describes the name, use, and parameters of tools.

Tools implementation: MCP implementation describe how the tools are invoked.

See Tool descriptor information example as follows:

~~~~
# Tool Descriptor
[
  {
    "name": "batch_configure_devices",
    "description": "Batch Configure Network Devices"，
    "parameters": {
      "type": "object",
      "properties": {
        "device_ips": {"type": "array", "items": {"type": "string"}, "description": "Device IP List"}，
        "commands": {"type": "array", "items": {"type": "string"}, "description": "CLI Sequence"}，
        "credential_id": {"type": "string", "description": "Credential ID"}
      }，
      "required": ["device_ips", "commands"]
    }
  },
  {
    "name": "check_device_status",
    "description": "Check the Status of Network Devices"，
    "parameters": {
      "type": "object",
      "properties": {
        "device_ip": {"type": "string"},
        "metrics": {"type": "array", "items": {"enum": ["cpu", "memory", "interface"]}}
      }
    }
  }
]
# Tool Implementation
from netmiko import ConnectHandler
from mcp_server import McpServer

app = FastAPI()
server = McpServer(app)

#Connection Pool Management
devices = {
    "192.168.1.1": {"device_type": "VendorA-XYZ"，"credential": "admin:password"},
    "192.168.1.2": {"device_type": "VendorB-ABC","credential":"admin:huawei@passowrd"}
     ....
}

@server.tool("batch_configure_devices")
async def batch_config(device_ips: list,commands: list,credential_id: str):
    results = {}
    for ip in device_ips:
        conn = ConnectHandler(
            ip = ip,
            username = devices[ip]["credential"].split(':')[0],
            password = devices[ip]["credential"].split(':')[1],
            device_type = devices[ip]["device_type"]
        )
        output = conn.send_config_set(commands)
        results[ip] = output
    return {"success": True, "details": results)

@server.tool("check_device_status")
async def check_status(device_ip: str, metrics: list):
    status = {}
    if "cpu" in metrics:
        status["cpu"] = get_cpu_usage (device_ip)
    if "memory" in metrics:
        status["memory"] = get_memory_usage(device_ip)
    return status
~~~~

Suppose a user submits a request (via the client) such as "Configure OSPF Area 0 with process ID 100 for all core switches in the Beijing data center," the MCP
client retrieves the necessary tooling descriptor information from the MCP server and forwards it to the LLM. The LLM determines the appropriate tools and responds
in JSON format as follows:

~~~~
{
"method": "batch_configure_devices",
"params": {
   "device_ips":["192.168.10.1",....,"192.168.10.10"],
   "command": [
     "router ospf 100",
     "network 192.168.0.0 0.0.255.255 area 0"
   ]
 }
}
}

~~~~

The MCP server executes the network management operation in JSON format and returns the results (in JSON) to the MCP client, which forwards them to the LLM. The
LLM parses the response, generates a natural-language summary, and sends it back to the client for final presentation to the user. See natural lanauge summary example as follows:

~~~~

{
  "192.168.10.1": "Configure Successfully, take 2.3 seconds",
  "192.168.10.2": "Error: no response from the device",
}

~~~~

# Deployment considerations

While the overall workflow remains consistent, the MCP Server's deployment location (on-premises or remote) introduces operational variations.  This section explores two deployment scenarios.

## MCP hosted within the Network Controller

~~~~
                  +--------------+
                  |     User     |
                  +-------+------+
                          |
                  Natural Language
                 Command  |
               ...........|............................
               .          |                           .
               .  +-------+------+       +-----------+.
               .  |  MCP Client  +-------+  LLM      |.
               .  +-------+------+       +-----------+.
               .          |                           .
               .   Tools Request                      .Network
               .          |                           .Controller
               .  +-------+------+                    .
               .  |  MCP Server  |                    .
               .  +-------+------+                    .
               .          |                           .
               ...........|............................
                          |
                  Netconf/Telemetry
      +-------------------+------------------+
      |                   |                  |
      |                   |                  |
+-----+--------+  +-------+------+    +------+-------+
|   Network    |  |   Network    |    |   Network    |
|   Device     |  |   Device     |    |   Device     |
+--------------+  +--------------+    +--------------+
~~~~

- Scope: The MCP Server,collocated with the LLM model and MCP Client, is hosted within the operator's local network, the network devices stay as it is.
- Key Characteristics:
  -  Centralized Management: A single MCP Client instance can manage multiple MCP server in geographically dispersed network.
  -  Scalability: Cloud-native scaling accommodates dynamic tool registry updates and high request volumes.

## MCP Server Hosted Within the Network Device

~~~~
                   +--------------+
                   |     User     |
                   +-------+------+
                           |
                  Natural Language
                        Command
.........................................................
.                          |                            .
.                  +-------+------+       +-----------+ .
. Network          |  MCP Client  +-------+  LLM      | .
. Controller       +-------+------+       +-----------+ .
.                          |                            .
.                   Tools Request                       .
.........................................................
.                  +-------+------+                     .
.                  |  MCP Server  |                     .
.                  +-------+------+                     .
.Network                        CLI                     .
.Device                          |                      .
.     +--------------------+--------------------+       .
.     |                    |                    |       .
.+----+-------+    +-------+------+     +-------+------+.
.| Network    |    |   Network    |     |   Network    |.
.| Device     |    |   Device     |     |   Device     |.
.+------------+    +--------------+     +--------------+.
.                                                       .
.........................................................
~~~~

- Scope: The MCP Client operates in a cloud environment, serving distributed MCP Server via public/private APIs.
- Key Characteristics:
  -  Low Latency: Direct access to network devices minimizes tool execution delays.
  -  Data Control: All processing (LLM queries, tool executions) remains within the operator’s infrastructure.

# Impact of integrating MCP on Network Management

~~~~

+------------+-----------------------------+-----------------------+
|            |   MCP Hosted Within         |   MCP Server Hosted   |
|            | the Network Controller      | Within Network Device |
+------------+-----------------------------+-----------------------+
|            |                             |1.Protocol for Context |
|Management  |  No impact,reuse            |  Management           |
|Protocol    |  existing NM Protocols      |2 Including approval   |
|            |                             | mechanisms where human|
|            |                             | input is required.    |
|            |                             |3.Coexist with NM proto|
|            |                             |in case not all devices|
|            |                             |support MCP            |
+------------+-----------------------------+-----------------------+
|Management  |  Use internal tools and     |  Need to ensure right |
|   Tools    |  LLMs within the controller |  tools and background |
|            |  for managing context and   |  info in the network  |
|            |  decision making            |  device               |
+------------+-----------------------------+-----------------------+
|  Task      |  Works with pre-structured  |                       |
|Management  |  goal driven tasks.         |    Same Rule Apply    |
|            |  Tasks are usually designed |                       |
|            |  and pre-defined by client  |                       |
+------------+-----------------------------+-----------------------+
|            |  Yes,                       |    Yes                |
| Stateful   |  Agents can retain context  |                       |
|Management  |  from previous interaction, |    Same Rule Apply    |
|            |  enabling continuity in     |                       |
|            |  long term task or          |                       |
|            |  conversation               |                       |
-------------+-----------------------------+-----------------------+

~~~~

## MCP Hosted Within the Network Controller

- Pro
  - Resource utilization efficiency:
    Controllers usually have stronger computing and storage resources, which can better support the operation of MCP Server and will not have a significant
    impact on the performance of the network equipment itself.
  - Security：
    - Security mechanisms can be implemented centrally on the controller, and the overall security can be improved through unified authentication, authorization
      and audit mechanisms.
    - Reduces the risk of equipment being exposed to the network and reduces the possibility of being attacked.
  - Protocol adaptability：
    - Communicating with devices through the NETCONF protocol can better be compatible with existing devices and protocols, reducing the need for equipment
      modification.
    - NETCONF protocol has wide support and mature tool chains in the industry, which is easy to develop and maintain.
- Con
  - Latency and real-time performance：
    - Since management instructions need to be forwarded through the controller, latency may increase and real-time performance may be affected.
    - For some scenarios with extremely high real-time requirements, it may not meet the requirements.
  - Protocol conversion complexity：
    - The MCP protocol needs to be converted to the NETCONF protocol, which increases the complexity and development cost of protocol conversion.
    - It is necessary to deal with compatibility and consistency issues between different protocols.

## MCP Server Hosted within the Network Device

- Pro
  - The protocol stack Simplification:
    - If you deploy the MCP Server directly on the network device, you can skip the NETCONF protocol layer and manage the device directly through MCP.
      This reduces the complexity of protocol conversion and simplifies the overall architecture.
    - It reduces the development and maintenance costs caused by protocol adaptation, especially when the device manufacturer supports the MCP protocol.
  - Real-time performance and response speed:
    - The MCP Server is directly deployed on the device, which reduces the transmission latency in the middle and can respond to management instructions
      faster, which is suitable for scenarios with high real-time requirements.
- Con
  - Device Resource Consumption:
    - Network devices usually have limited resources (CPU, memory, etc.). Deploying MCP Server may occupy a large amount of resources, affecting the normal
      operation of the device.
    - It is necessary to optimize and expand the hardware and software resources of the device, which increases the complexity of the device.
  - Security and Management Complexity:
    - Each device needs to manage the security of the MCP server separately (such as authentication, authorization, audit, etc.), which increases the
      complexity of management.
    - Each device needs to independently deploy and maintain the MCP Server, which increases the operation and maintenance cost.
  - Incompatible with Legacy devices:
    - Legacy devices do not have the ability to support MCP servers and still need NETCONF to implement network configuration. This makes it impossible
      for the network to form a unified control mechanism.

# IANA Considerations

This document has no IANA actions.

# Security Considerations


The deployment of MCP in network management environments introduces several security considerations that implementers and operators must address.

## Expanded Attack Surface

MCP introduces AI capabilities directly into the network control plane, creating new attack vectors that did not exist in conventional network management systems. Unlike traditional SNMP or NETCONF management that primarily processes structured data, MCP systems must handle natural language queries. This expanded interface increases the potential for input-based attacks, including prompt injection and context manipulation that could lead to unintended network modifications.

The protocol's stateful nature and context persistence create additional vulnerabilities. Malicious context injection in earlier sessions could influence future network management decisions, potentially remaining dormant until triggered by specific network conditions or queries.

## Model Integrity as a Security Foundation

The reliability of network management decisions depends entirely on the integrity of the underlying AI models. Unlike traditional network management systems where logic is explicitly programmed, MCP systems rely on learned behaviors that can be subtly corrupted. Model poisoning attacks could introduce biases that only manifest under specific network conditions, making detection extremely difficult.

## Data Sensitivity and Inference Risks

Network management systems process highly sensitive operational data including performance metrics, failure patterns, and capacity utilization. MCP systems that learn from this data could inadvertently expose sensitive information through model inversion attacks or membership inference. An attacker with access to model outputs could potentially reconstruct network topology, identify traffic patterns, or infer the existence of specific network segments.

--- back
