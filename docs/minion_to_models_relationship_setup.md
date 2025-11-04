# Minion to Models Relationship Setup

## Overview

This document outlines the relationship between Users, Minions, Models, and Providers in the AI Refinement Dashboard system. The key concept is that **Minions** are user-created entities that combine model configurations with character profiles.

## Terminology Clarification

- **Model** = Technical configuration (API key, base URL, model ID, etc.)
- **Profile** = Character/personality (name, avatar, experience, level, behavior)
- **Minion** = Model + Profile combined (user-created entity)
- **User** = Owner of multiple Minions
- **Provider** = Service/company that hosts models (NVIDIA, OpenAI, Anthropic, etc.)

## System Architecture

### User → Minions Relationship

```
User: swordfish
├── Minion 1: "DeepSeek R1" (NVIDIA provider)
│   ├── Model Config: deepseek-ai/deepseek-r1, API key, base URL
│   ├── Profile: name="DeepSeek R1", avatar="🧠", level=5, experience=1000
│   └── Use Case: coding tasks, math problems
├── Minion 2: "Claude Assistant" (Anthropic provider)
│   ├── Model Config: claude-3-5-sonnet, API key, base URL
│   ├── Profile: name="Claude", avatar="🤖", level=3, experience=500
│   └── Use Case: general chat, creative writing
└── Minion 3: "Custom Coder" (Custom provider)
    ├── Model Config: custom-endpoint, API key, base URL
    ├── Profile: name="My Coder", avatar="💻", level=1, experience=100
    └── Use Case: personal projects, experimentation
```

### Provider Grouping for Minions

```
Provider: NVIDIA
├── Minion: "DeepSeek R1" (swordfish's minion)
├── Minion: "NVIDIA Llama" (swordfish's minion)
└── Minion: "Moonshot Kimi" (swordfish's minion)

Provider: Anthropic
├── Minion: "Claude Assistant" (swordfish's minion)
└── Minion: "Claude Coder" (swordfish's minion)

Provider: Custom
├── Minion: "My Local Model" (swordfish's minion)
└── Minion: "Personal Assistant" (swordfish's minion)
```

## Database Schema

### Current Structure (Already Implemented)

```sql
-- Users table (existing)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- External API Models table (Minions - already implemented)
CREATE TABLE external_api_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- Minion name (e.g., "nvidia-llama-nemotron-super")
    display_name TEXT,                     -- Minion display name (e.g., "Grafana")
    description TEXT,                      -- Minion description
    provider TEXT NOT NULL,                -- Provider (nvidia, openai, anthropic, etc.)
    model_id TEXT NOT NULL,                -- Model ID (e.g., "nvidia/llama-3.3-nemotron-super-49b-v1.5")
    api_key TEXT,                          -- API key
    base_url TEXT,                         -- Base URL
    capabilities TEXT,                     -- JSON array of capabilities
    parameters TEXT,                       -- Model parameters (e.g., "49B")
    context_length INTEGER,                -- Context length
    max_tokens INTEGER,                    -- Max tokens
    temperature REAL DEFAULT 0.7,          -- Temperature
    top_p REAL DEFAULT 0.9,                -- Top-p
    system_prompt TEXT,                    -- System prompt
    experience INTEGER DEFAULT 0,          -- Minion experience points
    level TEXT DEFAULT 'beginner',         -- Minion level
    avatar_path TEXT,                      -- Avatar file path
    avatar_url TEXT,                       -- Avatar URL
    quantization TEXT,                     -- Quantization (e.g., "fp8")
    architecture TEXT,                     -- Architecture (e.g., "llama")
    license TEXT,                          -- License (e.g., "NVIDIA")
    embedding_length INTEGER,              -- Embedding length
    republic_id TEXT,                      -- Republic ID
    republic_key TEXT,                     -- Republic key
    xp_to_next_level INTEGER DEFAULT 100, -- XP to next level
    last_sync_timestamp TEXT,              -- Last sync timestamp
    sync_status TEXT DEFAULT "synced",     -- Sync status
    is_active BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    tags TEXT,                             -- JSON array of tags
    metadata TEXT,                         -- JSON object for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, model_id)
);

-- Minions table (separate from external_api_models - for future use)
CREATE TABLE minions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    model_id INTEGER NOT NULL,             -- Foreign key to external_api_models
    avatar_path TEXT,
    avatar_url TEXT,
    skillset TEXT,                         -- JSON array of skills
    personality TEXT,                      -- JSON object with personality traits
    behavior_config TEXT,                  -- JSON object with behavior settings
    is_active BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    tags TEXT,                             -- JSON array
    metadata TEXT,                         -- JSON object for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES external_api_models (id)
);

-- Provider groups table (NEW - for grouping)
CREATE TABLE provider_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,             -- nvidia, openai, anthropic, custom
    display_name TEXT NOT NULL,            -- NVIDIA, OpenAI, Anthropic, Custom
    description TEXT,
    icon TEXT,                             -- Material icon name
    color TEXT,                            -- Hex color code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default provider groups
INSERT INTO provider_groups (name, display_name, description, icon, color) VALUES
('nvidia', 'NVIDIA', 'NVIDIA hosted models', 'smart_toy', '#76B900'),
('openai', 'OpenAI', 'OpenAI GPT models', 'psychology', '#00A67E'),
('anthropic', 'Anthropic', 'Anthropic Claude models', 'robot_2', '#D97706'),
('huggingface', 'Hugging Face', 'Hugging Face models', 'favorite', '#FF6B6B'),
('ollama', 'Ollama', 'Local Ollama models', 'computer', '#4ECDC4'),
('custom', 'Custom', 'User-defined models', 'settings', '#6B7280');
```

