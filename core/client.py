"""
Ollama API Client with streaming, model management, and low-resource GPU optimization.
"""

import os
import shutil
import subprocess
import time
import json
import urllib.request
import urllib.error
from typing import Generator, List, Dict, Any, Optional

class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip("/")
        self.cancel_requested = False

    def is_server_running(self) -> bool:
        """Checks if the Ollama service is reachable."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def ensure_server_running(self) -> bool:
        """Ensures Ollama is running, automatically starting it if needed."""
        if self.is_server_running():
            return True
        
        # Locate ollama executable
        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            cand = os.path.join(local_appdata, "Programs", "Ollama", "ollama.exe")
            if os.path.exists(cand):
                ollama_bin = cand
        
        if not ollama_bin:
            return False

        try:
            flags = 0
            if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
                flags |= subprocess.CREATE_NEW_PROCESS_GROUP
            if hasattr(subprocess, 'DETACHED_PROCESS'):
                flags |= subprocess.DETACHED_PROCESS

            subprocess.Popen(
                [ollama_bin, "serve"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags
            )
            
            # Wait up to 6 seconds for Ollama to initialize
            for _ in range(12):
                time.sleep(0.5)
                if self.is_server_running():
                    return True
        except Exception as e:
            print(f"Failed to auto-start Ollama: {e}")
        
        return self.is_server_running()

    def list_models(self) -> List[str]:
        """Returns a list of installed model names."""
        if not self.is_server_running():
            self.ensure_server_running()
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                return models
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def pull_model_stream(self, model_name: str) -> Generator[Dict[str, Any], None, None]:
        """
        Pulls a model from Ollama library, yielding progress updates:
        {"status": "pulling manifest", "completed": 100, "total": 1000, "percent": 10.0}
        """
        url = f"{self.host}/api/pull"
        payload = json.dumps({"name": model_name, "stream": True}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                for line in resp:
                    if self.cancel_requested:
                        break
                    line = line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        completed = data.get("completed", 0)
                        total = data.get("total", 0)
                        pct = (completed / total * 100.0) if total > 0 else 0.0
                        yield {
                            "status": status,
                            "completed": completed,
                            "total": total,
                            "percent": round(pct, 1)
                        }
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield {"status": f"Error: {e}", "completed": 0, "total": 0, "percent": 0.0}

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        num_ctx: int = 2048,
        num_predict: int = 1024,
        gpu_layers: int = 99
    ) -> Generator[str, None, None]:
        """
        Sends chat messages to Ollama and streams tokens in real time.
        Offloads layers to NVIDIA RTX 5060 while keeping num_ctx tuned for ~1GB VRAM.
        """
        self.cancel_requested = False
        if not self.is_server_running():
            self.ensure_server_running()

        url = f"{self.host}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_ctx": num_ctx,
                "num_predict": num_predict,
                "num_gpu": gpu_layers
            }
        }
        
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                for line in resp:
                    if self.cancel_requested:
                        break
                    line = line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        msg = chunk.get("message", {})
                        content = msg.get("content", "")
                        if content:
                            yield content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield f"\n\n[Error generating response: {e}]"

    def stop_generation(self):
        """Signals to cancel ongoing generation."""
        self.cancel_requested = True
