---
config:
  layout: elk
---
flowchart TD
 subgraph MinionLevels["Minion Levels / Skills"]
        L1["Level 1: Basic Intent Filtering"]
        L2["Level 2: Local File Analysis / PDF Parsing"]
        L3["Level 3: OS Tool Control / Screenshot / Automation Scripts"]
        L4["Level 4: Advanced Automation / Multi-step Tasks"]
  end
 subgraph Orchestrator["Orchestrator Control"]
        OS1["Route tasks based on Minion level"]
        OS2["Load balancing & dynamic registry"]
        OS3["Fallback to AI / RAG if no helper available"]
  end
 subgraph Helpers["Server-side Helpers"]
        KHelper[" Knowledge Helper<br>Port 6000+"]
        WHelper[" WebSearch Helper<br>Port 7000+"]
        RHelper[" Report / Content Helper<br>Port 8000+"]
        THelper[" Task / Automation Helper<br>Port 9000+"]
  end
 subgraph Fallback["Fallback / RAG Agent"]
        RAG["LangChain / RAG Agent"]
        O[" Orchestrator LLM / Agent<br>Server-side"]
  end
    U[" User"] -- Request task --> M["🤖 Minion LLM / Agent<br>Client-side"]
    M --> MinionLevels
    M -- WS / async messaging --> O
    O --> Orchestrator & RAG
    L1 -- Can access --> KHelper
    L2 -- Can access --> KHelper & RHelper
    L3 -- Can access --> WHelper & THelper
    L4 -- Can access --> THelper & RHelper
    RHelper --> FS[" Server / Temp File Storage"]
    THelper --> FS
    FS -- File link via WS --> M
    U -- Click link → HTTP GET --> FS
    RAG --> O
