# Pi Zero 2W Testing Guide - 3-Antenna System
## Incremental Testing Strategy

**Critical:** Test one module at a time to isolate issues. This follows TDD principles and makes debugging much easier.

---

## Pre-Deployment Checklist

### Hardware Verification
- [ ] GPIO 3 (Physical Pin 5) wired to ULN2803 pin 3 + LED 3
- [ ] All 3 relays connected to 12V supply
- [ ] All 3 LEDs have 1KΩ resistors
- [ ] Button connected to GPIO 17 (Physical Pin 11) + GND
- [ ] Common ground established for all components
- [ ] Power supply stable (5V for Pi, 12V for relays)

### Software Preparation
```bash
# On Pi Zero 2W
cd ~
mkdir antenna_controller_3ant
cd antenna_controller_3ant

# Copy files from development machine via SCP or upload
# Files needed:
# - antenna_hardware.py
# - ssh_command_handler.py
# - button_handler.py
# - antenna_cli.py
# - test_antenna_hardware.py
# - test_ssh_command_handler.py
# - test_button_handler.py

# Verify gpiozero is installed
python3 -c "import gpiozero; print(gpiozero.__version__)"
```

---

## Phase 1: Hardware Layer Testing (CRITICAL FIRST STEP)

**Goal:** Verify GPIO 3 works, all 3 relays function, exclusive selection logic

### 1A. Run Hardware Unit Tests
```bash
# Test without actual GPIO (mock test)
python3 -m unittest test_antenna_hardware.py -v

# Expected: 10/10 tests PASS
# If failures: Review code changes before proceeding
```

### 1B. Manual GPIO Test Script
Create a minimal test to verify GPIO 3 actually works:

```bash
cat > test_gpio3_manual.py << 'EOF'
#!/usr/bin/env python3
"""Manual test for GPIO 3 (Physical Pin 5)"""
import time
from gpiozero import OutputDevice

print("Testing GPIO 3 (Physical Pin 5) for Antenna 3")
print("=" * 50)

relay3 = OutputDevice(3, active_high=True, initial_value=False)

print("Test 1: Turn ON GPIO 3 (relay 3 should energize, LED 3 should light)")
relay3.on()
input("Press ENTER when verified... ")

print("Test 2: Turn OFF GPIO 3 (relay 3 should de-energize, LED 3 should turn off)")
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
print("\n✓ GPIO 3 manual test complete")
EOF

chmod +x test_gpio3_manual.py
python3 test_gpio3_manual.py
```

**Verification:**
- [ ] Relay 3 clicks ON when GPIO 3 goes HIGH
- [ ] LED 3 lights up when GPIO 3 goes HIGH
- [ ] Relay 3 releases when GPIO 3 goes LOW
- [ ] LED 3 turns off when GPIO 3 goes LOW
- [ ] No unexpected behavior on GPIO 27 or GPIO 22

### 1C. Test Exclusive Selection
```bash
cat > test_exclusive_selection.py << 'EOF'
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
EOF

chmod +x test_exclusive_selection.py
python3 test_exclusive_selection.py
```

**Critical Checks:**
- [ ] Only ONE LED is lit at any time
- [ ] Switching is clean (no LED flickers)
- [ ] All three antennas can be selected individually
- [ ] OFF state turns off all LEDs
- [ ] No relay "chatter" during transitions

**⚠️ STOP:** Do not proceed to Phase 2 until Phase 1 is 100% verified

---

## Phase 2: SSH Command Handler Testing

**Goal:** Verify A3 command works via SSH interface

### 2A. Run SSH Handler Unit Tests
```bash
python3 -m unittest test_ssh_command_handler.py -v

# Expected: 11/11 tests PASS
```

### 2B. Manual Command Testing
```bash
cat > test_ssh_commands.py << 'EOF'
#!/usr/bin/env python3
"""Test SSH command handler with hardware"""
from antenna_hardware import AntennaHardware
from ssh_command_handler import SSHCommandHandler

print("Testing SSH Command Handler")
print("=" * 50)

hw = AntennaHardware()
handler = SSHCommandHandler(hw)

commands = ['A1', 'A2', 'A3', 'OFF', 'STAT', 'A1', 'STAT']

for cmd in commands:
    print(f"\nCommand: {cmd}")
    response = handler.handle_command(cmd)
    print(f"Response: {response}")
    current = hw.get_current_antenna()
    led1 = "●" if hw.get_led_state(1) else "○"
    led2 = "●" if hw.get_led_state(2) else "○"
    led3 = "●" if hw.get_led_state(3) else "○"
    print(f"LEDs: {led1} {led2} {led3}  (Current: {current})")
    input("Verify LEDs and press ENTER... ")

hw.cleanup()
print("\n✓ SSH command test complete")
EOF

chmod +x test_ssh_commands.py
python3 test_ssh_commands.py
```

