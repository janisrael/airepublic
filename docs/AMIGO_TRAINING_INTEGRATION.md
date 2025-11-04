# Amigo Training Integration Guide
## Using ai-republic to Train Amigo 1.0

---

## Overview

You can now train Amigo 1.0 directly through the ai-republic Training page! This integrates seamlessly with the existing system.

---

## Quick Start: Train Amigo via UI

### Step 1: Access Training Page

1. Go to **Training** page in ai-republic dashboard
2. Click **"Start Training"** button

### Step 2: Configure Amigo Training

**Basic Settings:**
- **Job Name:** `amigo-stage1-nl-to-code`
- **Base Model:** `claude-3.7-sonnet-reasoning-gemma3-12b` (or select from dropdown)
- **Training Type:** `LoRA`

**LoRA Configuration:**
- **LoRA Rank:** `32`
- **LoRA Alpha:** `64`
- **LoRA Dropout:** `0.05`
- **Use QLoRA:** ✅ **Check this** (for RTX 4050)

**Training Parameters:**
- **Epochs:** `3` (for test) or `5` (for full training)
- **Batch Size:** `2` (auto-adjusted for QLoRA)
- **Learning Rate:** `0.0002`
- **Max Length:** `2048` (for code generation)

**Dataset:**
- You can upload your own dataset OR
- Use HuggingFace dataset IDs (see below)

### Step 3: Prepare HuggingFace Datasets (Optional)

**Option A: Download via Backend API**
```bash
# Start backend
cd ai-refinement-dashboard/backend
source venv/bin/activate
python -c "
from services.amigo_dataset_service import get_amigo_dataset_service
service = get_amigo_dataset_service()

# Download test dataset (100 samples)
result = service.download_dataset('bigcode/humanevalpack', split='python', max_samples=100)
print(result)
"
```

**Option B: Download via Python Script**
```bash
cd ai-refinement-dashboard
python -m backend.services.amigo_dataset_service
```

### Step 4: Start Training

1. Click **"Start Training"**
2. Monitor progress in real-time
3. Check logs and metrics

---

## Using HuggingFace Datasets Directly

The system now supports direct HuggingFace dataset IDs:

**Amigo-Recommended Datasets:**
1. `bigcode/humanevalpack` - HumanEval (small, ~500MB)
2. `bigcode/commitpackft` - Commit messages → code (large, ~5-10GB)
3. `bigcode/python_self_instruct` - Python self-instruct (~2-5GB)

**In Training UI:**
- Dataset field accepts HuggingFace IDs
- System automatically downloads and formats
- Supports dataset splits (e.g., `bigcode/humanevalpack:python`)

---

## Backend API Endpoints

### List Available Amigo Datasets

```bash
GET /api/amigo/datasets
```

Response:
```json
{
  "success": true,
  "datasets": [
    {
      "id": "bigcode/humanevalpack",
      "name": "HumanEval Pack",
      "description": "HumanEval with natural language problem descriptions → code solutions",
      "size": "~500MB"
    }
  ]
}
```

### Download Dataset

```bash
POST /api/amigo/datasets/download
{
  "dataset_id": "bigcode/humanevalpack",
  "split": "python",
  "max_samples": 100
}
```

### Prepare Training Data

```bash
POST /api/amigo/datasets/prepare
{
  "dataset_ids": ["bigcode/humanevalpack"],
  "max_samples_per_dataset": 100,
  "test_split": 0.1
}
```

---

## Training Configuration for RTX 4050

**Automatic QLoRA Detection:**
- System detects if model is >=9B parameters
- Automatically enables QLoRA (4-bit quantization)
- Adjusts batch size for your GPU

**Manual QLoRA:**
- Check **"Use QLoRA"** in training config
- Forces 4-bit quantization even for smaller models

**Optimized Settings:**
- Batch Size: 2 (with gradient accumulation = 4, effective batch = 8)
- Max Length: 2048 tokens (for code)
- FP16: Enabled (mixed precision)

---

## Monitoring Training

### Real-Time Progress
- Training page shows live progress
- Step-by-step updates
- Loss metrics

### Check Logs
```bash
# Backend logs
tail -f ai-refinement-dashboard/backend/logs/training.log

# Training output
cat training_data/job_{job_id}/output.log
```

### GPU Usage
```bash
watch -n 1 nvidia-smi
```

---

## Training Stages

### Stage 1: NL→Code (Current)
- **Dataset:** bigcode/humanevalpack (test) or bigcode/commitpackft (full)
- **Epochs:** 3-5
- **Time:** 2-4 hours (test) or 5-10 days (full on RTX 4050)

### Future Stages (Coming Soon)
- Stage 2: Code Context Understanding
- Stage 3: Debugging Enhancement
- Stage 4: Complex Reasoning
- Stage 5: DPO Refinement

---

## Troubleshooting

### Out of Memory
- Reduce batch size to 1
- Reduce max_length to 1024
- Enable QLoRA if not already enabled

### Slow Training
- Expected on RTX 4050 Mobile
- Consider cloud GPU for faster results
- Test with small dataset first (100 samples)

### Dataset Download Fails
- Check internet connection
- Verify HuggingFace dataset ID
- Try smaller dataset first

---

## Example: Complete Training Flow

1. **Start Backend:**
   ```bash
   cd ai-refinement-dashboard/backend
   source venv/bin/activate
   python app_server_new.py
   ```

2. **Start Frontend:**
   ```bash
   cd ai-refinement-dashboard/frontend
   npm run dev
   ```

3. **Access Training Page:**
   - Open http://localhost:5173
   - Go to Training page
   - Click "Start Training"

4. **Configure:**
   - Job Name: `amigo-test-100`
   - Base Model: `claude-3.7-sonnet-reasoning-gemma3-12b`
   - Dataset: `bigcode/humanevalpack:python` (or upload your own)
   - Max Samples: `100` (for test)
   - Use QLoRA: ✅
   - Epochs: `3`

5. **Start Training:**
   - Click "Start Training"
   - Monitor progress
   - Wait for completion (~2-4 hours for 100 samples)

6. **Test Model:**
   - Training creates model in `models/amigo-test-100_lora/`
   - Can be loaded into Ollama for testing

---

## Next Steps

After Stage 1 training completes:
1. Test the model on NL→Code tasks
2. Evaluate quality
3. If good, proceed with full dataset training
4. Continue to Stage 2 (Code Context)

---

**Ready to train Amigo?** Start with a 100-sample test run! 🚀





