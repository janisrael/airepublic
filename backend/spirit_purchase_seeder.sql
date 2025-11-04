-- Spirit Purchase System Seeder
-- Generated on: 2025-10-02 09:18:24

-- Purchase System Schema

-- USER SPIRIT PURCHASES TABLE
CREATE TABLE user_spirit_purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    spirit_id INTEGER NOT NULL REFERENCES spirits_registry(id),
    purchase_type TEXT NOT NULL, -- 'individual', 'bundle', 'subscription'
    payment_method TEXT NOT NULL, -- 'usd', 'points', 'subscription'
    amount_paid_usd DECIMAL(10,2) DEFAULT 0.00,
    amount_paid_points INTEGER DEFAULT 0,
    bundle_id INTEGER REFERENCES spirit_bundles(id),
    subscription_plan_id INTEGER REFERENCES subscription_plans(id),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- For subscription-based access
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SPIRIT BUNDLES TABLE
CREATE TABLE spirit_bundles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    spirits JSONB NOT NULL, -- Array of spirit IDs
    original_price_usd DECIMAL(10,2) NOT NULL,
    bundle_price_usd DECIMAL(10,2) NOT NULL,
    savings_usd DECIMAL(10,2) NOT NULL,
    savings_percentage INTEGER NOT NULL,
    points_cost INTEGER NOT NULL,
    category TEXT NOT NULL,
    icon TEXT,
    is_popular BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SUBSCRIPTION PLANS TABLE
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    billing_cycle TEXT NOT NULL, -- 'monthly', 'yearly'
    free_spirits JSONB, -- Array of spirit IDs or 'ALL'
    discount_on_purchases INTEGER DEFAULT 0,
    exclusive_spirits JSONB DEFAULT '[]',
    max_minions INTEGER DEFAULT -1, -- -1 for unlimited
    max_spirits_per_minion INTEGER DEFAULT 5,
    features JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER SUBSCRIPTIONS TABLE
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
    status TEXT NOT NULL, -- 'active', 'cancelled', 'expired'
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    auto_renew BOOLEAN DEFAULT TRUE,
    payment_method TEXT, -- 'paypal', 'stripe', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER POINTS TABLE (for point-based purchases)
CREATE TABLE user_points (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    total_points INTEGER DEFAULT 0,
    earned_points INTEGER DEFAULT 0,
    spent_points INTEGER DEFAULT 0,
    bonus_points INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- POINTS TRANSACTIONS TABLE
CREATE TABLE points_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    transaction_type TEXT NOT NULL, -- 'earned', 'spent', 'bonus', 'refund'
    amount INTEGER NOT NULL,
    description TEXT,
    reference_id INTEGER, -- ID of related purchase or earning
    reference_type TEXT, -- 'purchase', 'training', 'achievement', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SPIRIT ACCESS TABLE (tracks which spirits user has access to)
CREATE TABLE user_spirit_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    spirit_id INTEGER NOT NULL REFERENCES spirits_registry(id),
    access_type TEXT NOT NULL, -- 'purchased', 'subscription', 'free', 'trial'
    source TEXT NOT NULL, -- 'individual_purchase', 'bundle', 'subscription', 'free_tier'
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- NULL for permanent access
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, spirit_id)
);

-- Add purchase columns to spirits_registry
ALTER TABLE spirits_registry ADD COLUMN IF NOT EXISTS price_usd DECIMAL(10,2) DEFAULT 0.00;
ALTER TABLE spirits_registry ADD COLUMN IF NOT EXISTS price_points INTEGER DEFAULT 0;
ALTER TABLE spirits_registry ADD COLUMN IF NOT EXISTS is_purchaseable BOOLEAN DEFAULT TRUE;
ALTER TABLE spirits_registry ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE;
ALTER TABLE spirits_registry ADD COLUMN IF NOT EXISTS free_with_subscription BOOLEAN DEFAULT FALSE;
ALTER TABLE spirits_registry ADD COLUMN IF NOT EXISTS tier TEXT DEFAULT 'free'; -- 'free', 'basic', 'professional', 'premium'


