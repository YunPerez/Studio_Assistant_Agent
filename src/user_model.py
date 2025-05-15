# src/user_model.py
import json
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class UserProfile:
    user_id: str
    name: str
    learning_style: str       # "visual", "auditivo", "kinestésico"
    level_of_knowledge: str    # por ejemplo "Principiante", "Intermedio", "Avanzado"

    @classmethod
    def load_profile(cls, path: str) -> "UserProfile":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def save_profile(self, path: str):
        # Asegúrate de que exista la carpeta
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

