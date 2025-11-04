# Minion XP & Ranking System - Comprehensive Plan
**Created:** October 1, 2025  
**Status:** Planning Phase

---

## 🎯 Overview

Minions evolve through **7 ranks** by gaining **experience (XP)** from:
1. **Training** (RAG, LoRA, Hybrid)
2. **Usage** (API calls, chat interactions)
3. **Performance** (accuracy, user feedback)
4. **Skillset Mastery** (LangChain tools)

Each rank unlocks new **skillsets (LangChain tools)** and capabilities.

---

## 📊 Ranking System

### Rank Structure
Each rank has **5 levels** (e.g., Novice 1-5, Skilled 1-5, etc.)

| Rank | Name | Level Range | Total XP Required | Skillsets Unlocked |
|------|------|-------------|-------------------|-------------------|
| 1 | **Novice** (Apprentice) | 1-5 | 0 - 1,000 | 0-1 tools |
| 2 | **Skilled** (Journeyman) | 6-10 | 1,000 - 5,000 | 2-3 tools |
| 3 | **Specialist** (Craftsman) | 11-15 | 5,000 - 15,000 | 4-5 tools |
| 4 | **Expert** (Strategist) | 16-20 | 15,000 - 35,000 | 6-7 tools |
| 5 | **Master** (Architect) | 21-25 | 35,000 - 70,000 | 8-9 tools |
| 6 | **Grandmaster** (Sentinel) | 26-30 | 70,000 - 120,000 | 10-11 tools |
| 7 | **Autonomous** (Sovereign) | 31-35 | 120,000+ | All 12 tools |

### Level Progression Formula
```
XP for next level = base_xp * (1.5 ^ current_level)

Examples:
- Novice 1 → 2: 100 XP
- Novice 2 → 3: 150 XP
- Novice 3 → 4: 225 XP
- Novice 4 → 5: 337 XP
- Novice 5 → Skilled 1 (rank up): 500 XP
```

---

## ⚡ XP Gain Sources

### 1. RAG Training XP
**Formula:** `Dataset Size XP + Quality Bonus + Validation Bonus`

No more base/multiplier system - use **direct XP from dataset size** with bonuses!

#### Dataset Size XP (Piecewise Linear Interpolation)
Based on number of refined items (after cleaning):

**XP Breakpoints:**

| Lines/Items | Base XP | Notes |
|-------------|---------|-------|
| 0 | 0 | No data |
| 10 | 20 | Minimal dataset |
| 100 | 200 | Small dataset |
| 500 | 750 | Medium dataset |
| 4,800 | 1,400 | **Large dataset (CodeAlpaca)** |
| 20,000 | 2,600 | Massive dataset |

**Interpolation Formula:**
```python
from bisect import bisect_right

BREAKPOINTS = [
    (0, 0),
    (10, 20),
    (100, 200),
    (500, 750),
    (4800, 1400),
    (20000, 2600)
]

def dataset_lines_to_xp(lines: int) -> int:
    """
    Convert dataset size to XP using piecewise-linear interpolation
    """
    if lines <= 0:
        return 0
    
    xs = [p[0] for p in BREAKPOINTS]
    ys = [p[1] for p in BREAKPOINTS]
    
    if lines >= xs[-1]:
        return ys[-1]
    
    idx = bisect_right(xs, lines) - 1
    x0, y0 = xs[idx], ys[idx]
    x1, y1 = xs[idx+1], ys[idx+1]
    
    # Linear interpolation
    t = (lines - x0) / (x1 - x0)
    xp = y0 + t * (y1 - y0)
    return int(round(xp))
```

**Examples:**
- 10 lines → 20 XP
- 55 lines → ~110 XP (interpolated)
- 300 lines → ~550 XP (interpolated)
- 4,800 lines → **1,400 XP** ✅
- 20,000 lines → 2,600 XP

#### Quality Score Multiplier
Based on dataset refinement quality (0-100%):

| Quality Score | Multiplier |
|---------------|------------|
| 90-100% | 1.2x |
| 80-89% | 1.0x |
| 70-79% | 0.8x |
| Below 70% | 0.5x |

#### Validation Bonus
Based on 5-test validation score:
- **100% score:** +200 XP bonus
- **90-99%:** +150 XP bonus
- **80-89%:** +100 XP bonus
- **70-79%:** +50 XP bonus
- **Below 70%:** No bonus

