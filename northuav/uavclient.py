#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

import time
import sys
import readline
sys.path.append('./')

import northlib.ntrp as radioManager
from northuav.uavcom import UavCOM

uri = "radio:/0/72/2/E7E7E7E301"

class UavClient:
    def __init__(self, uav:UavCOM):
        self.uav = uav
        
    def show_menu(self):
        print("\n=== NorthstarLib UAV Terminal ===")
        print("Commands (case-insensitive):")
        print("  arm                    - Arm the UAV")
        print("  disarm                 - Disarm the UAV")
        print("  takeoff [altitude]     - Takeoff to altitude (default: 3.0m)")
        print("  land                   - Land the UAV")
        print("  move <x> <y> <z>       - Move to position")
        print("  yaw <angle>            - Rotate to angle in degrees")
        print("  home                   - Return to home position")
        print("  kill                   - Emergency kill command")
        print("  auto                   - Enable auto mode")
        print("  idle                   - Set to idle mode")
        print("  status                 - Show current status")
        print("  help                   - Show this menu")
        print("  exit                   - Exit application")
        print("Note: Use arrow keys for command history")
        print("================================")
        
    def handle_command(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return True
            
        cmd = parts[0].lower()
        
        try:
            if cmd == "arm":
                self.uav.arm()
                print("UAV armed")
                
            elif cmd == "disarm":
                self.uav.disarm()
                print("UAV disarmed")
                
            elif cmd == "takeoff":
                altitude = float(parts[1]) if len(parts) > 1 else 3.0
                self.uav.takeoff(altitude)
                print(f"Taking off to {altitude}m")
                
            elif cmd == "land":
                self.uav.land()
                print("Landing")
                
            elif cmd == "move":
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    self.uav.move([x, y, z])
                    print(f"Moving to position [{x}, {y}, {z}]")
                else:
                    print("Usage: move <x> <y> <z>")
                    
            elif cmd == "yaw":
                if len(parts) >= 2:
                    angle = float(parts[1])
                    self.uav.yaw(angle)
                    print(f"Rotating to {angle} degrees")
                else:
                    print("Usage: yaw <angle>")
                    
            elif cmd == "home":
                self.uav.home()
                print("Returning to home position")
                
            elif cmd == "kill":
                self.uav.kill()
                print("Emergency kill executed")
                    
            elif cmd == "auto":
                self.uav.setMode(self.uav.UAVCOM_STATE_AUTO)
                print("Auto mode enabled")
                
            elif cmd == "idle":
                self.uav.setMode(self.uav.UAVCOM_STATE_IDLE)
                print("Idle mode set")
                
            elif cmd == "status":
                mode_names = {
                    self.uav.UAVCOM_STATE_IDLE: "IDLE",
                    self.uav.UAVCOM_STATE_READY: "READY", 
                    self.uav.UAVCOM_STATE_AUTO: "AUTO",
                    self.uav.UAVCOM_STATE_MOVING: "MOVING",
                    self.uav.UAVCOM_STATE_TAKEOFF: "TAKEOFF",
                    self.uav.UAVCOM_STATE_LAND: "LAND"
                }
                mode_name = mode_names.get(self.uav.mode, "UNKNOWN")
                print(f"Mode: {mode_name} ({self.uav.mode})")
                print(f"Position: {self.uav.position}")
                print(f"Heading: {self.uav.heading}")
                print(f"Connection: {'Connected' if self.uav.connection else 'Disconnected'}")
                
            elif cmd == "help":
                self.show_menu()
                
            elif cmd == "exit":
                return False
                
            else:
                print(f"Unknown command: '{cmd}'. Type 'help' for available commands.")
                
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
        except Exception as e:
            print(f"Command error: {e}")
            
        return True
        
    def run(self):
        print("UAV Terminal Started")
        
        # Configure readline for command history and completion
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode emacs')
        
        # Add command completion
        commands = ['arm', 'disarm', 'takeoff', 'land', 'move', 'yaw', 'home', 'kill', 'auto', 'idle', 'status', 'help', 'exit']
        def completer(text, state):
            options = [cmd for cmd in commands if cmd.startswith(text.lower())]
            if state < len(options):
                return options[state]
            else:
                return None
        readline.set_completer(completer)
        
        self.show_menu()
        
        while True:
            try:
                command = input("> ")
                if not self.handle_command(command):
                    break
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == '__main__':
    uav = None
    try:
        radioManager.radioSearch(baud=2000000)  # Arduino DUE (USB Connection) has no Baudrate
        if not len(radioManager.availableRadios) > 0:
            print("No radios found. Exiting.")
            sys.exit()

        time.sleep(1)
        
        uav = UavCOM(uri=uri)
        print(f"Connected to UAV at {uri}")
        
        # Create and run client
        client = UavClient(uav)
        client.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        try:
            if uav:
                uav.destroy()
        except:
            pass
        radioManager.closeAvailableRadios()
        
        print("UAV Terminal exit")
        time.sleep(0.1)
        sys.exit()