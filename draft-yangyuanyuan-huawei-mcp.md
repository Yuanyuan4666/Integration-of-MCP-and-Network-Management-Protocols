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
title: "MCP"
category: info

docname: draft-yangyuanyuan-huawei-mcp-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: AREA
workgroup: HuaWei
keyword:
 - large language model
 - model context protocol
venue:
  group: HuaWei
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

In this context, MCP provides a universal, open standard that offers LLMs a standardized way to transmit contextual information, simplifying the integration of AI models with data and tools. This document analyzes the market demand in the scenario of cross-vendor network equipment batch management, the advantages of MCP, and the deployment plan, while also evaluating the pros and cons of two deployment strategies.

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

# Operation Need

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

- Encapsulating diverse device operations into discrete MCP tools for host-side calling.
- Exposing LLM model APIs that transform natural language instructions into executable tool operations.
- Achieving the "language/text command -> automated execution" closure.

# Deployment Plan

During the deployment phase, there are three key aspects to consider:

- **Function-Specific MCP Servers**: Deploy dedicated MCP servers tailored to different functions and domains, such as network log analysis, device configuration management, energy consumption management, and security operations.
- **Secure and Scalable Architecture**: Implement stringent security measures to ensure only authorized AI models and users can access and control network resources via MCP.
- **Automated Workflows**: Leverage MCP to enable LLM-coordinated multi-tool automation, supporting real-time monitoring, diagnostics, and fault remediation.

Based on these considerations, we propose two solutions:

## MCP within Local NCE

The user issues a natural language command, which is received by the operations and maintenance (O&M) console and forwarded to the MCP client. The LLM then processes the command, invokes the appropriate tools to pass instructions to the MCP server, which finally interacts with network devices using NETCONF and SNMP protocols.

## MCP in Remote Device

The main workflow is similar to *MCP within Local NCE*, with the key difference being the integration method of the MCP server. In this solution, the MCP server is integrated in the network devices. Within the network device, the MCP server interacts with network devices via CLI instead of NETCONF and SNMP protocols.

# IANA Considerations

This document has no IANA actions.

# Security Considerations

This document analyzes the application of MCP in sophisticated batch network management and proposes two deployment schemes, which may introduce certain security risks. Since MCP's internal instructions are invisible to users and only accessible to the LLM model, attackers could potentially inject malicious instructions, leading to information leakage or workflow errors.

To address such security risks, measures like version locking mechanisms, enhanced visibility, and context isolation can provide a certain level of protection.

# Conclusion

MCP Technology delivers an innovative solution for cross-vendor network device management at scale. By enhancing and extending traditional network management protocols (NETCONF/RESTCONF), it effectively addresses multi-vendor device management challenges while significantly improving network administration efficiency and service quality. As the technology matures, MCP is positioned for widespread adoption in network management domains.

--- back

# Reference
