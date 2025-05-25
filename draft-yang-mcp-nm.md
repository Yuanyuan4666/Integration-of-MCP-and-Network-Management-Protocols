---
###
# Internet-Draft Markdown Template
#
# Rename this file from draft-todo-yourname-protocol.md to get started.
# Draft name format is "draft-<yourname>-<workgroup>-<name>.md".
#
# For initial setup, you only need to edit the first block of fields.
# Only "title" needs to be changed; delete "abbrev" if your title is short.
# Any other content can be edited, but be careful not to introduce errors.
# Some fields will be set automatically during setup if they are unchanged.
#
# Don't include "-00" or "-latest" in the filename.
# Labels in the form draft-<yourname>-<workgroup>-<name>-latest are used by
# the tools to refer to the current version; see "docname" for example.
#
# This template uses kramdown-rfc: https://github.com/cabo/kramdown-rfc
# You can replace the entire file if you prefer a different format.
# Change the file extension to match the format (.xml for XML, etc...)
#
###
title: "Integration of MCP and Network Management Protocols"
category: info

docname: draft-yang-mcp-nm-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: AREA
workgroup: nmrg
keyword:
 - large language model
 - model context protocol
venue:
  group: nmrg
  type: Working Group
  mail: yangyuanyuan55@huawei.com
  arch: https://example.com/WG
  github: USER/REPO
  latest: https://example.com/LATEST

author:
 -
    fullname: Yang Yuanyuan
    organization: HuaWei
    email: yangyuanyuan55@huawei.com

normative:

informative:


--- abstract

With the emergence of various LLM models, enterprises face different frameworks or systems during deployment. For each LLM model, a corresponding toolchain needs to be developed, causing significant inconvenience. This document introduces MCP(Model Context Protocol), a technology that can effectively manage different LLM models. Further, this document discusses the application of MCP in cross-vendor network equipment batch management and proposes corresponding deployment strategies.  MCP has been seen as rapid adoption technology in the consumer field. The application of MCP in the network management field is meant to
    develop various rich AI driven network applications, realize intent based networks
    management automation in the multi-vendor heterogeneous network environment.
    This document outlines the applicability of MCP to the network management
    in the IP network that utilizes IETF technologies. It explores operational
    aspect, key components, generic workflow and deployment senarios. The impact
    of integrating MCP into the network management system is also discussed.

--- middle

# Introduction

With the emergence of various LLM models, enterprises face different frameworks and systems during deployment, such as ChatGPT's plugin mechanism and agent frameworks. Adapting to these mechanisms requires developing distinct toolchains, which increases development costs. Additionally, LLMs rely on contextual data, but various agents retrieve local and remote data in a fragmented manner, lacking a unified management approach.

The Model Control Protocol (MCP) provides a standardized framework for intent-based network automation in multi-vendor environments, specifically addressing the interoperability challenges between large language models (LLMs) and heterogeneous network equipment. By establishing vendor-neutral interfaces for tool encapsulation, intent translation, and closed-loop execution, MCP enables:

- Unified operation abstraction through normalized MCP tool definitions
- Closed-Loop Automation Execution

Further, this document specifies MCP's architecture and operational workflows for network automation scenarios, with particular focus on:

- The end-to-end processing chain from natural language input to device configuration
- Protocol translation requirements between AI systems and network elements
- Comparative analysis of on-premises versus cloud-hosted deployment models

# Terminology & Notation Conventions

The following terms are used throughout this document:

## MCP

- **Host**: The entity initiating the LLM request
- **Client**: A built-in module within a host, specifically designed for interaction with the MCP server.
- **CLI**: Command Line Interface
- **MCP Server**: A dedicated server that interacts with MCP clients and provides MCP services.
- **MCP protocol**: The whole MCP framework

## Others

- **LLM**: Large Language Model
- **Netconf**: Network Configuration Protocol
- **Restconf**: RESTful Network Configuration Protocol
- **SNMP**: Simple Network Management Protocol

# Problem Statemtent

