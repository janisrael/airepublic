# Amigo Dataset Download Status

## Current Status

### ✅ Successfully Downloaded

1. **bigcode/humanevalpack (python)** - ✅ Downloaded
   - **File:** `training_data/amigo_datasets/bigcode-humanevalpack_python.jsonl`
   - **Samples:** 164
   - **Size:** ~500MB (when full, but only Python split downloaded)
   - **Status:** Ready for training

---

## ❌ Datasets Not Available

### Issue: Deprecated Dataset Scripts

HuggingFace has deprecated dataset loading scripts. These datasets use old scripts that are no longer supported:

1. **bigcode/commitpackft** ❌
   - Error: "Dataset scripts are no longer supported, but found commitpackft.py"
   - **Alternative:** Need to find updated dataset or download manually

2. **WizardLM/WizardCoder-Python-V1.0** ❌
   - Error: Dataset doesn't exist or uses deprecated scripts
   - **Alternative:** Try other WizardCoder datasets

3. **bigcode/python_self_instruct** ❌
   - Error: Dataset doesn't exist on the Hub
   - **Alternative:** Use other Python instruction datasets

---

## 📋 Alternative Datasets to Try

### Working NL→Code Datasets (Modern Format):

1. **bigcode/the-stack-v2** (if we filter to Python/JavaScript)
   - Massive dataset, but can filter to specific languages
   - Uses Parquet format (modern, works)

2. **bigcode/starcoderdata**
   - StarCoder dataset in modern format
   - High-quality code examples

3. **Open-Orca/OpenOrca**
   - General instruction following
   - Includes coding examples

4. **microsoft/buglab**
   - Bug fixing scenarios
   - Modern format

5. **HuggingFaceH4/code_alpaca** (if exists)
   - Code instruction dataset

---

## 🎯 Current Training Capacity

With what we have:

**Available:**
- ✅ `bigcode/humanevalpack` (164 samples - Python only)
  - Small but high-quality
  - Good for initial testing/validation

**Missing:**
- ❌ Large-scale training datasets (5-10GB range)
- ❌ Commit message → code datasets
- ❌ Large Python instruction datasets

---

## 🔄 Next Steps

### Option 1: Use What We Have (Limited Training)
- Train with `humanevalpack` only
- Good for testing the training pipeline
- Limited dataset size may not provide full refinement

### Option 2: Find Alternative Datasets
- Search HuggingFace for datasets in Parquet format
- Focus on datasets created after 2024 (modern format)
- Download manually if needed

### Option 3: Download Alternative Primary Datasets
- Try `bigcode/starcoderdata` (if available in modern format)
- Try `Open-Orca/OpenOrca` (general coding)
- Filter `the-stack-v2` to Python subset

### Option 4: Manual Dataset Preparation
- Create custom dataset from GitHub commits (manual process)
- Use existing code repositories to create NL→Code pairs

---

## 💡 Recommendation

1. **Start with what we have:** Use `humanevalpack` for initial testing
2. **Search for alternatives:** Look for modern format datasets on HuggingFace
3. **Consider manual collection:** If critical datasets are unavailable

---

**Last Updated:** Current session  
**Status:** Partial download - 1 of 3 datasets successful



