#!/usr/bin/env python3
"""
NorthstarLib CLI - Main Entry Point
Simple command-line interface for UAV management
"""

import argparse
import sys
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ncclient import NorthClient
from ncconfig import NorthConfig

def handle_link(args):
    """Link agents to the daemon"""
    try:
        client = NorthClient()
        response = client.send_request({
            "action": "link", 
            "ids": [str(x) for x in args.ids]
        })
        
        if response and response.get("ok"):
            for agent_id in args.ids:
                print(f"Linked agent {agent_id}")
        else:
            print("Failed to link agents")
            
    except Exception as e:
        print(f"Error: {e}")

def handle_unlink(args):
    """Unlink agents from the daemon"""
    try:
        client = NorthClient()
        response = client.send_request({
            "action": "unlink",
            "ids": [str(x) for x in args.ids] if not args.all else [],
            "all": args.all
        })
        
        if response and response.get("ok"):
            if args.all:
                print("All agents unlinked")
            else:
                for agent_id in args.ids:
                    print(f"Unlinked agent {agent_id}")
        else:
            print("Failed to unlink agents")
            
    except Exception as e:
        print(f"Error: {e}")

def handle_status(args):
    """Get status from agents"""
    try:
        client = NorthClient()
        response = client.send_request({
            "action": "status",
            "ids": [str(x) for x in args.ids] if args.ids else None,
            "pos": args.pos,
            "rot": args.rot,
            "nav": args.nav,
            "batt": args.batt
        })
        
        if response and "status" in response:
            for agent_id, info in response["status"].items():
                print(f"Agent {agent_id}:")
                if "error" in info:
                    print(f"  Error: {info['error']}")
                    continue
                    
                if args.pos and "pos" in info:
                    print(f"  Position: {info['pos']}")
                if args.rot and "rot" in info:
                    print(f"  Rotation: {info['rot']}")
                if args.nav and "nav" in info:
                    print(f"  Navigation: {info['nav']}")
                if args.batt and "batt" in info:
                    print(f"  Battery: {info['batt']}")
        else:
            print("Failed to get status")
            
    except Exception as e:
        print(f"Error: {e}")

def handle_origin(args):
    """Set GPS origin coordinates"""
    try:
        # Parse coordinates
        coords = args.coordinates.replace('"', '').split(',')
        if len(coords) != 2:
            print("Error: Origin requires lat,lon format")
            return
            
        lat = float(coords[0].strip())
        lon = float(coords[1].strip())
        
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to set origin for")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "origin",
                "id": str(agent_id),
                "lat": lat,
                "lon": lon
            })
            
            if response and response.get("ok"):
                print(f"Origin set for agent {agent_id}: {lat}, {lon}")
            else:
                print(f"Failed to set origin for agent {agent_id}")
                
    except ValueError:
        print("Error: Invalid coordinate format")
    except Exception as e:
        print(f"Error: {e}")
        
def handle_arm(args):
    """Arm UAV agents"""
    try:
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to arm")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "arm",
                "id": str(agent_id)
            })
            
            if response and response.get("ok"):
                print(f"Armed agent {agent_id}")
            else:
                print(f"Failed to arm agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_disarm(args):
    """Disarm UAV agents"""
    try:
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to disarm")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "disarm",
                "id": str(agent_id)
            })
            
            if response and response.get("ok"):
                print(f"Disarmed agent {agent_id}")
            else:
                print(f"Failed to disarm agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_takeoff(args):
    """Command UAVs to takeoff"""
    try:
        client = NorthClient()
        altitude = float(args.altitude.replace('"', ''))
        time_param = float(args.time.replace('"', '')) if hasattr(args, 'time') and args.time else 10.0
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to takeoff")
            return
                
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "takeoff",
                "id": str(agent_id),
                "altitude": altitude,
                "time": time_param
            })
            
            if response and response.get("ok"):
                print(f"Takeoff command sent to agent {agent_id} (altitude: {altitude}m, time: {time_param}s)")
            else:
                print(f"Failed to send takeoff to agent {agent_id}")
                
    except ValueError:
        print("Error: Invalid altitude or time value")
    except Exception as e:
        print(f"Error: {e}")