In the scenario of cross-vendor network equipment batch management, a large number of devices from different vendors need to be uniformly managed, which can lead to the following issues:

## Inconsistent YANG Model Support

Different vendors implement different YANG models (standard or proprietary), leading to:

- Lack of uniform data structures for configuration/retrieval.
- Requirement for vendor-specific adaptations in automation scripts.

## Partial or Non-Standard RESTCONF/NETCONF Implementations

Some vendors only partially support standard YANG models, and proprietary extensions may break interoperability.

## Performance & Scalability Issues

When managing cross-vendor devices in bulk, NETCONF can be slower than RESTCONF (HTTP/HTTPS) for large-scale operations, while RESTCONF lacks native batching support. Additionally, both protocols may suffer from timeouts when handling many devices simultaneously.

# Operational Consideration

## Functional Modules

The LLM model, with its ability to comprehend diverse complex requirements and deliver corresponding functionalities, is well-suited for cross-vendor network equipment batch management, effectively addressing the aforementioned challenges. Therefore, we have introduced the MCP protocol to standardize the management of different LLM models, serving as the foundation for building an intelligent network control platform.

To be more specific, there are three functional modules needed:

### Encapsulating Device Operations into MCP Tools

- *Objective*: Standardize heterogeneous device operations into modular, reusable tools.
- *Implementation*:
  - *Tool Abstraction*: Vendor-specific commands are wrapped into discrete MCP Tools with uniform schemas.
  - *Tool Registry*: A centralized repository hosts MCP Tools with metadata (e.g., vendor compatibility, privilege requirements).
  - *Dynamic Loading*: MCP Servers dynamically invoke required tools via NETCONF on demand, thereby decoupling tool lifecycle management from the server's core functionality.
- *Benefits*:
  - Eliminates manual translation of commands across vendors.
  - Enables plug-and-play integration of new device types.

### LLM APIs for Words-to-Tool Translation

- Objective: Bridge natural language instructions to executable tool sequences.
- Workflow:
  - Command Parsing: LLM APIs (e.g., GPT-4, Claude) process user queries like "Upgrade all switches in Datacenter A during maintenance" into structured commands.
  - Toolchain Generation: The LLM selects and sequences MCP Tools (e.g., get_inventory → schedule_downtime → download_firmware → validate_upgrade).
  - Validation: Pre-execution checks verify tool compatibility with target devices.
- APIs Exposed:
  - mcp-translate: Converts words to toolchain JSON.
  - mcp-validate: Confirms tool availability/permissions.

### Closed-Loop Automation Execution

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

- User Input Submission: An operator submits a natural language request (e.g., "Disable port 22 on all edge switches") to the LLM interface.
- LLM Intent Processing: The LLM parses the input, identifies the operational intent, and forwards a structured request to the local O&M Console for validation and logging.
- MCP Tool Discovery: The O&M Console routes the request to the MCP Client, which queries the MCP Server to retrieve the available tools.
- LLM Toolchain Decision:
  - The LLM evaluates the context and if tools are required, select and sequence tools.
  - The decision is sent back to the MCP Client and then MCP Client will execute tools via server.
- Protocol Translation & Execution: The MCP Server executes the translated commands on target devices and returns results to the client.
- Result Aggregation & Feedback: The MCP Client collates tool outputs (success/failure logs) and forwards them to the LLM for summarization.

While the overall workflow remains consistent, the MCP Server's deployment location (on-premises or remote) introduces operational variations. This section defines two refined approaches to accommodate differing deployment scenarios.

## MCP within Network Controller

        +--------------+
        |     User     |
        +-------+------+
                |
        Natural Language
        Request |
     ......................
     .  +-------+------+  .N
     .  |     LLM      |  .E
     .  +-------+------+  .T
     .          |         .W
     .    O&M Console     .O
     .          |         .R
     .  +-------+------+  .K
     .  |  MCP Client  |  .
     .  +-------+------+  .C
     .          |         .O
     .   Tools Request    .N
     .          |         .T
     .  +-------+------+  .R
     .  |  MCP Server  |  .O
     .  +-------+------+  .L
     .          |         .L
     .          |         .E
     ...........|..........R
                |
            Netconf
        +--------------+
        |   Network    |
        |   Devices    |
        +--------------+

