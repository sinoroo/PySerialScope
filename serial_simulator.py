#!/usr/bin/env python3
"""
Virtual Serial Port Simulator for testing Sensor Monitor.
This script creates a virtual serial port pair and sends test data.

Usage:
    1. In terminal 1: sudo socat -d -d pty,raw,echo=0 pty,raw,echo=0
    2. Get the two ports (e.g., /dev/pts/10 and /dev/pts/11)
    3. In terminal 2: python3 serial_simulator.py /dev/pts/11
    4. In SensorMonitor app: Add serial connection to /dev/pts/10
"""

import serial
import time
import sys
import math
import json
from datetime import datetime


def simulate_sensor_data(port, duration=None):
    """
    Simulate sensor data on a virtual serial port.
    
    Args:
        port: Serial port path (e.g., /dev/pts/11)
        duration: Duration in seconds (None for infinite)
    """
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"✓ Connected to {port}")
        print("Sending simulated sensor data (JSON format)...")
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        data_count = 0
        
        while True:
            try:
                # Simulate sensor readings with some variation
                timestamp = time.time() - start_time
                vibration = 0.02 + 0.015 * math.sin(timestamp * 2)
                accX = 1.67 + 0.3 * math.sin(timestamp * 1.5)
                accY = -0.03 + 0.2 * math.cos(timestamp * 2.3)
                accZ = 7.86 + 0.5 * math.sin(timestamp * 1.8)
                
                # Send data in JSON format
                data_dict = {
                    "vibration": round(vibration, 3),
                    "accX": round(accX, 2),
                    "accY": round(accY, 2),
                    "accZ": round(accZ, 2)
                }
                data = json.dumps(data_dict) + "\n"
                ser.write(data.encode('utf-8'))
                
                data_count += 1
                timestamp_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print(f"[{timestamp_str}] Sent: {data.strip()}")
                
                # Check for duration
                if duration and (time.time() - start_time) > duration:
                    print(f"\nSimulation ended after {duration} seconds ({data_count} data points)")
                    break
                
                # Send data every 100ms (0.1 seconds)
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print(f"\nStopped after sending {data_count} data points")
                break
            except Exception as e:
                print(f"Error sending data: {e}")
                break
        
        ser.close()
        print("✓ Serial port closed")
        
    except serial.SerialException as e:
        print(f"✗ Failed to open serial port: {e}")
        print("\nTip: Create virtual ports first with:")
        print("  sudo apt-get install -y socat")
        print("  socat -d -d pty,raw,echo=0 pty,raw,echo=0")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 serial_simulator.py <PORT>")
        print("\nExample:")
        print("  1. Create virtual ports: socat -d -d pty,raw,echo=0 pty,raw,echo=0")
        print("  2. Run this script: python3 serial_simulator.py /dev/pts/11")
        print("  3. Connect in SensorMonitor to: /dev/pts/10")
        sys.exit(1)
    
    port = sys.argv[1]
    duration = None
    
    if len(sys.argv) > 2:
        try:
            duration = int(sys.argv[2])
            print(f"Running for {duration} seconds...\n")
        except ValueError:
            pass
    
    simulate_sensor_data(port, duration)