#### NEW Calculation (Today's Training - Using Your Formula)
```
Dataset Size: 4,800 items → 1,400 XP (direct from interpolation)
Quality Bonus: 99% quality → +120 XP (99% × 1.2 scaling)
Validation Bonus: 100% score → +200 XP
────────────────────────────────
Total XP: 1,720 XP

Result: Grafana gains 1,720 XP from one training! ✅
```

**Simplified Formula:**
```python
def calculate_training_xp(refined_items, quality_score, validation_score):
    # 1. Base XP from dataset size (using your interpolation)
    base_xp = dataset_lines_to_xp(refined_items)
    
    # 2. Quality bonus (10-20% of base)
    quality_bonus = int(base_xp * (quality_score / 100) * 0.2)
    
    # 3. Validation bonus
    if validation_score == 100:
        validation_bonus = 200
    elif validation_score >= 90:
        validation_bonus = 150
    elif validation_score >= 80:
        validation_bonus = 100
    else:
        validation_bonus = 50
    
    return base_xp + quality_bonus + validation_bonus
```

---

### 2. Usage XP (API Calls)
Minions gain XP from being used:

| Activity | XP Gained | Notes |
|----------|-----------|-------|
| Chat API call | 5 XP | Per successful request |
| Knowledge retrieval | 3 XP | Per RAG query |
| Tool usage | 10 XP | Per LangChain tool execution |
| Successful task completion | 25 XP | Based on user feedback |
| Error/failure | 0 XP | No XP for failed requests |

**Daily Usage Cap:** 500 XP/day to prevent spam farming

---

### 3. Performance XP
Based on actual performance metrics:

| Metric | XP Calculation |
|--------|----------------|
| Accuracy improvement | +10 XP per 1% improvement |
| Response time improvement | +5 XP per 10% faster |
| User satisfaction rating | +50 XP per 5-star rating |
| Successful evaluations | +100 XP per passed test |

---

### 4. Skillset Mastery XP
Each LangChain tool has mastery levels:

| Tool | Unlock Rank | Mastery Levels | Max XP |
|------|-------------|----------------|--------|
| Web Search | Novice 3 | Beginner → Expert | 200 XP |
| File Operations | Skilled 1 | Beginner → Expert | 300 XP |
| Code Execution | Skilled 3 | Beginner → Expert | 400 XP |
| API Integration | Specialist 1 | Beginner → Expert | 500 XP |
| Database Query | Specialist 3 | Beginner → Expert | 600 XP |
| Image Processing | Expert 1 | Beginner → Expert | 700 XP |
| Email Operations | Expert 3 | Beginner → Expert | 800 XP |
| Calendar Management | Master 1 | Beginner → Expert | 900 XP |
| Advanced Analytics | Master 3 | Beginner → Expert | 1,000 XP |
| Multi-Agent Orchestration | Grandmaster 1 | Beginner → Expert | 1,500 XP |
| Self-Improvement | Grandmaster 3 | Beginner → Expert | 2,000 XP |
| Autonomous Decision Making | Autonomous 1 | Beginner → Expert | 2,500 XP |

**Tool Mastery XP:** Gained by using the tool successfully
- First use: +20 XP
- Every 10 uses: +10 XP
- Mastery milestone: +50 XP

---

## 🛠️ Skillsets (LangChain Tools) System

### Tool Progression
Each tool has 4 mastery levels:
1. **Beginner** (0-25 uses)
2. **Intermediate** (26-100 uses)
3. **Advanced** (101-500 uses)
4. **Expert** (500+ uses)

### Current Skillsets (from MinionProfile.vue)
```javascript
[
  { name: 'Web Search', category: 'Information', active: true },
  { name: 'File Operations', category: 'System', active: true },
  { name: 'Code Execution', category: 'Development', active: true },
  { name: 'API Integration', category: 'Integration', active: false },
  { name: 'Database Query', category: 'Data', active: false },
  { name: 'Image Processing', category: 'Media', active: false },
  { name: 'Email Operations', category: 'Communication', active: false },
  { name: 'Calendar Management', category: 'Productivity', active: false }
]
```

