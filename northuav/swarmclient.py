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

class SwarmClient:
    def __init__(self, uav_configs):
        """
        Initialize swarm client with multiple UAVs
        uav_configs: list of tuples [(agent_id, radio_index), ...]
        Example: [(72, 0), (74, 1), (76, 2)]
        """
        self.uavs = {}
        self.agent_ids = []
        
        # Initialize UAVs
        for agent_id, radio_index in uav_configs:
            uri = f"radio:/{radio_index}/{agent_id:02d}/2/E7E7E7E301"
            uav = UavCOM(uri)
            self.uavs[agent_id] = uav
            self.agent_ids.append(agent_id)
            print(f"Initialized UAV {agent_id} on {uri}")
        
    def show_menu(self):
        print("\n=== NorthstarLib Swarm Client ===")
        print("Commands (case-insensitive):")
        print("  arm [id1] [id2] ...        - Arm specific UAVs (or 'all')")
        print("  disarm [id1] [id2] ...     - Disarm specific UAVs (or 'all')")
        print("  takeoff [id1] [id2] ... [altitude] - Takeoff UAVs to altitude")
        print("  land [id1] [id2] ...       - Land specific UAVs (or 'all')")
        print("  move <id> <x> <y> <z>      - Move specific UAV to position")
        print("  yaw <id> <angle>           - Rotate specific UAV")
        print("  home [id1] [id2] ...       - Send UAVs home (or 'all')")
        print("  kill [id1] [id2] ...       - Emergency kill (or 'all')")
        print("  origin <id> <lat> <lon>    - Set GPS origin for UAV")
        print("  formation <type> <size>    - Execute formation (triangle, line, circle)")
        print("  status [id1] [id2] ...     - Show UAV status (or 'all')")
        print("  list                       - List all connected UAVs")
        print("  help                       - Show this menu")
        print("  exit                       - Exit application")
        print("Note: Use 'all' to apply command to all UAVs")
        print("=======================================")
        
    def parse_uav_ids(self, args, start_index=0):
        """Parse UAV IDs from command arguments"""
        if start_index >= len(args):
            return []
            
        ids = []
        for i in range(start_index, len(args)):
            arg = args[i]
            if arg.lower() == 'all':
                return self.agent_ids
            try:
                agent_id = int(arg)
                if agent_id in self.uavs:
                    ids.append(agent_id)
                else:
                    print(f"Warning: UAV {agent_id} not found")
            except ValueError:
                # Stop parsing if we hit a non-numeric argument
                break
        return ids
        
    def execute_for_uavs(self, uav_ids, command_func, *args):
        """Execute a command function for multiple UAVs"""
        if not uav_ids:
            print("No valid UAV IDs provided")
            return
            
        for agent_id in uav_ids:
            try:
                command_func(self.uavs[agent_id], *args)
                print(f"Executed command for UAV {agent_id}")
            except Exception as e:
                print(f"Error with UAV {agent_id}: {e}")
                
    def handle_command(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return True
            
        cmd = parts[0].lower()
        
        try:
            if cmd == "arm":
                uav_ids = self.parse_uav_ids(parts, 1)
                self.execute_for_uavs(uav_ids, lambda uav: uav.arm())
                
            elif cmd == "disarm":
                uav_ids = self.parse_uav_ids(parts, 1)
                self.execute_for_uavs(uav_ids, lambda uav: uav.disarm())
                
            elif cmd == "takeoff":
                # Parse UAV IDs and optional altitude
                altitude = 3.0
                uav_ids = []
                
                for i, arg in enumerate(parts[1:], 1):
                    if arg.lower() == 'all':
                        uav_ids = self.agent_ids
                    else:
                        try:
                            # Try to parse as UAV ID
                            agent_id = int(arg)
                            if agent_id in self.uavs:
                                uav_ids.append(agent_id)
                            else:
                                # Might be altitude
                                altitude = float(arg)
                        except ValueError:
                            try:
                                # Try to parse as altitude
                                altitude = float(arg)
                            except ValueError:
                                print(f"Invalid argument: {arg}")
                
                if not uav_ids:
                    print("Usage: takeoff [id1] [id2] ... [altitude]")
                else:
                    self.execute_for_uavs(uav_ids, lambda uav: uav.takeoff(altitude))
                    print(f"Takeoff command sent to {len(uav_ids)} UAVs at {altitude}m")
                    
            elif cmd == "land":
                uav_ids = self.parse_uav_ids(parts, 1)
                self.execute_for_uavs(uav_ids, lambda uav: uav.land())
                
            elif cmd == "move":
                if len(parts) >= 5:
                    agent_id = int(parts[1])
                    x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                    if agent_id in self.uavs:
                        self.uavs[agent_id].move([x, y, z])
                        print(f"UAV {agent_id} moving to [{x}, {y}, {z}]")
                    else:
                        print(f"UAV {agent_id} not found")
                else:
                    print("Usage: move <id> <x> <y> <z>")
                    
            elif cmd == "yaw":
                if len(parts) >= 3:
                    agent_id = int(parts[1])
                    angle = float(parts[2])
                    if agent_id in self.uavs:
                        self.uavs[agent_id].yaw(angle)
                        print(f"UAV {agent_id} rotating to {angle} degrees")
                    else:
                        print(f"UAV {agent_id} not found")
                else:
                    print("Usage: yaw <id> <angle>")
                    
            elif cmd == "home":
                uav_ids = self.parse_uav_ids(parts, 1)
                self.execute_for_uavs(uav_ids, lambda uav: uav.home())
                
            elif cmd == "kill":
                uav_ids = self.parse_uav_ids(parts, 1)
                self.execute_for_uavs(uav_ids, lambda uav: uav.kill())
                print("Emergency kill executed")
                
            elif cmd == "origin":
                if len(parts) >= 4:
                    agent_id = int(parts[1])
                    lat, lon = float(parts[2]), float(parts[3])
                    if agent_id in self.uavs:
                        self.uavs[agent_id].origin(lat, lon)
                        print(f"GPS origin set for UAV {agent_id}: {lat}, {lon}")
                    else:
                        print(f"UAV {agent_id} not found")
                else:
                    print("Usage: origin <id> <latitude> <longitude>")
                    
            elif cmd == "formation":
                if len(parts) >= 3:
                    formation_type = parts[1].lower()
                    size = float(parts[2])
                    self.execute_formation(formation_type, size)
                else:
                    print("Usage: formation <type> <size>")
                    print("Types: triangle, line, circle")
                    
            elif cmd == "status":
                uav_ids = self.parse_uav_ids(parts, 1) if len(parts) > 1 else self.agent_ids
                self.show_status(uav_ids)
                
            elif cmd == "list":
                self.list_uavs()
                
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
        
    def execute_formation(self, formation_type, size):
        """Execute formation patterns"""
        if len(self.agent_ids) < 2:
            print("Need at least 2 UAVs for formation")
            return
            
        altitude = 5.0  # Default formation altitude
        
        if formation_type == "triangle" and len(self.agent_ids) >= 3:
            positions = [
                [0, 0, altitude],
                [size, 0, altitude], 
                [size/2, size*0.866, altitude]
            ]
            for i, agent_id in enumerate(self.agent_ids[:3]):
                self.uavs[agent_id].move(positions[i])
                print(f"UAV {agent_id} moving to triangle position {positions[i]}")
                
        elif formation_type == "line":
            for i, agent_id in enumerate(self.agent_ids):
                pos = [i * size, 0, altitude]
                self.uavs[agent_id].move(pos)
                print(f"UAV {agent_id} moving to line position {pos}")
                
        elif formation_type == "circle":
            import math
            num_uavs = len(self.agent_ids)
            for i, agent_id in enumerate(self.agent_ids):
                angle = 2 * math.pi * i / num_uavs
                x = size * math.cos(angle)
                y = size * math.sin(angle)
                pos = [x, y, altitude]
                self.uavs[agent_id].move(pos)
                print(f"UAV {agent_id} moving to circle position {pos}")
                
        else:
            print(f"Unknown formation type: {formation_type}")
            print("Available formations: triangle, line, circle")
            
    def show_status(self, uav_ids):
        """Show status for specified UAVs"""
        print("\n=== UAV Status ===")
        for agent_id in uav_ids:
            if agent_id in self.uavs:
                uav = self.uavs[agent_id]
                print(f"UAV {agent_id}:")
                print(f"  Position: {uav.position}")
                print(f"  Heading: {uav.heading}")
                print(f"  Connection: {'Connected' if uav.connection else 'Disconnected'}")
                print()
            else:
                print(f"UAV {agent_id}: Not found")
                
    def list_uavs(self):
        """List all connected UAVs"""
        print("\n=== Connected UAVs ===")
        for agent_id in self.agent_ids:
            uav = self.uavs[agent_id]
            status = "Connected" if uav.connection else "Disconnected"
            print(f"UAV {agent_id}: {status}")
        print()
        
    def run(self):
        print("Swarm Client Started")
        print(f"Managing {len(self.agent_ids)} UAVs: {self.agent_ids}")
        
        # Configure readline for command history and completion
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode emacs')
        
        # Add command completion
        commands = ['arm', 'disarm', 'takeoff', 'land', 'move', 'yaw', 'home', 'kill', 
                   'origin', 'formation', 'status', 'list', 'help', 'exit']
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
                
    def destroy(self):
        """Clean up all UAV connections"""
        for agent_id, uav in self.uavs.items():
            try:
                uav.destroy()
                print(f"Cleaned up UAV {agent_id}")
            except:
                pass

if __name__ == '__main__':
    try:
        radioManager.radioSearch(baud=2000000)  # Arduino DUE (USB Connection) has no Baudrate
        if not len(radioManager.availableRadios) > 0:
            print("No radios found. Exiting.")
            sys.exit()

        time.sleep(1)
        
        # Configure UAVs: [(agent_id, radio_index), ...]
        uav_configs = [
            (72, 0),  # UAV 72 on radio 0
            (74, 1),  # UAV 74 on radio 1  
            (76, 2),  # UAV 76 on radio 2
        ]
        
        # Create and run swarm client
        swarm = SwarmClient(uav_configs)
        swarm.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        try:
            if 'swarm' in locals():
                swarm.destroy()
        except:
            pass
        radioManager.closeAvailableRadios()
        
        print("Swarm Client exit")
        time.sleep(0.1)
        sys.exit()