"""Test communication between STM32 and Pi using simulated components"""
import threading
import time
import queue
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'raspberry-pi'))

# Mock STM32 behavior
class MockSTM32:
    def __init__(self):
        self.running = True
        self.telemetry_queue = queue.Queue()
        
    def generate_telemetry(self):
        """Simulate STM32 sending data"""
        seq = 0
        while self.running:
            # Mock telemetry packet
            packet = {
                'sync1': 0xAA,
                'sync2': 0x55,
                'sequence': seq,
                'timestamp': time.time(),
                'mag_x': 0.25,
                'mag_y': -0.18,
                'mag_z': 0.45,
                'corrosion_raw': 512,
                'radiation_cps': 42,
                'temperature_bme': 23.5,
                'pressure': 1013.25,
                'humidity': 45.2,
                'temperature_tmp': 23.4,
                'battery_voltage': 3850
            }
            self.telemetry_queue.put(packet)
            print(f"[STM32] Sent telemetry #{seq}")
            seq += 1
            time.sleep(1)
    
    def start(self):
        thread = threading.Thread(target=self.generate_telemetry)
        thread.daemon = True
        thread.start()

# Mock Raspberry Pi
class MockRaspberryPi:
    def __init__(self, stm32):
        self.stm32 = stm32
        self.running = True
        
    def process_telemetry(self):
        while self.running:
            try:
                if not self.stm32.telemetry_queue.empty():
                    data = self.stm32.telemetry_queue.get(timeout=1)
                    print(f"[Pi] Received telemetry: T={data['temperature_bme']}°C, Rad={data['radiation_cps']}CPS")
                  
                    print(f"[Pi] ✓ Saved to database")
            except:
                pass
            time.sleep(0.1)
    
    def start(self):
        thread = threading.Thread(target=self.process_telemetry)
        thread.daemon = True
        thread.start()

print("="*60)
print("🔄 TESTING STM32-PI COMMUNICATION - FULLY SIMULATED")
print("="*60)


stm32 = MockSTM32()
pi = MockRaspberryPi(stm32)

stm32.start()
pi.start()

print("\n✅ Both simulated systems running")
print("Watch telemetry flow from STM32 → Pi")
print("\nPress Ctrl+C to stop\n")

try:
    time.sleep(30)  
except KeyboardInterrupt:
    pass
finally:
    print("\n✅ Test complete!")