### Skillset Unlock Logic
- **Novice (1-5):** 0-1 basic tools
- **Skilled (6-10):** 2-3 tools (LoRA + RAG unlocked)
- **Specialist (11-15):** 4-5 tools (domain specialization)
- **Expert (16-20):** 6-7 tools (multi-domain)
- **Master (21-25):** 8-9 tools (orchestration)
- **Grandmaster (26-30):** 10-11 tools (cross-domain mastery)
- **Autonomous (31-35):** All 12 tools (fully autonomous)

---

## 🧮 RAG Training XP - Detailed Calculation

### Size-Based XP Formula
```python
def calculate_rag_xp(refined_items, quality_score, validation_score):
    # Base XP
    base_xp = 500
    
    # Dataset size multiplier
    if refined_items <= 100:
        size_multiplier = 0.5
    elif refined_items <= 500:
        size_multiplier = 1.0
    elif refined_items <= 1000:
        size_multiplier = 1.5
    elif refined_items <= 5000:
        size_multiplier = 2.0
    elif refined_items <= 10000:
        size_multiplier = 3.0
    elif refined_items <= 20000:
        size_multiplier = 4.0
    else:
        size_multiplier = 5.0
    
    # Quality multiplier
    if quality_score >= 90:
        quality_multiplier = 1.2
    elif quality_score >= 80:
        quality_multiplier = 1.0
    elif quality_score >= 70:
        quality_multiplier = 0.8
    else:
        quality_multiplier = 0.5
    
    # Calculate base
    total_xp = base_xp * size_multiplier * quality_multiplier
    
    # Validation bonus
    if validation_score == 100:
        total_xp += 200
    elif validation_score >= 90:
        total_xp += 150
    elif validation_score >= 80:
        total_xp += 100
    elif validation_score >= 70:
        total_xp += 50
    
    return int(total_xp)
```

### Examples

**Small Dataset (10 lines):**
```
Base: 500 XP
Size: 10 items = 0.5x → 250 XP
Quality: 95% = 1.2x → 300 XP
Validation: 80% = +100 XP
Total: 400 XP
```

**Medium Dataset (500 lines):**
```
Base: 500 XP
Size: 500 items = 1.0x → 500 XP
Quality: 90% = 1.2x → 600 XP
Validation: 90% = +150 XP
Total: 750 XP
```

