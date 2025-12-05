# In button_handler.py
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s.%(msecs)03d - %(message)s',
                   datefmt='%H:%M:%S')

def _on_button_press(self):
    timestamp = datetime.now()
    current = self.hardware.get_current_antenna()
    logging.info(f"BUTTON PRESS DETECTED | Current: A{current}")
    
    self.cycle_antenna()
    
    new = self.hardware.get_current_antenna()
    logging.info(f"BUTTON PRESS COMPLETE | New: A{new}")
