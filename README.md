# Antenna Controller for Raspberry Pi Zero 2W 
December 4, 2025 (Source on SER8 - jcarter/code/scr3)
3-antenna controller with SSH commands and physical button control.

![0](https://github.com/user-attachments/assets/58b8d155-d3c9-4fb1-aa44-62ef03be9331)

## Hardware Requirements
- Raspberry Pi Zero 2W
- 3x 12V relays
- ULN2803 driver IC
- Push button (GPIO 17)
- 3x LEDs with 1kΩ resistors

## Installation
```bash
pip install gpiozero lgpio
git clone https://github.com/yourusername/antenna-controller
cd antenna-controller/src
python3 antenna_cli.py
```

## Usage
```bash
# 3-antenna mode (default)
python3 antenna_cli.py

# 2-antenna toggle mode
python3 antenna_cli.py --mode 2
```

## GPIO Pinout
- GPIO 27 (Pin 13) - Antenna 1
- GPIO 22 (Pin 15) - Antenna 2
- GPIO 4 (Pin 7) - Antenna 3
- GPIO 17 (Pin 11) - Button

## Commands
- `A1` - Select antenna 1
- `A2` - Select antenna 2
- `A3` - Select antenna 3
- `OFF` - Deactivate all
- `STAT` - Show status

## License
MIT License
