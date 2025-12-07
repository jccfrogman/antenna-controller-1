#!/usr/bin/env python3
"""
Button Press Diagnostic Tool
Tests button reliability and logs all press events

Usage:
  python3 diagnose_button.py
  [Press button 10 times]
  [Press Ctrl+C to see results]
"""
import gpiozero
import time
import signal
import sys
from datetime import datetime
from antenna_hardware import AntennaHardware
from button_handler import ButtonHandler

# Statistics tracking
press_count = 0
successful_changes = 0
failed_changes = 0
press_times = []
last_antenna = None

def on_button_event():
    """Called when button is pressed"""
    global press_count, successful_changes, failed_changes, last_antenna
    
    press_count += 1
    press_time = time.time()
    press_times.append(press_time)
    
    # Get state before and after
    before = hw.get_current_antenna()
    
    # Wait a moment to see if antenna actually changes
    time.sleep(0.1)
    after = hw.get_current_antenna()
    
    # Calculate time since last press
    if len(press_times) > 1:
        time_since_last = (press_times[-1] - press_times[-2]) * 1000
    else:
        time_since_last = 0
    
    # Check if state changed
    if after != before:
        successful_changes += 1
        status = "✓ SUCCESS"
    else:
        failed_changes += 1
        status = "✗ FAILED (no state change)"
    
    # Print result
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} | Press #{press_count:2d} | A{before}→A{after} | "
          f"{time_since_last:6.0f}ms since last | {status}")
    
    last_antenna = after

def signal_handler(sig, frame):
    """Handle Ctrl+C - print statistics"""
    print("\n" + "=" * 70)
    print("DIAGNOSTIC RESULTS")
    print("=" * 70)
    
    print(f"\nTotal button presses detected:  {press_count}")
    print(f"Successful antenna changes:     {successful_changes}")
    print(f"Failed changes (no effect):     {failed_changes}")
    
    if press_count > 0:
        success_rate = (successful_changes / press_count) * 100
        print(f"Success rate:                   {success_rate:.1f}%")
    
    # Timing analysis
    if len(press_times) > 1:
        intervals = [(press_times[i] - press_times[i-1]) * 1000 
                    for i in range(1, len(press_times))]
        avg_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        
        print(f"\nPress timing analysis:")
        print(f"  Average interval:  {avg_interval:.0f}ms")
        print(f"  Fastest press:     {min_interval:.0f}ms")
        print(f"  Slowest press:     {max_interval:.0f}ms")
        
        # Check if any presses were too fast
        too_fast = [i for i in intervals if i < 200]  # Less than debounce time
        if too_fast:
            print(f"  ⚠ {len(too_fast)} presses were < 200ms apart (may be debounced)")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS:")
    print("=" * 70)
    
    if success_rate < 90:
        print("\n⚠ Button reliability < 90% - Action needed:")
        if failed_changes > 0:
            print("  - State not changing: Check button wiring")
            print("  - Try increasing debounce time to 0.3 or 0.5 seconds")
        if too_fast:
            print("  - Slow down button presses (wait 500ms between presses)")
    elif success_rate < 100:
        print("\n⚠ Minor issues detected:")
        print("  - Consider increasing debounce to 0.3 seconds")
    else:
        print("\n✓ Button working perfectly! 100% success rate.")
    
    print("\nTo test with different debounce time:")
    print("  Edit button_handler.py and change debounce_time parameter")
    print("  Or modify this script to test various values\n")
    
    # Cleanup
    button_handler.cleanup()
    hw.cleanup()
    sys.exit(0)

# Main program
print("=" * 70)
print("BUTTON PRESS DIAGNOSTIC TOOL")
print("=" * 70)
print("\nInitializing hardware...")

try:
    hw = AntennaHardware()
    
    # Create button handler with custom callback
    button_handler = ButtonHandler(hw, antenna_count=2)  # Use 2-antenna mode for testing
    
    # Override the button callback to use our diagnostic function
    button_handler._on_button_press = on_button_event
    button_handler.button.when_pressed = on_button_event
    
    print("✓ Hardware initialized")
    print(f"✓ Button monitoring GPIO 17 (debounce: {button_handler.debounce_time*1000:.0f}ms)")
    print(f"✓ Testing in 2-antenna mode (A1↔A2 toggle)\n")
    
    print("=" * 70)
    print("Press button 10 times (or more)")
    print("Press Ctrl+C when done to see results")
    print("=" * 70)
    print()
    
    # Setup signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep program running
    while True:
        time.sleep(0.1)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
