# Minion Grouped Training Strategy
**Created:** October 1, 2025  
**Status:** Planning Phase  
**Strategy:** Latest Training + History Access

---

## 🎯 Core Concept

**Display Strategy:** Show only the **latest training** per minion on the main training page, with access to **full history** via modal.

**Benefits:**
- ✅ Clean, uncluttered UI
- ✅ Focus on current minion state
- ✅ Easy access to complete history
- ✅ Shows progression and evolution
- ✅ Scalable as minions grow

---

## 📊 Display Structure

### Main Training Page Layout
```
🤖 Minion Refinement
├── 📊 Grafana Minion
│   ┌─────────────────────────────────────┐
│   │ Grafana v1.3 (LoRA Training)        │
│   │ Status: ✅ Completed                │
│   │ Level: 4 | XP: 1,250 | Rank: Expert │
│   │ 📈 +75% Knowledge, +45% Accuracy    │
│   │ 🏷️ 3 Previous Trainings            │
│   │ [📊 View History] [🔄 Upgrade]      │
│   └─────────────────────────────────────┘
│
├── 📊 DataBot Minion
│   ┌─────────────────────────────────────┐
│   │ DataBot v2.1 (RAG Training)         │
│   │ Status: 🔄 Running                  │
│   │ Level: 2 | XP: 800 | Rank: Skilled  │
│   │ 📈 Processing...                    │
│   │ 🏷️ 2 Previous Trainings            │
│   │ [📊 View History] [⏸️ Stop]         │
│   └─────────────────────────────────────┘
```

### History Modal (Existing)
- Click "📊 View History" → opens MinionHistory.vue
- Shows full timeline of all trainings
- ECharts with real metrics
- PrimeVue Timeline with all events

---

## 🏗️ Implementation Strategy

### Phase 1: Backend Changes
**Goal:** Group external training jobs by minion and return latest + aggregated data

**New Endpoint:** `/api/users/{user_id}/external-training/minions/latest`

**Response Structure:**
```json
{
  "success": true,
  "minions": [
    {
      "id": 1,
      "display_name": "Grafana",
      "level": 4,
      "xp": 1250,
      "rank": "Expert",
      "latest_training": {
        "id": 5,
        "job_name": "Grafana v1.3",
        "training_type": "lora",
        "status": "COMPLETED",
        "progress": 1.0,
        "created_at": "2025-10-01T10:30:00",
        "completed_at": "2025-10-01T10:35:00"
      },
      "cumulative_improvements": {
        "knowledge": 75,
        "accuracy": 45,
        "speed": 15,
        "context_understanding": 60
      },
      "training_count": 3,
      "total_xp_gained": 1250
    }
  ]
}
```

**Backend Files to Create:**
- `backend/services/minion_latest_endpoints.py` - New endpoint
- `backend/services/minion_aggregation_service.py` - Aggregation logic

### Phase 2: Frontend Changes
**Goal:** Update Training.vue to show grouped minions with latest training

**New Components:**
- `frontend/src/components/MinionTrainingCard.vue` - Individual minion card
- `frontend/src/components/MinionTrainingSection.vue` - Minion refinement section
- `frontend/src/assets/minion_training.css` - Dedicated CSS

**Updated Components:**
- `frontend/src/views/Training.vue` - Main training page
- `frontend/src/components/ExternalTrainingModal.vue` - Add "Upgrade" mode

### Phase 3: Enhancements
**Goal:** Add XP system, level display, and upgrade functionality

**Features:**
- Minion level/XP display
- Cumulative improvements calculation
- "Upgrade" button with pre-filled config
- Training count display
- Minion comparison tools

---

## 🎨 UI/UX Design

### Minion Training Card
```html
<div class="minion-training-card">
  <div class="minion-header">
    <div class="minion-avatar">
      <img :src="minion.avatar" :alt="minion.display_name" />
    </div>
    <div class="minion-info">
      <h3>{{ minion.display_name }}</h3>
      <div class="minion-stats">
        <span class="level">Level {{ minion.level }}</span>
        <span class="xp">{{ minion.xp }} XP</span>
        <span class="rank">{{ minion.rank }}</span>
      </div>
    </div>
  </div>
  
  <div class="training-info">
    <h4>{{ minion.latest_training.job_name }}</h4>
    <div class="training-badges">
      <span class="training-type">{{ minion.latest_training.training_type }}</span>
      <span class="training-status" :class="minion.latest_training.status">
        {{ minion.latest_training.status }}
      </span>
    </div>
  </div>
  
  <div class="improvements">
    <div class="improvement-item">
      <span class="icon">🧠</span>
      <span class="label">Knowledge</span>
      <span class="value">+{{ minion.cumulative_improvements.knowledge }}%</span>
    </div>
    <!-- More improvements... -->
  </div>
  
  <div class="training-count">
    <span class="count">{{ minion.training_count }} Previous Trainings</span>
  </div>
  
  <div class="actions">
    <button class="btn btn-outline" @click="viewHistory(minion.id)">
      <span class="material-icons-round">history</span>
      View History
    </button>
    <button class="btn btn-primary" @click="upgradeMinion(minion.id)">
      <span class="material-icons-round">upgrade</span>
      Upgrade
    </button>
  </div>
</div>
```

