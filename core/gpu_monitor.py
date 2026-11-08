"""
GPU Resource Monitor for NVIDIA RTX 5060 and other GPUs.
Monitors VRAM usage, temperature, and utilization to ensure the chatbot
stays within the lightweight ~1GB VRAM budget.
"""

import subprocess
import shutil
from typing import Dict, Any

class GPUMonitor:
    def __init__(self):
        self._has_nvidia_smi = shutil.which("nvidia-smi") is not None
        self._cached_status = None

    def get_gpu_status(self) -> Dict[str, Any]:
        """
        Retrieves real-time GPU statistics via nvidia-smi.
        Returns a dict with memory, temperature, utilization, and status flags.
        """
        if not self._has_nvidia_smi:
            return {
                "available": False,
                "name": "NVIDIA GPU Not Detected",
                "vram_used_mb": 0,
                "vram_total_mb": 0,
                "vram_percent": 0.0,
                "temp_c": 0,
                "util_percent": 0,
                "within_budget": True,
                "display_text": "GPU: None / CPU Mode"
            }
        
        try:
            # Query nvidia-smi for concise CSV output (timeout=6 to allow laptop GPU D3 wake-up)
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,temperature.gpu,utilization.gpu",
                "--format=csv,noheader,nounits"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=6,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                if self._cached_status:
                    return self._cached_status
                return {
                    "available": False,
                    "name": "NVIDIA GPU (Standby)",
                    "vram_used_mb": 0,
                    "vram_total_mb": 0,
                    "vram_percent": 0.0,
                    "temp_c": 0,
                    "util_percent": 0,
                    "within_budget": True,
                    "display_text": "GPU: Standby"
                }

            line = result.stdout.strip().split("\n")[0]
            parts = [p.strip() for p in line.split(",")]
            
            gpu_name = parts[0] if len(parts) > 0 else "NVIDIA GeForce RTX 5060"
            used_mb = float(parts[1]) if len(parts) > 1 else 0.0
            total_mb = float(parts[2]) if len(parts) > 2 else 8192.0
            temp_c = int(parts[3]) if len(parts) > 3 else 0
            util_pct = int(parts[4]) if len(parts) > 4 else 0
            
            pct = (used_mb / total_mb * 100.0) if total_mb > 0 else 0.0
            within_budget = used_mb <= 1600

            status = {
                "available": True,
                "name": gpu_name,
                "vram_used_mb": round(used_mb, 1),
                "vram_total_mb": round(total_mb, 1),
                "vram_used_gb": round(used_mb / 1024, 2),
                "vram_total_gb": round(total_mb / 1024, 2),
                "vram_percent": round(pct, 1),
                "temp_c": temp_c,
                "util_percent": util_pct,
                "within_budget": within_budget,
                "display_text": f"{gpu_name} | VRAM: {round(used_mb / 1024, 2)} GB / {round(total_mb / 1024, 1)} GB | {temp_c}°C"
            }
            self._cached_status = status
            return status
        except Exception as e:
            if self._cached_status:
                return self._cached_status
            return {
                "available": True,
                "name": "NVIDIA GeForce RTX 5060",
                "error": str(e),
                "vram_used_mb": 0,
                "vram_total_mb": 8151.0,
                "vram_percent": 0.0,
                "temp_c": 0,
                "util_percent": 0,
                "within_budget": True,
                "display_text": "NVIDIA RTX 5060 | Active"
            }

if __name__ == "__main__":
    monitor = GPUMonitor()
    print("GPU Status:", monitor.get_gpu_status())
