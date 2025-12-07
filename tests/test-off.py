#!/usr/bin/env python3
"""Test button behavior from OFF state"""
from antenna_hardware import AntennaHardware
from button_handler import ButtonHandler
from ssh_command_handler import SSHCommandHandler

hw = AntennaHardware()
button_handler = ButtonHandler(hw)
ssh_handler = SSHCommandHandler(hw)

print("Testing Button from OFF state")
print("=" * 50)

print("\n1. Setting system to OFF via SSH")
ssh_handler.handle_command("OFF")
print(f"Current: A{hw.get_current_antenna()} (should be 0=OFF, all LEDs off)")
input("Verify all LEDs OFF, press ENTER... ")

print("\n2. Press button once")
print("Expected: Should go to A1 (LED 1 ON)")
input("Press button and verify LED 1 ON, then press ENTER... ")
print(f"Current: A{hw.get_current_antenna()} (should be 1)")

print("\n3. Press button again")
print("Expected: Should cycle to A2 (LED 2 ON)")
input("Press button and verify LED 2 ON, then press ENTER... ")
print(f"Current: A{hw.get_current_antenna()} (should be 2)")

button_handler.cleanup()
hw.cleanup()
print("\n✓ Button from OFF test complete")
