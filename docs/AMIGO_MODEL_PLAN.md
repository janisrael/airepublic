# Amigo 1.0 Model Creation Plan

## Overview
**Amigo 1.0** - A specialized AI model for debugging, reasoning, and coding tasks.

**Model Purpose:**
- **Natural Language to Code:** Direct conversion from descriptions to code (Cursor-style)
- **Debugging:** Identify and fix bugs in code
- **Reasoning:** Complex logical reasoning when needed
- **Coding:** Code generation, refactoring, and optimization

**Target:** Cursor AI-like capabilities - understand natural language and generate code directly

**Target Base Model Size:** 12B+ parameters (for sufficient reasoning capability)

---

## Phase 1: Dataset Research & Selection

### 1.1 HuggingFace Datasets for Debugging

#### Primary Debugging Datasets:
1. **bigcode/the-stack-v2** (300GB+)
   - Large code dataset with bug patterns
   - URL: https://huggingface.co/datasets/bigcode/the-stack-v2
   - Use: Code understanding, bug patterns

2. **bigcode/starcoderdata**
   - StarCoder dataset with code examples
   - URL: https://huggingface.co/datasets/bigcode/starcoderdata

3. **microsoft/buglab**
   - BugLab: Learning to Debug Using Bug Lab
   - Focused on bug fixing scenarios
   - URL: https://huggingface.co/datasets/microsoft/buglab

4. **facebook/instruct_human_eval**
   - HumanEval with instruction following
   - Code debugging tasks
   - URL: https://huggingface.co/datasets/facebook/instruct_human_eval

5. **Xwin-Lee/ShareGPT80**
   - Contains debugging conversations
   - Multi-turn debugging scenarios

#### Secondary Debugging Sources:
- **bigcode/python_bugs**
- **deepmind/code_contests** (with buggy solutions)
- **THUDM/codegeex2** (code generation with error handling)

---

### 1.2 HuggingFace Datasets for Reasoning

#### Primary Reasoning Datasets:
1. **allenai/orca_math_word_problems_200k**
   - Mathematical reasoning problems
   - Step-by-step reasoning
   - URL: https://huggingface.co/datasets/allenai/orca_math_word_problems_200k

2. **meta-math/MetaMathQA**
   - Mathematical reasoning with explanations
   - URL: https://huggingface.co/datasets/meta-math/MetaMathQA

3. **HuggingFaceH4/orca_dpo_pairs**
   - Direct preference optimization pairs
   - Reasoning chains

4. **WizardLM/WizardLM_evol_instruct_V2_196k**
   - Complex reasoning tasks
   - Multi-step problem solving
   - URL: https://huggingface.co/datasets/WizardLM/WizardLM_evol_instruct_V2_196k

5. **garage-bAInd/Open-Platypus**
   - STEM reasoning problems
   - Scientific reasoning

6. **penske/Claude-3.7-Sonnet-Reasoning**
   - Claude reasoning dataset (similar to model we just found!)
   - High-quality reasoning chains
   - URL: https://huggingface.co/datasets/penske/Claude-3.7-Sonnet-Reasoning

7. **reedmayhew/claude-3.7-sonnet-reasoning** (DATASET USED FOR THE MODEL WE JUST FOUND)
   - The exact reasoning dataset used to train the Claude 3.7 reasoning model
   - URL: https://huggingface.co/datasets/reedmayhew/claude-3.7-sonnet-reasoning
   - This is PERFECT for Amigo!

#### Secondary Reasoning Sources:
- **ai2/arc** (Abstract Reasoning Corpus)
- **google/BIG-bench** (reasoning tasks)
- **hellaswag** (commonsense reasoning)
- **commonsenseqa** (commonsense reasoning)

---

### 1.3 HuggingFace Datasets for Coding

#### Primary Coding Datasets:
1. **bigcode/the-stack-v2**
   - Massive code dataset (600+ programming languages)
   - Clean, deduplicated code
   - URL: https://huggingface.co/datasets/bigcode/the-stack-v2

