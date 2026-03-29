"""Meridian proxy lifecycle management."""

import shutil
import subprocess
import time
import urllib.request


class MeridianManager:
    """Start and stop the meridian proxy (Claude Max local proxy)."""

    def __init__(self, startup_timeout: int = 10) -> None:
        self.startup_timeout = startup_timeout
        self._proc: subprocess.Popen | None = None

    def start(self) -> None:
        """Launch meridian and block until it accepts connections."""
        if not shutil.which("meridian"):
            print("Warning: 'meridian' not found on PATH — skipping proxy launch")
            return

        print("Starting meridian proxy…")
        self._proc = subprocess.Popen(
            ["meridian"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for _ in range(self.startup_timeout * 10):
            if self._proc.poll() is not None:
                raise RuntimeError(f"meridian exited immediately with code {self._proc.returncode}")
            time.sleep(0.1)
            try:
                urllib.request.urlopen("http://127.0.0.1:3456", timeout=1)
                break
            except Exception:
                continue
        else:
            self._proc.terminate()
            raise RuntimeError(
                f"meridian did not become ready within {self.startup_timeout}s"
            )

        print("meridian proxy is ready")

    def stop(self) -> None:
        """Terminate meridian if it's running."""
        if self._proc is None or self._proc.poll() is not None:
            return
        print("Stopping meridian proxy…")
        self._proc.terminate()
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait()

    def __enter__(self) -> "MeridianManager":
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()
