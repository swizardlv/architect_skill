# Component Model
```mermaid
graph TD
    CLI["CLI Gateway"] --> FSM["FSM Orchestrator"]
    FSM --> Port["Storage Port"]
    Port --> Adapter["Memory/DB Adapter"]
```
