"""
PC control tools: open apps, system commands, media, etc.
"""
import os
import subprocess
import webbrowser
import platform
import psutil
import shutil


def open_youtube(query: str = "") -> str:
    """Open YouTube in the default browser, optionally searching for a query."""
    if query:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    else:
        url = "https://www.youtube.com"
    webbrowser.open(url)
    return f"Opened YouTube{f' searching for: {query}' if query else ''}."


def shutdown_pc(delay_seconds: int = 30) -> str:
    """Shut down the PC after a delay (default 30 seconds)."""
    subprocess.Popen(["shutdown", "/s", "/t", str(delay_seconds)])
    return f"PC will shut down in {delay_seconds} seconds. Say 'cancel shutdown' to abort."


def cancel_shutdown() -> str:
    """Cancel a scheduled shutdown."""
    subprocess.Popen(["shutdown", "/a"])
    return "Shutdown cancelled."


def restart_pc(delay_seconds: int = 30) -> str:
    """Restart the PC after a delay."""
    subprocess.Popen(["shutdown", "/r", "/t", str(delay_seconds)])
    return f"PC will restart in {delay_seconds} seconds."


def get_disk_space(drive: str = "C") -> str:
    """Get free and total disk space for a drive."""
    try:
        usage = psutil.disk_usage(f"{drive}:\\")
        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        percent = usage.percent
        return (
            f"Drive {drive}: Total: {total_gb:.1f} GB, "
            f"Used: {used_gb:.1f} GB ({percent}%), "
            f"Free: {free_gb:.1f} GB."
        )
    except Exception as e:
        return f"Could not get disk info for drive {drive}: {e}"


def get_system_info() -> str:
    """Get CPU, RAM, and basic system info."""
    cpu_percent = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_total = ram.total / (1024 ** 3)
    ram_used = ram.used / (1024 ** 3)
    ram_percent = ram.percent
    return (
        f"CPU usage: {cpu_percent}%. "
        f"RAM: {ram_used:.1f} GB used of {ram_total:.1f} GB ({ram_percent}%)."
    )


def set_volume(level: int) -> str:
    """Set system volume (0-100)."""
    level = max(0, min(100, level))
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        # Convert 0-100 to 0.0-1.0
        volume.SetMasterVolumeLevelScalar(level / 100.0, None)
        return f"Volume set to {level}%."
    except ImportError:
        # Fallback: use nircmd or PowerShell
        subprocess.Popen(
            ["powershell", "-c",
             f"(New-Object -ComObject WScript.Shell).SendKeys([char]173)"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return f"Volume adjustment attempted (pycaw not installed for precise control)."


def open_application(app_name: str) -> str:
    """Open a common Windows application by name."""
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "paint": "mspaint.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "spotify": "spotify.exe",
        "discord": "discord.exe",
        "vs code": "code.exe",
        "vscode": "code.exe",
        "task manager": "taskmgr.exe",
    }
    key = app_name.lower().strip()
    exe = app_map.get(key, app_name)
    try:
        subprocess.Popen([exe], shell=True)
        return f"Opened {app_name}."
    except Exception as e:
        return f"Could not open {app_name}: {e}"


def take_screenshot() -> str:
    """Take a screenshot and save to Desktop."""
    try:
        import pyautogui
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = os.path.join(desktop, "screenshot.png")
        pyautogui.screenshot(path)
        return f"Screenshot saved to {path}."
    except Exception as e:
        return f"Screenshot failed: {e}"


def list_running_processes(top_n: int = 10) -> str:
    """List top N processes by CPU usage."""
    procs = []
    for proc in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
    top = procs[:top_n]
    lines = [f"{p['name']}: CPU {p['cpu_percent']:.1f}%, RAM {p['memory_percent']:.1f}%" for p in top]
    return "Top processes:\n" + "\n".join(lines)