**Verification:**
- [ ] "A1" command → LED 1 ON only
- [ ] "A2" command → LED 2 ON only
- [ ] "A3" command → LED 3 ON only
- [ ] "OFF" command → All LEDs OFF
- [ ] "STAT" command → Returns correct status without changing LEDs
- [ ] Invalid commands return error message

**⚠️ STOP:** Do not proceed to Phase 3 until Phase 2 passes

---

## Phase 3: Button Handler Testing

**Goal:** Verify button cycles A1→A2→A3→A1 correctly

### 3A. Run Button Handler Unit Tests
```bash
python3 -m unittest test_button_handler.py -v

# Expected: 8/8 tests PASS
```

### 3B. Manual Button Cycling Test
```bash
cat > test_button_cycling.py << 'EOF'
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
EOF

chmod +x test_button_cycling.py
python3 test_button_cycling.py
```

**Critical Verification:**
- [ ] Button cycles in correct order: A1 → A2 → A3 → A1
- [ ] Pressing from A3 wraps to A1 (not back to A2)
- [ ] No double-triggering (200ms debounce working)
- [ ] Button does NOT cycle through OFF state
- [ ] Rapid pressing doesn't cause missed cycles

### 3C. Test OFF State Behavior
```bash
cat > test_button_from_off.py << 'EOF'
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
EOF

chmod +x test_button_from_off.py
python3 test_button_from_off.py
```

**Verification:**
- [ ] From OFF, button press goes to A1
- [ ] From A1, button press goes to A2 (normal cycling resumes)

**⚠️ STOP:** Do not proceed until button cycling is perfect

---

## Phase 4: Full CLI Integration Testing

**Goal:** Test complete system with interactive CLI

### 4A. Launch Interactive CLI
```bash
python3 antenna_cli.py
```

**Expected Startup:**
```
Initializing Antenna Controller...
✓ Hardware initialized
✓ Button handler active (GPIO 17)
✓ Ready for commands

============================================================
    ANTENNA CONTROLLER - Interactive CLI
    3-Antenna System with Physical Button Control
============================================================

Available Commands:
  A1      - Select Antenna 1
  A2      - Select Antenna 2
  A3      - Select Antenna 3
  OFF     - Deactivate all antennas
  STAT    - Show current antenna status
  HELP    - Show this help message
  QUIT    - Exit program

Physical Button:
  Press button to cycle A1 → A2 → A3 → A1
  (Button does not cycle through OFF state)

────────────────────────────────────────
Current Status:
  Antenna: A1 [ACTIVE]
  LED 1:   ● (ON)
  LED 2:   ○ (off)
  LED 3:   ○ (off)
────────────────────────────────────────

antenna>
```

### 4B. CLI Test Sequence
Execute these commands in order, verifying LEDs after each:

```
antenna> A2
 ✓ Status: A2
[Verify: LED 2 ON, others OFF]

antenna> A3
 ✓ Status: A3
[Verify: LED 3 ON, others OFF]

antenna> OFF
 ✓ Status: OFF
[Verify: All LEDs OFF]

antenna> A1
 ✓ Status: A1
[Verify: LED 1 ON, others OFF]

antenna> STAT
Status: A1
[Verify: No LED change]

antenna> [Press physical button]
[Verify: LED 2 ON - cycled to A2]

antenna> [Press physical button]
[Verify: LED 3 ON - cycled to A3]

antenna> [Press physical button]
[Verify: LED 1 ON - wrapped to A1]

antenna> A3
 ✓ Status: A3
[Verify: LED 3 ON - SSH command works during button usage]

antenna> [Press physical button]
[Verify: LED 1 ON - button continues from SSH-set state]
```

### 4C. Stress Testing
```
# Rapid SSH commands (no pauses)
antenna> A1
antenna> A2
antenna> A3
antenna> A1
antenna> A2
antenna> OFF
antenna> A3
[Verify: System stable, no relay chatter, final state A3]

# Rapid button presses (press quickly 10 times)
[Verify: Cycles predictably, no double-triggers, ends at correct antenna]

# Mixed rapid control (alternate SSH and button rapidly)
[Verify: System responds to most recent input, no lock-ups]
```

**⚠️ STOP:** Investigate any failures before RF testing

---

## Phase 5: RF Environment Testing

**Goal:** Verify stability under actual RF power

### 5A. Low Power Test (5W)
- [ ] Set transmitter to 5W output
- [ ] Select each antenna via SSH, transmit 30 seconds
- [ ] Cycle through antennas with button while transmitting
- [ ] Monitor for: relay chatter, LED flickering, Pi resets

### 5B. Medium Power Test (50W)
- [ ] Increase to 50W output
- [ ] Repeat all Phase 4 tests while transmitting
- [ ] Watch for: brown-outs, WiFi drops, GPIO errors

### 5C. High Power Test (100W or legal limit)
- [ ] Set to maximum legal power
- [ ] Repeat all Phase 4 tests
- [ ] Extended transmit test: 5 minutes per antenna
- [ ] Monitor: Pi CPU temperature, voltage stability

