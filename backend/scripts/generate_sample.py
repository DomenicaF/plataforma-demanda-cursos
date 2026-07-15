"""Genera un dataset de ejemplo (estilo Kaggle) de cursos en línea.

Crea seed/courses_sample.csv con cursos repartidos por área de conocimiento y a
lo largo del tiempo (2023-2025), con una demanda creciente en unas áreas y
estable/decreciente en otras, para que las tendencias sean visibles en el
tablero. Ejecutar una sola vez:  python scripts/generate_sample.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUT = Path(__file__).resolve().parents[1] / "seed" / "courses_sample.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

PLATFORMS = ["Coursera", "edX", "Udemy", "MITx", "FutureLearn"]
LANGS = ["es", "en", "en", "en", "pt"]
LEVELS = ["principiante", "intermedio", "avanzado"]

# Cada categoría con una "tendencia": base inicial y crecimiento mensual (%)
CATEGORIES = {
    "Data Science":        (6, 0.06, ["python", "data", "analysis", "statistics", "pandas"]),
    "Machine Learning":    (5, 0.07, ["machine learning", "models", "neural", "deep", "ai"]),
    "Web Development":     (8, 0.02, ["web", "javascript", "react", "frontend", "html"]),
    "Cybersecurity":       (3, 0.05, ["security", "network", "hacking", "encryption", "risk"]),
    "Cloud Computing":     (3, 0.055, ["cloud", "aws", "azure", "devops", "containers"]),
    "Business & Marketing": (7, 0.005, ["business", "marketing", "management", "strategy", "sales"]),
    "Design & UX":         (4, 0.01, ["design", "ux", "ui", "figma", "prototyping"]),
    "Artificial Intelligence": (2, 0.09, ["ai", "generative", "llm", "chatgpt", "prompt"]),
}

INSTRUCTORS = ["A. Pérez", "J. Smith", "M. García", "L. Chen", "R. Kumar",
               "S. Johnson", "C. Rossi", "N. Müller"]

start = date(2023, 1, 1)
months = 36  # 2023-01 .. 2025-12

rows = []
ext = 1
for m in range(months):
    d = date(start.year + (start.month - 1 + m) // 12,
             (start.month - 1 + m) % 12 + 1, 1)
    for cat, (base, growth, kw) in CATEGORIES.items():
        # nº de cursos publicados ese mes según la tendencia de la categoría
        n = max(1, round(base * ((1 + growth) ** m) * random.uniform(0.8, 1.2)))
        for _ in range(n):
            platform_idx = random.randrange(len(PLATFORMS))
            price = random.choice([0, 0, 19.99, 29.99, 49.99, 89.99])
            rows.append({
                "external_id": f"C{ext:05d}",
                "title": f"{cat}: {random.choice(kw).title()} ({d:%Y-%m})",
                "description": (
                    f"Curso de {cat} enfocado en {', '.join(random.sample(kw, 3))}. "
                    f"Nivel {random.choice(LEVELS)}."
                ),
                "instructor": random.choice(INSTRUCTORS),
                "price": price,
                "duration_hours": random.choice([4, 8, 12, 20, 30, 40]),
                "language": LANGS[platform_idx],
                "difficulty_level": random.choice(LEVELS),
                "num_students": random.randint(50, 15000),
                "published_at": (d + timedelta(days=random.randint(0, 27))).isoformat(),
                "platform": PLATFORMS[platform_idx],
                "category": cat,
            })
            ext += 1

fieldnames = ["external_id", "title", "description", "instructor", "price",
              "duration_hours", "language", "difficulty_level", "num_students",
              "published_at", "platform", "category"]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generado {OUT} con {len(rows)} cursos.")
