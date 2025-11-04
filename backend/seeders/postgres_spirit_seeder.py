#!/usr/bin/env python3
"""
PostgreSQL Spirit System Seeder
Populates the PostgreSQL database with spirit system data
"""

import sys
import os
import json
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres_connection import create_spirit_engine
from sqlalchemy.orm import sessionmaker
from model.spirit_models import (
    SpiritRegistry, MinionSpirit, SpiritMastery, SpiritBundle,
    SubscriptionPlan, UserSpiritPurchase, UserSpiritSubscription,
    UserPoints, PointsTransaction, UserSpiritAccess, ToolRegistry, SpiritMinion
)
from seeders.spirit_system_seeder import (
    create_spirits_data,
    create_minion_templates,
    create_tools_registry
)
from seeders.spirit_purchase_seeder import (
    create_spirit_purchase_data,
    create_skillset_bundles,
    create_subscription_benefits
)

def seed_spirits_registry(session):
    """Seed spirits registry with all spirit data"""
    print("📊 Seeding spirits registry...")
    
    spirits_data = create_spirits_data()
    spirit_pricing = create_spirit_purchase_data()
    
    # Flatten pricing data
    all_pricing = {}
    for tier_spirits in spirit_pricing.values():
        all_pricing.update(tier_spirits)
    
    spirits_created = 0
    for spirit_data in spirits_data:
        # Get pricing information
        spirit_name = spirit_data['name']
        pricing = all_pricing.get(spirit_name, {'usd': 0.00, 'points': 0, 'tier': 'free'})
        
        # Create spirit record
        spirit = SpiritRegistry(
            name=spirit_data['name'],
            category=spirit_data['category'],
            description=spirit_data['description'],
            icon=spirit_data['icon'],
            unlock_rank=spirit_data['unlock_rank'],
            unlock_level=spirit_data['unlock_level'],
            max_spirit_level=spirit_data['max_spirit_level'],
            tools=spirit_data['tools'],
            synergies=spirit_data['synergies'],
            conflicts=spirit_data['conflicts'],
            is_active=spirit_data['is_active'],
            price_usd=float(pricing['usd']),
            price_points=pricing['points'],
            tier=pricing['tier'],
            is_premium=pricing['tier'] in ['professional', 'premium'],
            free_with_subscription=pricing['tier'] == 'free'
        )
        
        session.add(spirit)
        spirits_created += 1
    
    session.commit()
    print(f"✅ Created {spirits_created} spirits")
    return spirits_created

def seed_tools_registry(session):
    """Seed tools registry with all tool data"""
    print("🛠️ Seeding tools registry...")
    
    tools_data = create_tools_registry()
    
    tools_created = 0
    for tool_data in tools_data:
        tool = ToolRegistry(
            name=tool_data['name'],
            category=tool_data['category'],
            description=tool_data['description'],
            is_active=True
        )
        
        session.add(tool)
        tools_created += 1
    
    session.commit()
    print(f"✅ Created {tools_created} tools")
    return tools_created

def seed_spirit_bundles(session):
    """Seed spirit bundles with purchase data"""
    print("📦 Seeding spirit bundles...")
    
    bundles_data = create_skillset_bundles()
    
    bundles_created = 0
    for bundle_data in bundles_data:
        bundle = SpiritBundle(
            name=bundle_data['name'],
            description=bundle_data['description'],
            spirits=bundle_data['spirits'],
            original_price_usd=float(bundle_data['original_price_usd']),
            bundle_price_usd=float(bundle_data['bundle_price_usd']),
            savings_usd=float(bundle_data['savings_usd']),
            savings_percentage=bundle_data['savings_percentage'],
            points_cost=bundle_data['points_cost'],
            category=bundle_data['category'],
            icon=bundle_data['icon'],
            is_popular=bundle_data['popular'],
            is_active=True
        )
        
        session.add(bundle)
        bundles_created += 1
    
    session.commit()
    print(f"✅ Created {bundles_created} bundles")
    return bundles_created

def seed_subscription_plans(session):
    """Seed subscription plans with benefits data"""
    print("📋 Seeding subscription plans...")
    
    plans_data = create_subscription_benefits()
    
    plans_created = 0
    for plan_data in plans_data:
        plan = SubscriptionPlan(
            name=plan_data['name'],
            price_usd=float(plan_data['price_usd']),
            billing_cycle=plan_data['billing_cycle'],
            free_spirits=plan_data['free_spirits'],
            discount_on_purchases=plan_data['discount_on_purchases'],
            exclusive_spirits=plan_data['exclusive_spirits'],
            max_minions=plan_data['max_minions'],
            max_spirits_per_minion=plan_data['max_spirits_per_minion'],
            features=plan_data['features'],
            is_active=True
        )
        
        session.add(plan)
        plans_created += 1
    
    session.commit()
    print(f"✅ Created {plans_created} subscription plans")
    return plans_created

def seed_database():
    """Main seeding function"""
    print("🌱 Seeding PostgreSQL Spirit System Database")
    print("=" * 60)
    
    try:
        # Create engine and session
        engine = create_spirit_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            # Seed all data
            spirits_count = seed_spirits_registry(session)
            tools_count = seed_tools_registry(session)
            bundles_count = seed_spirit_bundles(session)
            plans_count = seed_subscription_plans(session)
            
            print("\n🎉 PostgreSQL Spirit System Seeding Complete!")
            print("📊 Seeding Summary:")
            print(f"   📊 {spirits_count} Spirits")
            print(f"   🛠️ {tools_count} Tools")
            print(f"   📦 {bundles_count} Bundles")
            print(f"   📋 {plans_count} Subscription Plans")
            
            print("\n🔧 Database Ready For:")
            print("   - Spirit selection and assignment")
            print("   - Purchase processing")
            print("   - Subscription management")
            print("   - Points system")
            print("   - Minion creation with spirits")
            
            return True
        finally:
            session.close()
            
    except Exception as e:
        print(f"\n❌ Seeding failed: {e}")
        return False

def main():
    """Main function"""
    success = seed_database()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
