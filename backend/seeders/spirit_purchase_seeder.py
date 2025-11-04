#!/usr/bin/env python3
"""
Spirit Purchase System Seeder
Adds purchase capabilities to the spirit system

This seeder creates:
1. Purchase information for all spirits (USD prices, points, premium tiers)
2. Skillset bundles for bulk purchases
3. Subscription benefits and free spirits
4. Purchase history tracking schema
"""

import sys
import os
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_spirit_purchase_data():
    """Create spirit purchase information"""
    
    # Pricing tiers based on spirit power and unlock requirements
    spirit_pricing = {
        # FREE TIER - Basic spirits (free with account)
        "free_tier": {
            "Writer Spirit": {"usd": 0.00, "points": 0, "tier": "free"},
            "Analyst Spirit": {"usd": 0.00, "points": 0, "tier": "free"},
            "Builder Spirit": {"usd": 0.00, "points": 0, "tier": "free"},
            "Connector Spirit": {"usd": 0.00, "points": 0, "tier": "free"},
            "Checker Spirit": {"usd": 0.00, "points": 0, "tier": "free"}
        },
        
        # BASIC TIER - $2.99-$4.99 (affordable for most users)
        "basic_tier": {
            "Creative Spirit": {"usd": 2.99, "points": 30, "tier": "basic"},
            "Researcher Spirit": {"usd": 3.99, "points": 40, "tier": "basic"},
            "Debugger Spirit": {"usd": 4.99, "points": 50, "tier": "basic"},
            "Communicator Spirit": {"usd": 3.99, "points": 40, "tier": "basic"},
            "Scheduler Spirit": {"usd": 2.99, "points": 30, "tier": "basic"},
            "Translator Spirit": {"usd": 4.99, "points": 50, "tier": "basic"}
        },
        
        # PROFESSIONAL TIER - $7.99-$12.99 (specialized spirits)
        "professional_tier": {
            "Mathematician Spirit": {"usd": 7.99, "points": 80, "tier": "professional"},
            "DevOps Spirit": {"usd": 9.99, "points": 100, "tier": "professional"},
            "Security Spirit": {"usd": 12.99, "points": 130, "tier": "professional"},
            "Educator Spirit": {"usd": 8.99, "points": 90, "tier": "professional"},
            "Designer Spirit": {"usd": 9.99, "points": 100, "tier": "professional"}
        },
        
        # PREMIUM TIER - $14.99-$19.99 (advanced/expert spirits)
        "premium_tier": {
            "Consultant Spirit": {"usd": 14.99, "points": 150, "tier": "premium"},
            "Healer Spirit": {"usd": 16.99, "points": 170, "tier": "premium"}
        }
    }
    
    return spirit_pricing

def create_skillset_bundles():
    """Create skillset bundles for bulk purchases"""
    
    bundles = [
        {
            "name": "Content Creator Bundle",
            "description": "Complete content creation toolkit",
            "spirits": ["Writer Spirit", "Creative Spirit", "Translator Spirit", "Designer Spirit"],
            "original_price_usd": 18.96,
            "bundle_price_usd": 12.99,
            "savings_usd": 5.97,
            "savings_percentage": 31,
            "points_cost": 130,
            "category": "Content & Creative",
            "icon": "📝",
            "popular": True
        },
        {
            "name": "Developer Pro Bundle",
            "description": "Full-stack development powerhouse",
            "spirits": ["Builder Spirit", "Debugger Spirit", "DevOps Spirit", "Security Spirit", "Analyst Spirit"],
            "original_price_usd": 32.96,
            "bundle_price_usd": 19.99,
            "savings_usd": 12.97,
            "savings_percentage": 39,
            "points_cost": 200,
            "category": "Development & Technical",
            "icon": "💻",
            "popular": True
        },
        {
            "name": "Data Science Bundle",
            "description": "Complete data analysis toolkit",
            "spirits": ["Analyst Spirit", "Researcher Spirit", "Mathematician Spirit", "Checker Spirit"],
            "original_price_usd": 16.97,
            "bundle_price_usd": 11.99,
            "savings_usd": 4.98,
            "savings_percentage": 29,
            "points_cost": 120,
            "category": "Data & Analysis",
            "icon": "📊",
            "popular": False
        },
        {
            "name": "Business Professional Bundle",
            "description": "Business consulting and communication",
            "spirits": ["Consultant Spirit", "Communicator Spirit", "Scheduler Spirit", "Analyst Spirit"],
            "original_price_usd": 25.97,
            "bundle_price_usd": 17.99,
            "savings_usd": 7.98,
            "savings_percentage": 31,
            "points_cost": 180,
            "category": "Business & Communication",
            "icon": "💼",
            "popular": False
        },
        {
            "name": "Ultimate Creator Bundle",
            "description": "Everything you need for content and design",
            "spirits": ["Writer Spirit", "Creative Spirit", "Designer Spirit", "Translator Spirit", "Educator Spirit"],
            "original_price_usd": 32.96,
            "bundle_price_usd": 19.99,
            "savings_usd": 12.97,
            "savings_percentage": 39,
            "points_cost": 200,
            "category": "Premium Creative",
            "icon": "🎨",
            "popular": True
        },
        {
            "name": "Security Expert Bundle",
            "description": "Complete security and compliance toolkit",
            "spirits": ["Security Spirit", "Analyst Spirit", "Debugger Spirit", "Checker Spirit"],
            "original_price_usd": 27.97,
            "bundle_price_usd": 18.99,
            "savings_usd": 8.98,
            "savings_percentage": 32,
            "points_cost": 190,
            "category": "Security & Compliance",
            "icon": "🔒",
            "popular": False
        },
        {
            "name": "Complete Collection",
            "description": "All spirits - ultimate power user package",
            "spirits": [
                "Writer Spirit", "Creative Spirit", "Translator Spirit", "Analyst Spirit", 
                "Researcher Spirit", "Mathematician Spirit", "Builder Spirit", "Debugger Spirit", 
                "DevOps Spirit", "Connector Spirit", "Communicator Spirit", "Scheduler Spirit", 
                "Checker Spirit", "Security Spirit", "Educator Spirit", "Designer Spirit", 
                "Consultant Spirit", "Healer Spirit"
            ],
            "original_price_usd": 142.86,
            "bundle_price_usd": 79.99,
            "savings_usd": 62.87,
            "savings_percentage": 44,
            "points_cost": 800,
            "category": "Ultimate",
            "icon": "🌟",
            "popular": True
        }
    ]
    
    return bundles

