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
title: "integration of MCP and network management protocols"
category: info

docname: draft-yangyuanyuan-huawei-mcp-latest
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

With the emergence of various LLM models, enterprises face different frameworks or systems during deployment. For each LLM model, a corresponding toolchain needs to be developed, causing significant inconvenience. This document introduces MCP(Model Context Protocol), a technology that can effectively manage different LLM models. Further, this document discusses the application of MCP in cross-vendor network equipment batch management and proposes corresponding deployment strategies.

--- middle

# Introduction

With the emergence of various LLM models, enterprises face different frameworks and systems during deployment, such as ChatGPT's plugin mechanism and agent frameworks. Adapting to these mechanisms requires developing distinct toolchains, which increases development costs. Additionally, LLMs rely on contextual data, but various agents retrieve local and remote data in a fragmented manner, lacking a unified management approach.

The Model Control Protocol (MCP) provides a standardized framework for intent-based network automation in multi-vendor environments, specifically addressing the interoperability challenges between large language models (LLMs) and heterogeneous network equipment. By establishing vendor-neutral interfaces for tool encapsulation, intent translation, and closed-loop execution, MCP enables:

- Unified operation abstraction through normalized MCP tool definitions
- Seamless LLM integration via structured API contracts
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

# Solution

The LLM model, with its ability to comprehend diverse complex requirements and deliver corresponding functionalities, is well-suited for cross-vendor network equipment batch management, effectively addressing the aforementioned challenges. Therefore, we have introduced the MCP protocol to standardize the management of different LLM models, serving as the foundation for building an intelligent network control platform.

To be more specific, there are three parts:

## Encapsulating Device Operations into MCP Tools

- *Objective*: Standardize heterogeneous device operations into modular, reusable tools.
- *Implementation*:
  - *Tool Abstraction*: Vendor-specific CLI/API commands are wrapped into discrete MCP Tools with uniform JSON/Protobuf schemas.
  - *Tool Registry*: A centralized repository hosts MCP Tools with metadata (e.g., vendor compatibility, privilege requirements).
  - *Dynamic Loading*: Servers (e.g., network controllers) invoke tools on demand via MCP RPCs, decoupling tool updates from core platform logic.
- *Benefits*:
  - Eliminates manual translation of commands across vendors.
  - Enables plug-and-play integration of new device types.

## LLM APIs for Intent-to-Tool Translation

- Objective: Bridge natural language instructions to executable tool sequences.
- Workflow:
  - Intent Parsing: LLM APIs (e.g., GPT-4, Claude) process user queries like "Upgrade all switches in Datacenter A during maintenance" into structured intents.
  - Toolchain Generation: The LLM selects and sequences MCP Tools (e.g., get_inventory → schedule_downtime → download_firmware → validate_upgrade).
  - Validation: Pre-execution checks verify tool compatibility with target devices (e.g., ensuring upgrade_tool supports Arista EOS versions).
- APIs Exposed:
  - mcp-translate: Converts text to toolchain JSON.
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

# Operational Consideration

During the deployment phase, there are three key aspects to consider:

- **Function-Specific MCP Servers**: Deploy dedicated MCP servers tailored to different functions and domains, such as network log analysis, device configuration management, energy consumption management, and security operations.
- **Secure and Scalable Architecture**: Implement stringent security measures to ensure only authorized AI models and users can access and control network resources via MCP.
- **Automated Workflows**: Leverage MCP to enable LLM-coordinated multi-tool automation, supporting real-time monitoring, diagnostics, and fault remediation.

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
   .  +-------+------+  .N C
   .  |     LLM      |  .E O
   .  +-------+------+  .T N
   .          |         .W T
   .    O&M Console     .O R
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

MCP Technology delivers an innovative solution for cross-vendor network device management at scale. By enhancing and extending traditional network management protocols (NETCONF/RESTCONF), it effectively addresses multi-vendor device management challenges while significantly improving network administration efficiency and service quality. As the technology matures, MCP is positioned for widespread adoption in network management domains.

# IANA Considerations

This document has no IANA actions.

# Security Considerations

This document analyzes the application of MCP in sophisticated batch network management and proposes two deployment schemes, which may introduce certain security risks. Since MCP's internal instructions are invisible to users and only accessible to the LLM model, attackers could potentially inject malicious instructions, leading to information leakage or workflow errors.

To address such security risks, measures like version locking mechanisms, enhanced visibility, and context isolation can provide a certain level of protection.

--- back

# Reference
