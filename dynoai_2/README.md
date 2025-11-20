# DynoAI 2 with DeepCode Integration

This project demonstrates how to integrate DeepCode capabilities into DynoAI 2.

## Prerequisites

1. **Install DeepCode**:
   Ensure the `deepcode-hku` package is installed. If you are in the DeepCode repository root:
   ```bash
   pip install -e .
   ```

2. **Configuration**:
   DeepCode requires configuration files (`mcp_agent.config.yaml` and `mcp_agent.secrets.yaml`).
   Copy them from the DeepCode root to this directory or ensure they are in the working directory when running the script.

## Structure

- `integration.py`: The main integration script that initializes the DeepCode agent and triggers code generation.
- `requirements.txt`: Dependencies.

## Usage

Run the integration demo:

```bash
python integration.py
```

This will trigger the DeepCode agent to generate a feature (e.g., a login module) using the `execute_chat_based_planning_pipeline`.

