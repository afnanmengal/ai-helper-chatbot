"""
Configuration module for the Lightweight AI Helper Chatbot.
Optimized for low resource usage (~1GB VRAM on NVIDIA RTX 5060).
"""

import os
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    # Ollama API Endpoint
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    
    # Lightweight models optimized for ~1GB VRAM budget
    default_model: str = "qwen2.5:0.5b"
    supported_light_models: list = field(default_factory=lambda: [
        "qwen2.5:0.5b",
        "llama3.2:1b",
        "qwen2.5:1.5b",
        "deepseek-r1:8b"
    ])
    
    # Resource constraints for RTX 5060 (~1GB VRAM usage)
    context_window: int = 2048        # 2k context keeps VRAM tight around 0.9-1.1GB
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 1024
    
    # GPU Settings
    gpu_layers: int = 99              # Offload all layers to RTX 5060
