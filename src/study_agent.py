# src/study_agent.py

import os
import re
import json
from abc import ABC
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader
from openai import OpenAI
from dotenv import load_dotenv

# ── CARGA DE CONFIG ─────────────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME     = os.getenv("MODEL_NAME", "gpt-4o-mini-2024-07-18")

if not OPENAI_API_KEY:
    raise RuntimeError("No se encontró OPENAI_API_KEY en el entorno")

client = OpenAI(api_key=OPENAI_API_KEY)

# ── PROGRESS TRACKER ────────────────────────────────────────────────────────────
class ProgressTracker:
    def __init__(self, filename: str = "progress.json"):
        self.filename = filename
        # cargar datos si existe
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as f:
                self._data: Dict[str, Any] = json.load(f)
        else:
            self._data = {
                "documents_ingested": 0,
                "questions_generated": 0,
                "summaries_generated": 0,
                "adaptations": 0,
                "rag_queries": 0,
                "sections_indexed": 0
            }

    def update(self, key: str, amount: int = 1):
        # suma incremental
        self._data[key] = self._data.get(key, 0) + amount
        # guardar inmediatamente
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self) -> Dict[str, Any]:
        return self._data


# ── DATA PROCESSING ─────────────────────────────────────────────────────────────
class DataProcessor:
    @staticmethod
    def load_text_from_pdf(path: str) -> str:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    @staticmethod
    def load_text_from_txt(path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)


# ── BASE LLM CALL ───────────────────────────────────────────────────────────────
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


# ── PREGUNTAS ──────────────────────────────────────────────────────────────────
class QuestionGenerator(OpenAIGenerator):
    def generate(self, text: str, n: int = 5) -> List[str]:
        prompt = (
            f"Eres un tutor que genera {n} preguntas de comprensión lectora basadas en este texto:\n\n"
            f"{text[:100000]}\n\n"
            "Para cada pregunta:\n"
            " - Proporciona 3 opciones de respuesta (A, B, C).\n"
            " - Señala claramente cuál es la correcta.\n"
            "Numera cada pregunta 1., 2., etc."
        )
        out = self._call(prompt)
        blocks: List[str] = []
        current: Optional[str] = None
        for line in out.split("\n"):
            line = line.strip()
            if not line:
                continue
            if re.match(r'^\d+\.', line):
                if current:
                    blocks.append(current.strip())
                current = re.sub(r'^\d+\.\s*', '', line)
            else:
                if current is not None:
                    current += "\n" + line
        if current:
            blocks.append(current.strip())
        return blocks[:n]


# ── RESUMEN ─────────────────────────────────────────────────────────────────────
class Summarizer(OpenAIGenerator):
    def summarize(self, text: str, style: str = "short") -> str:
        prompt = f"Resume el siguiente texto de forma {style}:\n\n{text[:100000]}"
        return self._call(prompt)


# ── ADAPTACIÓN AL USUARIO ───────────────────────────────────────────────────────
class AdaptationGenerator(OpenAIGenerator):
    def generate(self, text: str, style: str, level: str) -> str:
        prompt = f"""
Eres un tutor que adapta su enseñanza al estilo de aprendizaje "{style}" y nivel "{level}".
A partir de este texto:

{text[:10000]}

Responde **solo** con tres secciones numeradas:
1) Resumen breve del texto (1–2 frases).
2) Sugerencia de estudio específicamente PARA el estilo "{style}".
3) Actividad práctica PARA el estilo "{style}".
4) Realiza un diagrama o esquema visual que resuma el texto y la actividad práctica únicamente PARA el estilo "Visual".

No menciones otros estilos.
"""
        return self._call(prompt)


# ── VECTOR SEARCH (RAG) ────────────────────────────────────────────────────────
class VectorSearchEngine:
    def __init__(self, collection_name: str = "notas_estudio"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.Client(Settings())
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[str], ids: List[str]):
        embeddings = self.model.encode(documents).tolist()
        self.collection.add(documents=documents, ids=ids, embeddings=embeddings)

    def search(self, query: str, n_results: int = 3) -> List[str]:
        emb = self.model.encode([query]).tolist()
        results = self.collection.query(query_embeddings=emb, n_results=n_results)
        return results["documents"][0]


# ── STUDY AGENT ────────────────────────────────────────────────────────────────
class StudyAgent:
    def __init__(self):
        self.processor     = DataProcessor()
        self.qgen          = QuestionGenerator()
        self.summ          = Summarizer()
        self.adapt_gen     = AdaptationGenerator()
        self.search_engine = VectorSearchEngine()
        self.tracker       = ProgressTracker("progress.json")

    def ingest(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            raw = self.processor.load_text_from_pdf(path)
        elif ext == ".txt":
            raw = self.processor.load_text_from_txt(path)
        else:
            raise ValueError("Formato no soportado, usa .pdf o .txt")
        clean = self.processor.clean_text(raw)
        self.tracker.update("documents_ingested", 1)
        return clean

    def index_text_sections(self, text: str, chunk_size: int = 500, overlap: int = 50):
        sections = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i : i + chunk_size].strip()
            if len(chunk) > 100:
                sections.append(chunk)
        if sections:
            ids = [f"sec_{i}" for i in range(len(sections))]
            self.search_engine.add_documents(sections, ids)
            self.tracker.update("sections_indexed", len(sections))

    def retrieve_relevant_sections(self, query: str, n: int = 3) -> List[str]:
        docs = self.search_engine.search(query, n)
        joined = "\n\n".join(docs)
        answer = self.summ.summarize(
            f"Responde a esta consulta usando solo el texto:\n\n{joined}\n\nConsulta: {query}",
            style="short"
        )
        self.tracker.update("rag_queries", 1)
        return [answer]

    def ask_questions(
        self,
        text: str,
        n: int = 5,
        style: str = "Visual",
        level: str = "Intermedio"
    ) -> List[str]:
        self.tracker.update("questions_generated", n)
        return self.qgen.generate(text, n)

    def get_summary(self, text: str, style: str = "short") -> str:
        s = self.summ.summarize(text, style)
        self.tracker.update("summaries_generated", 1)
        return s

    def adapt_to_user(self, text: str, style: str, level: str) -> str:
        out = self.adapt_gen.generate(text, style, level)
        self.tracker.update("adaptations", 1)
        return out

    def get_progress(self) -> Dict[str, Any]:
        return self.tracker.get()