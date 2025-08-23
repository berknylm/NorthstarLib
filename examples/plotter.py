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
import threading
import queue
import readline
sys.path.append('./')

import northlib.ntrp as radioManager
from   northlib.ntrp.northpipe import NorthPipe,NorthNRF
import northlib.ntrp.ntrp as ntrp
from northlib.ncmd.northcom import NorthCOM
from northlib.ncmd.nrxtable import NrxTableLog

from liveplot import LivePlot

uri = "radio:/0/74/2/E7E7E7E301"

class InteractivePlotter:
    def __init__(self, uavcom, uavtable):
        self.uavcom = uavcom
        self.uavtable = uavtable
        self.lp = None
        self.is_logging = False
        self.log_thread = None
        self.current_param = None
        self.log_running = False
        self.data_queue = queue.Queue()
        
    def show_menu(self):
        print("\n=== NorthstarLib Interactive Plotter ===")
        print("Commands (case-insensitive):")
        print("  get <parameter>    - Read parameter value once")
        print("  set <parameter> <value> - Set parameter value")
        print("  log <parameter>    - Start continuous logging and plotting")
        print("  stop               - Stop current logging")
        print("  show               - Show parameter table")
        print("  exit               - Exit application")
        print("Note: Use arrow keys for command history")
        print("==========================================")
        
    def show_parameters(self):
        print("\n=== Available Parameters ===")
        NrxTableLog(self.uavtable)
        print("============================\n")
        
    def validate_parameter(self, param_name):
        if self.uavtable.search(param_name) is not None:
            return True
        else:
            print(f"Parameter '{param_name}' not found.")
            return False
                
    def handle_get(self, param_name):
        if not self.validate_parameter(param_name):
            return
        try:
            value = self.uavcom.GET(param_name)
            print(f"Parameter '{param_name}' = {value}")
        except Exception as e:
            print(f"Error reading parameter: {e}")
            
    def handle_set(self, param_name, value_str):
        if not self.validate_parameter(param_name):
            return
        try:
            # Try to convert to appropriate type
            try:
                value = float(value_str)
                if value.is_integer():
                    value = int(value)
            except ValueError:
                value = value_str  # Keep as string if conversion fails
                
            self.uavcom.SET(param_name, value)
            print(f"Parameter '{param_name}' set to {value}")
        except Exception as e:
            print(f"Error setting parameter: {e}")
            
    def data_reader_worker(self):
        """Worker thread that reads data and puts it in queue"""
        while self.log_running:
            if not self.uavcom.radio.isRadioAlive():
                print("Radio connection lost!")
                break
                
            try:
                value = self.uavcom.GET(self.current_param)
                self.data_queue.put(value)
                print(f"{self.current_param}: {value}")
            except Exception as e:
                print(f"Error reading parameter during logging: {e}")
                
            time.sleep(0.05)  # 20Hz logging rate
            
    def handle_log(self, param_name):
        if self.is_logging:
            print("Logging is already running. Use STOP to stop current logging first.")
            return
            
        if not self.validate_parameter(param_name):
            return
            
        # Set plot limits
        try:
            minstr = input("> Enter min plot value (press Enter for -1): ")
            maxstr = input("> Enter max plot value (press Enter for 1): ")
            minlp = float(minstr) if minstr != '' else -1
            maxlp = float(maxstr) if maxstr != '' else 1
        except ValueError:
            minlp, maxlp = -1, 1
            
        # Initialize plot on main thread (matplotlib window opens here)
        self.lp = LivePlot(minlp, maxlp, 100)
        print(f"Matplotlib plot window opened for '{param_name}'")
        
        # Start logging
        self.current_param = param_name
        self.is_logging = True
        self.log_running = True
        
        # Clear any old data
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except queue.Empty:
                break
        
        # Start data reader thread
        self.log_thread = threading.Thread(target=self.data_reader_worker, daemon=True)
        self.log_thread.start()
        
        print(f"\nStarted logging '{param_name}'. Type 'STOP' to stop logging.")
        
        # Main thread handles plotting
        try:
            while self.log_running:
                try:
                    # Get data from queue with timeout
                    value = self.data_queue.get(timeout=0.1)
                    self.lp.add_data(value)  # Plot on main thread
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Plotting error: {e}")
                    break
        except KeyboardInterrupt:
            pass
            
    def handle_stop(self):
        if self.is_logging:
            self.log_running = False
            self.is_logging = False
            if self.log_thread:
                self.log_thread.join(timeout=1.0)
            print("Logging stopped.")
        else:
            print("No logging currently running.")
            
    def parse_command(self, command_line):
        parts = command_line.strip().split()
        if not parts:
            return
            
        cmd = parts[0].lower()  # Make case-insensitive
        
        if cmd == "get" and len(parts) == 2:
            self.handle_get(parts[1])
        elif cmd == "set" and len(parts) == 3:
            self.handle_set(parts[1], parts[2])
        elif cmd == "log" and len(parts) == 2:
            self.handle_log(parts[1])
        elif cmd == "stop":
            self.handle_stop()
        elif cmd == "show":
            self.show_parameters()
        elif cmd == "exit":
            return False
        else:
            print("Invalid command format. Examples:")
            print("  get sys.test")
            print("  set sys.test 123")
            print("  log sys.test")
            print("  stop")
            print("  show")
            print("  exit")
        return True
            
    def run(self):
        print("Interactive Plotter Started")
        
        # Configure readline for command history and completion
        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode emacs')
        
        # Add command completion
        commands = ['get', 'set', 'log', 'stop', 'show', 'exit']
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
                if self.is_logging:
                    # During logging, check for stop command
                    command = input("> ")
                    if command.lower().strip() == "stop":
                        self.handle_stop()
                    elif command.lower().strip() == "exit":
                        self.handle_stop()
                        break
                    else:
                        print("Type 'stop' to stop logging or 'exit' to quit.")
                    continue
                else:
                    command = input("> ")
                    
                if not self.parse_command(command):
                    break
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                
        # Cleanup
        if self.is_logging:
            self.log_running = False
            if self.log_thread:
                self.log_thread.join(timeout=1.0)

if __name__ == '__main__':
    uavcom = None
    try:
        radioManager.radioSearch(baud=2000000)  # (USB Connection) has no Baudrate
        if not len(radioManager.availableRadios) > 0:
            print("No radios found. Exiting.")
            sys.exit()

        time.sleep(1)
        
        uavcom = NorthCOM(uri=uri)
        uavcom.connect()        # Request ACK to sended MSG
        uavcom.synchronize()    # Syncronize the NRX Table

        uavtable = uavcom.getParamTable()
        
        # Create and run interactive plotter
        plotter = InteractivePlotter(uavcom, uavtable)
        plotter.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        try:
            if uavcom:
                uavcom.destroy()
        except:
            pass
        radioManager.closeAvailableRadios()
        
        print("Plotter app exit")
        time.sleep(0.1)
        sys.exit()
