#!/usr/bin/env python3
"""
Power Rangers: Neo Seoul - Main Entry Point
Improved backend with centralized AI handling and robust error management
"""
import sys
import logging
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config
from core.ai_client import ai_client
from game.engine import GameEngine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.logs_dir / 'game.log')
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print game banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🤖 POWER RANGERS: NEO SEOUL 🤖                       ║
    ║                                                              ║
    ║           Enhanced Text Adventure Game                       ║
    ║        With AI-Powered Natural Language Processing           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_system_status():
    """Print current system status"""
    ai_status = ai_client.get_status()
    config_info = config.get_safe_dict()
    
    print("=" * 60)
    print("SYSTEM STATUS")
    print("=" * 60)
    print(f"🤖 AI Client:      {'✅ ONLINE' if ai_status['available'] else '❌ OFFLINE'}")
    print(f"🧠 AI Model:       {ai_status['model']}")
    print(f"📁 Data Directory: {config_info['data_dir']}")
    print(f"👤 Default Player: {config_info['default_player']}")
    print(f"🏠 Default Location: {config_info['default_location']}")
    
    if not ai_status['available'] and ai_status['last_error']:
        print(f"⚠️  AI Error:       {ai_status['last_error']}")
        print("   Game will run in basic mode with rule-based responses.")
    
    print("=" * 60)

def run_interactive_game(player_name: str = None):
    """Run interactive game session"""
    try:
        print_banner()
        print_system_status()
        
        print("\nInitializing game engine...")
        engine = GameEngine()
        
        if not engine.start_game(player_name):
            print("❌ Failed to start game. Please check the logs.")
            return False
        
        print("✅ Game started successfully!")
        print("\n" + "=" * 60)
        print("GAME COMMANDS")
        print("=" * 60)
        print("• Type naturally: 'look around', 'go to lobby', 'talk to person'")
        print("• Special commands: 'help', 'status', 'inventory', 'save', 'quit'")
        print("• AI Status: 'ai_status' (shows current AI system status)")
        print("=" * 60)
        
        # Show initial location
        initial_response = engine.process_input("look")
        print(f"\n{initial_response}")
        
        # Main game loop
        while engine.running:
            try:
                print()  # Empty line for readability
                user_input = input("🎮 > ").strip()
                
                if not user_input:
                    continue
                
                response = engine.process_input(user_input)
                print(f"\n{response}")
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Game interrupted by user.")
                print("Saving game...")
                engine.save_game()
                break
            except EOFError:
                print("\nGoodbye!")
                engine.save_game()
                break
        
        engine.shutdown()
        print("\n👋 Thanks for playing Power Rangers: Neo Seoul!")
        return True
        
    except Exception as e:
        logger.error(f"Fatal error in interactive game: {e}")
        print(f"💥 Fatal error: {e}")
        return False

def run_test_mode():
    """Run comprehensive test suite"""
    try:
        from scripts.test_game import GameTester
        
        print_banner()
        print("🧪 Running in TEST MODE")
        
        tester = GameTester()
        success = tester.run_all_tests()
        
        return success
        
    except ImportError:
        print("❌ Test suite not available. Please check scripts/test_game.py")
        return False
    except Exception as e:
        logger.error(f"Test mode error: {e}")
        print(f"💥 Test mode error: {e}")
        return False

def run_api_mode(port: int = 5000):
    """Run API server mode (for frontend integration)"""
    try:
        print_banner()
        print(f"🌐 Running in API SERVER MODE on port {port}")
        print("This would start a Flask/FastAPI server for frontend integration")
        print("API mode not yet implemented - use interactive mode for now")
        return False
        
    except Exception as e:
        logger.error(f"API mode error: {e}")
        print(f"💥 API mode error: {e}")
        return False

def main():
    """Main entry point with command line argument handling"""
    parser = argparse.ArgumentParser(
        description="Power Rangers: Neo Seoul - Enhanced Text Adventure Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Interactive game mode
  python main.py --player Tourist        # Start with specific player
  python main.py --test                   # Run test suite
  python main.py --api --port 5000       # API server mode (future)
        """
    )
    
    parser.add_argument(
        '--player', '-p',
        type=str,
        help='Player name to load/create (default: Tourist)'
    )
    
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Run comprehensive test suite'
    )
    
    parser.add_argument(
        '--api', '-a',
        action='store_true',
        help='Run API server mode for frontend integration'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for API server mode (default: 5000)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run appropriate mode
    try:
        if args.test:
            success = run_test_mode()
        elif args.api:
            success = run_api_mode(args.port)
        else:
            success = run_interactive_game(args.player)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())