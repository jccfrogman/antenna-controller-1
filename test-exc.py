#!/usr/bin/env python3
"""Test that only one antenna is active at a time"""
from antenna_hardware import AntennaHardware
import time

print("Testing Exclusive Antenna Selection")
print("=" * 50)

hw = AntennaHardware()

print("\nStartup: Should be A1 (LED 1 ON, LED 2 OFF, LED 3 OFF)")
input("Verify and press ENTER... ")

print("\nSwitching to A2 (LED 1 OFF, LED 2 ON, LED 3 OFF)")
hw.set_antenna(2)
time.sleep(0.5)
input("Verify and press ENTER... ")

print("\nSwitching to A3 (LED 1 OFF, LED 2 OFF, LED 3 ON)")
hw.set_antenna(3)
time.sleep(0.5)
input("Verify and press ENTER... ")

print("\nSwitching to OFF (ALL LEDs OFF)")
hw.set_antenna(0)
time.sleep(0.5)
input("Verify and press ENTER... ")

print("\nSwitching back to A1 (LED 1 ON, LED 2 OFF, LED 3 OFF)")
hw.set_antenna(1)
time.sleep(0.5)
input("Verify and press ENTER... ")

hw.cleanup()
print("\n✓ Exclusive selection test complete")
