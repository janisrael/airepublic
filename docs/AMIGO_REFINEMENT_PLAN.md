# Amigo 1.0 Refinement Plan
## Refining claude-3.7-sonnet-reasoning-gemma3-12B for Natural Language → Code

---

## Decision Summary

✅ **Base Model:** `claude-3.7-sonnet-reasoning-gemma3-12B` (already in Ollama)

**Why this model is perfect:**
- Already has strong reasoning foundation (saves Stage 1 training)
- Good code generation baseline
- 12B parameters (optimal size)
- Ready for refinement focus: Natural Language → Code

**Current Model Status:**
- Location: Ollama (`claude-3.7-sonnet-reasoning-gemma3-12B:latest`)
- Capabilities: Reasoning ✅, Code generation ✅, NL→Code refinement needed ⏳

---

## Refinement Strategy: From Reasoning-First to Code-First

### Current Behavior:
- Model shows excellent reasoning: "Let me think... step 1, step 2..."
- Can generate code but with reasoning chains
- Good for complex problems but verbose for simple NL→code tasks

### Target Behavior (Cursor-style):
- **Direct NL→Code:** "Create a function to sort users" → code (minimal reasoning)
- **Context-aware:** Understand existing codebase when generating
- **Fast & Precise:** Skip unnecessary reasoning for straightforward tasks
- **Keep Reasoning:** Still reason when problem is complex

---

## Stage-by-Stage Refinement Plan

### Stage 1: Natural Language → Code Direct Conversion ⭐⭐⭐

**Goal:** Teach model to convert natural language directly to code without verbose reasoning chains for straightforward tasks.

**Datasets:**
1. **bigcode/commitpackft** (Primary)
   - Commit messages → code changes
   - Examples: "Add user login function" → actual code
   - Size: ~5-10GB
   - URL: https://huggingface.co/datasets/bigcode/commitpackft

2. **bigcode/humanevalpack** (Primary)
   - HumanEval: NL problem → code solution
   - Clean instruction following
   - Size: ~500MB
   - URL: https://huggingface.co/datasets/bigcode/humanevalpack

3. **bigcode/python_self_instruct** (Secondary)
   - Self-instructed Python tasks
   - NL → Python code
   - Size: ~2-5GB

**Training Approach:**
- **Method:** Supervised Fine-Tuning (SFT) + LoRA
- **LoRA Rank:** 32
- **LoRA Alpha:** 64
- **Learning Rate:** 2e-4
- **Batch Size:** 8
- **Focus:** Train on examples where NL description directly maps to code
- **Key:** Reduce reasoning verbosity for simple tasks, keep it for complex ones

**Expected Outcome:**
- Model generates code directly from NL instructions
- Minimal reasoning chains for straightforward tasks
- Still reasons when problem requires complex thinking

**Duration:** 
- **On A100 80GB:** 3-5 epochs (~2-3 days)
- **On RTX 4050 Mobile (QLoRA):** 3-5 epochs (~5-10 days) ⚠️
  - Slower due to limited VRAM and lower compute
  - QLoRA (4-bit) makes it feasible but slower

---

### Stage 2: Code Context Understanding

**Goal:** Enable model to understand existing codebase context when generating new code.

**Datasets:**
1. **bigcode/commitpackft** (continued - multi-file context)
   - Commits with full file context
   - Understand project structure

2. **bigcode/the-stack-v2** (filtered - multi-file projects)
   - Complete project structures
   - Code with imports and dependencies
   - Size: ~10-20GB filtered subset

**Training Approach:**
- **Method:** SFT with longer context (8192 tokens)
- **Focus:** Multi-file code generation
- **Context:** Include surrounding code when generating

**Expected Outcome:**
- Model understands project structure
- Can generate code that fits existing codebase
- Aware of imports and dependencies

**Duration:** 2-3 epochs (~1-2 days)

---

### Stage 3: Debugging Enhancement

**Goal:** Add debugging capabilities while preserving NL→code skills.

**Datasets:**
1. **microsoft/buglab**
   - Bug fixing scenarios
   - Size: ~500MB-1GB

2. **bigcode/python_bugs**
   - Python-specific debugging
   - Size: ~500MB

**Training Approach:**
- **Method:** SFT + LoRA (preserve Stage 1&2 capabilities)
- **Focus:** Bug identification and fixing
- **Key:** Maintain NL→code capability while adding debugging

**Expected Outcome:**
- Can identify bugs in code
- Can fix bugs from error descriptions
- Maintains direct code generation ability

**Duration:** 2-3 epochs (~1-2 days)

---

### Stage 4: Complex Reasoning (Selective)

**Goal:** Keep complex reasoning for difficult problems while maintaining code-first behavior.

