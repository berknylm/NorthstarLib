using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class NorthStarController : MonoBehaviour
{
    [SerializeField] private string host = "127.0.0.1";
    [SerializeField] private int port = 7777;
    [SerializeField] private bool debugMode = true;

    private readonly Queue<CommandRequest> commandQueue = new Queue<CommandRequest>();
    private bool isProcessing = false;

    public Action<string> OnSuccess;
    public Action<string> OnError;

    private class CommandRequest
    {
        public string command;
        public Dictionary<string, object> args;
        public Action<bool> callback;
    }

    [Serializable]
    public class Response
    {
        public bool ok;
        public string error;
        public Dictionary<string, object> status;
    }

    public static NorthStarController Instance { get; private set; }

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        StartCoroutine(ProcessCommands());
    }

    private IEnumerator ProcessCommands()
    {
        while (true)
        {
            if (commandQueue.Count > 0 && !isProcessing)
            {
                isProcessing = true;
                var request = commandQueue.Dequeue();
                yield return SendCommand(request);   // <-- yield the IEnumerator directly
                isProcessing = false;
            }
            yield return null;
        }
    }

    private IEnumerator SendCommand(CommandRequest request)
    {
        bool success = false;
        string responseText = "";

        yield return SendTCP(request.command, request.args, (result, response) =>
        {
            success = result;
            responseText = response;
        });

        if (success)
        {
            OnSuccess?.Invoke(responseText);
            if (debugMode) Debug.Log($"Command '{request.command}' succeeded");
        }
        else
        {
            OnError?.Invoke(responseText);
            if (debugMode) Debug.LogError($"Command '{request.command}' failed: {responseText}");
        }

        request.callback?.Invoke(success);
    }

    private IEnumerator SendTCP(string command, Dictionary<string, object> args, Action<bool, string> callback)
    {
        var requestData = new Dictionary<string, object> { ["action"] = command };
        if (args != null) foreach (var kvp in args) requestData[kvp.Key] = kvp.Value;

        TcpClient client = null;
        NetworkStream stream = null;

        bool success = false;
        string response = "";

        try // NOTE: try-finally (no catch). yield'lar sadece try içinde.
        {
            client = new TcpClient();
            var connectTask = client.ConnectAsync(host, port);
            while (!connectTask.IsCompleted) yield return null;

            if (connectTask.IsFaulted)
            {
                response = connectTask.Exception?.GetBaseException().Message ?? "Connection failed";
                callback(false, response);
                yield break;
            }

            if (!client.Connected)
            {
                callback(false, "Connection failed");
                yield break;
            }

            stream = client.GetStream();

            // Write
            var json = JsonToString(requestData);
            var data = Encoding.UTF8.GetBytes(json);
            var writeTask = stream.WriteAsync(data, 0, data.Length);
            while (!writeTask.IsCompleted) yield return null;

            if (writeTask.IsFaulted)
            {
                response = writeTask.Exception?.GetBaseException().Message ?? "Write failed";
                callback(false, response);
                yield break;
            }

            stream.Flush();
            try { client.Client.Shutdown(SocketShutdown.Send); } catch { /* optional */ }

            // Read
            var buffer = new byte[4096];
            var sb = new StringBuilder();
            while (true)
            {
                var readTask = stream.ReadAsync(buffer, 0, buffer.Length);
                while (!readTask.IsCompleted) yield return null;

                if (readTask.IsFaulted)
                {
                    response = readTask.Exception?.GetBaseException().Message ?? "Read failed";
                    callback(false, response);
                    yield break;
                }

                int bytes = readTask.Result;
                if (bytes == 0) break;
                sb.Append(Encoding.UTF8.GetString(buffer, 0, bytes));
            }

            response = sb.ToString();
            var parsed = JsonFromString<Response>(response);
            success = parsed.ok;
            if (!success && !string.IsNullOrEmpty(parsed.error))
                response = parsed.error;
        }
        finally
        {
            stream?.Close();
            client?.Close();
        }

        callback(success, response);
    }

    private void QueueCommand(string command, Dictionary<string, object> args = null, Action<bool> callback = null)
    {
        if (args == null) args = new Dictionary<string, object>();

        commandQueue.Enqueue(new CommandRequest
        {
            command = command,
            args = args,
            callback = callback
        });
    }

    public void ExecuteCommand(string command, params object[] parameters)
    {
        var args = ParseParameters(command, parameters);
        QueueCommand(command, args);
    }

    public void ExecuteCommand(string command, Action<bool> callback, params object[] parameters)
    {
        var args = ParseParameters(command, parameters);
        QueueCommand(command, args, callback);
    }

    private Dictionary<string, object> ParseParameters(string command, object[] parameters)
    {
        var args = new Dictionary<string, object>();

        switch (command.ToLower())
        {
            case "link":
                args["ids"] = ConvertToStringArray(parameters);
                break;

            case "unlink":
                if (parameters.Length > 0 && parameters[0].ToString().ToLower() == "all")
                {
                    args["all"] = true;
                    args["ids"] = Array.Empty<string>();
                }
                else
                {
                    args["ids"] = ConvertToStringArray(parameters);
                    args["all"] = false;
                }
                break;

            case "origin":
                if (parameters.Length >= 2)
                {
                    args["lat"] = Convert.ToDouble(parameters[0], CultureInfo.InvariantCulture);
                    args["lon"] = Convert.ToDouble(parameters[1], CultureInfo.InvariantCulture);
                    if (parameters.Length > 2) args["id"] = parameters[2].ToString();
                    if (parameters.Length > 3) args["setcmd"] = Convert.ToBoolean(parameters[3], CultureInfo.InvariantCulture);
                }
                break;

            case "arm":
            case "disarm":
            case "land":
                if (parameters.Length > 0)
                {
                    args["id"] = parameters[0].ToString();
                    if (parameters.Length > 1) args["setcmd"] = Convert.ToBoolean(parameters[1], CultureInfo.InvariantCulture);
                }
                break;

            case "takeoff":
                if (parameters.Length > 0) args["altitude"] = Convert.ToSingle(parameters[0], CultureInfo.InvariantCulture);
                if (parameters.Length > 1) args["time"] = Convert.ToSingle(parameters[1], CultureInfo.InvariantCulture);
                if (parameters.Length > 2) args["id"] = parameters[2].ToString();
                if (parameters.Length > 3) args["setcmd"] = Convert.ToBoolean(parameters[3], CultureInfo.InvariantCulture);
                break;

            case "move":
                if (parameters.Length >= 4)
                {
                    args["position"] = new float[]
                    {
                        Convert.ToSingle(parameters[0], CultureInfo.InvariantCulture),
                        Convert.ToSingle(parameters[1], CultureInfo.InvariantCulture),
                        Convert.ToSingle(parameters[2], CultureInfo.InvariantCulture)
                    };
                    if (parameters.Length > 3) args["time"] = Convert.ToSingle(parameters[3], CultureInfo.InvariantCulture);
                    if (parameters.Length > 4) args["id"] = parameters[4].ToString();
                    if (parameters.Length > 5) args["setcmd"] = Convert.ToBoolean(parameters[5], CultureInfo.InvariantCulture);
                }
                break;

            case "kill":
                if (parameters.Length > 0) args["id"] = parameters[0].ToString();
                break;

            case "delay":
                if (parameters.Length > 0) args["seconds"] = Convert.ToSingle(parameters[0], CultureInfo.InvariantCulture);
                if (parameters.Length > 1) args["id"] = parameters[1].ToString();
                if (parameters.Length > 2) args["setcmd"] = Convert.ToBoolean(parameters[2], CultureInfo.InvariantCulture);
                break;

            case "launch":
                args["ids"] = ConvertToStringArray(parameters);
                break;

            case "status":
                if (parameters.Length > 0) args["ids"] = ConvertToStringArray(parameters);
                break;

            case "shutdown":
                break;

            default:
                Debug.LogWarning($"Unknown command: {command}");
                break;
        }

        return args;
    }

    private string[] ConvertToStringArray(object[] parameters)
    {
        var result = new string[parameters.Length];
        for (int i = 0; i < parameters.Length; i++)
            result[i] = parameters[i]?.ToString();
        return result;
    }

    public void Link(params int[] agentIds) => ExecuteCommand("link", agentIds.Cast<object>().ToArray());
    public void Unlink(params int[] agentIds) => ExecuteCommand("unlink", agentIds.Cast<object>().ToArray());
    public void UnlinkAll() => ExecuteCommand("unlink", "all");
    public void Origin(double lat, double lon, int agentId, bool setCmd = false) => ExecuteCommand("origin", lat, lon, agentId, setCmd);
    public void Arm(int agentId, bool setCmd = false) => ExecuteCommand("arm", agentId, setCmd);
    public void Disarm(int agentId, bool setCmd = false) => ExecuteCommand("disarm", agentId, setCmd);
    public void Takeoff(float altitude, float time, int agentId, bool setCmd = false) => ExecuteCommand("takeoff", altitude, time, agentId, setCmd);
    public void Move(float x, float y, float z, float time, int agentId, bool setCmd = false) => ExecuteCommand("move", x, y, z, time, agentId, setCmd);
    public void Move(Vector3 position, float time, int agentId, bool setCmd = false) => ExecuteCommand("move", position.x, position.y, position.z, time, agentId, setCmd);
    public void Land(int agentId, bool setCmd = false) => ExecuteCommand("land", agentId, setCmd);
    public void Kill(int agentId) => ExecuteCommand("kill", agentId);
    public void Delay(float seconds, int agentId, bool setCmd = true) => ExecuteCommand("delay", seconds, agentId, setCmd);
    public void Launch(params int[] agentIds) => ExecuteCommand("launch", agentIds.Cast<object>().ToArray());
    public void Status(params int[] agentIds) => ExecuteCommand("status", agentIds.Cast<object>().ToArray());
    public void Shutdown() => ExecuteCommand("shutdown");

    private string JsonToString(Dictionary<string, object> data)
    {
        var json = new StringBuilder("{");
        bool first = true;

        foreach (var kvp in data)
        {
            if (!first) json.Append(",");
            first = false;

            json.Append($"\"{kvp.Key}\":");

            if (kvp.Value == null)
            {
                json.Append("null");
            }
            else if (kvp.Value is string s)
            {
                json.Append($"\"{s}\"");
            }
            else if (kvp.Value is bool b)
            {
                json.Append(b ? "true" : "false");
            }
            else if (kvp.Value is Array arr)
            {
                json.Append("[");
                for (int i = 0; i < arr.Length; i++)
                {
                    if (i > 0) json.Append(",");
                    var item = arr.GetValue(i);
                    if (item is string si)
                        json.Append($"\"{si}\"");
                    else if (item is IFormattable f)
                        json.Append(f.ToString(null, CultureInfo.InvariantCulture));
                    else
                        json.Append(item?.ToString());
                }
                json.Append("]");
            }
            else if (kvp.Value is IFormattable formattable)
            {
                json.Append(formattable.ToString(null, CultureInfo.InvariantCulture));
            }
            else
            {
                json.Append(kvp.Value.ToString());
            }
        }

        json.Append("}");
        return json.ToString();
    }

    private T JsonFromString<T>(string json) where T : new()
    {
        var result = new T();
        if (typeof(T) == typeof(Response))
        {
            var response = new Response();

            if (json.Contains("\"ok\":true")) response.ok = true;
            else if (json.Contains("\"ok\":false")) response.ok = false;

            var errorStart = json.IndexOf("\"error\":\"", StringComparison.Ordinal);
            if (errorStart != -1)
            {
                errorStart += 9;
                var errorEnd = json.IndexOf("\"", errorStart, StringComparison.Ordinal);
                if (errorEnd != -1)
                    response.error = json.Substring(errorStart, errorEnd - errorStart);
            }

            return (T)(object)response;
        }
        return result;
    }
}
