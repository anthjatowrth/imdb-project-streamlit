GENRE_FR: dict[str, str] = {

    # ── TMDB — genres officiels (28 genres) ──────────────────────────────────
    "action":                   "Action",
    "adventure":                "Aventure",
    "animation":                "Animation",
    "comedy":                   "Comédie",
    "crime":                    "Crime",
    "documentary":              "Documentaire",
    "drama":                    "Drame",
    "family":                   "Famille",
    "fantasy":                  "Fantaisie",
    "history":                  "Histoire",
    "horror":                   "Horreur",
    "music":                    "Musique",
    "mystery":                  "Mystère",
    "romance":                  "Romance",
    "science fiction":          "Science-fiction",
    "thriller":                 "Thriller",
    "tv movie":                 "Téléfilm",
    "war":                      "Guerre",
    "western":                  "Western",

    # ── TMDB — genres TV spécifiques ─────────────────────────────────────────
    "action & adventure":       "Action-Aventure",
    "kids":                     "Enfants",
    "news":                     "Actualités",
    "reality":                  "Télé-réalité",
    "sci-fi & fantasy":         "Science-fiction & Fantaisie",
    "soap":                     "Feuilleton",
    "talk":                     "Talk-show",
    "war & politics":           "Guerre & Politique",

    # ── IMDB — genres supplémentaires ────────────────────────────────────────
    "biography":                "Biographie",
    "sport":                    "Sport",
    "musical":                  "Comédie musicale",
    "short":                    "Court-métrage",
    "film-noir":                "Film noir",
    "talk-show":                "Talk-show",
    "reality-tv":               "Télé-réalité",
    "game-show":                "Jeu télévisé",
    "adult":                    "Adulte",
    "lifestyle":                "Mode de vie",
    "home and garden":          "Maison & Jardin",
    "food":                     "Gastronomie",
    "travel":                   "Voyage",
    "nature":                   "Nature",
    "mini-series":              "Mini-série",

    # ── Variantes orthographiques fréquentes ─────────────────────────────────
    "sci-fi":                   "Science-fiction",
    "sci fi":                   "Science-fiction",
    "science-fiction":          "Science-fiction",   # déjà traduit, pass-through
    "sciencefiction":           "Science-fiction",
    "action/adventure":         "Action-Aventure",
    "romcom":                   "Comédie romantique",
    "romantic comedy":          "Comédie romantique",
    "rom-com":                  "Comédie romantique",
    "docu":                     "Documentaire",
    "docuseries":               "Docu-série",
    "mockumentary":             "Faux documentaire",
    "superhero":                "Super-héros",
    "coming-of-age":            "Initiation",
    "coming of age":            "Initiation",
    "road movie":               "Road movie",
    "disaster":                 "Catastrophe",
    "epic":                     "Épopée",
    "martial arts":             "Arts martiaux",
    "sports":                   "Sport",
    "erotic":                   "Érotique",

    # ── Pass-through : genres parfois déjà en français dans le CSV ───────────
    "comédie":                  "Comédie",
    "drame":                    "Drame",
    "aventure":                 "Aventure",
    "documentaire":             "Documentaire",
    "horreur":                  "Horreur",
    "fantaisie":                "Fantaisie",
    "guerre":                   "Guerre",
    "histoire":                 "Histoire",
    "musique":                  "Musique",
    "mystère":                  "Mystère",
    "biographie":               "Biographie",
    "famille":                  "Famille",
    "crime":                    "Crime",
    "thriller":                 "Thriller",
    "western":                  "Western",
    "romance":                  "Romance",
    "animation":                "Animation",
    "sport":                    "Sport",
}


def translate_genre_to_fr(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    key = text.strip().lower()
    return GENRE_FR.get(key, text.strip().capitalize())