- Scope: The MCP Server is hosted within the operator's local network, colocated with the O&M Console and MCP Client.
- Key Characteristics:
  - Low Latency: Direct access to network devices minimizes tool execution delays.
  - Data Control: All processing (LLM queries, tool executions) remains within the operator’s infrastructure.

### Use cases

- Air-Gapped Networks (Military/Critical Infrastructure)
  - Scenario: A power grid control network prohibits external connectivity.
  - Implementation:
    - MCP Server runs on local servers with pre-loaded tool definitions.
    - LLM operates offline (e.g., quantized model) or via approved internal APIs.
  - Advantage: Ensures zero data exfiltration risks.

## MCP in Remote Device

      +--------------+
      |     User     |
      +-------+------+
              |
      Natural Language
      Request |
   ......................
   .  +-------+------+  .
   .  |     LLM      |  .
   .  +-------+------+  .
   .          |         .
   .    O&M Console     .
   .          |         .R O
   .  +-------+------+  .K L
   .  |  MCP Client  |  .  L
   .  +-------+------+  .  L
   .          |         .  E
   .   Tools Request    .  R
   .          |         .
   ......................
   ......................
   .  +-------+------+  .N D
   .  |  MCP Server  |  .E E
   .  +-------+------+  .T V
   .          |         .W I
   .  +--------------+  .O C
   .  |   Network    |  .R E
   .  |   Devices    |  .K
   .  +--------------+  .
   ......................

- Scope: The MCP Server operates in a cloud environment, serving distributed MCP Clients via public/private APIs.
- Key Characteristics:
  - Centralized Management: A single MCP Server instance can manage multiple geographically dispersed networks.
  - Scalability: Cloud-native scaling accommodates dynamic tool registry updates and high request volumes.

### Use cases

- Global Enterprise Network Automation
  - Scenario: A multinational corporation standardizes configurations across hundreds of branch offices.
  - Implementation:
    - MCP Server hosted on AWS/Azure with regional replicas.
    - Tools like deploy_vpn_template adapt to local compliance rules.
  - Advantage: Unified toolchain reduces configuration drift.

# Conclusion


# IANA Considerations

This document has no IANA actions.

# Security Considerations


--- back

# Reference

1.  Introduction

   The Model Control Protocol (MCP) provides a standardized way for LLMs to
   access and utilize information from different sources, making it easier
   to build AI applications that can interact with external systems.

   MCP has been seen as rapid adoption technology in the consumer field.
   The application of MCP in the network management field is meant to
   develop various rich AI driven network applications, realize intent based networks
   management automation in the multi-vendor heterogeneous network environment. By
   establishing standard interfaces for tool encapsulation, intent
   translation, and closed-loop execution, MCP enables:

   *  Unified operation abstraction through normalized MCP tool
      definitions

   *  Seamless LLM integration via structured API contracts

   *  Closed-Loop Automation Execution

   This document outlines the applicability of MCP to the network management
   in the IP network that utilizes IETF technologies. It explores operational
   aspect, key components, generic workflow and deployment senarios. The impact
   of integrating MCP into the network management system is also discussed.

2.  Terminology & Notation Conventions

   The following terms are used throughout this document:

2.1.  MCP

   *  *Host*: The entity initiating the LLM request

   *  *Client*: A built-in module within a host, specifically designed
      for interaction with the MCP server.

   *  *CLI*: Command Line Interface

   *  *MCP Server*: A dedicated server that interacts with MCP clients
      and provides MCP services.

   *  *MCP protocol*: The whole MCP framework

2.2.  Others

   *  *LLM*: Large Language Model

   *  *Netconf*: Network Configuration Protocol

   *  *Restconf*: RESTful Network Configuration Protocol

