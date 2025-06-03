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

normative:

informative:


--- abstract

The application of MCP in the network management field is meant to develop various rich AI driven network applications, realize intent based networks management automation in the multi-vendor heterogeneous network environment. This document discusses the applicability of MCP to the network management in the IP network that utilizes IETF technologies. It explores operational aspect, key components, generic workflow and deployment senarios. The impact of integrating MCP into the network management system is also discussed.

--- middle

# Introduction

The Model Control Protocol (MCP) provides a standardized way for LLMs to access and utilize information from different sources, interact with tools, making it easier to build AI applications that can interact with external systems.

MCP has been seen as rapid adoption technology in the consumer field. The application of MCP in the network management field is meant to develop various rich AI driven network applications, realize intent based networks management automation in the multi-vendor heterogeneous network environment. By establishing standard interfaces for tool encapsulation, intent translation, and closed-loop execution within the network management system or the network controller, MCP enables AI
Agents to have:

- Unified operation abstraction through normalized MCP tool definitions
- Seamless LLM integration via structured API contracts
- Closed-Loop Automation Execution

This document discusses the applicability of MCP to the network management plane in the IP network that utilizes IETF technologies. It explores operational aspect, key components, generic workflow and deployment senarios. The impact of integrating MCP into the network management system will also be discussed.

# Terminology & Notation Conventions

The following terms are used throughout this document:

## MCP

- **MCP Protocol**: MCP is an open standard designed to facilitate communication between LLMs and external data sources or tools.
- **MCP Host**: The entity initiating the LLM request.
- **MCP Client**: A built-in module within a host, specifically designed for interaction with the MCP server.
- **MCP Server**: A dedicated server that interacts with MCP clients and provides MCP services.

## Others

- **LLM**: Large Language Model
- **Netconf**: Network Configuration Protocol
- **Restconf**: RESTful Network Configuration Protocol
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

The LLM model with MCP support and its ability to comprehend diverse complex requirements and deliver corresponding functionalities, is well- suited for large scale multi-vendor network management environments, effectively addressing the aforementioned operational challenges in section {{ops-radiu}}. Therefore, we have introduced the MCP protocol in the network management environments for building an intelligent network management and control platform.

## Encapsulating Device Operations into MCP Tools

- *Objective*: Standardize heterogeneous device operations into modular, reusable tools.
- *Implementation*:
  - *Tool Abstraction*: Vendor-specific commands are wrapped into discrete MCP Tools with uniform schemas.
  - *Tool Registry*: A centralized repository hosts MCP Tools with metadata (e.g., vendor compatibility, privilege requirements).
  - *Dynamic Loading*: MCP Servers dynamically invoke required tools via network management protocol on demand, thereby decoupling tool lifecycle management from the server's core functionality.
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

- Scope: The MCP Server is hosted within the operator's local network, collocated with the O&M Console and MCP Client.
- Key Characteristics:
  - Low Latency: Direct access to network devices minimizes tool execution delays.
  - Data Control: All processing (LLM queries, tool executions) remains within the operator’s infrastructure.

## MCP Server Hosted Within the Network Device

~~~~
                   +--------------+
                   |     User     |
                   +-------+------+
                           |
                  Natural Language
                  Command  |
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

- Scope: The MCP Server operates in a cloud environment, serving distributed MCP Clients via public/private APIs.
- Key Characteristics:
  - Centralized Management: A single MCP Server instance can manage multiple geographically dispersed networks.
  - Scalability: Cloud-native scaling accommodates dynamic tool registry updates and high request volumes.

# Impact of integrating MCP on Network Management

~~~~
+------------+-----------------------------+-----------------------+
|            |   MCP Hosted Within         |   MCP Server Hosted   |
|            | the Network Controller      | Within Network Device |
|            |                             |                       |
|            |                             |                       |
|Management  |  No impact,reuse            |1.Protocol for Context |
|Protocol    |  existing NM Protocols      |2 Management including |
|            |                             | approval mechanisms   |
|            |                             | where human input is  |
|            |                             | required.             |
|            |                             |3.Coexist with NM proto|
|            |                             |in case not all devices|
|            |                             |support MCP            |
+------------+-----------------------------+-----------------------+
|            |                             |                       |
|Management  |  use internal tools and     |  Need to ensure right |
|   Tools    |  LLMs for managing context  |  tools and background |
|            |  and decision making        |  info in the network  |
|            |                             |  device               |
+------------+-----------------------------+-----------------------+
|            |                             |                       |
|            |                             |                       |
|  Task      |  Works with pre-structured  |                       |
|Management  |  goal driven tasks.         |    Same Rule Apply    |
|            |  Tasks are usually designed |                       |
|            |  and pre-defined by client  |                       |
|            |                             |                       |
+------------+-----------------------------+-----------------------+
|            |                             |                       |
| Stateful   |  Agents can retain context  |                       |
|Management  |  from previous interaction, |    Same Rule Apply    |
|            |  enabling continuity in     |                       |
|            |  long term task or          |                       |
|            |  conversation               |                       |
-------------+-----------------------------+-----------------------+
~~~~

# IANA Considerations

This document has no IANA actions.

# Security Considerations



--- back