### Current Minion Structure (Based on Your Example)

```json
{
  "id": 1,
  "name": "nvidia-llama-nemotron-super",
  "display_name": "Grafana",
  "description": "I am Grafana, the planner Minion. I break down challenges, use tools wisely, and deliver complete solutions",
  "provider": "nvidia",
  "model_id": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
  "api_key": "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",
  "base_url": "https://integrate.api.nvidia.com/v1",
  "capabilities": ["chat", "reasoning", "coding"],
  "parameters": "49B",
  "context_length": 131072,
  "max_tokens": 65536,
  "temperature": 0.6,
  "top_p": 0.95,
  "system_prompt": "I am Grafana, the planner Minion. I break down challenges, use tools wisely, and deliver complete solutions",
  "experience": 50,
  "level": "4",
  "avatar_url": "http://localhost:5000/api/avatars/959a575f-44ac-47b2-bb71-7e565a14c5b3.png",
  "quantization": "fp8",
  "architecture": "llama",
  "license": "NVIDIA",
  "tags": ["nvidia", "llama", "chat", "math", "reasoning"],
  "republic_id": "grafana-d7a1494e",
  "republic_key": "rep_TnrW-UrbjRb6XklzRRVQy_-5P3xVXKOmcpANP9SN7dA",
  "xp_to_next_level": 200,
  "last_sync_timestamp": "2025-09-28T15:39:53.838350",
  "sync_status": "synced",
  "is_active": 1,
  "is_favorite": 0,
  "created_at": "2025-09-28 11:36:00",
  "updated_at": "2025-09-28 12:50:52"
}
```

### Provider Grouping Structure

```json
{
  "provider": "nvidia",
  "display_name": "NVIDIA",
  "icon": "smart_toy",
  "color": "#76B900",
  "minions": [
    {
      "id": 1,
      "name": "nvidia-llama-nemotron-super",
      "display_name": "Grafana",
      "avatar_url": "http://localhost:5000/api/avatars/959a575f-44ac-47b2-bb71-7e565a14c5b3.png",
      "level": "4",
      "experience": 50
    }
  ]
}
```

## User-Specific Minion Management

### User A (swordfish)
- 3 NVIDIA Minions
- 2 Anthropic Minions
- 1 Custom Minion

### User B (other_user)
- 1 NVIDIA Minion
- 3 OpenAI Minions
- 2 Custom Minions

### User C (developer)
- 2 Hugging Face Minions
- 1 Ollama Minion
- 3 Custom Minions

## Frontend Implementation

### Enhanced `/models` Page (Minion Management)

```vue
<template>
  <div class="minion-management">
    <!-- Provider Filter -->
    <div class="provider-filter">
      <button 
        v-for="provider in providerGroups" 
        :key="provider.name"
        @click="filterByProvider(provider.name)"
        :class="{ active: selectedProvider === provider.name }"
        class="provider-button"
      >
        <span class="material-icons-round">{{ provider.icon }}</span>
        {{ provider.display_name }}
        <span class="count">({{ getMinionCount(provider.name) }})</span>
      </button>
    </div>

    <!-- Grouped Minions -->
    <div v-for="provider in groupedMinions" :key="provider.name" class="provider-section">
      <div class="provider-header">
        <h3>{{ provider.display_name }}</h3>
        <span class="material-icons-round">{{ provider.icon }}</span>
        <span class="minion-count">{{ provider.minions.length }} minions</span>
      </div>
      
      <div class="minions-grid">
        <div v-for="minion in provider.minions" :key="minion.id" class="minion-card">
          <div class="minion-avatar">{{ minion.avatar }}</div>
          <div class="minion-info">
            <h4>{{ minion.name }}</h4>
            <p>Level {{ minion.level }} • {{ minion.experience }} XP</p>
            <div class="minion-stats">
              <span class="stat">Queries: {{ minion.total_queries || 0 }}</span>
              <span class="stat">Success: {{ (minion.success_rate * 100) || 0 }}%</span>
            </div>
          </div>
          <div class="minion-actions">
            <button @click="editMinion(minion)" class="btn-edit">Edit</button>
            <button @click="useMinion(minion)" class="btn-use">Use</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create New Minion Button -->
    <button @click="createMinion" class="create-minion-btn">
      <span class="material-icons-round">add</span>
      Create New Minion
    </button>
  </div>
</template>
```

