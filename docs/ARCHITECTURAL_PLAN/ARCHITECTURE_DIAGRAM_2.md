---
config:
  layout: elk
---
flowchart TD
 subgraph LocalTools["Client side Local Tools"]
        LT1["Screen Capture OS Control"]
        LT2["File Parser Report Analyzer"]
  end
 subgraph Registry["Helper Service Registry"]
        R1["Knowledge Helper 6000, 6001..."]
        R2["WebSearch Helper 7000, 7001..."]
        R3["Report Helper 8000, 8001..."]
  end
 subgraph HelpersCluster["Server side Helper Cluster"]
        K1["Knowledge Helper 6000"]
        K2["Knowledge Helper 6001"]
        W1["WebSearch Helper 7000"]
        R1h["Report Helper 8000"]
  end
 subgraph Fallback["LLM fallback"]
        RAG["LangChain RAG Agent"]
        O["Orchestrator LLM Agent"]
  end
    U["User"] -- Request task query --> M["Minion LLM Agent"]
    M -- Direct access run local tools --> LT1 & LT2
    M -- Send request via WS --> O
    O -- Check category via Registry --> HelpersCluster
    HelpersCluster -- Execute task generate file --> FS["Server Storage Temp File"]
    FS -- File ready link --> O
    O -- WS Message file_ready progress errors --> M
    M -- Notify user show progress --> U
    U -- Click link HTTP GET --> FS
    O -- No helper complex query --> RAG
    RAG --> O


