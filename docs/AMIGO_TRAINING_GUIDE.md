# Amigo 1.0 Training Guide
## Step-by-Step Training Setup & Execution

---

## 🎯 My Recommendation

**Start Local → Test → Decide**

1. **Phase 1: Setup & Test (1-2 hours)**
   - Set up training environment
   - Download small test dataset (100-1000 samples)
   - Run 1 epoch test training (~2-4 hours)
   - Verify it works on your RTX 4050

2. **Phase 2: Decision Point**
   - If test works well → Continue locally OR move to cloud
   - If issues → Troubleshoot or use cloud

3. **Phase 3: Full Training**
   - Stage 1: 3-5 epochs with full dataset
   - Monitor and evaluate

---

## Prerequisites Check

### 1. Verify Ollama Model
```bash
# Check if base model is available
ollama list | grep claude-3.7-sonnet-reasoning-gemma3-12B

# If not found, pull it
ollama pull claude-3.7-sonnet-reasoning-gemma3-12B
```

### 2. Check GPU Availability
```bash
# Install NVIDIA driver tools (if not already)
sudo dnf install nvidia-settings

# Verify GPU
nvidia-smi
```

### 3. Python Environment
- Python 3.10-3.12 (not 3.13 for compatibility)
- 62GB RAM ✅
- 312GB free space ✅

---

## Step 1: Create Training Directory Structure

```bash
# Navigate to your workspace
cd /home/swordfish/development/ai-republic-v2

# Create training directory
mkdir -p amigo-training
cd amigo-training

# Create subdirectories
mkdir -p {datasets,training,checkpoints,logs,scripts}
```

**Directory Structure:**
```
amigo-training/
├── datasets/          # Downloaded datasets
├── training/          # Training scripts
├── checkpoints/       # Model checkpoints
├── logs/              # Training logs
└── scripts/           # Utility scripts
```

---

## Step 2: Set Up Python Environment

```bash
cd /home/swordfish/development/ai-republic-v2/amigo-training

# Create virtual environment
python3.12 -m venv venv  # or python3.11
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers>=4.40.0
pip install datasets>=2.16.0
pip install accelerate>=0.25.0
pip install peft>=0.8.0
pip install bitsandbytes>=0.42.0  # For 4-bit quantization (QLoRA)
pip install trl>=0.8.0  # Training library
pip install huggingface_hub  # For dataset/model management
pip install wandb  # Optional: for training visualization
pip install tqdm  # Progress bars
```

**Verify Installation:**
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

---

## Step 3: Get Base Model from HuggingFace

**Option A: Use HuggingFace Model (Recommended)**
```bash
# The Ollama model is based on this HuggingFace model
# We need the actual PyTorch model for training, not GGUF

# Install huggingface-cli
pip install huggingface_hub[cli]

# Login to HuggingFace (optional, for private models)
huggingface-cli login

# Download model (we'll use the base Gemma model or convert from Ollama)
# Actually, we'll use the HuggingFace version of the fine-tuned model
```

**Option B: Extract from Ollama GGUF (More Complex)**
- Ollama uses GGUF format (quantized)
- For training, we need full precision model
- Better to use HuggingFace version

**Recommended Approach:**
Use the HuggingFace model that `claude-3.7-sonnet-reasoning-gemma3-12B` is based on:
- Base: `google/gemma-2-9b-it` or `google/gemma-3-12b-it`
- But the reasoning model is at: `reedmayhew/claude-3.7-sonnet-reasoning-gemma3-12B`

---

## Step 4: Download Test Dataset (Small First)

```bash
cd /home/swordfish/development/ai-republic-v2/amigo-training

# Create dataset download script
cat > scripts/download_test_dataset.py << 'EOF'
from datasets import load_dataset
import json

print("Downloading test dataset: bigcode/humanevalpack (small, ~500MB)")
print("This will take a few minutes...")

# Load HumanEval (small dataset for testing)
dataset = load_dataset("bigcode/humanevalpack", "python")

# Save a small subset for testing (first 100 samples)
test_subset = dataset['test'].select(range(100))
test_subset.to_json("datasets/humaneval_test_100.jsonl", lines=True)

print(f"✅ Saved 100 samples to datasets/humaneval_test_100.jsonl")
print(f"Total samples: {len(test_subset)}")
EOF

python scripts/download_test_dataset.py
```

