# src/study_agent.py

import os
import re
import json
import textwrap
from abc import ABC
from typing import List, Dict, Any
from dataclasses import dataclass

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI

# ── CARGA DE CONFIGURACIÓN ──────────────────────────────────────────────────────

load_dotenv()  # Carga .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME     = os.getenv("MODEL_NAME", "gpt-4o-mini-2024-07-18")

if not OPENAI_API_KEY:
    raise RuntimeError("No se encontró OPENAI_API_KEY en el entorno")

client = OpenAI(api_key=OPENAI_API_KEY)


# ── USER PROFILE ─────────────────────────────────────────────────────────────────

@dataclass
class UserProfile:
    user_id:        str
    name:           str
    learning_style: str  # "visual", "auditivo", "kinestésico", etc.

    @classmethod
    def load(cls, path: str) -> "UserProfile":
        data = json.loads(open(path, "r", encoding="utf-8").read())
        return cls(**data)

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)


# ── PROGRESS TRACKER ─────────────────────────────────────────────────────────────

class ProgressTracker:
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}

    def update(self, user_id: str, key: str, value: Any):
        self._data.setdefault(user_id, {})
        self._data[user_id][key] = value

    def get(self, user_id: str) -> Dict[str, Any]:
        return self._data.get(user_id, {})


# ── DATA PROCESSING ──────────────────────────────────────────────────────────────

class DataProcessor:
    @staticmethod
    def load_text_from_pdf(path: str) -> str:
        reader = PdfReader(path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text)

    @staticmethod
    def load_text_from_txt(path: str) -> str:
        return open(path, "r", encoding="utf-8").read()

    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)


# ── GENERATOR BASE ───────────────────────────────────────────────────────────────

class OpenAIGenerator(ABC):
    def __init__(self, model: str = MODEL_NAME, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    def _call(self, prompt: str) -> str:
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return resp.choices[0].message.content.strip()


# ── QUESTIONS ───────────────────────────────────────────────────────────────────

class QuestionGenerator(OpenAIGenerator):
    def generate(self, text: str, n: int = 5) -> List[str]:
        prompt = (
            f"Eres un tutor que genera {n} preguntas de comprensión "
            f"basadas en el siguiente material:\n\n{text[:100000]}"
        )
        out = self._call(prompt)
        questions: List[str] = []
        for line in out.split("\n"):
            m = re.match(r"^\s*(\d+)\.\s*(.*)", line)
            if m:
                questions.append(m.group(2).strip())
            if len(questions) >= n:
                break
        return questions


# ── SUMMARIZER ───────────────────────────────────────────────────────────────────

class Summarizer(OpenAIGenerator):
    def summarize(self, text: str, style: str = "short") -> str:
        prompt = f"Resume el siguiente texto de forma {style}:\n\n{text[:100000]}"
        return self._call(prompt)


# ── STUDY AGENT ─────────────────────────────────────────────────────────────────

class StudyAgent:
    def __init__(self, user: UserProfile):
        self.user = user
        self.processor = DataProcessor()
        self.qgen = QuestionGenerator()
        self.summ = Summarizer()
        self.tracker = ProgressTracker()

    def ingest(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            raw = self.processor.load_text_from_pdf(path)
        elif ext == ".txt":
            raw = self.processor.load_text_from_txt(path)
        else:
            raise ValueError("Formato no soportado, usa .pdf o .txt")
        return self.processor.clean_text(raw)

    def ask_questions(self, text: str, n: int = 5) -> List[str]:
        qs = self.qgen.generate(text, n)
        self.tracker.update(self.user.user_id, "questions_generated", len(qs))
        return qs

    def get_summary(self, text: str, style: str = "short") -> str:
        summary = self.summ.summarize(text, style)
        self.tracker.update(self.user.user_id, f"summary_{style}", True)
        return summary

    def adapt_to_user(self, text: str) -> str:
        base = self.get_summary(text, style="short")
        prefix = {
            "visual":      "📊 [Diagrama sugerido]",
            "auditivo":    "🎧 [Narración sugerida]",
            "kinestésico": "🏃 [Actividad sugerida]"
        }.get(self.user.learning_style, "")
        return f"{prefix}\n\n{base}" if prefix else base

    def get_progress(self) -> Dict[str, Any]:
        return self.tracker.get(self.user.user_id)


# ── EJEMPLO DE USO ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1) Crear o cargar perfil
    profile_path = "profiles/user_1.json"
    if os.path.exists(profile_path):
        user = UserProfile.load(profile_path)
    else:
        user = UserProfile(user_id="user_1", name="Yuneri", learning_style="visual")
        user.save(profile_path)

    agent = StudyAgent(user)

    documento = "docs/Historiadelosmayas.pdf"
    texto = agent.ingest(documento)

    # ── Vista previa ──────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print("📄 VISTA PREVIA DEL TEXTO".center(60))
    print("="*60 + "\n")
    print(textwrap.fill(texto[:1000], width=80), "\n")

    # ── Preguntas ─────────────────────────────────────────────────────────────────
    qs = agent.ask_questions(texto, n=5)
    print("\n" + "="*60)
    print("❓ PREGUNTAS DE COMPRENSIÓN".center(60))
    print("="*60 + "\n")
    for i, q in enumerate(qs, 1):
        print(f"{i}. {q}")
    print()

    # ── Resumen breve ─────────────────────────────────────────────────────────────
    summary = agent.get_summary(texto, style="short")
    print("\n" + "="*60)
    print("📝 RESUMEN BREVE".center(60))
    print("="*60 + "\n")
    print(textwrap.fill(summary, width=80), "\n")

    # ── Adaptación ────────────────────────────────────────────────────────────────
    adapted = agent.adapt_to_user(texto)
    print("\n" + "="*60)
    print("🎨 ADAPTADO A TU ESTILO".center(60))
    print("="*60 + "\n")
    print(textwrap.fill(adapted, width=80), "\n")

    # ── Progreso ───────────────────────────────────────────────────────────────────
    progress = agent.get_progress()
    print("\n" + "="*60)
    print("📊 PROGRESO REGISTRADO".center(60))
    print("="*60 + "\n")
    print(json.dumps(progress, indent=2, ensure_ascii=False))
    print()
    # ── Guardar progreso ───────────────────────────────────────────────────────────
    user.save(profile_path)
    print("\n" + "="*60)
    print("💾 PROGRESO GUARDADO".center(60))
    print("="*60 + "\n")
    print("¡Listo! Tu progreso ha sido guardado.")
    print()
    # ── Fin del script ─────────────────────────────────────────────────────────────