def handle_delay(args):
    """Wait for specified seconds"""
    try:
        seconds = float(args.seconds.replace('"', ''))
        print(f"Waiting {seconds} seconds...")
        time.sleep(seconds)
        print("Wait completed")
    except ValueError:
        print("Error: Invalid delay value")
    except Exception as e:
        print(f"Error: {e}")

def handle_move(args):
    """Move UAV to specified position"""
    try:
        # Parse coordinates - support both positional and named arguments
        if hasattr(args, 'pos') and args.pos:
            coords = args.pos.replace('"', '').split(',')
        else:
            coords = args.position.replace('"', '').split(',')
            
        if len(coords) != 3:
            print("Error: Position requires x,y,z format")
            return
            
        x = float(coords[0].strip())
        y = float(coords[1].strip())
        z = float(coords[2].strip())
        
        # Parse time parameter - support both positional and named arguments  
        time_param = 1.0  # default
        if hasattr(args, 't') and args.t:
            time_param = float(args.t.replace('"', ''))
        elif hasattr(args, 'time') and args.time:
            time_param = float(args.time.replace('"', ''))
        
        client = NorthClient()
        agent_id = int(args.agent)
        
        response = client.send_request({
            "action": "move",
            "id": str(agent_id),
            "position": [x, y, z],
            "time": time_param
        })
        
        if response and response.get("ok"):
            print(f"Move command sent to agent {agent_id}: ({x}, {y}, {z}) in {time_param}s")
        else:
            print(f"Failed to send move command to agent {agent_id}")
            
    except ValueError:
        print("Error: Invalid position or time format")
    except Exception as e:
        print(f"Error: {e}")