def create_subscription_benefits():
    """Create subscription benefits for spirit access"""
    
    subscription_plans = [
        {
            "name": "Free Plan",
            "price_usd": 0.00,
            "billing_cycle": "monthly",
            "free_spirits": ["Writer Spirit", "Analyst Spirit", "Builder Spirit", "Connector Spirit", "Checker Spirit"],
            "discount_on_purchases": 0,
            "exclusive_spirits": [],
            "max_minions": 2,
            "max_spirits_per_minion": 3,
            "features": ["Basic spirit access", "Community support", "Standard templates"]
        },
        {
            "name": "Creator Plan",
            "price_usd": 9.99,
            "billing_cycle": "monthly",
            "free_spirits": ["Writer Spirit", "Creative Spirit", "Analyst Spirit", "Builder Spirit", "Connector Spirit", "Checker Spirit", "Communicator Spirit"],
            "discount_on_purchases": 20,
            "exclusive_spirits": [],
            "max_minions": 5,
            "max_spirits_per_minion": 4,
            "features": ["7 free spirits", "20% off purchases", "Priority support", "Advanced templates", "Early access to new spirits"]
        },
        {
            "name": "Professional Plan",
            "price_usd": 19.99,
            "billing_cycle": "monthly",
            "free_spirits": [
                "Writer Spirit", "Creative Spirit", "Analyst Spirit", "Researcher Spirit", 
                "Builder Spirit", "Debugger Spirit", "Connector Spirit", "Communicator Spirit", 
                "Checker Spirit", "Security Spirit"
            ],
            "discount_on_purchases": 35,
            "exclusive_spirits": [],
            "max_minions": 10,
            "max_spirits_per_minion": 5,
            "features": ["10 free spirits", "35% off purchases", "Premium support", "Custom templates", "Beta access", "API access"]
        },
        {
            "name": "Enterprise Plan",
            "price_usd": 49.99,
            "billing_cycle": "monthly",
            "free_spirits": "ALL",  # All spirits included
            "discount_on_purchases": 50,
            "exclusive_spirits": ["Consultant Spirit", "Healer Spirit"],
            "max_minions": -1,  # Unlimited
            "max_spirits_per_minion": 5,
            "features": ["All spirits included", "50% off bundles", "White-glove support", "Custom integrations", "Team management", "Advanced analytics"]
        }
    ]
    
    return subscription_plans

def create_purchase_tracking_schema():
    """Create database schema for purchase tracking"""
    
    schema_sql = """
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
"""
    
    return schema_sql