2. **bigcode/starcoderdata**
   - StarCoder training data
   - High-quality code samples

3. **bigcode/python_bugs**
   - Python bug fixing examples
   - URL: https://huggingface.co/datasets/bigcode/python_bugs

4. **bigcode/humanevalpack**
   - HumanEval with multiple languages
   - Code generation tasks

5. **bigcode/commitpackft** ⭐ EXCELLENT FOR NL→CODE
   - Commit message and code changes
   - Natural language descriptions → code implementations
   - Perfect for Cursor-style training
   - URL: https://huggingface.co/datasets/bigcode/commitpackft

6. **TheBloke/CodeLlama-Instruct**
   - Instruction-tuned code datasets
   - Code completion, generation, explanation

7. **bigcode/python_self_instruct** ⭐ EXCELLENT FOR NL→CODE
   - Python self-instruction dataset
   - Natural language instructions → code
   - URL: https://huggingface.co/datasets/bigcode/python_self_instruct

### 1.5 Natural Language to Code Datasets (Cursor-style)

#### Primary NL→Code Datasets:
1. **bigcode/commitpackft** ⭐⭐⭐ BEST FOR CURSOR-STYLE
   - Commit messages → code changes
   - "Add feature X" → actual code implementation
   - Real-world natural language descriptions
   - URL: https://huggingface.co/datasets/bigcode/commitpackft

2. **bigcode/humanevalpack**
   - HumanEval with natural language problem descriptions
   - NL instruction → complete code solution
   - URL: https://huggingface.co/datasets/bigcode/humanevalpack

3. **bigcode/python_self_instruct**
   - Self-instructed Python tasks
   - NL description → Python code
   - URL: https://huggingface.co/datasets/bigcode/python_self_instruct

4. **WizardLM/WizardCoder-Python-V1.0**
   - WizardCoder Python dataset
   - High-quality NL→code examples
   - URL: https://huggingface.co/datasets/WizardLM/WizardCoder-Python-V1.0

5. **bigcode/starcoderdata** (filtered)
   - Code with docstrings/comments
   - Comments describe what code does (reverse: NL→code)

6. **xlang-ai/xCodeEval**
   - Multi-language code evaluation
   - NL tasks → code solutions
   - URL: https://huggingface.co/datasets/xlang-ai/xCodeEval

7. **bigcode/RepoMapping-v2**
   - Repository-level code understanding
   - Multi-file code generation from descriptions

---

### 1.4 Combined/Instruction Datasets

1. **Open-Orca/OpenOrca**
   - General instruction following with reasoning
   - Multi-domain capabilities
   - URL: https://huggingface.co/datasets/Open-Orca/OpenOrca

2. **garage-bAInd/Open-Platypus**
   - STEM + coding combined
   - Technical reasoning

3. **WizardLM/WizardLM_evol_instruct_V2_196k**
   - Evolved instructions for complex tasks
   - Includes coding and reasoning

---

## Phase 2: Recommended Dataset Combination for Amigo 1.0

### Core Training Dataset Mix:

#### Tier 1: Essential (Must Have) - NL→Code Focus

1. **bigcode/commitpackft** ⭐⭐⭐ HIGHEST PRIORITY FOR CURSOR-STYLE
   - Natural language commit messages → code changes
   - Real-world examples: "Add user authentication" → actual code
   - Perfect for teaching direct NL→code conversion
   - ~5-10GB
   - URL: https://huggingface.co/datasets/bigcode/commitpackft

2. **bigcode/humanevalpack** ⭐⭐
   - HumanEval: NL problem descriptions → code solutions
   - High-quality instruction following
   - ~500MB
   - URL: https://huggingface.co/datasets/bigcode/humanevalpack

3. **bigcode/python_self_instruct** ⭐⭐
   - Python self-instruction dataset
   - NL descriptions → Python implementations
   - ~2-5GB
   - URL: https://huggingface.co/datasets/bigcode/python_self_instruct