---

## Step 5: Prepare Dataset Format for Training

We need to format the dataset for NL→Code training:

```bash
cat > scripts/prepare_nl_to_code_dataset.py << 'EOF'
import json
from datasets import load_dataset
from typing import Dict, List

def format_nl_to_code(sample: Dict) -> Dict:
    """
    Format HumanEval sample for NL→Code training.
    Goal: Teach model to generate code directly from natural language.
    """
    # Extract problem description (natural language)
    nl_instruction = sample['prompt']
    
    # Extract solution (code)
    code_solution = sample['canonical_solution']
    
    # Format as instruction-following
    formatted = {
        "instruction": f"Write a Python function that {nl_instruction.strip()}",
        "input": "",  # No additional context needed
        "output": code_solution.strip()
    }
    
    return formatted

def prepare_dataset(input_file: str, output_file: str, max_samples: int = None):
    """Load and format dataset for training"""
    
    # Load JSONL file
    data = []
    with open(input_file, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    if max_samples:
        data = data[:max_samples]
    
    # Format for training
    formatted_data = []
    for sample in data:
        formatted = format_nl_to_code(sample)
        formatted_data.append(formatted)
    
    # Save formatted dataset
    with open(output_file, 'w') as f:
        for item in formatted_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Prepared {len(formatted_data)} samples")
    print(f"✅ Saved to {output_file}")

if __name__ == "__main__":
    # Prepare test dataset
    prepare_dataset(
        "datasets/humaneval_test_100.jsonl",
        "datasets/humaneval_nl_to_code_train.jsonl",
        max_samples=100
    )
    
    print("\nSample formatted entry:")
    with open("datasets/humaneval_nl_to_code_train.jsonl", 'r') as f:
        sample = json.loads(f.readline())
        print(json.dumps(sample, indent=2))
EOF

python scripts/prepare_nl_to_code_dataset.py
```

---

## Step 6: Create Training Script (QLoRA for RTX 4050)

```bash
cat > training/stage1_nl_to_code_qlora.py << 'EOF'
"""
Stage 1 Training: Natural Language → Code
Using QLoRA (4-bit quantization) for RTX 4050 Mobile
"""

import os
import json
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer
import wandb  # Optional

# Configuration
MODEL_NAME = "google/gemma-2-9b-it"  # Start with 9B, fits better on RTX 4050
# Alternative: "reedmayhew/claude-3.7-sonnet-reasoning-gemma3-12B" if available on HF
# Or: "google/gemma-3-12b-it" if you have enough VRAM

DATASET_PATH = "datasets/humaneval_nl_to_code_train.jsonl"
OUTPUT_DIR = "checkpoints/amigo_stage1"
LOGS_DIR = "logs/stage1"

# QLoRA Configuration (for RTX 4050)
BITS_AND_BYTES_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,  # 4-bit quantization
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# LoRA Configuration
LORA_CONFIG = LoraConfig(
    r=32,  # LoRA rank
    lora_alpha=64,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Training Configuration
TRAINING_ARGS = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,  # Start with 3 epochs for test
    per_device_train_batch_size=2,  # Small batch for RTX 4050
    gradient_accumulation_steps=4,  # Effective batch size = 2 * 4 = 8
    learning_rate=2e-4,
    fp16=True,  # Mixed precision
    logging_steps=10,
    save_steps=100,
    save_total_limit=3,
    warmup_steps=50,
    logging_dir=LOGS_DIR,
    report_to="wandb" if os.getenv("WANDB_API_KEY") else None,
    run_name="amigo_stage1_nl_to_code",
    remove_unused_columns=False,
)

def load_and_format_dataset(file_path: str):
    """Load JSONL dataset and format for training"""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    def format_prompt(example):
        """Format instruction and output for training"""
        instruction = example['instruction']
        output = example['output']
        
        # Create prompt in instruction-following format
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
        
        return {"text": prompt}
    
    return [format_prompt(item) for item in data]

def main():
    print("🚀 Starting Amigo Stage 1 Training (NL→Code)")
    print(f"Model: {MODEL_NAME}")
    print(f"Dataset: {DATASET_PATH}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    
    # Load tokenizer
    print("\n📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with 4-bit quantization
    print("📥 Loading model (4-bit QLoRA)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=BITS_AND_BYTES_CONFIG,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Add LoRA adapters
    model = get_peft_model(model, LORA_CONFIG)
    model.print_trainable_parameters()
    
    # Load and format dataset
    print("\n📥 Loading dataset...")
    train_data = load_and_format_dataset(DATASET_PATH)
    print(f"✅ Loaded {len(train_data)} training samples")
    
    # Convert to HuggingFace dataset
    from datasets import Dataset
    train_dataset = Dataset.from_list(train_data)
    
    # Tokenize dataset
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=2048,  # Adjust based on your GPU memory
            padding=False
        )
    
    print("🔤 Tokenizing dataset...")
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    
    # Initialize trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
        args=TRAINING_ARGS,
        max_seq_length=2048,
    )
    
    # Train
    print("\n🏋️ Starting training...")
    trainer.train()
    
    # Save final model
    print("\n💾 Saving model...")
    trainer.save_model()
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print(f"\n✅ Training complete! Model saved to {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Evaluate the model on test samples")
    print("2. Test with Ollama integration")
    print("3. If good, continue with full dataset")

if __name__ == "__main__":
    main()
EOF
```

