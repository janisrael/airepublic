# Amigo 1.0 Implementation Status

## ✅ Completed

### 1. LoRA Script Generator Updates
- ✅ Added Gemma model support (including `claude-3.7-sonnet-reasoning-gemma3-12b`)
- ✅ Added QLoRA (4-bit quantization) support for RTX 4050
- ✅ Automatic QLoRA detection for large models (>=9B)
- ✅ Optimized NL→Code tokenization format
- ✅ Longer max_length (2048) for code generation
- ✅ RTX 4050-specific optimizations

### 2. Amigo Dataset Service
- ✅ Created `AmigoDatasetService` for HuggingFace datasets
- ✅ Support for Amigo-specific datasets:
  - `bigcode/humanevalpack`
  - `bigcode/commitpackft`
  - `bigcode/python_self_instruct`
  - `WizardLM/WizardCoder-Python-V1.0`
- ✅ Automatic format detection and conversion
- ✅ NL→Code formatting for training

### 3. Documentation
- ✅ `AMIGO_TRAINING_INTEGRATION.md` - Complete guide for training via UI
- ✅ `AMIGO_TRAINING_GUIDE.md` - Manual training guide
- ✅ `AMIGO_HARDWARE_ANALYSIS.md` - Hardware-specific estimates
- ✅ `AMIGO_REFINEMENT_PLAN.md` - Full refinement strategy

---

## 🚧 In Progress / Next Steps

### 1. API Routes (Optional Enhancement)
- [ ] Add `/api/amigo/datasets` endpoint
- [ ] Add `/api/amigo/datasets/download` endpoint
- [ ] Add `/api/amigo/datasets/prepare` endpoint

### 2. Frontend Integration (Optional Enhancement)
- [ ] Add Amigo dataset selector in Training UI
- [ ] Add "Use QLoRA" checkbox
- [ ] Add dataset preview/preparation UI

### 3. Training Execution
- [ ] Test with 100-sample dataset
- [ ] Verify QLoRA works on RTX 4050
- [ ] Run full Stage 1 training

---

## 🎯 How to Use Now

### Option 1: Via Training UI (Recommended)

1. **Start ai-republic:**
   ```bash
   # Backend
   cd ai-refinement-dashboard/backend
   source venv/bin/activate
   python app_server_new.py
   
   # Frontend
   cd ai-refinement-dashboard/frontend
   npm run dev
   ```

2. **Go to Training Page:**
   - Open http://localhost:5173
   - Click "Start Training"

3. **Configure:**
   - Job Name: `amigo-stage1-test`
   - Base Model: `claude-3.7-sonnet-reasoning-gemma3-12b`
   - Training Type: `LoRA`
   - **Use QLoRA:** ✅ (important for RTX 4050)
   - Epochs: `3`
   - Batch Size: `2`
   - Max Length: `2048`

4. **Upload Dataset or Use HuggingFace:**
   - Upload your own JSONL file (instruction, input, output format)
   - OR prepare dataset first using Python script

### Option 2: Direct Python Script

```bash
# Prepare dataset
cd ai-refinement-dashboard/backend
source venv/bin/activate
python -c "
from services.amigo_dataset_service import get_amigo_dataset_service
service = get_amigo_dataset_service()

# Download and prepare
result = service.prepare_training_data(
    ['bigcode/humanevalpack'],
    max_samples_per_dataset=100,
    test_split=0.1
)
print(result)
"
```

Then use the generated `amigo_train_*.jsonl` and `amigo_val_*.jsonl` files in Training UI.

---

## 🔧 Technical Details

### QLoRA Configuration
- **4-bit quantization:** Enabled automatically for models >=9B
- **Batch size:** Auto-adjusted to 2 for RTX 4050
- **Gradient accumulation:** 4 (effective batch = 8)
- **Mixed precision:** FP16 enabled

### Model Mapping
- `claude-3.7-sonnet-reasoning-gemma3-12b` → `google/gemma-3-12b-it`
- Automatically mapped in `LoRAScriptGenerator`

### Dataset Format
```json
{
  "instruction": "Write a Python function that sorts a list",
  "input": "",
  "output": "def sort_list(lst):\n    return sorted(lst)"
}
```

---

## 📊 Expected Timeline

**Test Run (100 samples, 3 epochs):**
- Dataset download: ~5-10 minutes
- Dataset preparation: ~2-5 minutes
- Training: ~2-4 hours (RTX 4050 with QLoRA)
- **Total: ~3-5 hours**

**Full Training (full dataset, 5 epochs):**
- Dataset download: ~1-2 hours
- Dataset preparation: ~30-60 minutes
- Training: ~5-10 days (RTX 4050 with QLoRA)
- **Total: ~5-10 days**

---

## 🎉 Ready to Train!

The system is now ready to train Amigo 1.0! Start with a small test run to verify everything works, then proceed with full training.

**Next:** Run a 100-sample test training via the Training UI!





