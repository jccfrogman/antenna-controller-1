#!/usr/bin/env python3
"""Test button cycling through 3 antennas"""
from antenna_hardware import AntennaHardware
from button_handler import ButtonHandler
import time

print("Testing Button Cycling: A1 → A2 → A3 → A1")
print("=" * 50)

hw = AntennaHardware()
button_handler = ButtonHandler(hw)

print("\nStartup: A1 active (LED 1 ON)")
print("Press button repeatedly and watch LED sequence:")
print("  Press 1: A1 → A2 (LED 2 ON)")
print("  Press 2: A2 → A3 (LED 3 ON)")
print("  Press 3: A3 → A1 (LED 1 ON) ← Should wrap around!")
print("  Press 4: A1 → A2 (LED 2 ON)")
print("\nPress button 6 times to complete 2 full cycles")
print("Type 'done' when finished")

while True:
    user_input = input("\nCurrent antenna: A{} | Command: ".format(hw.get_current_antenna()))
    if user_input.lower() == 'done':
        break

button_handler.cleanup()
hw.cleanup()
print("\n✓ Button cycling test complete")
