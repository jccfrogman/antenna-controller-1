# src/antenna_cli.py
"""
Antenna Controller - Interactive CLI Interface
Simple command-line interface for testing antenna control system
"""

import sys
import signal
import argparse
from antenna_hardware import AntennaHardware
from ssh_command_handler import SSHCommandHandler
from button_handler import ButtonHandler

# Use modern lgpio
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
Device.pin_factory = LGPIOFactory()


class AntennaControllerCLI:
    """Interactive CLI for antenna control"""
    
    def __init__(self, antenna_count=3):
        """Initialize hardware and handlers
        
        Args:
            antenna_count (int): Number of antennas to cycle through (2 or 3)
        """
        self.antenna_count = antenna_count
        print("Initializing Antenna Controller...")
        
        try:
            self.hw = AntennaHardware()
            self.ssh_handler = SSHCommandHandler(self.hw)
            self.button_handler = ButtonHandler(self.hw, antenna_count=antenna_count)
            
            # Setup signal handler for clean shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            print("✓ Hardware initialized")
            print("✓ Button handler active (GPIO 17)")
            print("✓ Ready for commands\n")
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            sys.exit(1)
    
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C and termination signals"""
        print("\n\nShutting down...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up GPIO...")
        self.button_handler.cleanup()
        self.hw.cleanup()
        print("✓ Cleanup complete")
    
    def print_banner(self):
        """Print welcome banner"""
        print("=" * 60)
        print("    ANTENNA CONTROLLER - Interactive CLI")
        print(f"    {self.antenna_count}-Antenna System with Physical Button Control")
        print("=" * 60)
        print()
    
    def print_help(self):
        """Print available commands"""
        print("Available Commands:")
        print("  A1      - Select Antenna 1")
        print("  A2      - Select Antenna 2")
        print("  A3      - Select Antenna 3")
        print("  OFF     - Deactivate all antennas")
        print("  STAT    - Show current antenna status")
        print("  HELP    - Show this help message")
        print("  QUIT    - Exit program")
        print()
        print("Physical Button:")
        if self.antenna_count == 2:
            print("  Press button to toggle A1 ↔ A2")
        else:
            print("  Press button to cycle A1 → A2 → A3 → A1")
        print("  (Button does not cycle through OFF state)")
        print()
    
    def print_status(self):
        """Print current system status"""
        current = self.hw.get_current_antenna()
        
        print("\n" + "─" * 40)
        print("Current Status:")
        
        if current == 0:
            print("  Antenna: OFF")
            print("  LED 1:   ○ (off)")
            print("  LED 2:   ○ (off)")
            print("  LED 3:   ○ (off)")
        elif current == 1:
            print("  Antenna: A1 [ACTIVE]")
            print("  LED 1:   ● (ON)")
            print("  LED 2:   ○ (off)")
            print("  LED 3:   ○ (off)")
        elif current == 2:
            print("  Antenna: A2 [ACTIVE]")
            print("  LED 1:   ○ (off)")
            print("  LED 2:   ● (ON)")
            print("  LED 3:   ○ (off)")
        elif current == 3:
            print("  Antenna: A3 [ACTIVE]")
            print("  LED 1:   ○ (off)")
            print("  LED 2:   ○ (off)")
            print("  LED 3:   ● (ON)")
        
        print("─" * 40 + "\n")
    
    def run(self):
        """Main interactive loop"""
        self.print_banner()
        self.print_help()
        self.print_status()
        
        print("Enter commands (type HELP for command list):\n")
        
        while True:
            try:
                # Get user input
                command = input("antenna> ").strip()
                
                # Skip empty input
                if not command:
                    continue
                
                # Check for local commands first
                cmd_upper = command.upper()
                
                if cmd_upper in ['QUIT', 'EXIT', 'Q']:
                    print("\nExiting...")
                    self.cleanup()
                    break
                
                elif cmd_upper == 'HELP':
                    self.print_help()
                    continue
                
                elif cmd_upper == 'STATUS':
                    # Alternative to STAT
                    cmd_upper = 'STAT'
                
                # Process command through SSH handler
                response = self.ssh_handler.handle_command(command)
                
                # Print response
                if "ERROR" in response.upper():
                    print(f"  ✗ {response}")
                else:
                    print(f"  ✓ {response}")
                
                # Show status after state changes (not for STAT query)
                if cmd_upper != 'STAT':
                    self.print_status()
                
            except EOFError:
                # Handle Ctrl+D
                print("\nExiting...")
                self.cleanup()
                break
            
            except Exception as e:
                print(f"  ✗ Error: {e}")


def main():
    """Entry point"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Antenna Controller CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--mode',
        type=int,
        choices=[2, 3],
        default=3,
        help='Number of antennas to cycle through with button (default: 3)'
    )
    args = parser.parse_args()
    
    try:
        cli = AntennaControllerCLI(antenna_count=args.mode)
        cli.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()