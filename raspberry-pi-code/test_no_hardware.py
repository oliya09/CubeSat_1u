"""Test Raspberry Pi code without any hardware"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock all hardware imports automatically
import builtins
import importlib

class MockGPIO:
    BCM = 'BCM'
    OUT = 'OUT'
    HIGH = 1
    LOW = 0
    
    def setmode(self, mode): print(f"📌 Mock: GPIO mode={mode}")
    def setup(self, pin, mode): print(f"📌 Mock: Pin {pin} setup as {mode}")
    def output(self, pin, state): print(f"📌 Mock: Pin {pin} = {state}")
    def cleanup(self): print("📌 Mock: GPIO cleaned up")

# Replace RPi.GPIO with mock
sys.modules['RPi'] = type('RPi', (), {})
sys.modules['RPi.GPIO'] = MockGPIO()

# Now import your actual code
from flight_controller import CubeSatFlightController

print("="*60)
print("🚀 RUNNING IN SIMULATION MODE - NO HARDWARE NEEDED")
print("="*60)

# Create controller but don't try real hardware
controller = CubeSatFlightController()

# Manually override to use mock
controller.comm.stm32_serial = None  # No real serial
print("\n✅ Controller initialized in simulation mode")
print("\nAvailable commands you can test:")
print("  - Telemetry logging")
print("  - Image capture simulation")
print("  - Data compression algorithms")
print("  - State machine logic")
print("\nPress Ctrl+C to exit")

try:
    import time
    while True:
        # Generate mock telemetry
        mock_telemetry = {
            'timestamp': time.time(),
            'temperature_bme': 23.5,
            'radiation_cps': 42,
            'battery_voltage': 3850
        }
        controller.telemetry.save_telemetry(mock_telemetry)
        print(f"📊 Mock telemetry saved: {mock_telemetry['temperature_bme']}°C")
        time.sleep(2)
except KeyboardInterrupt:
    print("\n✅ Test complete!")