def generate_purchase_seeder_sql():
    """Generate SQL INSERT statements for purchase system"""
    
    spirit_pricing = create_spirit_purchase_data()
    bundles = create_skillset_bundles()
    subscription_plans = create_subscription_benefits()
    schema_sql = create_purchase_tracking_schema()
    
    sql_statements = []
    
    # Add header
    sql_statements.append("-- Spirit Purchase System Seeder")
    sql_statements.append("-- Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sql_statements.append("")
    
    # Add schema
    sql_statements.append("-- Purchase System Schema")
    sql_statements.append(schema_sql)
    sql_statements.append("")
    
    # Update spirits with pricing information
    sql_statements.append("-- Update Spirits with Pricing Information")
    
    all_spirits = {}
    for tier, spirits in spirit_pricing.items():
        all_spirits.update(spirits)
    
    for spirit_name, pricing in all_spirits.items():
        sql = f"""UPDATE spirits_registry SET 
            price_usd = {pricing['usd']},
            price_points = {pricing['points']},
            tier = '{pricing['tier']}',
            is_premium = {str(pricing['tier'] in ['professional', 'premium']).lower()},
            free_with_subscription = {str(pricing['tier'] == 'free').lower()}
        WHERE name = '{spirit_name}';"""
        sql_statements.append(sql)
    
    sql_statements.append("")
    
    # Insert bundles
    sql_statements.append("-- Insert Spirit Bundles")
    for bundle in bundles:
        sql = f"""INSERT INTO spirit_bundles (
            name, description, spirits, original_price_usd, bundle_price_usd,
            savings_usd, savings_percentage, points_cost, category, icon,
            is_popular, is_active, created_at
        ) VALUES (
            '{bundle['name']}',
            '{bundle['description']}',
            '{json.dumps(bundle['spirits'])}',
            {bundle['original_price_usd']},
            {bundle['bundle_price_usd']},
            {bundle['savings_usd']},
            {bundle['savings_percentage']},
            {bundle['points_cost']},
            '{bundle['category']}',
            '{bundle['icon']}',
            {str(bundle['popular']).lower()},
            true,
            CURRENT_TIMESTAMP
        );"""
        sql_statements.append(sql)
    
    sql_statements.append("")
    
    # Insert subscription plans
    sql_statements.append("-- Insert Subscription Plans")
    for plan in subscription_plans:
        free_spirits = plan['free_spirits']
        if isinstance(free_spirits, list):
            free_spirits_json = json.dumps(free_spirits)
        else:
            free_spirits_json = f'"{free_spirits}"'
        
        sql = f"""INSERT INTO subscription_plans (
            name, price_usd, billing_cycle, free_spirits, discount_on_purchases,
            exclusive_spirits, max_minions, max_spirits_per_minion, features,
            is_active, created_at
        ) VALUES (
            '{plan['name']}',
            {plan['price_usd']},
            '{plan['billing_cycle']}',
            '{free_spirits_json}',
            {plan['discount_on_purchases']},
            '{json.dumps(plan['exclusive_spirits'])}',
            {plan['max_minions']},
            {plan['max_spirits_per_minion']},
            '{json.dumps(plan['features'])}',
            true,
            CURRENT_TIMESTAMP
        );"""
        sql_statements.append(sql)
    
    return sql_statements

def main():
    """Main seeder function"""
    print("💰 Spirit Purchase System Seeder")
    print("=" * 50)
    
    # Generate data
    spirit_pricing = create_spirit_purchase_data()
    bundles = create_skillset_bundles()
    subscription_plans = create_subscription_benefits()
    
    print(f"✅ Generated pricing for {sum(len(tier) for tier in spirit_pricing.values())} spirits")
    print(f"✅ Generated {len(bundles)} spirit bundles")
    print(f"✅ Generated {len(subscription_plans)} subscription plans")
    
    # Generate SQL
    sql_statements = generate_purchase_seeder_sql()
    
    # Write to file
    output_file = "spirit_purchase_seeder.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✅ SQL seeder written to: {output_file}")
    
    # Write JSON data files
    with open("spirit_pricing.json", 'w', encoding='utf-8') as f:
        json.dump(spirit_pricing, f, indent=2, ensure_ascii=False)
    
    with open("spirit_bundles.json", 'w', encoding='utf-8') as f:
        json.dump(bundles, f, indent=2, ensure_ascii=False)
    
    with open("subscription_plans.json", 'w', encoding='utf-8') as f:
        json.dump(subscription_plans, f, indent=2, ensure_ascii=False)
    
    print("✅ JSON data files created:")
    print("   - spirit_pricing.json")
    print("   - spirit_bundles.json")
    print("   - subscription_plans.json")
    
    print("\n💰 Purchase System Summary:")
    print(f"   💵 {len(spirit_pricing['free_tier'])} Free Spirits")
    print(f"   💰 {len(spirit_pricing['basic_tier'])} Basic Spirits ($2.99-$4.99)")
    print(f"   💎 {len(spirit_pricing['professional_tier'])} Professional Spirits ($7.99-$12.99)")
    print(f"   👑 {len(spirit_pricing['premium_tier'])} Premium Spirits ($14.99-$19.99)")
    print(f"   📦 {len(bundles)} Spirit Bundles (up to 44% savings)")
    print(f"   📋 {len(subscription_plans)} Subscription Plans")
    
    print("\n🚀 Ready for monetization implementation!")

if __name__ == "__main__":
    main()