-- Update Spirits with Pricing Information
UPDATE spirits_registry SET 
            price_usd = 0.0,
            price_points = 0,
            tier = 'free',
            is_premium = false,
            free_with_subscription = true
        WHERE name = 'Writer Spirit';
UPDATE spirits_registry SET 
            price_usd = 0.0,
            price_points = 0,
            tier = 'free',
            is_premium = false,
            free_with_subscription = true
        WHERE name = 'Analyst Spirit';
UPDATE spirits_registry SET 
            price_usd = 0.0,
            price_points = 0,
            tier = 'free',
            is_premium = false,
            free_with_subscription = true
        WHERE name = 'Builder Spirit';
UPDATE spirits_registry SET 
            price_usd = 0.0,
            price_points = 0,
            tier = 'free',
            is_premium = false,
            free_with_subscription = true
        WHERE name = 'Connector Spirit';
UPDATE spirits_registry SET 
            price_usd = 0.0,
            price_points = 0,
            tier = 'free',
            is_premium = false,
            free_with_subscription = true
        WHERE name = 'Checker Spirit';
UPDATE spirits_registry SET 
            price_usd = 2.99,
            price_points = 30,
            tier = 'basic',
            is_premium = false,
            free_with_subscription = false
        WHERE name = 'Creative Spirit';
UPDATE spirits_registry SET 
            price_usd = 3.99,
            price_points = 40,
            tier = 'basic',
            is_premium = false,
            free_with_subscription = false
        WHERE name = 'Researcher Spirit';
UPDATE spirits_registry SET 
            price_usd = 4.99,
            price_points = 50,
            tier = 'basic',
            is_premium = false,
            free_with_subscription = false
        WHERE name = 'Debugger Spirit';
UPDATE spirits_registry SET 
            price_usd = 3.99,
            price_points = 40,
            tier = 'basic',
            is_premium = false,
            free_with_subscription = false
        WHERE name = 'Communicator Spirit';
UPDATE spirits_registry SET 
            price_usd = 2.99,
            price_points = 30,
            tier = 'basic',
            is_premium = false,
            free_with_subscription = false
        WHERE name = 'Scheduler Spirit';
UPDATE spirits_registry SET 
            price_usd = 4.99,
            price_points = 50,
            tier = 'basic',
            is_premium = false,
            free_with_subscription = false
        WHERE name = 'Translator Spirit';
UPDATE spirits_registry SET 
            price_usd = 7.99,
            price_points = 80,
            tier = 'professional',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'Mathematician Spirit';
UPDATE spirits_registry SET 
            price_usd = 9.99,
            price_points = 100,
            tier = 'professional',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'DevOps Spirit';
UPDATE spirits_registry SET 
            price_usd = 12.99,
            price_points = 130,
            tier = 'professional',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'Security Spirit';
UPDATE spirits_registry SET 
            price_usd = 8.99,
            price_points = 90,
            tier = 'professional',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'Educator Spirit';
UPDATE spirits_registry SET 
            price_usd = 9.99,
            price_points = 100,
            tier = 'professional',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'Designer Spirit';
UPDATE spirits_registry SET 
            price_usd = 14.99,
            price_points = 150,
            tier = 'premium',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'Consultant Spirit';
UPDATE spirits_registry SET 
            price_usd = 16.99,
            price_points = 170,
            tier = 'premium',
            is_premium = true,
            free_with_subscription = false
        WHERE name = 'Healer Spirit';