3.  Overveiw of key challenges for the network management

  In large scale network management environment, a
  large number of devices from different vendors need to be uniformly
  managed, which can lead to the following issues:

3.1.  Inconsistent YANG Model Support

  Different vendors implement different YANG models (standard or
  proprietary), leading to:

  *  Lack of uniform data structures for configuration/retrieval.

  *  Requirement for vendor-specific adaptations in automation scripts.

3.2.  Partial or Non-Standard RESTCONF/NETCONF Implementations

  Some vendors only partially support standard RESTCONF/NETCONF protocol, and
  proprietary extensions may break interoperability.

3.3.  Performance & Scalability Issues

  NETCONF, while transactional and robust, can be more resource-intensive,
  particularly for large deployments and fast-changing configurations.
  
  RESTCONF, with its stateless, web-friendly architecture, scales better
  but may lack the advanced transactional features of NETCONF and can be
  less efficient for bandwidth-intensive operations.

4. Operational Considerations

This section outlines operational aspects of MCP with Network management requirements
as follows:
   *  *Function-Specific MCP Servers*: Deploy dedicated MCP servers
      tailored to different functions and domains, such as network log
      analysis, device configuration management, energy consumption
      management, and security operations.

   *  *Secure and Scalable Architecture*: Implement stringent security
      measures to ensure only authorized AI models and users can access
      and control network resources via MCP.

   *  *Automated Workflows*: Leverage MCP to enable LLM-coordinated
      multi-tool automation, supporting real-time monitoring,
      diagnostics, and fault remediation.


5.  Architecture Overview

The LLM model with MCP support, with its ability to comprehend diverse complex
requirements and deliver corresponding functionalities, is well-
suited for large scale multi-vendor network management environments,
effectively addressing the aforementioned operational challenges in section 4.
Therefore, we have introduced the MCP protocol in the network management environments
for building an intelligent network management and control platform.

5.1.  Encapsulating Device Operations into MCP Tools

   *  _Objective_: Standardize heterogeneous device operations into
      modular, reusable tools.

   *  _Implementation_:

      -  _Tool Abstraction_: Vendor-specific CLI/API commands are
         wrapped into discrete MCP Tools with uniform JSON/Protobuf
         schemas.

      -  _Tool Registry_: A centralized repository hosts MCP Tools with
         metadata (e.g., vendor compatibility, privilege requirements).

      -  _Dynamic Loading_: Servers (e.g., network controllers) invoke
         tools on demand via MCP RPCs, decoupling tool updates from core
         platform logic.

   *  _Benefits_:

      -  Eliminates manual translation of commands across vendors.

      -  Enables plug-and-play integration of new device types.

5.2.  LLM APIs for Intent-to-Tool Translation

   *  Objective: Bridge natural language instructions to executable tool
      sequences.

   *  Workflow:

      -  Intent Parsing: LLM APIs (e.g., GPT-4, Claude) process user
         queries like "Upgrade all switches in Datacenter A during
         maintenance" into structured intents.

      -  Toolchain Generation: The LLM selects and sequences MCP Tools
         (e.g., get_inventory → schedule_downtime → download_firmware →
         validate_upgrade).

      -  Validation: Pre-execution checks verify tool compatibility with
         target devices (e.g., ensuring upgrade_tool supports Arista EOS
         versions).

   *  APIs Exposed:

      -  mcp-translate: Converts text to toolchain JSON.

      -  mcp-validate: Confirms tool availability/permissions.

5.3.  Closed-Loop Automation Execution

   *  Objective: Achieve end-to-end automation from language input to
      network changes.

   *  Execution Flow:

      -  User Input: Operator submits request via chat/voice (e.g.,
         "Block TCP port 22 on all edge routers").

      -  LLM Processing:

         o  Intent → Toolchain: Identifies get_edge_routers +
            configure_acl tools.

         o  Parameter Binding: Maps "TCP port 22" to {"protocol": "tcp",
            "port": 22, "action": "deny"}.

      -  Orchestration: MCP Runtime schedules tools, handles
         dependencies (e.g., backup configs first), and enforces RBAC.

      -  Feedback: Real-time logs/rollback if configure_acl fails on any
         device.

   *  Key Features:

      -  Idempotency: Tools safely retry/rollback.

      -  Auditability: Full traceability of LLM decisions and tool
         executions.

