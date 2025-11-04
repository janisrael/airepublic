# Pending Job Display Issue Investigation

**Date**: 2025-01-XX  
**Issue**: Completed training jobs still show "Pending Job" UI with View/Train/Delete buttons instead of "View History" and "Upgrade Again"

## Problem Summary

After a training job completes, the UI still displays it as a "Pending Job" with the wrong action buttons.

## Root Cause Analysis

### File: `frontend/src/components/MinionTrainingCard.vue`

**Line 274**: Filter logic for pending jobs
```javascript
const candidates = (this.pendingJobs || []).filter(job => 
    job.minionId === this.minion.id && 
    job.status !== 'COMPLETED' && 
    job.status !== 'FAILED'
);
```

**Issues Identified**:

1. **Line 283**: Attempts to reassign `const` variable
   ```javascript
   candidates = candidates.filter(j => new Date(j.created_at) > new Date(latestCreated));
   ```
   - `candidates` is declared as `const` on line 274
   - This will cause a runtime error or silently fail
   - The filter never executes, so completed jobs aren't filtered out

2. **Status Matching**: Case sensitivity issue possible
   - Filter checks for `'COMPLETED'` and `'FAILED'` (uppercase)
   - If API returns `'completed'` or `'Completed'`, filter won't work

3. **Logic Flow**: The matching logic on lines 291-295 might incorrectly match completed jobs
   ```javascript
   const latestId = this.minion?.latest_training?.id;
   if (latestId) {
       const match = candidates.find(j => String(j.id) === String(latestId));
       if (match) return match;  // Could return COMPLETED job if not filtered properly
   }
   ```

## Solution Required

### Fix 1: Change `const` to `let` and fix filtering logic

```javascript
pendingJob() {
    // Find pending jobs for this minion (ignore completed/failed)
    let candidates = (this.pendingJobs || []).filter(job => 
        job.minionId === this.minion.id && 
        job.status !== 'COMPLETED' && 
        job.status !== 'FAILED' &&
        job.status !== 'completed' &&  // Handle lowercase
        job.status !== 'failed'
    );
    
    if (!candidates.length) return null;

    // If the minion has a latest_training reference, only consider pending jobs
    // that were created after the latest training record
    try {
        const latestCreated = this.minion?.latest_training?.created_at;
        const latestStatus = this.minion?.latest_training?.status;
        
        if (latestCreated && latestStatus) {
            // Only filter by date if latest training is COMPLETED
            // If latest is PENDING/RUNNING, show it
            if (latestStatus === 'COMPLETED' || latestStatus === 'completed') {
                candidates = candidates.filter(j => new Date(j.created_at) > new Date(latestCreated));
            }
        }
    } catch (e) {
        console.warn('Error filtering candidates by date:', e);
    }

    if (!candidates.length) return null;

    // Prefer the pending job that matches latest_training id if present
    // BUT only if latest_training is not COMPLETED
    const latestId = this.minion?.latest_training?.id;
    const latestStatus = this.minion?.latest_training?.status;
    
    if (latestId && latestStatus && latestStatus !== 'COMPLETED' && latestStatus !== 'completed') {
        const match = candidates.find(j => String(j.id) === String(latestId));
        if (match) return match;
    }

    // Otherwise return the most recently created pending job
    candidates.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    return candidates[0] || null;
}
```

### Fix 2: Ensure `pendingJobs` prop doesn't contain COMPLETED jobs

Check where `pendingJobs` is populated in parent component (`Training.vue` or `MinionTrainingSection.vue`) and ensure it filters out COMPLETED/FAILED jobs before passing to child.

## Testing Checklist

- [ ] Completed jobs don't show "Pending Job" label
- [ ] Completed jobs show "View History" and "Upgrade" buttons
- [ ] PENDING jobs show "Pending Job" label correctly
- [ ] RUNNING jobs show training overlay correctly
- [ ] Status case sensitivity handled (COMPLETED vs completed)
- [ ] Multiple pending jobs handled correctly (show most recent)

## Related Files

- `frontend/src/components/MinionTrainingCard.vue` - Fix pendingJob computed property
- `frontend/src/components/MinionTrainingSection.vue` - Check pendingJobs prop population
- `frontend/src/views/Training.vue` - Check pendingJobs data source

## Status

⚠️ **Investigation Complete** - Ready for implementation (after RAG attachment testing)