**Critical RF Checks:**
- [ ] No unintended antenna switching during TX
- [ ] Button debouncing still effective
- [ ] SSH session remains stable
- [ ] LEDs remain accurately lit
- [ ] Relays don't false-trigger

---

## Phase 6: Long-Term Stability

### 6A. 24-Hour Burn-In
```bash
# Create overnight cycling script
cat > overnight_test.py << 'EOF'
#!/usr/bin/env python3
"""24-hour cycling test"""
from antenna_hardware import AntennaHardware
from ssh_command_handler import SSHCommandHandler
import time
from datetime import datetime

hw = AntennaHardware()
handler = SSHCommandHandler(hw)

cycle_count = 0
start_time = datetime.now()

try:
    while True:
        for antenna in [1, 2, 3, 0]:  # Include OFF state
            handler.handle_command(f'A{antenna}' if antenna > 0 else 'OFF')
            cycle_count += 1
            elapsed = (datetime.now() - start_time).total_seconds() / 3600
            print(f"[{datetime.now()}] Cycle {cycle_count} | A{antenna} | {elapsed:.1f}h elapsed")
            time.sleep(30)  # 30 seconds per state = 2 minutes per cycle
except KeyboardInterrupt:
    print(f"\n✓ Completed {cycle_count} cycles over {elapsed:.1f} hours")
    hw.cleanup()
EOF

# Run overnight
nohup python3 overnight_test.py > overnight.log 2>&1 &

# Check next morning
tail -f overnight.log
```

**Verification:**
- [ ] No relay failures
- [ ] No GPIO errors in logs
- [ ] WiFi remained connected
- [ ] No Pi resets/reboots

---

## Troubleshooting Guide

### Issue: GPIO 3 doesn't activate relay/LED
**Diagnosis:**
```bash
# Check GPIO 3 is not in use
gpioinfo | grep -A 1 "line 3"

# Test with direct gpiozero
python3 -c "from gpiozero import LED; led=LED(3); led.on(); input('Check LED'); led.off()"
```
**Fixes:**
- Verify physical wiring to Pin 5
- Check ULN2803 connection
- Ensure GPIO 3 not reserved by system

### Issue: Button triggers multiple times per press
**Diagnosis:** Debounce time too short for your button type
**Fix:** Increase debounce in `button_handler.py`:
```python
# Change from 0.2 to 0.3 or 0.5
debounce_time=0.3
```

### Issue: LEDs don't match relay state
**Diagnosis:** LED wiring issue or relay coil current too low
**Fixes:**
- Verify LED is parallel to relay driver input (GPIO side)
- Check 1KΩ resistor value
- Test LED independently

### Issue: System unstable during RF transmission
**Diagnosis:** RF ingress or power supply sag
**Fixes:**
- Add ferrite cores to all cables
- Verify RF shielding on enclosure
- Separate Pi power supply from relay power
- Add more decoupling capacitors

### Issue: A3 command rejected as invalid
**Diagnosis:** Old code still loaded
**Fix:**
```bash
# Force reimport
rm -rf __pycache__
python3 antenna_cli.py
```

### Issue: Rotation wraps incorrectly (A3 → A2 instead of A3 → A1)
**Diagnosis:** Logic error in modulo calculation
**Check:**
```python
# Test rotation math
for i in range(6):
    current = i % 3 + 1
    next_ant = (current % 3) + 1
    print(f"{current} → {next_ant}")
# Should show: 1→2, 2→3, 3→1, 1→2, 2→3, 3→1
```

---

## Success Criteria Summary

### ✓ Phase 1: Hardware
- [ ] All 3 GPIO pins control relays correctly
- [ ] Exclusive selection works (only 1 relay on at a time)
- [ ] LEDs accurately reflect relay states

### ✓ Phase 2: SSH Commands
- [ ] A1, A2, A3, OFF commands work
- [ ] STAT reports correct state
- [ ] Invalid commands rejected gracefully

### ✓ Phase 3: Button Control
- [ ] Button cycles A1 → A2 → A3 → A1
- [ ] No double-triggering
- [ ] Works from OFF state

### ✓ Phase 4: Integration
- [ ] CLI displays correctly
- [ ] SSH and button control coexist seamlessly
- [ ] System responds to most recent input

### ✓ Phase 5: RF Stability
- [ ] No false triggers during TX
- [ ] WiFi remains stable
- [ ] No relay chatter

### ✓ Phase 6: Reliability
- [ ] 24-hour test completes
- [ ] No unexplained errors
- [ ] System recovers from interruptions

---

## Production Deployment

Once all phases pass:

1. **Create systemd service** (auto-start on boot)
2. **Set up log rotation** (prevent disk filling)
3. **Configure static IP** (consistent SSH access)
4. **Document antenna-to-radio mapping** (A1=?, A2=?, A3=?)
5. **Create backup** (SD card image)

**Congratulations! Your 3-antenna system is operational.**