def handle_land(args):
    """Command UAVs to land"""
    try:
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to land")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "land",
                "id": str(agent_id)
            })
            
            if response and response.get("ok"):
                print(f"Land command sent to agent {agent_id}")
            else:
                print(f"Failed to send land command to agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_home(args):
    """Send UAVs to home position"""
    try:
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to send home")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "home",
                "id": str(agent_id)
            })
            
            if response and response.get("ok"):
                print(f"Home command sent to agent {agent_id}")
            else:
                print(f"Failed to send home command to agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_kill(args):
    """Emergency kill UAV agents"""
    try:
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to kill")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "kill",
                "id": str(agent_id)
            })
            
            if response and response.get("ok"):
                print(f"Kill command sent to agent {agent_id}")
            else:
                print(f"Failed to send kill command to agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_launch(args):
    """Launch all queued commands on UAV agents"""
    try:
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to launch")
            return
            
        response = client.send_request({
            "action": "launch",
            "ids": agent_ids
        })
        
        if response and response.get("ok"):
            print(f"Launch command sent to {len(agent_ids)} agents")
        else:
            print("Failed to send launch command")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_run(args):
    """Start the daemon"""
    try:
        from ncdaemon import NorthDaemon
        daemon = NorthDaemon()
        daemon.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("Daemon stopped")
    except Exception as e:
        print(f"Error starting daemon: {e}")

# Set command handlers (async operations)
def handle_origin_set(args):
    """Queue GPS origin setting command"""
    try:
        # Parse coordinates
        coords = args.coordinates.replace('"', '').split(',')
        if len(coords) != 2:
            print("Error: Origin requires lat,lon format")
            return
            
        lat = float(coords[0].strip())
        lon = float(coords[1].strip())
        
        client = NorthClient()
        
        if args.all:
            # Get all linked agents
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to set origin for")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "origin",
                "id": str(agent_id),
                "lat": lat,
                "lon": lon,
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Origin command queued for agent {agent_id}: {lat}, {lon}")
            else:
                print(f"Failed to queue origin command for agent {agent_id}")
                
    except ValueError:
        print("Error: Invalid coordinate format")
    except Exception as e:
        print(f"Error: {e}")

def handle_arm_set(args):
    """Queue arm command"""
    try:
        client = NorthClient()
        
        if args.all:
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to arm")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "arm",
                "id": str(agent_id),
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Arm command queued for agent {agent_id}")
            else:
                print(f"Failed to queue arm command for agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_disarm_set(args):
    """Queue disarm command"""
    try:
        client = NorthClient()
        
        if args.all:
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to disarm")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "disarm",
                "id": str(agent_id),
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Disarm command queued for agent {agent_id}")
            else:
                print(f"Failed to queue disarm command for agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_takeoff_set(args):
    """Queue takeoff command"""
    try:
        client = NorthClient()
        altitude = float(args.altitude.replace('"', ''))
        time_param = float(args.time.replace('"', '')) if hasattr(args, 'time') and args.time else 10.0
        
        if args.all:
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to takeoff")
            return
                
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "takeoff",
                "id": str(agent_id),
                "altitude": altitude,
                "time": time_param,
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Takeoff command queued for agent {agent_id} (altitude: {altitude}m, time: {time_param}s)")
            else:
                print(f"Failed to queue takeoff command for agent {agent_id}")
                
    except ValueError:
        print("Error: Invalid altitude or time value")
    except Exception as e:
        print(f"Error: {e}")

def handle_move_set(args):
    """Queue move command"""
    try:
        # Parse coordinates - support both positional and named arguments
        if hasattr(args, 'pos') and args.pos:
            coords = args.pos.replace('"', '').split(',')
        else:
            coords = args.position.replace('"', '').split(',')
            
        if len(coords) != 3:
            print("Error: Position requires x,y,z format")
            return
            
        x = float(coords[0].strip())
        y = float(coords[1].strip())
        z = float(coords[2].strip())
        
        # Parse time parameter - support both positional and named arguments
        time_param = 1.0  # default
        if hasattr(args, 't') and args.t:
            time_param = float(args.t.replace('"', ''))
        elif hasattr(args, 'time') and args.time:
            time_param = float(args.time.replace('"', ''))
        
        client = NorthClient()
        agent_id = int(args.agent)
        
        response = client.send_request({
            "action": "move",
            "id": str(agent_id),
            "position": [x, y, z],
            "time": time_param,
            "setcmd": True
        })
        
        
        if response and response.get("ok"):
            print(f"Move command queued for agent {agent_id}: ({x}, {y}, {z}) in {time_param}s")
        else:
            print(f"Failed to queue move command for agent {agent_id}")
            
    except ValueError:
        print("Error: Invalid position or time format")
    except Exception as e:
        print(f"Error: {e}")

def handle_land_set(args):
    """Queue land command"""
    try:
        client = NorthClient()
        
        if args.all:
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to land")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "land",
                "id": str(agent_id),
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Land command queued for agent {agent_id}")
            else:
                print(f"Failed to queue land command for agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_home_set(args):
    """Queue home command"""
    try:
        client = NorthClient()
        
        if args.all:
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to send home")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "home",
                "id": str(agent_id),
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Home command queued for agent {agent_id}")
            else:
                print(f"Failed to queue home command for agent {agent_id}")
                
    except Exception as e:
        print(f"Error: {e}")

def handle_delay_set(args):
    """Queue delay command"""
    try:
        seconds = float(args.seconds.replace('"', ''))
        
        client = NorthClient()
        
        if args.all:
            config = NorthConfig()
            agent_ids = config.load_links()
        else:
            agent_ids = args.agents if hasattr(args, 'agents') and args.agents else []
            
        if not agent_ids:
            print("No agents to delay")
            return
            
        for agent_id in agent_ids:
            response = client.send_request({
                "action": "delay",
                "id": str(agent_id),
                "seconds": seconds,
                "setcmd": True
            })
            
            if response and response.get("ok"):
                print(f"Delay command queued for agent {agent_id}: {seconds} seconds")
            else:
                print(f"Failed to queue delay command for agent {agent_id}")
                
    except ValueError:
        print("Error: Invalid delay value")
    except Exception as e:
        print(f"Error: {e}")

def handle_stop(args):
    """Stop the daemon"""
    try:
        client = NorthClient()
        response = client.send_request({"action": "shutdown"})
        if response:
            print("Daemon stopped")
        else:
            print("Could not stop daemon (may not be running)")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(prog="nc", description="NorthstarLib CLI")
    subparsers = parser.add_subparsers(dest="cmd")

    # Daemon commands
    run_parser = subparsers.add_parser("run", help="Start daemon")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host address")
    run_parser.add_argument("--port", type=int, default=7777, help="Port number")
    run_parser.set_defaults(func=handle_run)

    # Link command
    link_parser = subparsers.add_parser("link", help="Link agents")
    link_parser.add_argument("ids", nargs="+", type=int, help="Agent IDs")
    link_parser.set_defaults(func=handle_link)

    # Unlink command
    unlink_parser = subparsers.add_parser("unlink", help="Unlink agents")
    unlink_parser.add_argument("ids", nargs="*", type=int, help="Agent IDs")
    unlink_parser.add_argument("--all", action="store_true", help="Unlink all agents")
    unlink_parser.set_defaults(func=handle_unlink)

    # Origin command
    origin_parser = subparsers.add_parser("origin", help="Set GPS origin coordinates")
    origin_parser.add_argument("coordinates", help="GPS coordinates as \"lat,lon\"")
    origin_parser.add_argument("--all", action="store_true", help="Set for all agents")
    origin_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    origin_parser.set_defaults(func=handle_origin)

    # Arm command
    arm_parser = subparsers.add_parser("arm", help="Arm UAVs")
    arm_parser.add_argument("--all", action="store_true", help="Arm all agents")
    arm_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    arm_parser.set_defaults(func=handle_arm)

    # Disarm command
    disarm_parser = subparsers.add_parser("disarm", help="Disarm UAVs")
    disarm_parser.add_argument("--all", action="store_true", help="Disarm all agents")
    disarm_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    disarm_parser.set_defaults(func=handle_disarm)

    # Takeoff command
    takeoff_parser = subparsers.add_parser("takeoff", help="Command UAVs to takeoff")
    takeoff_parser.add_argument("altitude", help="Takeoff altitude in meters")
    takeoff_parser.add_argument("time", nargs="?", help="Time for takeoff in seconds (optional)")
    takeoff_parser.add_argument("--all", action="store_true", help="Takeoff all agents")
    takeoff_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    takeoff_parser.set_defaults(func=handle_takeoff)

    # Delay command
    delay_parser = subparsers.add_parser("delay", help="Wait for specified seconds")
    delay_parser.add_argument("seconds", help="Number of seconds to wait")
    delay_parser.set_defaults(func=handle_delay)

    # Move command - support multiple syntax formats
    move_parser = subparsers.add_parser("move", help="Move UAV to position")
    move_parser.add_argument("position", nargs="?", help="Position as \"x,y,z\" (positional)")
    move_parser.add_argument("time", nargs="?", help="Time in seconds (positional)")
    move_parser.add_argument("agent", type=int, help="Agent ID")
    move_parser.add_argument("--pos", help="Position as \"x,y,z\" (named parameter)")
    move_parser.add_argument("--t", help="Time in seconds (named parameter)")
    move_parser.set_defaults(func=handle_move)

    # Land command
    land_parser = subparsers.add_parser("land", help="Command UAVs to land")
    land_parser.add_argument("--all", action="store_true", help="Land all agents")
    land_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    land_parser.set_defaults(func=handle_land)

    # Home command
    home_parser = subparsers.add_parser("home", help="Send UAVs to home position")
    home_parser.add_argument("--all", action="store_true", help="Send all agents home")
    home_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    home_parser.set_defaults(func=handle_home)

    # Kill command
    kill_parser = subparsers.add_parser("kill", help="Emergency kill UAVs")
    kill_parser.add_argument("--all", action="store_true", help="Kill all agents")
    kill_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    kill_parser.set_defaults(func=handle_kill)

    # Launch command
    launch_parser = subparsers.add_parser("launch", help="Execute all queued commands")
    launch_parser.add_argument("--all", action="store_true", help="Launch all agents")
    launch_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    launch_parser.set_defaults(func=handle_launch)

    # Status command (kept for debugging)
    status_parser = subparsers.add_parser("status", help="Get agent status")
    status_parser.add_argument("ids", nargs="*", type=int, help="Agent IDs")
    status_parser.add_argument("-pos", action="store_true", help="Show position")
    status_parser.add_argument("-rot", action="store_true", help="Show rotation") 
    status_parser.add_argument("-nav", action="store_true", help="Show navigation")
    status_parser.add_argument("-batt", action="store_true", help="Show battery")
    status_parser.set_defaults(func=handle_status)

    stop_parser = subparsers.add_parser("stop", help="Stop daemon")
    stop_parser.set_defaults(func=handle_stop)

    # Set command group for async operations
    set_parser = subparsers.add_parser("set", help="Queue commands for async execution")
    set_subparsers = set_parser.add_subparsers(dest="set_cmd")

    # Set Origin command
    set_origin_parser = set_subparsers.add_parser("origin", help="Queue GPS origin setting")
    set_origin_parser.add_argument("coordinates", help="GPS coordinates as \"lat,lon\"")
    set_origin_parser.add_argument("--all", action="store_true", help="Set for all agents")
    set_origin_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_origin_parser.set_defaults(func=lambda args: handle_origin_set(args))

    # Set Arm command
    set_arm_parser = set_subparsers.add_parser("arm", help="Queue arm command")
    set_arm_parser.add_argument("--all", action="store_true", help="Arm all agents")
    set_arm_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_arm_parser.set_defaults(func=lambda args: handle_arm_set(args))

    # Set Disarm command
    set_disarm_parser = set_subparsers.add_parser("disarm", help="Queue disarm command")
    set_disarm_parser.add_argument("--all", action="store_true", help="Disarm all agents")
    set_disarm_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_disarm_parser.set_defaults(func=lambda args: handle_disarm_set(args))

    # Set Takeoff command
    set_takeoff_parser = set_subparsers.add_parser("takeoff", help="Queue takeoff command")
    set_takeoff_parser.add_argument("altitude", help="Takeoff altitude in meters")
    set_takeoff_parser.add_argument("time", nargs="?", help="Time for takeoff in seconds (optional)")
    set_takeoff_parser.add_argument("--all", action="store_true", help="Takeoff all agents")
    set_takeoff_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_takeoff_parser.set_defaults(func=lambda args: handle_takeoff_set(args))

    # Set Move command - support multiple syntax formats
    set_move_parser = set_subparsers.add_parser("move", help="Queue move command")
    set_move_parser.add_argument("position", nargs="?", help="Position as \"x,y,z\" (positional)")
    set_move_parser.add_argument("time", nargs="?", help="Time in seconds (positional)")
    set_move_parser.add_argument("agent", type=int, help="Agent ID")
    set_move_parser.add_argument("--pos", help="Position as \"x,y,z\" (named parameter)")
    set_move_parser.add_argument("--t", help="Time in seconds (named parameter)")
    set_move_parser.set_defaults(func=lambda args: handle_move_set(args))

    # Set Land command
    set_land_parser = set_subparsers.add_parser("land", help="Queue land command")
    set_land_parser.add_argument("--all", action="store_true", help="Land all agents")
    set_land_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_land_parser.set_defaults(func=lambda args: handle_land_set(args))

    # Set Home command
    set_home_parser = set_subparsers.add_parser("home", help="Queue home command")
    set_home_parser.add_argument("--all", action="store_true", help="Send all agents home")
    set_home_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_home_parser.set_defaults(func=lambda args: handle_home_set(args))

    # Set Delay command
    set_delay_parser = set_subparsers.add_parser("delay", help="Queue delay command")
    set_delay_parser.add_argument("seconds", help="Number of seconds to wait")
    set_delay_parser.add_argument("--all", action="store_true", help="Delay all agents")
    set_delay_parser.add_argument("agents", nargs="*", type=int, help="Specific agent IDs")
    set_delay_parser.set_defaults(func=lambda args: handle_delay_set(args))

    # Parse and execute
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()