### CSS Structure
```css
/* minion_training.css */
.minion-training-card {
  /* Card styling */
}

.minion-header {
  /* Header with avatar and info */
}

.minion-stats {
  /* Level, XP, rank display */
}

.improvements {
  /* Cumulative improvements grid */
}

.actions {
  /* Action buttons */
}
```

---

## 🔧 Technical Implementation

### Backend Aggregation Logic
```python
# minion_aggregation_service.py
class MinionAggregationService:
    def get_latest_training_per_minion(self, user_id):
        """Get latest training job for each minion"""
        pass
    
    def calculate_cumulative_improvements(self, minion_id):
        """Calculate total improvements from all trainings"""
        pass
    
    def get_training_count(self, minion_id):
        """Get total number of trainings for minion"""
        pass
    
    def calculate_total_xp(self, minion_id):
        """Calculate total XP gained from all trainings"""
        pass
```

### Frontend Component Structure
```javascript
// MinionTrainingCard.vue
export default {
  name: 'MinionTrainingCard',
  props: {
    minion: {
      type: Object,
      required: true
    }
  },
  methods: {
    viewHistory() {
      // Open MinionHistory modal
    },
    upgradeMinion() {
      // Open ExternalTrainingModal in upgrade mode
    }
  }
}
```

---

## 📋 Implementation Checklist

### Backend Tasks
- [ ] Create `minion_latest_endpoints.py`
- [ ] Create `minion_aggregation_service.py`
- [ ] Implement latest training endpoint
- [ ] Implement cumulative improvements calculation
- [ ] Add training count logic
- [ ] Add XP calculation (when XP system is ready)

### Frontend Tasks
- [ ] Create `MinionTrainingCard.vue` component
- [ ] Create `MinionTrainingSection.vue` component
- [ ] Create `minion_training.css` stylesheet
- [ ] Update `Training.vue` to use new components
- [ ] Add "Upgrade" mode to `ExternalTrainingModal.vue`
- [ ] Implement cumulative improvements display
- [ ] Add training count display
- [ ] Add level/XP display (when XP system is ready)

### Integration Tasks
- [ ] Test new endpoint with existing frontend
- [ ] Verify history modal still works
- [ ] Test upgrade functionality
- [ ] Ensure backward compatibility
- [ ] Update documentation

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Show only latest training per minion
- ✅ Display cumulative improvements
- ✅ Show training count
- ✅ Access to full history via modal
- ✅ "Upgrade" button with pre-filled config
- ✅ Level/XP display (when ready)

### Non-Functional Requirements
- ✅ Clean, uncluttered UI
- ✅ Fast loading (aggregated data)
- ✅ Responsive design
- ✅ Backward compatibility
- ✅ Component-based architecture
- ✅ Centralized CSS

---

## 🔄 Future Enhancements

### Phase 4: Advanced Features
- Minion comparison tools
- Training recommendations
- Automated upgrade suggestions
- Minion marketplace
- Social sharing features

### Phase 5: Gamification
- Achievement system
- Training streaks
- Leaderboards
- Badges and rewards
- Progress celebrations

---

## 📝 Notes

### Golden Rules
- **Don't touch old working code** - Create new pipeline
- **Component-based architecture** - Separate components
- **Centralized CSS** - Feature-specific stylesheets
- **Option API** - Use Vue 3 Option API
- **Backward compatibility** - Keep existing functionality

### File Organization
```
backend/
├── services/
│   ├── minion_latest_endpoints.py (new)
│   └── minion_aggregation_service.py (new)

frontend/
├── src/
│   ├── components/
│   │   ├── MinionTrainingCard.vue (new)
│   │   └── MinionTrainingSection.vue (new)
│   └── assets/
│       └── minion_training.css (new)
```

---

**Last Updated:** October 1, 2025, 8:30 PM  
**Next Phase:** Backend implementation  
**Dependencies:** XP system planning, existing MinionHistory modal