-- Insert Spirit Bundles
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Content Creator Bundle',
            'Complete content creation toolkit',
            '["Writer Spirit", "Creative Spirit", "Translator Spirit", "Designer Spirit"]',
            18.96,
            12.99,
            5.97,
            31,
            130,
            'Content & Creative',
            '📝',
            true,
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Developer Pro Bundle',
            'Full-stack development powerhouse',
            '["Builder Spirit", "Debugger Spirit", "DevOps Spirit", "Security Spirit", "Analyst Spirit"]',
            32.96,
            19.99,
            12.97,
            39,
            200,
            'Development & Technical',
            '💻',
            true,
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Data Science Bundle',
            'Complete data analysis toolkit',
            '["Analyst Spirit", "Researcher Spirit", "Mathematician Spirit", "Checker Spirit"]',
            16.97,
            11.99,
            4.98,
            29,
            120,
            'Data & Analysis',
            '📊',
            false,
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Business Professional Bundle',
            'Business consulting and communication',
            '["Consultant Spirit", "Communicator Spirit", "Scheduler Spirit", "Analyst Spirit"]',
            25.97,
            17.99,
            7.98,
            31,
            180,
            'Business & Communication',
            '💼',
            false,
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Ultimate Creator Bundle',
            'Everything you need for content and design',
            '["Writer Spirit", "Creative Spirit", "Designer Spirit", "Translator Spirit", "Educator Spirit"]',
            32.96,
            19.99,
            12.97,
            39,
            200,
            'Premium Creative',
            '🎨',
            true,
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Security Expert Bundle',
            'Complete security and compliance toolkit',
            '["Security Spirit", "Analyst Spirit", "Debugger Spirit", "Checker Spirit"]',
            27.97,
            18.99,
            8.98,
            32,
            190,
            'Security & Compliance',
            '🔒',
            false,
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            'Complete Collection',
            'All spirits - ultimate power user package',
            '["Writer Spirit", "Creative Spirit", "Translator Spirit", "Analyst Spirit", "Researcher Spirit", "Mathematician Spirit", "Builder Spirit", "Debugger Spirit", "DevOps Spirit", "Connector Spirit", "Communicator Spirit", "Scheduler Spirit", "Checker Spirit", "Security Spirit", "Educator Spirit", "Designer Spirit", "Consultant Spirit", "Healer Spirit"]',
            142.86,
            79.99,
            62.87,
            44,
            800,
            'Ultimate',
            '🌟',
            true,
            true,
            CURRENT_TIMESTAMP
        );

-- Insert Subscription Plans
INSERT INTO subscription_plans (
            name, price_usd, billing_cycle, free_spirits, discount_on_purchases,
            exclusive_spirits, max_minions, max_spirits_per_minion, features,
            is_active, created_at
        ) VALUES (
            'Free Plan',
            0.0,
            'monthly',
            '["Writer Spirit", "Analyst Spirit", "Builder Spirit", "Connector Spirit", "Checker Spirit"]',
            0,
            '[]',
            2,
            3,
            '["Basic spirit access", "Community support", "Standard templates"]',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO subscription_plans (
            name, price_usd, billing_cycle, free_spirits, discount_on_purchases,
            exclusive_spirits, max_minions, max_spirits_per_minion, features,
            is_active, created_at
        ) VALUES (
            'Creator Plan',
            9.99,
            'monthly',
            '["Writer Spirit", "Creative Spirit", "Analyst Spirit", "Builder Spirit", "Connector Spirit", "Checker Spirit", "Communicator Spirit"]',
            20,
            '[]',
            5,
            4,
            '["7 free spirits", "20% off purchases", "Priority support", "Advanced templates", "Early access to new spirits"]',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO subscription_plans (
            name, price_usd, billing_cycle, free_spirits, discount_on_purchases,
            exclusive_spirits, max_minions, max_spirits_per_minion, features,
            is_active, created_at
        ) VALUES (
            'Professional Plan',
            19.99,
            'monthly',
            '["Writer Spirit", "Creative Spirit", "Analyst Spirit", "Researcher Spirit", "Builder Spirit", "Debugger Spirit", "Connector Spirit", "Communicator Spirit", "Checker Spirit", "Security Spirit"]',
            35,
            '[]',
            10,
            5,
            '["10 free spirits", "35% off purchases", "Premium support", "Custom templates", "Beta access", "API access"]',
            true,
            CURRENT_TIMESTAMP
        );
INSERT INTO subscription_plans (
            name, price_usd, billing_cycle, free_spirits, discount_on_purchases,
            exclusive_spirits, max_minions, max_spirits_per_minion, features,
            is_active, created_at
        ) VALUES (
            'Enterprise Plan',
            49.99,
            'monthly',
            '"ALL"',
            50,
            '["Consultant Spirit", "Healer Spirit"]',
            -1,
            5,
            '["All spirits included", "50% off bundles", "White-glove support", "Custom integrations", "Team management", "Advanced analytics"]',
            true,
            CURRENT_TIMESTAMP
        );