
import json
import time
from collections import deque

import wikipediaapi

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

TARGET_ARTICLES = 200
MAX_WORDS = 1000
MAX_LINKS_PER_ARTICLE = 20
REQUEST_DELAY = 0.5

SEED_ARTICLES = [
    "World War II",
    "United Nations",
    "Democracy",
    "Cold War",
    "European Union",
]

OUTPUT_FILE = "wikipedia_articles.json"

# Identifie clairement le client auprès de Wikipedia.
wiki = wikipediaapi.Wikipedia(
    user_agent="HistoryPoliticsGraphProject/1.0 (educational project)",
    language="en",
)

# --------------------------------------------------
# 2. Fonctions utilitaires
# --------------------------------------------------

def extract_first_words(text, max_words=MAX_WORDS):
    """Conserve au maximum les max_words premiers mots."""
    words = text.split()
    return " ".join(words[:max_words])


def get_article(title):
    """Récupère une page Wikipédia et ses informations utiles."""
    try:
        page = wiki.page(title)

        if not page.exists():
            print(f"Page introuvable : {title}")
            return None

        content = extract_first_words(page.text)

        return {
            "title": page.title,
            "url": page.fullurl,
            "text": content,
            "word_count": len(content.split()),
            "links": list(page.links.keys()),
        }

    except Exception as error:
        print(f"Erreur pour {title}: {error}")
        return None


# --------------------------------------------------
# 3. Collecte BFS
# --------------------------------------------------

def collect_articles():
    queue = deque(SEED_ARTICLES)
    visited = set()
    articles = {}

    while queue and len(articles) < TARGET_ARTICLES:
        title = queue.popleft()

        if title in visited:
            continue

        visited.add(title)

        article = get_article(title)

        if article is None:
            continue

        articles[article["title"]] = article

        print(
            f"[{len(articles)}/{TARGET_ARTICLES}] "
            f"{article['title']} "
            f"({article['word_count']} mots)"
        )

        # Ajouter jusqu'à 20 liens candidats à la file BFS.
        for linked_title in article["links"][:MAX_LINKS_PER_ARTICLE]:
            if linked_title not in visited:
                queue.append(linked_title)

        # Respecter un délai entre les requêtes.
        time.sleep(REQUEST_DELAY)

    return articles


# --------------------------------------------------
# 4. Exécution et sauvegarde JSON
# --------------------------------------------------

if __name__ == "__main__":
    print("Début de la collecte Wikipédia...")
    print(f"Objectif : {TARGET_ARTICLES} articles")
    print()

    articles = collect_articles()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=2)

    print()
    print(f"Collecte terminée : {len(articles)} articles.")
    print(f"Fichier enregistré : {OUTPUT_FILE}")
