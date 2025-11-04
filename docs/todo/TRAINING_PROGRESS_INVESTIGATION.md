# Training Progress Investigation Report

**Date**: 2025-01-XX  
**Issue**: Training overlay shows progress stuck at 0% during RAG training

## Problem Summary

The training overlay is polling correctly (`/api/v2/training-jobs/{job_id}`), but the `progress` field remains at 0 throughout the entire training process. The frontend expects `progress` (0-100) to update step-by-step.

## Root Cause Analysis

### 1. Frontend Expectations

**File**: `frontend/src/components/MinionTrainingCard.vue`

- **Polling**: Line 656-710 - `pollTrainingStatus()` polls `/api/v2/training-jobs/{job_id}` every few seconds
- **Progress Calculation**: Line 723 - Uses `job.progress` to calculate step index:
  ```javascript
  const stepIndex = Math.floor((job.progress || 0) / (100 / this.trainingSteps.length))
  ```
- **Step Updates**: Lines 727-736 - Marks steps as completed/active based on `stepIndex`

**Expected Flow**:
- Progress 0-11% → Step 0 (Capture Before Metrics)
- Progress 11-22% → Step 1 (Dataset Loading & Refinement)
- Progress 22-33% → Step 2 (Knowledge Base Creation)
- ... and so on for 9 steps

### 2. Backend API Response

**File**: `backend/app/routes/training_routes_v2.py`

- **Endpoint**: Line 537 - `GET /api/v2/training-jobs/<int:job_id>`
- **Serialization**: Line 37 - `_job_to_dict()` includes `'progress': job.progress`
- **Model Field**: `backend/model/training.py` Line 54 - `progress = Column(Float, default=0.0, nullable=False)`

✅ The API correctly returns the `progress` field from the database.

### 3. The Missing Link

**File**: `backend/services/external_training/rag/rag_service.py`

**Problem**: The RAG training service **never updates the `progress` field** during training.

- Lines 83-165: Training steps are executed sequentially
- **All websocket progress updates are commented out** (Lines 83, 94, 104, 113, 118, 133, 139, 144, 150)
- No database updates to `job.progress` field

**Training Steps** (9 total):
1. Step 0: Capture Before Metrics (~11%)
2. Step 1: Dataset Loading & Refinement (~22%)
3. Step 2: Knowledge Base Creation (~33%)
4. Step 3: Embedding Creation (~44%)
5. Step 4: Minion Update (~56%)
6. Step 5: Training Validation (~67%)
7. Step 6: Testing (~78%)
8. Step 7: Capture After Metrics (~89%)
9. Step 8: Calculate Improvements (~100%)

### 4. Training Service Methods

**File**: `backend/app/services/training_service.py`

- **Line 64**: `update_training_job_status()` - Only updates `status`, not `progress`
- **Missing**: No method to update `progress` field

## Solution Required

### Phase 1: Add Progress Update Method to TrainingService

Add a new method to `backend/app/services/training_service.py`:

```python
def update_training_job_progress(self, job_id: int, progress: float, current_step: Optional[int] = None) -> bool:
    """Update training job progress (0.0 to 100.0)"""
    try:
        job = self.get_training_job(job_id)
        if job:
            job.progress = max(0.0, min(100.0, progress))  # Clamp to 0-100
            if current_step is not None:
                # Optionally store current step for better tracking
                pass
            job.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        return False
    except Exception as e:
        self.session.rollback()
        raise e
```

### Phase 2: Update RAG Training Service

Modify `backend/services/external_training/rag/rag_service.py`:

1. **Import TrainingService** at the top
2. **Create instance** in `train_minion_with_rag()` method
3. **Update progress** after each step:

```python
# After Step 0
training_service.update_training_job_progress(job_id, 11.1)

# After Step 1
training_service.update_training_job_progress(job_id, 22.2)

# After Step 2
training_service.update_training_job_progress(job_id, 33.3)

# ... and so on for each step
```

**Alternative Approach**: Calculate progress dynamically:
- Total steps: 9
- Progress per step: 100 / 9 = ~11.11%
- Update: `progress = (step_number + 1) * (100 / 9)`

### Phase 3: Verify Frontend Step Mapping

Ensure the frontend's `trainingSteps` array matches the backend steps:

**File**: `frontend/src/components/MinionTrainingCard.vue`

Check that the step names match:
1. "Capture Before Metrics"
2. "Dataset Loading & Refinement"
3. "Knowledge Base Creation"
4. "Embedding Creation"
5. "Minion Update"
6. "Training Validation"
7. "Testing"
8. "Capture After Metrics"
9. "Calculate Improvements"

## Implementation Notes

1. **Thread Safety**: Since training runs in a background thread (`_run_training_in_background`), ensure database updates are thread-safe
2. **Transaction Isolation**: Each progress update should commit immediately so polling can see updates
3. **Error Handling**: If progress update fails, log error but don't stop training
4. **Performance**: Progress updates are lightweight, but avoid excessive commits

## Testing Checklist

- [ ] Progress starts at 0 when training begins
- [ ] Progress updates incrementally as each step completes
- [ ] Frontend overlay shows correct step as active
- [ ] Completed steps show checkmark
- [ ] Progress reaches 100% when training completes
- [ ] Progress persists if page is refreshed
- [ ] Failed training shows appropriate progress state

## Related Files

- `backend/app/services/training_service.py` - Add progress update method
- `backend/services/external_training/rag/rag_service.py` - Update progress during training
- `backend/app/routes/training_routes_v2.py` - Already returns progress correctly
- `frontend/src/components/MinionTrainingCard.vue` - Already handles progress correctly
- `backend/model/training.py` - Progress field exists and is correct

## Status

✅ **Investigation Complete** - Ready for implementation