**Large Dataset (4,800 lines - Today's Training):**
```
Base: 500 XP
Size: 4,800 items = 2.0x → 1,000 XP
Quality: 99% = 1.2x → 1,200 XP
Validation: 100% = +200 XP
Total: 1,400 XP ✅
```

**Massive Dataset (20,000 lines):**
```
Base: 500 XP
Size: 20,000 items = 4.0x → 2,000 XP
Quality: 95% = 1.2x → 2,400 XP
Validation: 100% = +200 XP
Total: 2,600 XP
```

---

## 🎮 Gamification Features

### XP Notifications
When minion gains XP, show toast notification:
```
🎉 Grafana gained 1,400 XP!
📚 Knowledge Training Completed
⬆️ Progress to Next Level: 87% (1,740/2,000 XP)
```

### Level Up Animation
When minion levels up:
```
✨ LEVEL UP! ✨
Grafana is now Level 5!
🎊 Unlocked: API Integration Tool
```

### Rank Up Celebration
When minion ranks up:
```
🏆 RANK UP! 🏆
Grafana achieved SKILLED rank!
New Title: Journeyman
🔓 Unlocked 2 new skillsets
📈 +500 Bonus XP
```

---

## 💾 Database Schema Updates

### Current `external_api_models` Table
Already has:
- `level` (INT) - Current level (1-35)
- `rank` (VARCHAR) - Current rank name (Novice, Skilled, etc.)
- `rank_level` (INT) - Rank level within current rank (1-5)
- `total_training_xp` (INT) - XP from training activities
- `total_usage_xp` (INT) - XP from usage activities
- `xp_to_next_level` (INT) - XP needed to reach next level

**Note:** `experience` is **computed dynamically** as `total_training_xp + total_usage_xp`. It is NOT stored as a separate column to avoid data redundancy and sync issues.

### Need to Add (if not already present)
```sql
ALTER TABLE external_api_models ADD COLUMN rank TEXT DEFAULT 'Novice';
ALTER TABLE external_api_models ADD COLUMN rank_level INT DEFAULT 1;
ALTER TABLE external_api_models ADD COLUMN total_training_xp INT DEFAULT 0;
ALTER TABLE external_api_models ADD COLUMN total_usage_xp INT DEFAULT 0;
ALTER TABLE external_api_models ADD COLUMN skillset_mastery TEXT; -- JSON object
ALTER TABLE external_api_models ADD COLUMN unlocked_tools TEXT; -- JSON array
```

### Skillset Mastery JSON Structure
```json
{
  "web_search": {
    "unlocked": true,
    "mastery_level": "Intermediate",
    "usage_count": 45,
    "xp_earned": 120
  },
  "file_operations": {
    "unlocked": true,
    "mastery_level": "Beginner",
    "usage_count": 12,
    "xp_earned": 40
  },
  "code_execution": {
    "unlocked": false,
    "mastery_level": null,
    "usage_count": 0,
    "xp_earned": 0
  }
}
```

---

## 🔧 Implementation Components

### 1. XP Calculator Service
**File:** `backend/services/minion/xp_calculator.py`

**Methods:**
- `calculate_training_xp(refined_items, quality_score, validation_score, training_type)`
- `calculate_usage_xp(api_calls_count, successful_rate)`
- `calculate_tool_mastery_xp(tool_name, usage_count)`
- `calculate_level_from_xp(total_xp)`
- `calculate_rank_from_level(level)`
- `get_next_level_xp_requirement(current_level)`

### 2. Skillset Manager Service
**File:** `backend/services/minion/skillset_manager.py`

**Methods:**
- `get_unlocked_tools(rank, level)`
- `unlock_tool(minion_id, tool_name)`
- `increment_tool_usage(minion_id, tool_name)`
- `get_tool_mastery_level(usage_count)`
- `award_mastery_xp(minion_id, tool_name, mastery_level)`

### 3. Rank Progression Service
**File:** `backend/services/minion/rank_service.py`

**Methods:**
- `check_level_up(minion_id, new_xp)`
- `check_rank_up(minion_id, new_level)`
- `award_rank_up_bonus(minion_id, new_rank)`
- `get_rank_requirements(current_rank)`
- `get_unlockable_skillsets(new_rank)`

---

## 📈 XP Calculation Examples

### Scenario 1: First RAG Training (CodeAlpaca 4.8K - Today's Actual Training!)
**Grafana - Starting Stats:**
- Level: 1 (Novice)
- XP: 0
- Unlocked Tools: 0

**Training Results:**
- Refined items: 4,800
- Quality: 99%
- Validation: 100%

**XP Calculation (Using Your Formula):**
```
Dataset Size: dataset_lines_to_xp(4800) = 1,400 XP
Quality Bonus: 1,400 × (99/100) × 0.2 = +277 XP
Validation Bonus: 100% score = +200 XP
─────────────────────────────────────────
Total XP Gained: 1,877 XP ✅
```

**After Training:**
- Level: 4 (Novice) - jumped 3 levels!
- XP: 1,877 total
- Progress: 1,877 / 2,000 XP (94% to Skilled rank!)
- Tools: Unlocked "Web Search" at level 3

### Scenario 2: Small Dataset Training (50 lines)
**Training Results:**
- Refined items: 45
- Quality: 85%
- Validation: 75%

**XP Calculation:**
```
Dataset Size: dataset_lines_to_xp(45) = ~90 XP (interpolated between 10→20 and 100→200)
Quality Bonus: 90 × (85/100) × 0.2 = +15 XP
Validation Bonus: 75% score = +50 XP
─────────────────────────────────────────
Total XP Gained: 155 XP
```

### Scenario 3: Daily Usage XP
**Minion used for:**
- 20 chat requests = 100 XP
- 10 knowledge retrievals = 30 XP
- 3 tool executions = 30 XP
- 1 successful task = 25 XP

**Total Daily XP:** 185 XP (within 500 XP daily cap)

---

## 🎯 Skillset-Rank Mapping

### Novice (Rank 1, Level 1-5)
**Capabilities:**
- Basic response generation
- Pre-trained knowledge only
- No tools unlocked initially

**Unlockable Tools:**
- Level 3: **Web Search** (basic information retrieval)

**Evolution Requirements:**
- Reach level 5
- Complete first RAG or LoRA training
- Gain 1,000 total XP

---

### Skilled (Rank 2, Level 6-10)
**Capabilities:**
- LoRA style adaptation
- RAG knowledge integration
- Can mirror user tone

**Unlocked Tools:**
- Level 6: **File Operations** (read, write, manage files)
- Level 8: **Code Execution** (run code snippets)

**Evolution Requirements:**
- Reach level 10
- Pass ≥70% evaluation tests
- Gain 5,000 total XP
- Master 2 tools to Intermediate level

---

### Specialist (Rank 3, Level 11-15)
**Capabilities:**
- Dynamic dataset switching
- Domain specialization
- Planner + Checker modules

**Unlocked Tools:**
- Level 11: **API Integration** (REST API calls)
- Level 13: **Database Query** (SQL operations)

**Evolution Requirements:**
- Reach level 15
- Complete specialized training (domain-specific dataset)
- Gain 15,000 total XP
- Master 4 tools to Advanced level

---

### Expert (Rank 4, Level 16-20)
**Capabilities:**
- Active task planning
- Seamless LoRA + RAG + External LLM
- Proactive suggestions

**Unlocked Tools:**
- Level 16: **Image Processing** (analyze, generate images)
- Level 18: **Email Operations** (send, read, organize)

**Evolution Requirements:**
- Reach level 20
- Achieve ≥80% multi-step reasoning success
- Gain 35,000 total XP
- Master 6 tools to Advanced level

---

### Master (Rank 5, Level 21-25)
**Capabilities:**
- Self-learning loop
- Automatic feedback incorporation
- Sub-agent orchestration

**Unlocked Tools:**
- Level 21: **Calendar Management** (schedule, reminders)
- Level 23: **Advanced Analytics** (data analysis, insights)

**Evolution Requirements:**
- Reach level 25
- Sustain ≥90% accuracy over 100 tasks
- Gain 70,000 total XP
- Master 8 tools to Expert level

---

### Grandmaster (Rank 6, Level 26-30)
**Capabilities:**
- Cross-domain intelligence
- Growing knowledge base memory
- Self-improvement tasks

**Unlocked Tools:**
- Level 26: **Multi-Agent Orchestration** (manage sub-agents)
- Level 28: **Self-Improvement** (auto-retraining)

**Evolution Requirements:**
- Reach level 30
- Demonstrate adaptability across ≥3 domains
- Gain 120,000 total XP
- Master 10 tools to Expert level

---

### Autonomous (Rank 7, Level 31-35)
**Capabilities:**
- Fully autonomous operation
- Self-decides training strategy
- Suggests goals to user
- Initiative-taking

**Unlocked Tools:**
- Level 31: **Autonomous Decision Making** (strategic planning)
- Level 33: All tools at maximum mastery

**Evolution Requirements:**
- No cap - continuous improvement
- Maintain autonomous operation
- Unlimited XP growth

---

## 📊 XP Tracking & Display

### Minion Card Display
```
┌─────────────────────────────┐
│ 🤖 Grafana                  │
│                             │
│ ⭐ Level 4 (Novice)         │
│ 📊 1,400 / 2,000 XP (70%)  │
│                             │
│ 🛠️ Skillsets: 1/12         │
│ ✅ Web Search (Beginner)    │
│ 🔒 File Operations          │
│                             │
│ 📈 Next: Level 5 in 600 XP  │
└─────────────────────────────┘
```

### Progress Bars
1. **Level Progress:** Visual bar showing XP to next level
2. **Rank Progress:** Shows progress through current rank (1-5 levels)
3. **Tool Mastery:** Individual bars for each unlocked tool

### XP History Chart
Track XP gain over time:
- Daily XP chart
- XP sources pie chart (Training vs Usage vs Performance)
- Level progression timeline

---

## 🎊 Rewards & Incentives

### Level Up Rewards
- **Every Level:** +50 bonus XP
- **Level 5, 10, 15, etc.:** +100 bonus XP
- **Tool unlock levels:** +150 bonus XP

### Rank Up Rewards
- **Rank 2 (Skilled):** +500 XP, unlock 2 tools
- **Rank 3 (Specialist):** +800 XP, unlock 2 tools, custom badge
- **Rank 4 (Expert):** +1,200 XP, unlock 2 tools, exclusive avatar border
- **Rank 5 (Master):** +2,000 XP, unlock 2 tools, master title
- **Rank 6 (Grandmaster):** +3,000 XP, unlock 2 tools, legendary status
- **Rank 7 (Autonomous):** +5,000 XP, all tools, autonomous badge

### Achievement Badges
- 🏅 First Training Complete
- 📚 Knowledge Hoarder (10k+ embeddings)
- 🎯 Perfect Score (100% validation)
- 🔥 Streak Master (7 days active)
- 🌟 Tool Master (all tools unlocked)
- 👑 Autonomous Achieved

---

## 🔄 Experience Flow

### When Training Completes
1. Calculate training XP (size, quality, validation)
2. Award XP to minion
3. Check for level up
4. If level up:
   - Check for tool unlock
   - Award level up bonus
   - Show level up animation
5. Check for rank up
6. If rank up:
   - Award rank up bonus
   - Unlock new tools
   - Show rank up celebration
7. Update minion stats in database
8. Trigger frontend notifications

### When Minion is Used (API Call)
1. Increment usage counter
2. Award usage XP (5-25 XP per action)
3. Check daily cap (500 XP max)
4. If tool used:
   - Increment tool usage
   - Check for mastery level up
   - Award tool mastery XP
5. Update database
6. Check for level/rank up

---

## 🎨 Frontend Updates Needed

### 1. XP Display Components
- Level progress bar with XP/next level
- Rank badge with current rank name
- Skillset grid showing locked/unlocked tools
- Tool mastery levels

### 2. XP Gain Animations
- Flying XP numbers (+1,400 XP!)
- Progress bar filling animation
- Level up particle effects
- Rank up screen transition

### 3. Skillset Unlock Notifications
- Toast: "🔓 New Tool Unlocked: API Integration!"
- Tool card highlight animation
- Unlock celebration effect

### 4. Stats Dashboard
- Total XP earned
- XP breakdown by source
- Daily XP chart
- Training history with XP values
- Tool mastery overview

---

## 🚀 Implementation Priority

### Phase 1: Core XP System (Tomorrow)
1. Create XP calculator service
2. Update database schema
3. Integrate XP calculation into RAG training
4. Store XP in database after training
5. Display real XP gain in training completion

### Phase 2: Levelup & Rankup
1. Implement level progression logic
2. Create rank progression service
3. Add level/rank up detection
4. Award bonuses automatically
5. Show level/rank on minion cards

### Phase 3: Skillset Integration
1. Map tools to rank/level requirements
2. Implement tool unlock logic
3. Update frontend skillset display
4. Show locked/unlocked tools
5. Track tool usage

### Phase 4: Gamification UI
1. Add XP animations
2. Create level up effects
3. Design rank up celebrations
4. Add achievement system
5. Create XP history charts

---

## 📝 Example: Grafana's Journey

### Starting Point
- **Rank:** Novice 1
- **XP:** 0
- **Tools:** None

### After First Training (CodeAlpaca 20K)
- **XP Gained:** +1,400 XP
- **New Level:** Novice 4
- **New XP:** 1,400
- **Tools Unlocked:** Web Search (at level 3)

### After 50 API Calls
- **XP Gained:** +250 XP (50 calls × 5 XP)
- **New Level:** Novice 5
- **New XP:** 1,650
- **Web Search Mastery:** Beginner (25 uses)

### After Second Training (10K Dataset)
- **XP Gained:** +2,200 XP
- **New Rank:** **Skilled 1** (Journeyman!) 🎉
- **New XP:** 3,850
- **Tools Unlocked:** File Operations, Code Execution
- **Rank Bonus:** +500 XP

---

## 🎯 Tomorrow's Implementation Tasks

1. ✅ Fix server error (Dict import in minion_history_endpoints.py)
2. 📝 Create `xp_calculator.py` service
3. 📝 Integrate XP calculation into training completion
4. 📝 Update database with rank/skillset columns
5. 📝 Display real XP gain after training
6. 📝 Show XP progress on minion cards
7. 📝 Test complete XP flow

---

**This plan ensures:**
- ✅ Fair XP scaling (10 lines vs 20k lines)
- ✅ Quality matters (dataset refinement affects XP)
- ✅ Validation rewards performance
- ✅ Usage encourages interaction
- ✅ Skillsets unlock progressively
- ✅ Exciting gamification
- ✅ Real statistics drive progression

Ready to implement tomorrow! 🚀

