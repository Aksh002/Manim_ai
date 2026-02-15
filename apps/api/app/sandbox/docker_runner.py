from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.core.config import get_settings
from app.services.render_types import RenderResult, RenderTimeoutError


class DockerRunner:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self, job_id: str, code: str, quality: str) -> RenderResult:
        with tempfile.TemporaryDirectory(prefix=f"sandbox_{job_id}_") as tmp_dir:
            workspace_dir = Path(tmp_dir) / "workspace"
            output_dir = Path(tmp_dir) / "output"
            workspace_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            script_path = workspace_dir / "scene.py"
            script_path.write_text(code, encoding="utf-8")

            cmd = [
                "docker",
                "run",
                "--rm",
                "--cpus",
                self.settings.sandbox_cpu,
                "--memory",
                self.settings.sandbox_memory,
                "--pids-limit",
                str(self.settings.sandbox_pids_limit),
                "--tmpfs",
                "/tmp:size=256m",
                "-v",
                f"{workspace_dir}:/workspace:rw",
                "-v",
                f"{output_dir}:/output:rw",
            ]

            if self.settings.sandbox_network_disabled:
                cmd.extend(["--network", "none"])
            if self.settings.sandbox_read_only:
                cmd.append("--read-only")
            if self.settings.sandbox_no_new_privileges:
                cmd.extend(["--security-opt", "no-new-privileges"])
            if Path(self.settings.sandbox_seccomp_profile).exists():
                cmd.extend(["--security-opt", f"seccomp={self.settings.sandbox_seccomp_profile}"])

            cmd.extend(
                [
                    self.settings.renderer_image,
                    "/entrypoint.sh",
                    "scene.py",
                    "GeneratedScene",
                    quality,
                ]
            )

            try:
                subprocess.run(
                    cmd,
                    check=True,
                    timeout=self.settings.render_timeout_sec,
                    capture_output=True,
                    text=True,
                )
            except subprocess.TimeoutExpired as exc:
                raise RenderTimeoutError("Sandbox render timed out") from exc
            except subprocess.CalledProcessError as exc:
                stderr = (exc.stderr or "").strip()
                stdout = (exc.stdout or "").strip()
                raise RuntimeError(stderr or stdout or "Sandbox render failed") from exc

            output_file = output_dir / "output.mp4"
            if not output_file.exists():
                raise RuntimeError("Sandbox render finished but output.mp4 is missing")

            fd, stable_output = tempfile.mkstemp(prefix=f"{job_id}_", suffix=".mp4")
            os.close(fd)
            shutil.copyfile(output_file, stable_output)
            return RenderResult(video_file=stable_output)