**Dataset:**
- **WizardLM/WizardLM_evol_instruct_V2_196k** (subset - complex coding)
- **reedmayhew/claude-3.7-sonnet-reasoning** (subset - complex problems only)

**Training Approach:**
- **Method:** SFT with filtered examples
- **Filter:** Only train on genuinely complex problems that need reasoning
- **Key:** Model learns when to reason vs when to code directly

**Expected Outcome:**
- Simple tasks: Direct code generation
- Complex tasks: Reasoning then code
- Smart decision-making on when to reason

**Duration:** 1-2 epochs (~1 day)

---

### Stage 5: Integration & Preference Optimization

**Goal:** Balance all capabilities through preference learning.

**Method:** Direct Preference Optimization (DPO)

**Preference Pairs:**
- Direct code generation > Verbose reasoning for simple tasks
- Accurate code > Fast but incorrect code
- Context-aware > Generic solutions
- Complex reasoning when needed > Always reasoning

**Duration:** 1 epoch (~1 day)

---

## Training Environment Setup

### Hardware Requirements:
- **GPU:** 2x A100 80GB (recommended) or 1x A100 80GB (minimum)
- **RAM:** 64GB+ system RAM
- **Storage:** 500GB+ for datasets and checkpoints

### Software Stack:
```bash
# Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (for QLoRA - 4-bit training)
pip install torch transformers datasets accelerate
pip install peft bitsandbytes  # For 4-bit quantization
pip install trl wandb  # For training and logging
pip install huggingface_hub  # For dataset/model management

# Note: bitsandbytes enables 4-bit training to fit 12B model on RTX 4050
```

### Training Script Structure:
```
amigo-training/
├── datasets/
│   ├── download_datasets.py
│   └── prepare_nl_to_code.py
├── training/
│   ├── stage1_nl_to_code.py
│   ├── stage2_context.py
│   ├── stage3_debugging.py
│   ├── stage4_reasoning.py
│   └── stage5_dpo.py
├── config/
│   ├── stage1_config.yaml
│   └── base_config.yaml
└── evaluate/
    └── eval_nl_to_code.py
```

---

## Expected Timeline

**Total Training Time:** 
- **On A100 80GB:** ~7-10 days (depending on dataset sizes)
- **On RTX 4050 Mobile (QLoRA):** ~15-25 days ⚠️
  - Much slower but still feasible with 4-bit quantization
  - Consider cloud training for faster results

- Stage 1 (NL→Code): 2-3 days
- Stage 2 (Context): 1-2 days
- Stage 3 (Debugging): 1-2 days
- Stage 4 (Reasoning): 1 day
- Stage 5 (DPO): 1 day
- Evaluation & Iteration: 1-2 days

---

## Evaluation Metrics

### NL→Code Evaluation:
- **HumanEval:** Code generation from descriptions
- **MBPP:** Python programming problems
- **MultiPL-E:** Multi-language code generation
- **CodeT:** Code generation with tests

### Debugging Evaluation:
- **DebugBench:** Bug fixing capabilities
- **BugLab Test Set:** Real-world bug scenarios

### Reasoning Evaluation:
- **GSM8K:** Mathematical reasoning (keep this capability)
- **Code Reasoning:** Complex coding problems that need reasoning

### Preference Metrics:
- **Directness:** Less reasoning for simple tasks ✅
- **Accuracy:** Code correctness ✅
- **Context Awareness:** Understanding existing codebase ✅

---

## Key Differences from Original Plan

### Changed Priorities:
1. **NL→Code is now Stage 1** (was Stage 3)
   - Cursor-style functionality is primary goal
   
2. **Using existing reasoning model as base** (instead of training from scratch)
   - Saves time and leverages existing capability
   
3. **Selective reasoning** (not always reasoning)
   - Model learns when to reason vs when to code directly

### Benefits:
- Faster path to working model (reasoning already there)
- Better NL→code focus (Cursor-style)
- Maintains reasoning for complex problems
- More efficient training (don't retrain reasoning)

---

## Next Steps

1. ⏳ **Validate Dataset Availability**
   - Check all datasets are accessible
   - Verify sizes and download requirements

2. ⏳ **Set Up Training Environment**
   - Prepare GPU environment
   - Install all dependencies
   - Test with small dataset first

3. ⏳ **Extract Base Model from Ollama**
   - Convert GGUF back to HuggingFace format (if needed)
   - Or download original base model + reasoning weights

4. ⏳ **Prepare Stage 1 Datasets**
   - Download commitpackft
   - Download humanevalpack
   - Format for training

5. ⏳ **Start Stage 1 Training**
   - Begin NL→code fine-tuning
   - Monitor metrics closely

---

**Status:** Planning Complete
**Next Action:** Validate datasets and set up training environment
**Target:** Cursor-style natural language to code generation