4. **WizardLM/WizardCoder-Python-V1.0** ⭐
   - WizardCoder Python dataset
   - Excellent NL→code examples
   - ~2-5GB

#### Tier 2: Code Context & Understanding
5. **bigcode/the-stack-v2** (filtered subset)
   - Code understanding base
   - Use 10-20GB subset focused on:
     - Python, JavaScript, TypeScript
     - Code with comprehensive comments/docstrings
     - Multi-file projects

6. **microsoft/buglab**
   - Core debugging capability
   - Bug fixing patterns
   - ~500MB-1GB

7. **bigcode/python_bugs**
   - Python-specific debugging
   - Error handling patterns
   - ~500MB

#### Tier 2: Important (Highly Recommended)
5. **WizardLM/WizardLM_evol_instruct_V2_196k**
   - Complex reasoning capability
   - Multi-step problem solving
   - ~5-10GB

6. **allenai/orca_math_word_problems_200k**
   - Mathematical reasoning
   - Step-by-step thinking
   - ~500MB

7. **bigcode/humanevalpack**
   - Code generation evaluation
   - Multi-language support
   - ~100MB

#### Tier 3: Enhancement (Optional but beneficial)
8. **Open-Orca/OpenOrca** (subset)
   - General instruction following
   - ~5GB filtered subset

9. **garage-bAInd/Open-Platypus**
   - STEM reasoning
   - Technical problem solving

---

## Phase 3: Base Model Selection

### ⭐ DECISION: Use `claude-3.7-sonnet-reasoning-gemma3-12B` as Base for Amigo 1.0

**Why this model is PERFECT as base:**

✅ **Already has reasoning foundation**
- Trained on reedmayhew/claude-3.7-sonnet-reasoning dataset
- Shows excellent step-by-step reasoning capability
- Can explain code generation process

✅ **Good code generation baseline**
- Based on Gemma 3 12B (strong coding model)
- Can generate clean, working Python code
- Understands code structure and best practices

✅ **Optimal size**
- 12B parameters (perfect for reasoning + coding)
- Not too small (maintains capability)
- Not too large (manageable for fine-tuning)

✅ **Ready to refine**
- Already instruction-tuned
- Has reasoning chains built-in
- Just needs natural language → code refinement

**Model Location:** Available in Ollama as `claude-3.7-sonnet-reasoning-gemma3-12B:latest`

### Alternative Base Models (if we decide to start fresh):

1. **google/gemma-3-12b-it**
   - Original base model
   - Would need full reasoning + coding training
   - URL: https://huggingface.co/google/gemma-3-12b-it

2. **meta-llama/Llama-3.1-8B-Instruct**
   - 8B parameters (lighter)
   - Strong reasoning
   - Good alternative if 12B too large

3. **Qwen/Qwen2.5-14B-Instruct**
   - 14B parameters
   - Excellent coding capability
   - Strong reasoning

### Final Recommendation: **claude-3.7-sonnet-reasoning-gemma3-12B** ⭐
- Already has reasoning foundation (saves training time)
- Based on proven Gemma 3 12B architecture
- Just needs natural language → code refinement
- Faster path to Amigo 1.0 completion

---

## Phase 4: Training Strategy

### Multi-Stage Fine-Tuning Approach:

#### Stage 1: Natural Language to Code (HIGHEST PRIORITY - Cursor-like)
- **Dataset:** 
  - bigcode/commitpackft (code descriptions → code)
  - bigcode/humanevalpack (NL instructions → code)
  - microsoft/DialoGPT-code (conversational coding)
  - bigcode/python_self_instruct (instruction following)
- **Purpose:** Transform natural language descriptions directly into code
- **Focus:** Cursor auto-settings style: "add a function to sort users by age" → code
- **Method:** Supervised Fine-Tuning (SFT) with LoRA
- **Duration:** 3-5 epochs
- **Key:** Teach model to skip reasoning chains for direct code generation when appropriate

