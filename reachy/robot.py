"""
Reachy Mini interface — real robot or mock mode.
Set mock_mode: true in config.yaml to run without hardware.
"""
import yaml


class ReachyMini:
    def __init__(self, config: dict):
        self.config = config
        self.mock = config["reachy"]["mock_mode"]

        if self.mock:
            print("[Reachy] Running in MOCK mode (no hardware required).")
            self._robot = None
        else:
            self._connect()

    def _connect(self):
        try:
            from reachy_sdk import ReachySDK
            ip = self.config["reachy"]["ip"]
            print(f"[Reachy] Connecting to robot at {ip}...")
            self._robot = ReachySDK(host=ip)
            print("[Reachy] Connected.")
        except ImportError:
            print("[Reachy] reachy-sdk not installed. Falling back to mock mode.")
            self.mock = True
            self._robot = None
        except Exception as e:
            print(f"[Reachy] Connection failed: {e}. Falling back to mock mode.")
            self.mock = True
            self._robot = None

    def nod(self):
        """Nod head to indicate listening or agreement."""
        if self.mock:
            print("[Reachy] *nods head*")
            return
        # Real robot head movement (placeholder for actual SDK calls)
        pass

    def idle(self):
        """Return to neutral/idle pose."""
        if self.mock:
            print("[Reachy] *returns to idle*")
            return
        pass

    def listening_pose(self):
        """Visual indicator that Reachy is listening."""
        if self.mock:
            print("[Reachy] *listening pose*")
            return
        pass

    def speaking_pose(self):
        """Visual indicator that Reachy is speaking."""
        if self.mock:
            print("[Reachy] *speaking pose*")
            return
        pass

    def disconnect(self):
        if not self.mock and self._robot:
            self._robot.disconnect()
            print("[Reachy] Disconnected.")
