#!/usr/bin/env python3
"""
One-Click Installation for Power Rangers: Neo Seoul Enhanced Backend
Handles complete setup including dependencies, data migration, and testing
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print installation banner"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║  🤖 POWER RANGERS: NEO SEOUL - ENHANCED BACKEND 🤖  ║
    ║                                                      ║
    ║              One-Click Installation                  ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def print_step(step_num, total_steps, description):
    """Print installation step"""
    print(f"\n📦 Step {step_num}/{total_steps}: {description}")
    print("-" * 50)

def run_command(command, description, check=True):
    """Run a command with error handling"""
    print(f"  🔄 {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {description} completed successfully")
            return True
        else:
            print(f"  ⚠️ {description} completed with warnings")
            if result.stderr:
                print(f"     Warning: {result.stderr[:100]}")
            return not check  # Return True if check=False, False if check=True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ {description} failed: {e}")
        if e.stderr:
            print(f"     Error: {e.stderr[:200]}")
        return False
    except Exception as e:
        print(f"  💥 {description} crashed: {e}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        print("   Please upgrade Python and try again.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("  ⚠️ requirements.txt not found, creating basic requirements...")
        basic_requirements = """anthropic>=0.25.7,<0.30.0
pathlib2>=2.3.0
python-dotenv>=1.0.0
pytest>=7.3.0
colorlog>=6.7.0
"""
        with open(requirements_file, 'w') as f:
            f.write(basic_requirements)
    
    # Upgrade pip first
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      "Upgrading pip", check=False):
        print("  ⚠️ Pip upgrade failed, continuing with existing version...")
    
    # Install requirements
    return run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Installing Python dependencies")

def setup_project_structure():
    """Set up project directory structure"""
    try:
        # Create __init__.py files for packages
        packages = ['core', 'game', 'combat', 'scripts', 'tests']
        
        for package in packages:
            package_dir = Path(package)
            package_dir.mkdir(exist_ok=True)
            
            init_file = package_dir / '__init__.py'
            if not init_file.exists():
                init_file.touch()
        
        # Create other necessary directories
        other_dirs = ['data', 'logs']
        for directory in other_dirs:
            Path(directory).mkdir(exist_ok=True)
        
        print("  ✅ Project structure created")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create project structure: {e}")
        return False

def run_setup_script():
    """Run the main setup script"""
    setup_script = Path("scripts/setup.py")
    
    if setup_script.exists():
        return run_command([sys.executable, str(setup_script)], 
                          "Running setup and migration script")
    else:
        print("  ⚠️ Setup script not found, creating basic data structure...")
        return setup_project_structure()

def run_tests():
    """Run test suite to validate installation"""
    test_script = Path("main.py")
    
    if test_script.exists():
        print("  🧪 Running test suite...")
        return run_command([sys.executable, str(test_script), "--test"], 
                          "Running comprehensive tests", check=False)
    else:
        print("  ⚠️ Test script not found, skipping tests")
        return True

def create_launch_shortcuts():
    """Create convenient launch shortcuts"""
    try:
        # Create batch file for Windows
        if platform.system() == "Windows":
            batch_content = f'''@echo off
cd /d "{Path.cwd()}"
"{sys.executable}" main.py
pause
'''
            with open("start_game.bat", 'w') as f:
                f.write(batch_content)
            print("  ✅ Created start_game.bat")
        
        # Create shell script for Unix-like systems
        else:
            script_content = f'''#!/bin/bash
cd "{Path.cwd()}"
"{sys.executable}" main.py
'''
            script_path = Path("start_game.sh")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable
            os.chmod(script_path, 0o755)
            print("  ✅ Created start_game.sh")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️ Could not create launch shortcuts: {e}")
        return True  # Not critical

def display_completion_info():
    """Display installation completion information"""
    print("\n" + "=" * 60)
    print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n🚀 How to start playing:")
    print("   python main.py")
    
    if platform.system() == "Windows" and Path("start_game.bat").exists():
        print("   OR double-click: start_game.bat")
    elif Path("start_game.sh").exists():
        print("   OR run: ./start_game.sh")
    
    print("\n🧪 How to run tests:")
    print("   python main.py --test")
    
    print("\n📖 Available commands:")
    print("   python main.py --help          # Show all options")
    print("   python main.py --player Tourist # Start with specific player")
    print("   python scripts/demo.py         # Run interactive demo")
    
    print("\n⚙️ Configuration:")
    print("   Edit .env file to add your Anthropic API key")
    print("   Game works offline without API key (basic mode)")
    
    print("\n📁 Important files:")
    print("   main.py           # Main game launcher")
    print("   .env              # Configuration file")
    print("   data/             # Game data files")
    print("   logs/game.log     # Game log file")
    
    print("\n🤖 AI Status:")
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "ANTHROPIC_API_KEY" in content and "your_key_here" not in content:
                    print("   ✅ API key configured - AI features enabled")
                else:
                    print("   ⚠️ Edit .env to add API key for AI features")
        except:
            print("   ⚠️ Edit .env to configure API key")
    else:
        print("   ⚠️ No .env file - game will run in basic mode")
    
    print("\n" + "=" * 60)
    print("Happy gaming! 🎮✨")
    print("=" * 60)

def main():
    """Main installation function"""
    print_banner()
    
    print("🔍 This installer will:")
    print("  • Check Python compatibility")
    print("  • Install required dependencies") 
    print("  • Set up project structure")
    print("  • Migrate existing data files")
    print("  • Run comprehensive tests")
    print("  • Create launch shortcuts")
    
    try:
        input("\nPress ENTER to start installation, or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\n👋 Installation cancelled by user.")
        return 0
    
    total_steps = 6
    current_step = 0
    
    # Step 1: Check Python version
    current_step += 1
    print_step(current_step, total_steps, "Checking Python compatibility")
    if not check_python_version():
        return 1
    
    # Step 2: Install dependencies
    current_step += 1
    print_step(current_step, total_steps, "Installing dependencies")
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check the errors above.")
        return 1
    
    # Step 3: Set up project structure
    current_step += 1
    print_step(current_step, total_steps, "Setting up project structure")
    if not setup_project_structure():
        print("❌ Failed to set up project structure.")
        return 1
    
    # Step 4: Run setup script
    current_step += 1
    print_step(current_step, total_steps, "Running setup and migration")
    if not run_setup_script():
        print("⚠️ Setup script had issues, but continuing...")
    
    # Step 5: Run tests
    current_step += 1
    print_step(current_step, total_steps, "Running validation tests")
    if not run_tests():
        print("⚠️ Some tests failed, but installation may still work")
    
    # Step 6: Create shortcuts
    current_step += 1
    print_step(current_step, total_steps, "Creating launch shortcuts")
    create_launch_shortcuts()
    
    # Display completion information
    display_completion_info()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 Installation interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error during installation: {e}")
        print("Please check the error messages above and try manual installation.")
        sys.exit(1)