---

## Step 7: Run Test Training

```bash
cd /home/swordfish/development/ai-republic-v2/amigo-training
source venv/bin/activate

# Run test training (100 samples, 3 epochs)
python training/stage1_nl_to_code_qlora.py
```

**Expected Timeline for Test:**
- 100 samples, 3 epochs
- RTX 4050 Mobile: ~2-4 hours

**Monitor Training:**
```bash
# Watch GPU usage
watch -n 1 nvidia-smi

# Check logs
tail -f logs/stage1/*.log
```

---

## Step 8: Evaluate Test Results

After test training completes:

```bash
# Create evaluation script
cat > scripts/eval_test_model.py << 'EOF'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL_PATH = "checkpoints/amigo_stage1"

# Load model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

# Test prompts
test_prompts = [
    "Write a Python function to sort a list of dictionaries by a specific key",
    "Create a function that calculates the factorial of a number",
    "Write a Python function to find the maximum value in a list"
]

print("🧪 Testing Amigo Stage 1 (NL→Code)\n")

for prompt in test_prompts:
    print(f"Input: {prompt}")
    print("Output:")
    
    # Generate
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        do_sample=True
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response)
    print("\n" + "="*50 + "\n")
EOF

python scripts/eval_test_model.py
```

---

## Step 9: Decision Point

After test training, you have three options:

### Option A: Continue Locally (Budget-Friendly)
- ✅ Free (electricity only)
- ⏱️ Slow: 5-10 days for Stage 1
- 📝 Good for learning

### Option B: Use Cloud GPU (Faster)
- 💰 Cost: ~$25-80 for Stage 1
- ⏱️ Fast: 2-3 days for Stage 1
- 🚀 Professional setup

### Option C: Hybrid
- Test locally ✅
- Full training on cloud 🚀

---

## Step 10: Full Training (If Continuing Locally)

If test worked well, proceed with full dataset:

```bash
# Download full datasets
python scripts/download_full_datasets.py  # Create this script

# Run full training
python training/stage1_nl_to_code_qlora.py
```

**Update dataset path** in training script to use full datasets.

---

## Troubleshooting

### Out of Memory (OOM) Errors
- Reduce `max_length` in tokenizer (2048 → 1024)
- Reduce `per_device_train_batch_size` (2 → 1)
- Increase `gradient_accumulation_steps` (4 → 8)

### Slow Training
- Expected on RTX 4050 Mobile
- Consider cloud GPU for faster results

### Model Not Learning
- Check dataset format
- Verify loss is decreasing
- Increase learning rate or epochs

---

## Next Steps After Stage 1

1. **Evaluate Stage 1**
   - Test NL→Code capability
   - Compare with base model

2. **Stage 2: Code Context**
   - Multi-file code generation
   - Project structure understanding

3. **Convert to Ollama**
   - Convert trained model to GGUF
   - Create Ollama Modelfile
   - Test in Ollama

---

**Ready to start?** Begin with Step 1 and work through sequentially! 🚀





