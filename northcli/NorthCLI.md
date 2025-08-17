# NorthCLI - UAV Command Line Interface

## Quick Start
```bash
python nc.py run                             # Start daemon
python nc.py link 72 74 76                   # Link agents
python nc.py origin "41.535, 24.424" --all   # Set GPS origin
python nc.py arm --all                       # Arm all
python nc.py takeoff "12" 72 74              # Takeoff to 12m
python nc.py move "10.3, 14.2, 3.0" 72       # Move agent 72
python nc.py delay "10"                      # Wait 10 seconds
python nc.py land --all                      # Land all
python nc.py kill --all                     # Emergency kill all
python nc.py disarm --all                   # Disarm all
```

## Commands

| Command | Example | Description |
|---------|---------|-------------|
| `run` | `python nc.py run` | Start daemon |
| `stop` | `python nc.py stop` | Stop daemon |
| `link` | `python nc.py link 72 74` | Link agents to radios |
| `unlink` | `python nc.py unlink --all` | Unlink agents |
| `origin` | `python nc.py origin "lat,lon" --all` | Set GPS origin |
| `arm` | `python nc.py arm --all` | Arm UAVs |
| `disarm` | `python nc.py disarm --all` | Disarm UAVs |
| `takeoff` | `python nc.py takeoff "12" 72 74` | Takeoff to altitude |
| `move` | `python nc.py move "x,y,z" 72` | Move to position (single agent) |
| `delay` | `python nc.py delay "10"` | Wait seconds |
| `land` | `python nc.py land --all` | Land UAVs |
| `kill` | `python nc.py kill --all` | Emergency kill UAVs |
| `launch` | `python nc.py launch --all` | Execute all queued commands |

## Notes
- Use quotes around coordinates and numbers: `"12"`, `"x,y,z"`
- Agent linking order: first agent → radio 0, second → radio 1, etc.
- Use `--all` for all agents or specify individual IDs

## Async Commands

- Use `set` keyword for async commands. 
- Async operation sets in the uav, when send `launch` command, uav executes the operation.

| Command | Example | Description |
|---------|---------|-------------|
| `origin` | `python nc.py set origin "lat,lon" --all` | Set GPS origin command |
| `arm` | `python nc.py set arm --all` | Set Arm command in all UAVs |
| `disarm` | `python nc.py set disarm --all` | Set Disarm command in all UAVs |
| `takeoff` | `python nc.py set takeoff "12" 72 74` | Set Takeoff to altitude command |
| `move` | `python nc.py set move "x,y,z" 72` | Set Move to position (single agent) |
| `delay` | `python nc.py set delay "10"` | Set Wait seconds |
| `land` | `python nc.py set land --all` | Set Land UAVs |

