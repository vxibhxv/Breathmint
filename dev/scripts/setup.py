#!/usr/bin/env python3
"""
Setup and Migration Script for Power Rangers: Neo Seoul
Handles initialization and migration from old file structure
"""
import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import config

logger = logging.getLogger(__name__)

class GameSetup:
    """
    Handles game setup and data migration
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.old_files = [
            'nodes.json', 'events.json', 'players.json', 
            'saves.json', 'characters.json'
        ]
    
    def run_full_setup(self) -> bool:
        """Run complete setup process"""
        print("🚀 Power Rangers: Neo Seoul - Setup & Migration")
        print("=" * 60)
        
        success = True
        
        # Step 1: Create directory structure
        if not self.create_directories():
            success = False
        
        # Step 2: Migrate existing data files
        if not self.migrate_data_files():
            success = False
        
        # Step 3: Initialize missing data files
        if not self.initialize_data_files():
            success = False
        
        # Step 4: Validate setup
        if not self.validate_setup():
            success = False
        
        # Step 5: Create .env file if needed
        self.create_env_file()
        
        if success:
            print("\n✅ Setup completed successfully!")
            print("\n🎮 You can now run the game with:")
            print("   python main.py")
            print("\n🧪 Or run tests with:")
            print("   python main.py --test")
        else:
            print("\n❌ Setup completed with errors. Check the messages above.")
        
        return success
    
    def create_directories(self) -> bool:
        """Create necessary directory structure"""
        print("\n📁 Creating directory structure...")
        
        directories = [
            'core',
            'game', 
            'combat',
            'data',
            'logs',
            'scripts',
            'tests'
        ]
        
        try:
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(exist_ok=True)
                print(f"  ✓ {directory}/")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error creating directories: {e}")
            return False
    
    def migrate_data_files(self) -> bool:
        """Migrate existing data files to new structure"""
        print("\n📦 Migrating existing data files...")
        
        migrated_count = 0
        
        for filename in self.old_files:
            old_path = self.project_root / filename
            new_path = config.data_dir / filename
            
            if old_path.exists():
                try:
                    if not new_path.exists():
                        shutil.copy2(old_path, new_path)
                        print(f"  ✓ Migrated {filename}")
                        migrated_count += 1
                    else:
                        print(f"  ⚠️ {filename} already exists in data/")
                except Exception as e:
                    print(f"  ❌ Error migrating {filename}: {e}")
            else:
                print(f"  - {filename} not found (will be created)")
        
        if migrated_count > 0:
            print(f"  📋 Migrated {migrated_count} files")
        
        return True
    
    def initialize_data_files(self) -> bool:
        """Initialize missing data files with defaults"""
        print("\n🏗️ Initializing data files...")
        
        default_data = {
            'nodes.json': self._get_default_nodes(),
            'events.json': self._get_default_events(),
            'players.json': self._get_default_players(),
            'saves.json': {},
            'characters.json': self._get_default_characters()
        }
        
        initialized_count = 0
        
        for filename, default_content in default_data.items():
            file_path = config.data_dir / filename
            
            if not file_path.exists():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_content, f, indent=2, ensure_ascii=False)
                    print(f"  ✓ Created {filename}")
                    initialized_count += 1
                except Exception as e:
                    print(f"  ❌ Error creating {filename}: {e}")
                    return False
            else:
                print(f"  ✓ {filename} exists")
        
        if initialized_count > 0:
            print(f"  📋 Initialized {initialized_count} files")
        
        return True
    
    def _get_default_nodes(self) -> Dict[str, Any]:
        """Get default node data"""
        return {
            "hotel_room": {
                "name": "hotel_room",
                "characters": ["tourist"],
                "description": "A brown room with softly glowing lights. It's a little cramped, but it smells like you. Clothes are strewn across the room. A bed, a table and chair, and a bathroom door make up the sparse furnishings. Your passport and empty wallet lie on the nightstand.",
                "events": ["tourist_hotel_awakening"],
                "connections": ["hotel_lobby", "bar"],
                "items": ["passport", "empty_wallet", "green_flowery_shirt", "green_shorts"]
            },
            "hotel_lobby": {
                "name": "hotel_lobby",
                "characters": [],
                "description": "A small, dimly lit lobby with peeling wallpaper and flickering lights. The reception desk is unmanned most of the time. A few tattered tourist brochures advertise local attractions in faded colors.",
                "events": [],
                "connections": ["hotel_room", "street"],
                "items": ["tourist_brochure"]
            }
        }
    
    def _get_default_events(self) -> Dict[str, Any]:
        """Get default event data"""
        return {
            "tourist_hotel_awakening": {
                "name": "tourist_hotel_awakening",
                "description": "A tourist wakes up hungover in a hotel room in Seoul with an empty wallet",
                "event_type": "conversation",
                "characters": ["tourist"],
                "start_node": "hotel_room",
                "end_node": "hotel_room",
                "consequence": [
                    "Your head hurts. You move like you're underwater, eyes heavy, skull sloshing like a balloon.",
                    "You tumble off the bed, landing with the grace of a bull. You see a passport with your name and face on it. A wallet, with no money.",
                    "You're wearing a green flowery shirt, and green quilted shorts. Time to explore Seoul."
                ]
            }
        }
    
    def _get_default_players(self) -> Dict[str, Any]:
        """Get default player data"""
        return {
            "Tourist": {
                "name": "Tourist",
                "health": 100,
                "max_health": 100,
                "inventory": ["joint", "hotel_key"],
                "stats": {"strength": 10, "intelligence": 10},
                "location": "hotel_room",
                "relationships": {}
            }
        }
    
    def _get_default_characters(self) -> Dict[str, Any]:
        """Get default character data"""
        return {
            "tourist": {
                "name": "Tourist",
                "description": "A backpacker exploring Seoul",
                "events": ["tourist_hotel_awakening"],
                "nodes": ["hotel_room"]
            }
        }
    
    def validate_setup(self) -> bool:
        """Validate that setup was successful"""
        print("\n🔍 Validating setup...")
        
        # Check directories
        required_dirs = ['core', 'game', 'data', 'logs']
        for directory in required_dirs:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                print(f"  ❌ Missing directory: {directory}")
                return False
        
        print("  ✓ All directories exist")
        
        # Check data files
        for filename in self.old_files:
            file_path = config.data_dir / filename
            if not file_path.exists():
                print(f"  ❌ Missing data file: {filename}")
                return False
            
            # Try to load as JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except Exception as e:
                print(f"  ❌ Invalid JSON in {filename}: {e}")
                return False
        
        print("  ✓ All data files valid")
        
        # Test imports
        try:
            from core.config import config
            from core.ai_client import ai_client
            from game.engine import GameEngine
            print("  ✓ All imports successful")
        except Exception as e:
            print(f"  ❌ Import error: {e}")
            return False
        
        return True
    
    def create_env_file(self):
        """Create .env file if it doesn't exist"""
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_file.exists():
            if env_example.exists():
                try:
                    shutil.copy2(env_example, env_file)
                    print(f"\n📝 Created .env file from .env.example")
                    print("   Edit .env to configure your API key and preferences")
                except Exception as e:
                    print(f"  ⚠️ Could not create .env file: {e}")
            else:
                # Create basic .env file
                basic_env = """# Power Rangers: Neo Seoul Configuration
# Copy your Anthropic API key here
ANTHROPIC_API_KEY=your_key_here

# Game settings
DEFAULT_PLAYER=Tourist
LOG_LEVEL=INFO
"""
                try:
                    with open(env_file, 'w') as f:
                        f.write(basic_env)
                    print(f"\n📝 Created basic .env file")
                    print("   Edit .env to add your Anthropic API key")
                except Exception as e:
                    print(f"  ⚠️ Could not create .env file: {e}")
    
    def clean_old_files(self) -> bool:
        """Clean up old files after successful migration"""
        print("\n🧹 Cleaning up old files...")
        
        # List of old files that can be safely removed after migration
        old_files_to_clean = [
            'game_ai.py.backup',
            'game_ai.py.emergency_backup', 
            'safe_anthropic.py',
            'safe_anthropic_emergency.py',
            'emergency_anthropic.py',
            'emergency_hotfix.py',
            'emergency_test_game.py',
            'ONE_LINE_FIX.py'
        ]
        
        cleaned_count = 0
        
        for filename in old_files_to_clean:
            file_path = self.project_root / filename
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"  ✓ Removed {filename}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ⚠️ Could not remove {filename}: {e}")
        
        if cleaned_count > 0:
            print(f"  📋 Cleaned up {cleaned_count} old files")
        else:
            print("  - No old files to clean")
        
        return True

def main():
    """Main setup function"""
    setup = GameSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        setup.clean_old_files()
    else:
        setup.run_full_setup()

if __name__ == "__main__":
    main()