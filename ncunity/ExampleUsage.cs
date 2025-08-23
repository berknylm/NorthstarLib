using UnityEngine;

public class ExampleUsage : MonoBehaviour
{
    [SerializeField] private NorthStarController controller;
    [SerializeField] private int[] agentIds = { 72, 74, 76 };

    void Start()
    {
        controller.OnSuccess += (response) => Debug.Log("Success: " + response);
        controller.OnError += (error) => Debug.LogError("Error: " + error);
    }

    public void StartMission()
    {
        controller.Link(72, 74, 76);
        controller.Origin(40.8038411, 29.3580665, 72);
        controller.Origin(40.8038411, 29.3580665, 74);
        controller.Origin(40.8038411, 29.3580665, 76);
        controller.Arm(72);
        controller.Arm(74);
        controller.Arm(76);
        controller.Takeoff(10f, 15f, 72);
        controller.Takeoff(10f, 15f, 74);
        controller.Takeoff(10f, 15f, 76);
    }

    public void MoveFormation()
    {
        controller.Move(-5f, 0f, 7f, 12f, 72);
        controller.Move(0f, 0f, 12f, 12f, 74);
        controller.Move(5f, 0f, 7f, 12f, 76);
    }

    public void LandAll()
    {
        controller.Land(72);
        controller.Land(74);
        controller.Land(76);
        controller.Disarm(72);
        controller.Disarm(74);
        controller.Disarm(76);
    }

    public void SendAllHome()
    {
        controller.Home(72);
        controller.Home(74);
        controller.Home(76);
    }

    public void QueuedMission()
    {
        controller.Arm(72, true);
        controller.Arm(74, true);
        controller.Arm(76, true);
        controller.Delay(3f, 72);
        controller.Delay(3f, 74);
        controller.Delay(3f, 76);
        controller.Takeoff(10f, 15f, 72, true);
        controller.Takeoff(10f, 15f, 74, true);
        controller.Takeoff(10f, 15f, 76, true);
        controller.Delay(10f, 72);
        controller.Delay(10f, 74);
        controller.Delay(10f, 76);
        controller.Move(-5f, 0f, 7f, 8f, 72, true);
        controller.Move(0f, 0f, 12f, 8f, 74, true);
        controller.Move(5f, 0f, 7f, 8f, 76, true);
        controller.Delay(15f, 72);
        controller.Delay(15f, 74);
        controller.Delay(15f, 76);
        controller.Land(72, true);
        controller.Land(74, true);
        controller.Land(76, true);
        controller.Launch(72, 74, 76);
    }

    public void DirectCommand()
    {
        controller.ExecuteCommand("move", 5f, 0f, 8f, 10f, 72);
        controller.ExecuteCommand("takeoff", 12f, 15f, 74);
        controller.ExecuteCommand("link", 72, 74, 76);
    }

    public void WithCallback()
    {
        controller.ExecuteCommand("arm", (success) => {
            if (success)
                controller.ExecuteCommand("takeoff", 8f, 12f, 72);
        }, 72);
    }

    public void EmergencyKill()
    {
        controller.Kill(72);
        controller.Kill(74);
        controller.Kill(76);
    }

    public void CheckStatus()
    {
        controller.Status(72, 74, 76);
    }

    public void UnlinkAll()
    {
        controller.UnlinkAll();
    }
}