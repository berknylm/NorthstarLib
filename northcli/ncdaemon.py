#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  __  __ ____ _  __ ____ ___ __  __
#  \ \/ // __// |/ //  _// _ |\ \/ /
#   \  // _/ /    /_/ / / __ | \  / 
#   /_//___//_/|_//___//_/ |_| /_/  
# 
#   2024 Yeniay Uav Flight Control Systems
#   Research and Development Team

"""
Background daemon for managing UAV connections
Handles multiple client requests and maintains UAV connections
"""

import json
import socket
import threading
import time
from ncconfig import NorthConfig

__author__ = 'Yeniay RD'
__all__ = ['NorthDaemon']


class NorthDaemon:
    """North Daemon for managing UAV connections"""
    
    def __init__(self):
        self.config = NorthConfig()
        self.uav_connections = {}
        self.running = False
        self.server_socket = None
    
    def _init_radios(self):
        """Initialize radio connections"""
        try:
            import sys
            from pathlib import Path
            # Add parent directory to path to find northlib
            parent_dir = str(Path(__file__).parent.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from northlib import ntrp as radio_manager
            radio_manager.radioSearch(baud=2000000)
            if not radio_manager.getAvailableRadios():
                print("Warning: No radios found")
            return True
        except ImportError:
            print("Error: Cannot import northlib. Check installation.")
            return False
        except Exception as e:
            print(f"Error initializing radios: {e}")
            return False
    
    def _connect_linked_agents(self):
        """Connect to all linked agents"""
        try:
            import sys
            from pathlib import Path
            # Add parent directory to path to find northuav
            parent_dir = str(Path(__file__).parent.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from northuav.uavcom import UavCOM
            
            linked_agents = sorted(self.config.load_links())
            for idx, agent_id in enumerate(linked_agents):
                uri = f"radio:/{idx}/{int(agent_id):02d}/2/E7E7E7E301"
                print(f"Connecting agent {agent_id} to radio {idx}: {uri}")
                com = UavCOM(uri)
                self.uav_connections[agent_id] = com
                time.sleep(0.05)  # Small delay between connections
        except ImportError:
            print("Error: Cannot import northuav. Check installation.")
        except Exception as e:
            print(f"Error connecting to agents: {e}")
    
    def _handle_client(self, client_socket):
        """Handle individual client request"""
        try:
            # Receive request
            request_data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                request_data += chunk
            
            if not request_data:
                return
            
            request = json.loads(request_data.decode('utf-8'))
            response = self._process_request(request)
            
            # Send response
            response_data = json.dumps(response).encode('utf-8')
            client_socket.sendall(response_data)
            
        except Exception as e:
            print(f"Error handling client: {e}")
            error_response = {"ok": False, "error": str(e)}
            try:
                client_socket.sendall(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()
    
    def _process_request(self, request):
        """Process incoming request and return response"""
        action = request.get("action")
        
        if action == "link":
            return self._handle_link(request)
        elif action == "unlink":
            return self._handle_unlink(request)
        elif action == "status":
            return self._handle_status(request)
        elif action == "cmd":
            return self._handle_command(request)
        elif action == "origin":
            return self._handle_origin(request)
        elif action == "arm":
            return self._handle_arm(request)
        elif action == "disarm":
            return self._handle_disarm(request)
        elif action == "takeoff":
            return self._handle_takeoff(request)
        elif action == "move":
            return self._handle_move(request)
        elif action == "land":
            return self._handle_land(request)
        elif action == "home":
            return self._handle_home(request)
        elif action == "kill":
            return self._handle_kill(request)
        elif action == "launch":
            return self._handle_launch(request)
        elif action == "delay":
            return self._handle_delay(request)
        elif action == "shutdown":
            return self._handle_shutdown()
        else:
            return {"ok": False, "error": f"Unknown action: {action}"}
    
    def _handle_link(self, request):
        """Handle agent linking request"""
        try:
            new_ids = request.get("ids", [])
            current_ids = self.config.load_links()
            all_ids = sorted(list(set(current_ids + new_ids)))
            self.config.save_links(all_ids)
            
            # Try to connect new agents
            for agent_id in new_ids:
                if agent_id not in self.uav_connections:
                    try:
                        import sys
                        from pathlib import Path
                        # Add parent directory to path to find northuav
                        parent_dir = str(Path(__file__).parent.parent)
                        if parent_dir not in sys.path:
                            sys.path.insert(0, parent_dir)
                        
                        from northuav.uavcom import UavCOM
                        # Calculate radio index based on sorted position in all_ids list
                        radio_idx = all_ids.index(agent_id)
                        uri = f"radio:/{radio_idx}/{int(agent_id):02d}/2/E7E7E7E301"
                        print(f"Linking agent {agent_id} to radio {radio_idx}: {uri}")
                        com = UavCOM(uri)
                        self.uav_connections[agent_id] = com
                        time.sleep(0.05)
                    except Exception as e:
                        print(f"Failed to connect agent {agent_id}: {e}")
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_unlink(self, request):
        """Handle agent unlinking request"""
        try:
            if request.get("all", False):
                self.config.save_links([])
                # Disconnect all agents
                for agent_id, com in list(self.uav_connections.items()):
                    try:
                        com.destroy()
                    except:
                        pass
                self.uav_connections.clear()
            else:
                ids_to_remove = request.get("ids", [])
                current_ids = self.config.load_links()
                remaining_ids = [id for id in current_ids if id not in ids_to_remove]
                self.config.save_links(remaining_ids)
                
                # Disconnect specified agents
                for agent_id in ids_to_remove:
                    if agent_id in self.uav_connections:
                        try:
                            self.uav_connections[agent_id].destroy()
                            del self.uav_connections[agent_id]
                        except:
                            pass
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_status(self, request):
        """Handle status request"""
        try:
            target_ids = request.get("ids")
            if target_ids is None:
                target_ids = self.config.load_links()
            
            status_info = {}
            for agent_id in target_ids:
                if agent_id in self.uav_connections:
                    com = self.uav_connections[agent_id]
                    agent_status = {}
                    
                    try:
                        if request.get("pos", False):
                            agent_status["pos"] = com.position
                        if request.get("rot", False):
                            agent_status["rot"] = com.heading
                        if request.get("nav", False):
                            agent_status["nav"] = "navigation_data_placeholder"
                        if request.get("batt", False):
                            agent_status["batt"] = "battery_data_placeholder"
                    except Exception as e:
                        agent_status["error"] = f"Communication error: {e}"
                    
                    status_info[agent_id] = agent_status
                else:
                    status_info[agent_id] = {"error": "Not connected"}
            
            return {"ok": True, "status": status_info}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_command(self, request):
        """Handle command request"""
        try:
            agent_id = request.get("id")
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            
            if request.get("takeoff", False):
                altitude = request.get("altitude", 3.0)
                com.takeoff(altitude)
            elif request.get("land", False):
                com.land()
            elif request.get("pos"):
                pos = request["pos"]
                com.move([pos[0], pos[1], pos[2]])
            else:
                return {"ok": False, "error": "No valid command specified"}
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_origin(self, request):
        """Handle origin setting request"""
        try:
            agent_id = request.get("id")
            lat = request.get("lat")
            lon = request.get("lon")
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            # Check if origin method supports setcmd parameter
            if setcmd and hasattr(com, 'origin') and 'setcmd' in com.origin.__code__.co_varnames:
                com.origin(lat, lon, setcmd=setcmd)
            elif setcmd:
                # If setcmd is requested but not supported, we'll need to handle it differently
                # For now, just call the regular origin method
                com.origin(lat, lon)
            else:
                com.origin(lat, lon)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_arm(self, request):
        """Handle arm request"""
        try:
            agent_id = request.get("id")
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            com.arm(setcmd=setcmd)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_disarm(self, request):
        """Handle disarm request"""
        try:
            agent_id = request.get("id")
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            com.disarm(setcmd=setcmd)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_takeoff(self, request):
        """Handle takeoff request"""
        try:
            agent_id = request.get("id")
            altitude = request.get("altitude", 3.0)
            time_param = request.get("time", 10.0)
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            com.takeoff(altitude, t=time_param, setcmd=setcmd)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_move(self, request):
        """Handle move request"""
        try:
            agent_id = request.get("id")
            position = request.get("position")
            time_param = request.get("time", 1.0)
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            if not position or len(position) != 3:
                return {"ok": False, "error": "Invalid position data"}
            
            com = self.uav_connections[agent_id]
            com.move(position, t=time_param, setcmd=setcmd)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_land(self, request):
        """Handle land request"""
        try:
            agent_id = request.get("id")
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            com.land(setcmd=setcmd)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_home(self, request):
        """Handle home request"""
        try:
            agent_id = request.get("id")
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            com.home(setcmd=setcmd)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_kill(self, request):
        """Handle kill request"""
        try:
            agent_id = request.get("id")
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            com.kill()
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_launch(self, request):
        """Handle launch request - execute all queued commands"""
        try:
            target_ids = request.get("ids")
            if target_ids is None:
                target_ids = self.config.load_links()
            
            if not target_ids:
                return {"ok": False, "error": "No agents to launch"}
                
            for agent_id in target_ids:
                if agent_id in self.uav_connections:
                    com = self.uav_connections[agent_id]
                    # Call launch method on UavCOM to execute queued commands
                    if hasattr(com, 'launch'):
                        com.launch()
                    else:
                        # Fallback: call uavexeCMD_LAUNCH if available
                        if hasattr(com, 'uavexeCMD_LAUNCH'):
                            com.txCMD(dataID=42, channels=bytearray([2]))  # UAVEXE_CMD_LAUNCH
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_delay(self, request):
        """Handle delay request"""
        try:
            agent_id = request.get("id")
            seconds = request.get("seconds", 1.0)
            setcmd = request.get("setcmd", False)
            
            if agent_id not in self.uav_connections:
                return {"ok": False, "error": f"Agent {agent_id} not connected"}
            
            com = self.uav_connections[agent_id]
            # Check if delay method exists and supports setcmd
            if hasattr(com, 'exe_DELAY'):
                com.exe_DELAY(seconds, setcmd=setcmd)
            else:
                # If no delay method, we could implement a basic delay
                if not setcmd:
                    import time
                    time.sleep(seconds)
            
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def _handle_shutdown(self):
        """Handle shutdown request"""
        print("Shutdown requested")
        self.running = False
        return {"ok": True}
    
    def run(self, host="127.0.0.1", port=7777):
        """Start the daemon"""
        print(f"Starting North Daemon on {host}:{port}")
        
        # Initialize radios
        if not self._init_radios():
            print("Failed to initialize radios. Continuing anyway...")
        
        # Save daemon info
        self.config.save_daemon_info(host, port)
        
        # Clear any existing links to start fresh
        self.config.save_links([])
        
        # Connect to linked agents (will be empty after clearing)
        self._connect_linked_agents()
        print(f"Connected to {len(self.uav_connections)} agents")
        
        # Start server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((host, port))
            self.server_socket.listen(5)
            self.running = True
            
            print("Daemon ready. Press Ctrl+C to stop.")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, addr = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self._handle_client, 
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except OSError:
                    if self.running:
                        print("Server socket error")
                    break
                    
        except Exception as e:
            print(f"Error running daemon: {e}")
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources"""
        print("Shutting down daemon...")
        
        # Close all UAV connections
        for com in self.uav_connections.values():
            try:
                com.destroy()
            except:
                pass
        self.uav_connections.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # Remove daemon info file
        self.config.remove_daemon_info()
        
        print("Daemon stopped")