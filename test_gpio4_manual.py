#!/usr/bin/env python3
"""Manual test for GPIO 4 (Physical Pin 7)"""
import time
from gpiozero import OutputDevice

print("Testing GPIO 4 (Physical Pin 7) for Antenna 3")
print("=" * 50)

relay3 = OutputDevice(4, active_high=True, initial_value=False)

print("Test 1: Turn ON GPIO 4 (relay 3 should energize, LED 3 should light)")
relay3.on()
input("Press ENTER when verified... ")

print("Test 2: Turn OFF GPIO 4 (relay 3 should de-energize, LED 3 should turn off)")
relay3.off()
input("Press ENTER when verified... ")

print("Test 3: Rapid cycling (watch for bouncing)")
for i in range(5):
    print(f"  Cycle {i+1}/5")
    relay3.on()
    time.sleep(0.5)
    relay3.off()
    time.sleep(0.5)

relay3.close()
print("\n✓ GPIO 4 manual test complete")