5.5 General workflow

   A general workflow is as follows:

   *  User Input Submission: An operator submits a natural language
      request (e.g., "Disable port 22 on all edge routers") to the LLM
      interface.

   *  LLM Intent Processing: The LLM/Agent parses the input, identifies the
      operational intent, and forwards a structured request to the local
      O&M Console or MCP client for validation and logging.

   *  MCP Tool Discovery: The O&M Console/MCP CLient routes the request to the MCP
      Server, which retrieves the data or invoke available tools.

   *  LLM Toolchain Decision:

      -  The LLM evaluates the context and if tools are required, select
         and sequence tools.

      -  The decision is sent back to the MCP Client and then MCP Client
         will execute tools via server.

   *  Protocol Translation & Execution: The MCP Server executes the
      translated commands on target devices and returns results to the
      client.

   *  Result Aggregation & Feedback: The MCP Client collates tool
      outputs (success/failure logs) and forwards them to the LLM for
      summarization.

5.6 Deployment considerations

   While the overall workflow remains consistent, the MCP Server's
   deployment location (on-premises or remote) introduces operational
   variations.  This section explores two deployment considerations.

5.6.1.  MCP hosted within the Network Controller

                   +--------------+
                   |     User     |
                   +-------+------+
                           |
                   Natural Language
                  Command  |
                ......................
                .  +-------+------+  .
                .  |  LLM/Agent   |  .
                .  +-------+------+  .
                .          |         .
                .          |         .
                .  +-------+------+  .
                .  |  MCP Client  |  .
                .  +-------+------+  .Network
                .          |         .Controller
                .   Tools Request    .
                .          |         .
                .  +-------+------+  .
                .  |  MCP Server  |  .
                .  +-------+------+  .
                .          |         .
                .          |         .
                ...........|..........
                           |
                  Netconf/Telemetry
                           |
                   +--------------+
                   |   Network    |
                   |   Devices    |
                   +--------------+

   *  Scope: The MCP Server operates within the centralized nework controller,
      colocated with the O&M Console and LLM,serving distributed Network Devices
      via Netconf and Telemetry standard protocol.

   *  Key Characteristics:

      -  Centralized Management: A single MCP Server instance can manage
         multiple geographically dispersed networks devices.

      -  Scalability: Cloud-native scaling accommodates dynamic tool
         registry updates and high request volumes.

5.6.2.  MCP Within the Network Device

                     +--------------+
                     |     User     |
                     +-------+------+
                            |
                    Natural Language
                    Request |
                  ......................
                  .  +-------+------+  .
                  .  |  LLM/Agent   |  .
                  .  +-------+------+  .
                  .          |         .
                  .          |         .
                  .          |         .
                  .  +-------+------+  .
                  .  |  MCP Client  |  .
                  .  +-------+------+  .Network
                  .          |         .Controller
                  .   Tools Request    .
                  .          |         .
                  .          |         .
                  ......................
                  .  +-------+------+  .
                  .  |  MCP Server  |  .
                  .  +-------+------+  .Network
                  .        CLI         .Device
                  .          |         .
                  . +--------------+   .
                  . |   Network    |   .
                  . |   Devices    |   .
                  . +--------------+   .
                  ......................
   *  Scope: The MCP Server operates within each network device, dedicated serving
      one single Network device via public/private APIs or CLI.

   *  Key Characteristics:

      -  Low Latency: Direct access to network devices minimizes tool
         execution delays.

      -  Data Control: All processing (LLM queries, tool executions)
         remains within the operator’s infrastructure.


7.  IANA Considerations

   This document has no IANA actions.

8.  Security Considerations

    TBC.

Appendix A.  Reference

Author's Address

   Yang Yuanyuan
   HuaWei
   Email: yangyuanyuan55@huawei.com
