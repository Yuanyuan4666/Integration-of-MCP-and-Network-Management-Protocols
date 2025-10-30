# Network Device Management System

This project consists of a server and client application for managing network devices through MCP (Model Context Protocol) with natural language interface.

## Overview

### Server 
A FastAPI-based MCP server that provides various network device management tools including:
- NETCONF connections and configuration management
- Device command execution
- Interface status monitoring
- ACL configuration
- VRF information querying

### Client
An MCP client that communicates with the server and uses Ollama LLM to process natural language queries into device management commands.

## Prerequisites

### 1. eNSP Installation
- Install VirtualBox
- Install eNSP following: [https://support.huawei.com/enterprise/zh/management-system/ensp-pid-9017384/bulletins](https://support.huawei.com/enterprise/zh/management-system/ensp-pid-9017384/bulletins)
- Obtain router IP addresses from eNSP

### 2. Ollama Installation
- Download from: [https://ollama.com/download/windows](https://ollama.com/download/windows)
- Installation guide: [https://3ms.huawei.com/km/blogs/details/20483926](https://3ms.huawei.com/km/blogs/details/20483926)
- Available models:
  ```bash
  ollama run --insecure http://ollama.rnd.huawei.com/library/qwen3:1.7b
  ollama run --insecure http://ollama.rnd.huawei.com/library/qwen3:4b
