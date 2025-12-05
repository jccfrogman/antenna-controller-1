#!/usr/bin/env python3
"""
Standalone Button Logger - Simple Test Script
Monitors button presses and logs all events to understand behavior

NO modifications to existing code required!

Usage:
  python3 button_logger.py
  [Press button 20 times]
  [Press Ctrl+C when done]
  [Check button_log.txt for results]
"""

import time
import signal
import sys
from datetime import datetime
from gpiozero import Button, OutputDevice

# Configuration
BUTTON_PIN = 17
RELAY_PINS = [27, 22, 4]  # A1, A2, A3
ANTENNA_COUNT = 2  # Test in 2-antenna mode
DEBOUNCE_TIME = 0.02

# Statistics
press_count = 0
success_count = 0
fail_count = 0
press_times = []

# Hardware setup
print("Initializing hardware...")
button = Button(BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE_TIME)
relays = [OutputDevice(pin, active_high=True, initial_value=False) for pin in RELAY_PINS]

# Start with A1 active
relays[0].on()
current_antenna = 1

# Open log file
log_file = open('button_log.txt', 'w')
log_file.write("Button Press Log - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
log_file.write("=" * 80 + "\n")
log_file.write(f"Configuration: {ANTENNA_COUNT}-antenna mode, {DEBOUNCE_TIME*1000:.0f}ms debounce\n")
log_file.write("=" * 80 + "\n\n")
log_file.flush()

def get_current_antenna():
    """Return which antenna is currently active"""
    for i, relay in enumerate(relays, start=1):
        if relay.is_active:
            return i
    return 0  # OFF

def set_antenna(antenna_num):
    """Set active antenna"""
    global current_antenna
    # Turn all off
    for relay in relays:
        relay.off()
    # Turn on selected
    if antenna_num > 0:
        relays[antenna_num - 1].on()
    current_antenna = antenna_num

def cycle_antenna():
    """Cycle to next antenna"""
    global current_antenna
    if current_antenna == 0:
        next_ant = 1
    else:
        next_ant = (current_antenna % ANTENNA_COUNT) + 1
    set_antenna(next_ant)

def on_button_press():
    """Handle button press"""
    print("RAW PRESS EVENT:", time.time())
    global press_count, success_count, fail_count
    
    press_count += 1
    press_time = time.time()
    press_times.append(press_time)
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    # Get state before
    before = get_current_antenna()
    
    # Cycle antenna
    cycle_antenna()
    
    # Small delay to ensure relay has switched
    time.sleep(0.01)
    
    # Get state after
    after = get_current_antenna()
    
    # Calculate timing
    if len(press_times) > 1:
        interval = (press_times[-1] - press_times[-2]) * 1000
    else:
        interval = 0
    
    # Determine success/failure
    if after != before:
        success_count += 1
        status = "SUCCESS"
        symbol = "✓"
    else:
        fail_count += 1
        status = "FAILED"
        symbol = "✗"
    
    # Log to file
    log_line = f"{timestamp} | Press #{press_count:3d} | A{before}→A{after} | {interval:7.0f}ms | {status}\n"
    log_file.write(log_line)
    log_file.flush()
    
    # Print to console
    print(f"{timestamp} | Press #{press_count:3d} | A{before}→A{after} | {interval:7.0f}ms | {symbol}")

def cleanup(sig=None, frame=None):
    """Cleanup and show statistics"""
    print("\n" + "=" * 80)
    print("TEST COMPLETE - Results:")
    print("=" * 80)
    
    # Write statistics to log file
    log_file.write("\n" + "=" * 80 + "\n")
    log_file.write("STATISTICS\n")
    log_file.write("=" * 80 + "\n")
    log_file.write(f"Total presses detected:     {press_count}\n")
    log_file.write(f"Successful changes:         {success_count}\n")
    log_file.write(f"Failed (no change):         {fail_count}\n")
    
    if press_count > 0:
        success_rate = (success_count / press_count) * 100
        log_file.write(f"Success rate:               {success_rate:.1f}%\n")
        
        print(f"Total presses detected:     {press_count}")
        print(f"Successful changes:         {success_count}")
        print(f"Failed (no change):         {fail_count}")
        print(f"Success rate:               {success_rate:.1f}%")
    
    # Timing analysis
    if len(press_times) > 1:
        intervals = [(press_times[i] - press_times[i-1]) * 1000 
                    for i in range(1, len(press_times))]
        avg_interval = sum(intervals) / len(intervals)
        min_interval = min(intervals)
        max_interval = max(intervals)
        
        log_file.write(f"\nTiming Analysis:\n")
        log_file.write(f"  Average interval:         {avg_interval:.0f}ms\n")
        log_file.write(f"  Fastest press:            {min_interval:.0f}ms\n")
        log_file.write(f"  Slowest press:            {max_interval:.0f}ms\n")
        
        print(f"\nTiming Analysis:")
        print(f"  Average interval:         {avg_interval:.0f}ms")
        print(f"  Fastest press:            {min_interval:.0f}ms")
        print(f"  Slowest press:            {max_interval:.0f}ms")
        
        # Check for patterns
        too_fast = [i for i in intervals if i < 200]
        if too_fast:
            msg = f"  ⚠ {len(too_fast)} presses < 200ms (may hit debounce)\n"
            log_file.write(msg)
            print(msg.strip())
    
    # Recommendations
    log_file.write("\n" + "=" * 80 + "\n")
    log_file.write("RECOMMENDATIONS\n")
    log_file.write("=" * 80 + "\n")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if press_count > 0:
        success_rate = (success_count / press_count) * 100
        
        if success_rate >= 100:
            msg = "✓ Perfect! 100% success rate - button working flawlessly.\n"
            log_file.write(msg)
            print(msg.strip())
        elif success_rate >= 95:
            msg = "⚠ Good but not perfect (95-99% success)\n"
            msg += "  Consider:\n"
            msg += "  - Increase debounce to 300ms or 500ms\n"
            msg += "  - Check for loose wiring\n"
            msg += "  - Add ferrite bead if transmitting nearby\n"
            log_file.write(msg)
            print(msg.strip())
        elif success_rate >= 80:
            msg = "⚠ Moderate reliability (80-94% success)\n"
            msg += "  Action needed:\n"
            msg += "  - Increase debounce to 500ms\n"
            msg += "  - Check button quality/wiring\n"
            msg += "  - Test with RF transmitter OFF\n"
            log_file.write(msg)
            print(msg.strip())
        else:
            msg = "✗ Poor reliability (<80% success)\n"
            msg += "  Immediate action:\n"
            msg += "  - Check button wiring (loose connection?)\n"
            msg += "  - Try different button\n"
            msg += "  - Check GPIO 17 not in use by other process\n"
            msg += "  - Increase debounce to 1000ms for testing\n"
            log_file.write(msg)
            print(msg.strip())
    
    log_file.write("\nLog file saved: button_log.txt\n")
    print("\nLog file saved: button_log.txt")
    
    # Cleanup
    log_file.close()
    button.close()
    for relay in relays:
        relay.off()
        relay.close()
    
    sys.exit(0)

# Setup signal handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# Register button callback
button.when_pressed = on_button_press

# Instructions
print("=" * 80)
print("BUTTON LOGGER - Standalone Test")
print("=" * 80)
print(f"Monitoring GPIO {BUTTON_PIN} with {DEBOUNCE_TIME*1000:.0f}ms debounce")
print(f"Testing in {ANTENNA_COUNT}-antenna mode (A1↔A2 toggle)")
print("\nPress button 20 times (or more)")
print("Press Ctrl+C when done")
print("Results will be saved to: button_log.txt")
print("=" * 80)
print()

# Keep running
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    cleanup()
