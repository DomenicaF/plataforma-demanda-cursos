"""Minería de texto: modelado de tópicos sobre las descripciones de los cursos.

Aplica LDA (Latent Dirichlet Allocation) sobre el texto de los cursos para
descubrir los temas latentes de la oferta formativa, en línea con las técnicas
revisadas en el estado del arte (Yin y Yuan, 2022; Jiang et al., 2025).
"""
import re

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Lista breve de palabras vacías (ES/EN) suficiente para la demostración
STOPWORDS = {
    "de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "para",
    "con", "por", "que", "del", "al", "se", "su", "lo", "como", "más",
    "curso", "cursos", "aprende", "aprender", "online",
    "the", "of", "and", "to", "in", "for", "with", "on", "a", "an",
    "this", "course", "learn", "you", "your", "will",
}


def _preprocess(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-záéíóúñ\s]", " ", text)
    tokens = [t for t in text.split() if len(t) > 2 and t not in STOPWORDS]
    return " ".join(tokens)


def discover_topics(documents: list[str], num_topics: int = 5,
                    words_per_topic: int = 8) -> list[dict]:
    """Devuelve una lista de tópicos con sus palabras más representativas."""
    docs = [_preprocess(d) for d in documents if d and d.strip()]
    docs = [d for d in docs if d]
    if len(docs) < num_topics:
        return []

    vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=800)
    try:
        dtm = vectorizer.fit_transform(docs)
    except ValueError:
        return []
    if dtm.shape[1] == 0:
        return []

    # learning_method="online" es mucho más rápido en corpus grandes
    lda = LatentDirichletAllocation(
        n_components=num_topics, random_state=42,
        learning_method="online", max_iter=15,
    )
    lda.fit(dtm)

    vocab = vectorizer.get_feature_names_out()
    topics = []
    for idx, component in enumerate(lda.components_):
        top = component.argsort()[: -words_per_topic - 1 : -1]
        keywords = [vocab[i] for i in top]
        topics.append({"topic": idx + 1, "keywords": keywords})
    return topics
