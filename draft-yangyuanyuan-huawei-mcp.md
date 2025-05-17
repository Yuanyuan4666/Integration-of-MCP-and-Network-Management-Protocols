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
workgroup: WG Working Group
keyword:
 - next generation
 - unicorn
 - sparkling distributed ledger
venue:
  group: WG
  type: Working Group
  mail: WG@example.com
  arch: https://example.com/WG
  github: USER/REPO
  latest: https://example.com/LATEST

author:
 -
    fullname: Your Name Here
    organization: Your Organization Here
    email: your.email@example.com

normative:

informative:


--- abstract

In today's complex network environment, the unified management of multi-vendor network devices faces numerous challenges, such as diverse models and complex configurations. Traditional network management protocols like Netconf and Restconf are difficult to standardize during the management process, resulting in low efficiency. MCP (Model Context Protocol) technology, combined with LLM technology, brings new ideas and solutions for the batch management of multi-vendor network devices, and is expected to significantly improve the efficiency and flexibility of network management.


--- middle

# Introduction

In today's complex network environment, the unified management of multi-vendor network devices faces numerous challenges, such as diverse models and complex configurations. Traditional network management protocols like Netconf and Restconf are difficult to standardize during the management process, resulting in low efficiency. MCP (Model Context Protocol) technology, combined with LLM technology, brings new ideas and solutions for the batch management of multi-vendor network devices, and is expected to significantly improve the efficiency and flexibility of network management.


# Terminology & Notation Conventions

The following terms are used throughout this document:

## MCP

- Host
- Client
- CLI
- MCP Server
- MCP protocol
- LLM
- NCE equipment
- 自然语言指令
- Netconf
- Restconf
- SNMP

## Netconf协议

NETCONF（Network Configuration Protocol）是一种基于XML的网络配置管理协议，由IETF标准化（RFC 6241），旨在提供更灵活、可靠的设备配置方式。尽管它在一定程度上实现了设备管理的标准化，但在实际应用中，尤其是在**跨厂商设备管理**时，面临着**数据模型不统一、配置操作复杂、厂商实现差异**等问题。具体来说：

- 数据模型（YANG）不统一：不同厂商的YANG节点路径和接口命名不同，尽管可以采用**OpenConfig YANG模型**，但并非所有厂商完全支持。
- 配置操作复杂：NETCONF的XML配置较CLI更冗长，且不同厂商的YANG模型可能导致相同功能的XML结构不同。
- 厂商实现差异：厂商存在私有扩展，高级功能需要额外模块等等。

## Restconf协议

RESTCONF是NETCONF的现代化演进版本，采用 **HTTP/HTTPS + JSON** 进行数据交互，更适合现代自动化运维工具（如Ansible、Python脚本、Postman等）。尽管它比NETCONF更轻量、更易用，但在**跨厂商设备管理**中，仍然面临 **数据模型不一致、接口实现差异、功能支持不统一** 等问题，导致批量管理时难以高效整合。

- 数据模型（YANG）不统一，相同功能的API路径和JSON结构不同
- 接口实现差异：部分高级功能（如Telemetry）需额外License，部分操作（如BGP策略）需使用私有API扩展
- 功能支持不完整：部分厂商仅实现基础RESTCONF功能，缺少高级操作（如事务回滚）。

# MCP对传统网管协议的影响

MCP技术通过引入自然语言指令、LLM等先进技术，实现了对跨厂商网络设备的智能化、自动化批量管理。用户通过自然语言指令向系统下达管理任务，系统通过一系列处理将指令转化为对网络设备的具体操作。

- 提升协议兼容性

MCP通过统一的数据建模和转换机制，能够适配不同厂商对Netconf和Restconf协议的实现差异。它可以将用户的自然语言指令转化为符合不同厂商设备要求的Netconf或Restconf操作，从而在不改变设备原有协议支持的前提下，实现跨厂商设备的统一管理。

- 简化操作流程

MCP通过统一的数据建模和转换机制，能够适配不同厂商对Netconf和Restconf协议的实现差异。它可以将用户的自然语言指令转化为符合不同厂商设备要求的Netconf或Restconf操作，从而在不改变设备原有协议支持的前提下，实现跨厂商设备的统一管理。

- 增强批量管理能力

MCP能够对多个不同厂商的设备同时执行批量操作，通过优化的任务调度和并发控制机制，充分利用Netconf和Restconf协议的优势，提高管理效率。例如，在进行设备配置升级时，MCP可以同时向多个设备发送经过转换和优化的Netconf配置指令，确保操作的一致性和高效性。

# Security Considerations

TODO solution

# Security Considerations

TODO value

# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