### Minion Creation Modal

```vue
<template>
  <Modal :visible="showCreateModal" @close="closeModal">
    <div class="minion-creation">
      <h3>Create New Minion</h3>
      
      <!-- Minion Profile -->
      <div class="form-section">
        <h4>Minion Profile</h4>
        <div class="form-group">
          <label>Minion Name</label>
          <input v-model="newMinion.name" placeholder="e.g., My Coding Assistant" />
        </div>
        <div class="form-group">
          <label>Avatar</label>
          <input v-model="newMinion.avatar" placeholder="🤖" />
        </div>
        <div class="form-group">
          <label>Personality</label>
          <textarea v-model="newMinion.personality" placeholder="Describe your minion's personality..."></textarea>
        </div>
      </div>

      <!-- Model Configuration -->
      <div class="form-section">
        <h4>Model Configuration</h4>
        <div class="form-group">
          <label>Provider</label>
          <select v-model="newMinion.provider_group" @change="onProviderChange">
            <option v-for="provider in providerGroups" :key="provider.name" :value="provider.name">
              {{ provider.display_name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Model ID</label>
          <input v-model="newMinion.model_id" placeholder="e.g., deepseek-ai/deepseek-r1" />
        </div>
        <div class="form-group">
          <label>API Key</label>
          <input type="password" v-model="newMinion.api_key" placeholder="Your API key" />
        </div>
        <div class="form-group">
          <label>Base URL</label>
          <input v-model="newMinion.base_url" placeholder="https://api.example.com/v1" />
        </div>
      </div>

      <div class="form-actions">
        <button @click="closeModal" class="btn-cancel">Cancel</button>
        <button @click="createMinion" class="btn-create">Create Minion</button>
      </div>
    </div>
  </Modal>
</template>
```

## Backend API Implementation

### Minion Management Endpoints (Updated for Current Structure)

```python
# Get user's minions grouped by provider
@app.route('/api/minions', methods=['GET'])
@require_auth
def get_user_minions():
    user_id = g.user['user_id']
    
    # Get minions from external_api_models table
    minions = db.execute("""
        SELECT eam.*, pg.display_name as provider_display_name, pg.icon as provider_icon
        FROM external_api_models eam 
        LEFT JOIN provider_groups pg ON eam.provider = pg.name
        WHERE eam.is_active = TRUE
        ORDER BY eam.provider, eam.display_name
    """).fetchall()
    
    # Group by provider
    grouped_minions = {}
    for minion in minions:
        provider = minion['provider'] or 'custom'
        if provider not in grouped_minions:
            grouped_minions[provider] = {
                'name': provider,
                'display_name': minion['provider_display_name'] or 'Custom',
                'icon': minion['provider_icon'] or 'settings',
                'minions': []
            }
        grouped_minions[provider]['minions'].append(minion)
    
    return jsonify({'success': True, 'grouped_minions': grouped_minions})

# Create new minion
@app.route('/api/minions', methods=['POST'])
@require_auth
def create_minion():
    user_id = g.user['user_id']
    data = request.get_json()
    
    # Insert minion into external_api_models table
    minion_id = db.execute("""
        INSERT INTO external_api_models (
            name, display_name, description, provider, model_id,
            api_key, base_url, capabilities, parameters, context_length,
            max_tokens, temperature, top_p, system_prompt, experience,
            level, avatar_path, avatar_url, quantization, architecture,
            license, tags, metadata, is_active, is_favorite
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'], data['display_name'], data['description'], data['provider'], data['model_id'],
        data['api_key'], data['base_url'], json.dumps(data['capabilities']), data['parameters'], data['context_length'],
        data['max_tokens'], data['temperature'], data['top_p'], data['system_prompt'], data.get('experience', 0),
        data.get('level', 'beginner'), data.get('avatar_path'), data.get('avatar_url'), data.get('quantization'), data.get('architecture'),
        data.get('license'), json.dumps(data['tags']), json.dumps(data.get('metadata', {})), True, False
    )).lastrowid
    
    db.commit()
    
    return jsonify({'success': True, 'minion_id': minion_id})

# Update minion
@app.route('/api/minions/<int:minion_id>', methods=['PUT'])
@require_auth
def update_minion(minion_id):
    user_id = g.user['user_id']
    data = request.get_json()
    
    # Verify minion exists
    minion = db.execute("""
        SELECT * FROM external_api_models WHERE id = ?
    """, (minion_id,)).fetchone()
    
    if not minion:
        return jsonify({'error': 'Minion not found'}), 404
    
    # Update minion
    db.execute("""
        UPDATE external_api_models SET 
            name = ?, display_name = ?, description = ?, system_prompt = ?,
            temperature = ?, top_p = ?, experience = ?, level = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        data['name'], data['display_name'], data['description'], data['system_prompt'],
        data['temperature'], data['top_p'], data['experience'], data['level'],
        minion_id
    ))
    
    db.commit()
    
    return jsonify({'success': True})

# Delete minion
@app.route('/api/minions/<int:minion_id>', methods=['DELETE'])
@require_auth
def delete_minion(minion_id):
    user_id = g.user['user_id']
    
    # Verify minion exists
    minion = db.execute("""
        SELECT * FROM external_api_models WHERE id = ?
    """, (minion_id,)).fetchone()
    
    if not minion:
        return jsonify({'error': 'Minion not found'}), 404
    
    # Soft delete
    db.execute("""
        UPDATE external_api_models SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (minion_id,))
    
    db.commit()
    
    return jsonify({'success': True})
```

