"""
Reachy Mini robot interface.

Wraps the official `reachy_mini` SDK (NOT `reachy_sdk`, which targets the
full-size Reachy 2). Set `reachy.enabled: false` in config.yaml to run the
whole assistant in mock mode with no hardware attached — every motion is
logged to the console instead.

Motion API used here (all documented in the Reachy Mini Python SDK):
    mini.goto_target(head=..., antennas=..., body_yaw=..., duration=..., method=...)
    mini.media.<audio/camera>
    mini.start_head_tracking() / stop_head_tracking()
"""
from __future__ import annotations

import numpy as np

# Interpolation methods accepted by goto_target
_MINJERK = "minjerk"


class Robot:
    """Reachy Mini wrapper with a mock mode for hardware-free development."""

    def __init__(self, config: dict):
        cfg = config["reachy"]
        self.config = cfg
        self.duration = float(cfg.get("motion_duration", 0.6))
        self.mock = not cfg.get("enabled", False)
        self._mini = None
        self._ctx = None

        if self.mock:
            print("[Reachy] MOCK mode - no hardware required.")
        else:
            self._connect()

    # ── connection ───────────────────────────────────────────────────

    def _connect(self):
        try:
            from reachy_mini import ReachyMini
        except ImportError:
            print("[Reachy] `reachy_mini` is not installed "
                  "(pip install reachy-mini). Falling back to MOCK mode.")
            self.mock = True
            return

        kwargs = {"media_backend": self.config.get("media_backend", "default")}
        mode = self.config.get("connection_mode", "auto")
        if mode and mode != "auto":
            # The SDK auto-detects USB vs network; only override when asked.
            kwargs["connection_mode"] = mode

        try:
            print(f"[Reachy] Connecting (media_backend={kwargs['media_backend']})...")
            # ReachyMini is a context manager; enter it manually so the handle
            # can live for the lifetime of the assistant.
            self._ctx = ReachyMini(**kwargs)
            self._mini = self._ctx.__enter__()
            print("[Reachy] Connected.")
        except Exception as e:
            print(f"[Reachy] Connection failed: {e}. Falling back to MOCK mode.")
            self.mock = True
            self._mini = None
            self._ctx = None

    @property
    def connected(self) -> bool:
        return not self.mock and self._mini is not None

    @property
    def media(self):
        """Underlying `mini.media` handle, or None in mock mode."""
        return self._mini.media if self.connected else None

    # ── motion primitives ────────────────────────────────────────────
    #
    # Head poses use `create_head_pose(z=..., mm=True)` — vertical translation
    # only, which is the parameter set confirmed against the SDK docs. Rotation
    # (pitch/roll) would read as a more natural nod; add it once the exact
    # keyword names are verified against the installed SDK version.

    def _head(self, z_mm: float = 0.0):
        from reachy_mini.utils import create_head_pose
        return create_head_pose(z=z_mm, mm=True)

    def _goto(self, z_mm=0.0, antennas_deg=(0.0, 0.0), yaw_deg=0.0, duration=None):
        if not self.connected:
            return
        self._mini.goto_target(
            head=self._head(z_mm),
            antennas=np.deg2rad(list(antennas_deg)),
            body_yaw=np.deg2rad(yaw_deg),
            duration=duration if duration is not None else self.duration,
            method=_MINJERK,
        )

    def idle(self):
        """Neutral resting pose."""
        if self.mock:
            print("[Reachy] *idle*")
            return
        self._goto()

    def listening(self):
        """Attentive pose — head slightly raised, antennas perked up."""
        if self.mock:
            print("[Reachy] *listening pose*")
            return
        self._goto(z_mm=6.0, antennas_deg=(35.0, 35.0))
        if self.config.get("head_tracking", False):
            try:
                self._mini.start_head_tracking()
            except Exception as e:
                print(f"[Reachy] head tracking unavailable: {e}")

    def speaking(self):
        """Engaged pose while talking."""
        if self.mock:
            print("[Reachy] *speaking pose*")
            return
        if self.config.get("head_tracking", False):
            try:
                self._mini.stop_head_tracking()
            except Exception:
                pass
        self._goto(z_mm=2.0, antennas_deg=(15.0, 15.0))

    def nod(self):
        """Short affirmative bob."""
        if self.mock:
            print("[Reachy] *nods*")
            return
        half = self.duration / 2
        self._goto(z_mm=-8.0, duration=half)
        self._goto(z_mm=0.0, duration=half)

    def shake(self):
        """Negative head shake (body yaw left-right-centre)."""
        if self.mock:
            print("[Reachy] *shakes head*")
            return
        third = self.duration / 3
        self._goto(yaw_deg=-18.0, duration=third)
        self._goto(yaw_deg=18.0, duration=third)
        self._goto(yaw_deg=0.0, duration=third)

    def happy(self):
        """Cheerful flourish — antennas wide, head up."""
        if self.mock:
            print("[Reachy] *looks happy*")
            return
        half = self.duration / 2
        self._goto(z_mm=10.0, antennas_deg=(60.0, 60.0), duration=half)
        self._goto(z_mm=4.0, antennas_deg=(25.0, 25.0), duration=half)

    def confused(self):
        """Tilted, uncertain pose."""
        if self.mock:
            print("[Reachy] *looks confused*")
            return
        self._goto(antennas_deg=(45.0, -10.0), yaw_deg=10.0)

    # ── lifecycle ────────────────────────────────────────────────────

    def disconnect(self):
        if not self.connected:
            return
        try:
            if self.config.get("head_tracking", False):
                try:
                    self._mini.stop_head_tracking()
                except Exception:
                    pass
            self.idle()
        finally:
            try:
                self._ctx.__exit__(None, None, None)
                print("[Reachy] Disconnected.")
            except Exception as e:
                print(f"[Reachy] Disconnect error: {e}")
            self._mini = None
            self._ctx = None
