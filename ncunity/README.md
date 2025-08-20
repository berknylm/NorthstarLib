# NorthStar Unity Controller

Unity C# script for controlling NorthStar UAVs without external dependencies.

## Setup

1. Copy `NorthStarController.cs` to your Unity project
2. Attach to a GameObject
3. Configure host/port in Inspector
4. Start using the API

## Usage

### Basic Commands
```csharp
[SerializeField] private NorthStarController controller;

void Start()
{
    controller.OnSuccess += (response) => Debug.Log("Success");
    controller.OnError += (error) => Debug.LogError("Error: " + error);
}

public void SimpleFlight()
{
    controller.Link(72);
    controller.Arm(72);
    controller.Takeoff(10f, 15f, 72);
    controller.Move(5f, 0f, 8f, 12f, 72);
    controller.Land(72);
    controller.Disarm(72);
}
```

### Direct Commands
```csharp
controller.ExecuteCommand("link", 72, 74, 76);
controller.ExecuteCommand("takeoff", 10f, 15f, 72);
controller.ExecuteCommand("move", 5f, 0f, 8f, 12f, 72);
```

### Queued Commands
```csharp
controller.Arm(72, true);
controller.Takeoff(10f, 15f, 72, true);
controller.Move(5f, 0f, 8f, 12f, 72, true);
controller.Launch(72);
```

## API Reference

| Method | Parameters | Description |
|--------|------------|-------------|
| `Link()` | agentIds | Link agents |
| `Unlink()` | agentIds | Unlink agents |
| `UnlinkAll()` | | Unlink all |
| `Origin()` | lat, lon, agentId, setCmd | Set GPS origin |
| `Arm()` | agentId, setCmd | Arm motors |
| `Disarm()` | agentId, setCmd | Disarm motors |
| `Takeoff()` | altitude, time, agentId, setCmd | Takeoff |
| `Move()` | x, y, z, time, agentId, setCmd | Move to position |
| `Land()` | agentId, setCmd | Land |
| `Kill()` | agentId | Emergency kill |
| `Delay()` | seconds, agentId, setCmd | Add delay |
| `Launch()` | agentIds | Execute queued commands |
| `Status()` | agentIds | Get status |
| `Shutdown()` | | Stop daemon |

## Features

- No external dependencies (no Newtonsoft.Json needed)
- Non-blocking Unity execution
- Command queue system
- Built-in JSON serialization
- Event-based callbacks
- Support for all NorthStar commands
- Time parameters for takeoff/move