## Training Integration

### Minion as Reference Model

```python
# Use minion as reference model for training
@app.route('/api/training/start', methods=['POST'])
@require_auth
def start_training():
    user_id = g.user['user_id']
    data = request.get_json()
    
    # Get minion configuration from external_api_models
    minion = db.execute("""
        SELECT * FROM external_api_models WHERE id = ?
    """, (data['reference_minion_id'],)).fetchone()
    
    if not minion:
        return jsonify({'error': 'Minion not found'}), 404
    
    # Start training with minion as reference
    training_job = {
        'user_id': user_id,
        'reference_minion_id': minion['id'],
        'reference_model_config': {
            'model_id': minion['model_id'],
            'api_key': minion['api_key'],
            'base_url': minion['base_url'],
            'temperature': minion['temperature'],
            'max_tokens': minion['max_tokens']
        },
        'training_data': data['training_data'],
        'status': 'PENDING'
    }
    
    # ... training logic ...
    
    return jsonify({'success': True, 'job_id': job_id})
```

## Benefits of This Approach

### 1. **User Ownership**
- Each user owns their minions
- No sharing of minion configurations
- User-specific minion management

### 2. **Provider Organization**
- Minions grouped by provider for easy management
- Provider-level analytics and usage tracking
- Easy provider switching

### 3. **Character Development**
- Minions have personalities and behaviors
- Experience and level progression
- Avatar and visual identity

### 4. **Training Integration**
- Minions can be used as reference models
- Training history linked to specific minions
- Minion performance tracking

### 5. **Scalability**
- Easy to add new providers
- Flexible minion configuration
- Extensible profile system

## Implementation Phases

### Phase 1: Database Schema (1 day)
- Add `provider_group` column to existing models table
- Create `provider_groups` table
- Create `minions` table
- Migrate existing models to minions

### Phase 2: Backend API (2 days)
- Implement minion management endpoints
- Add provider grouping logic
- Update training integration
- Add minion statistics tracking

### Phase 3: Frontend Implementation (3 days)
- Update `/models` page with provider grouping
- Create minion management interface
- Add minion creation modal
- Implement minion editing functionality

### Phase 4: Integration Testing (1 day)
- Test minion creation and management
- Verify training integration
- Test provider grouping
- Validate user isolation

## Risk Assessment

### Low Risk
- No changes to existing training functionality
- No changes to existing model configurations
- Only adds organizational layer

### Medium Risk
- Database migration for existing models
- Frontend UI changes
- Backend API changes

### High Risk (Avoid)
- Modifying existing model structure
- Breaking existing training connections
- Changing existing authentication

## Conclusion

This approach provides a clean separation between technical model configurations and user-facing minion profiles while maintaining all existing functionality. The provider grouping adds organization without complexity, and the minion system creates a more engaging user experience with character development and personalization.

The implementation is low-risk and can be done incrementally without disrupting existing workflows.