#### Stage 2: Code Context Understanding
- **Dataset:** 
  - bigcode/the-stack-v2 (filtered - multi-file projects)
  - bigcode/commitpackft (code changes with context)
- **Purpose:** Understand codebase context, multi-file code generation
- **Method:** SFT
- **Duration:** 2-3 epochs

#### Stage 3: Debugging Capability
- **Dataset:** microsoft/buglab + bigcode/python_bugs
- **Purpose:** Add debugging and bug fixing skills
- **Method:** SFT + LoRA (to preserve NL→code capability)
- **Duration:** 2-3 epochs

#### Stage 4: Complex Reasoning (when needed)
- **Dataset:** WizardLM/WizardLM_evol_instruct_V2_196k (subset - complex coding tasks)
- **Purpose:** Handle complex multi-step coding problems
- **Method:** SFT
- **Duration:** 1-2 epochs

#### Stage 5: Integration & Refinement
- **Dataset:** Combined evaluation on all tasks
- **Purpose:** Balance NL→code, debugging, and reasoning
- **Method:** DPO (Direct Preference Optimization)
- **Duration:** 1 epoch

---

## Phase 5: Model Architecture Decisions

### Training Configuration:
- **Method:** LoRA + SFT hybrid approach
- **LoRA Rank:** 16-32
- **LoRA Alpha:** 32-64
- **Target Modules:** All linear layers
- **Learning Rate:** 1e-4 to 5e-4
- **Batch Size:** 4-8 (depending on GPU memory)
- **Sequence Length:** 8192 tokens

### Hardware Requirements:
- **Minimum:** 1x A100 40GB or 2x A6000 48GB
- **Recommended:** 2x A100 80GB
- **Training Time Estimate:** 3-5 days (depending on dataset size)

---

## Phase 6: Upload to HuggingFace

### Preparation:
1. Model evaluation on benchmarks:
   - HumanEval (coding)
   - GSM8K (mathematical reasoning)
   - MBPP (Python programming)
   - DebugBench (if available)

2. Model card creation:
   - Detailed description of capabilities
   - Training methodology
   - Dataset citations
   - Usage examples
   - Limitations

3. License selection:
   - Apache 2.0 (permissive)
   - Or custom license

4. Upload process:
```bash
# Install huggingface_hub
pip install huggingface_hub

# Login
huggingface-cli login

# Upload model
huggingface-cli upload swordfish/amigo-1.0 ./model_output \
    --repo-type model \
    --include "*.bin,*.safetensors,*.json,*.txt,*.md"
```

---

## Phase 7: Integration with ai-republic System

### External LLM Integration:
1. Add Amigo 1.0 to external_api_models table
2. Create API wrapper for HuggingFace Inference API
3. Or use local Ollama if model is quantized to GGUF
4. Add to provider list in external_api_service.py

---

## Next Steps

1. ✅ Research datasets (THIS DOCUMENT)
2. ⏳ Validate dataset availability and download sizes
3. ⏳ Select final base model
4. ⏳ Prepare training environment
5. ⏳ Download and prepare datasets
6. ⏳ Start Stage 1 training (reasoning)
7. ⏳ Evaluate and iterate
8. ⏳ Continue with remaining stages
9. ⏳ Final evaluation and refinement
10. ⏳ Upload to HuggingFace

---

## References

### Key Datasets:
- https://huggingface.co/datasets/reedmayhew/claude-3.7-sonnet-reasoning
- https://huggingface.co/datasets/microsoft/buglab
- https://huggingface.co/datasets/bigcode/the-stack-v2
- https://huggingface.co/datasets/WizardLM/WizardLM_evol_instruct_V2_196k
- https://huggingface.co/models/google/gemma-3-12b-it

### Related Models to Study:
- reedmayhew/claude-3.7-sonnet-reasoning-gemma3-12B (proven approach)
- Qwen/Qwen2.5-Coder series (coding focus)
- DeepSeek-Coder (coding capabilities)

---

**Created:** 2025-10-31
**Status:** Research Phase
**Target Completion:** TBD

