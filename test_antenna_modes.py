#!/usr/bin/env python3
"""
Test script to verify 2-antenna vs 3-antenna modes
Run this to verify button cycling behavior in both modes
"""

print("=" * 60)
print("Testing Antenna Mode Implementation")
print("=" * 60)

# Test modulo logic
print("\n2-Antenna Mode Logic Test:")
antenna_count = 2
for current in [0, 1, 2]:
    if current == 0:
        next_ant = 1
    else:
        next_ant = (current % antenna_count) + 1
    print(f"  Current: A{current if current > 0 else 'OFF'} → Next: A{next_ant}")

print("\n3-Antenna Mode Logic Test:")
antenna_count = 3
for current in [0, 1, 2, 3]:
    if current == 0:
        next_ant = 1
    else:
        next_ant = (current % antenna_count) + 1
    print(f"  Current: A{current if current > 0 else 'OFF'} → Next: A{next_ant}")

print("\n" + "=" * 60)
print("Expected Results:")
print("=" * 60)
print("\n2-Antenna Mode:")
print("  OFF → A1")
print("  A1 → A2")
print("  A2 → A1  ← Toggles back")

print("\n3-Antenna Mode:")
print("  OFF → A1")
print("  A1 → A2")
print("  A2 → A3")
print("  A3 → A1  ← Wraps around")

print("\n" + "=" * 60)
print("To test on hardware:")
print("=" * 60)
print("\n2-Antenna Mode:")
print("  python3 antenna_cli.py --mode 2")
print("  [Press button: should toggle A1 ↔ A2]")

print("\n3-Antenna Mode:")
print("  python3 antenna_cli.py --mode 3")
print("  [Press button: should cycle A1 → A2 → A3 → A1]")

print("\nDefault (no parameter):")
print("  python3 antenna_cli.py")
print("  [Uses 3-antenna mode by default]")

print("\nHelp:")
print("  python3 antenna_cli.py --help")
print()
