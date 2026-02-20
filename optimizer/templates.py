"""Template definitions for UGC marketing text generation.

Two product templates:
- Snell: Telegram clicker game
- Tube: Telegram bot for watching/rating short videos

Each template defines:
- Structural sections (hook, actions, reward, safety, CTA)
- Pools of Dutch text variations per section
- Banned words/phrases for moderation compliance
- Timing guidelines (for video scripts)
"""

# ─────────────────────────────────────────────
# GLOBAL MODERATION RULES (apply to ALL templates)
# ─────────────────────────────────────────────

BANNED_WORDS = [
    # Currency & finance (any language)
    "$", "€", "₽", "dollar", "euro", "roebel",
    "rijk worden", "rijkdom", "inkomen", "salaris",
    "passief inkomen", "snel geld", "makkelijk geld", "cash",
    "verdienen", "verdiensten", "winst",
    # Russian equivalents that might leak
    "заработок", "доход", "богатство", "пассивный доход",
    "быстрые деньги", "кэш",
    # Scam / MLM signals
    "piramide", "mlm", "investering", "storting",
    "gegarandeerd", "100%", "geen risico",
    # Misleading exact amounts
    "per dag verdienen", "per uur verdienen",
    "per week verdienen", "per maand verdienen",
]

BANNED_PATTERNS = [
    r"\d+\s*[\$€₽]",       # "50$", "100 €"
    r"[\$€₽]\s*\d+",       # "$50", "€100"
    r"\d+\s*dollar",        # "50 dollar"
    r"\d+\s*euro",          # "100 euro"
    r"\d+\s*per\s+dag",     # "100 per dag"
    r"\d+\s*per\s+uur",     # "50 per uur"
]

# ─────────────────────────────────────────────
# TEMPLATE: SNELL (Telegram Clicker Game)
# ─────────────────────────────────────────────

SNELL = {
    "id": "snell",
    "name": "Snell",
    "type": "clicker",
    "description": "Telegram clicker game",

    # Section 1: Hook (0-3 sec)
    "hooks": [
        "Op zoek naar een nieuwe verslavende game in Telegram?",
        "Ken je die nieuwe klikker-game waar iedereen het over heeft?",
        "Verveel je je? Deze Telegram-game is echt next level 👀",
        "Iedereen speelt dit in Telegram en ik snap waarom",
        "Wist je dat er een mega verslavend spel in Telegram zit?",
        "Deze game in Telegram is echt niet normaal verslavend",
        "Ik laat je zien hoe deze nieuwe Telegram-game werkt",
        "Stop met scrollen, dit moet je zien! Nieuwe Telegram-game",
        "Dit is de game waar al mijn vrienden aan verslaafd zijn",
        "Zoek je iets leuks voor tussendoor? Check deze Telegram-game",
        "Heb je al gehoord van die nieuwe klikker in Telegram?",
        "Even serieus... deze Telegram-game is echt tof",
        "POV: je ontdekt de meest verslavende Telegram-game",
        "Wie houdt er ook van simpele maar verslavende games?",
        "Nieuwe game alert! En je hebt alleen Telegram nodig",
    ],

    # Section 2: Actions / Gameplay (3-8 sec)
    "actions": [
        "Je start de bot in Telegram, klikt op het scherm, verzamelt energie en upgradet je personage. Simpel!",
        "Het werkt zo: open de bot, tik op het scherm om munten te verzamelen en level je karakter omhoog",
        "Je opent gewoon de bot in Telegram en begint te klikken. Hoe meer je klikt, hoe meer munten je spaart",
        "Start de bot, tik op je scherm en kijk hoe je muntjes omhoog vliegen. Upgrade je karakter om sneller te groeien",
        "De gameplay is simpel: klikken, energie opladen, personage upgraden en missies voltooien",
        "Open Telegram, start de bot en begin te tikken. Je personage groeit met elke klik",
        "Klik, verzamel, upgrade. Dat is het. En het is echt mega verslavend",
        "Je start de bot, klikt om punten te verzamelen en unlockt nieuwe levels en upgrades",
    ],

    # Section 3: Rewards (8-12 sec) — CAREFUL language!
    "rewards": [
        "Voor elke klik en missie krijg je in-game munten. Spaar ze om je account te upgraden en mee te doen aan toekomstige beloningen van het project",
        "Je verzamelt in-game punten door te klikken en taken te voltooien zoals kanalen volgen. Hoe meer punten, hoe beter je positie",
        "Met elke klik krijg je game-munten. Deze kun je gebruiken om je karakter sterker te maken en deel te nemen aan speciale events",
        "Het spel beloont je met in-game tokens voor je activiteit. Spaar ze en maak kans op toekomstige bonussen",
        "Je spaart in-game munten door actief te spelen. Hoe actiever je bent, hoe meer je ontgrendelt",
        "Elke klik levert game-punten op. Gebruik ze voor upgrades en wacht op toekomstige project-events",
        "Je krijgt in-game beloningen voor klikken en dagelijkse taken. Spaar en bouw je account op",
    ],

    # Section 4: Safety / No risks (12-15 sec)
    "safety": [
        "Het spel is helemaal gratis. Geen aankopen of betalingen nodig om te beginnen. Gewoon spelen in je vrije tijd",
        "Volledig gratis te spelen. Geen startkosten, geen verborgen kosten. Je hebt alleen Telegram nodig",
        "Je hoeft niks te betalen. Het is een gratis game in Telegram. Gewoon downloaden en spelen",
        "Geen kosten, geen aankopen vereist. Het is gewoon een gratis Telegram-game",
        "Het kost je niks om te beginnen. Gratis spel, geen verplichtingen. Speel wanneer je wilt",
        "Helemaal gratis. Geen creditcard, geen betaling. Open Telegram en begin te spelen",
    ],

    # Section 5: CTA (15-20 sec)
    "ctas": [
        "Klik op 'Meer info' om de bot in Telegram te openen en nu te beginnen!",
        "Tik op de link om de game in Telegram te starten. Laten we gaan!",
        "Druk op 'Meer info', open de bot en start met spelen!",
        "Klik hieronder om de bot te openen en je eerste munten te pakken!",
        "Tap op de link en begin nu met spelen in Telegram!",
        "Link in bio! Open de bot en begin te klikken!",
        "Druk op 'Meer info' en start de game direct in Telegram!",
    ],
}

# ─────────────────────────────────────────────
# TEMPLATE: TUBE (Video Watching/Rating Bot)
# ─────────────────────────────────────────────

TUBE = {
    "id": "tube",
    "name": "Tube",
    "type": "video_tasks",
    "description": "Telegram bot for watching and rating short videos",

    # Section 1: Hook (0-3 sec)
    "hooks": [
        "Op zoek naar een bijbaantje op je telefoon zonder kosten?",
        "Wij zoeken mensen om korte video's te beoordelen",
        "Wil je iets nuttigs doen met je vrije tijd op je telefoon?",
        "Ken je die bot waar je video's kijkt en beloningen krijgt?",
        "Heb je een telefoon en Telegram? Dan is dit iets voor jou",
        "Zoek je een makkelijke manier om micro-taken te doen?",
        "Even serieus... deze Telegram-bot is echt handig als bijverdienste",
        "Verveel je je? Bekijk video's en krijg er iets voor terug",
        "Wist je dat je beloond kunt worden voor het kijken van korte video's?",
        "POV: je ontdekt een simpele manier om micro-taken te doen op je telefoon",
        "Ik laat je zien hoe je beloningen krijgt voor het bekijken van video's",
        "Mensen vragen mij wat ik doe in mijn vrije tijd. Dit!",
        "Nieuwe ontdekking: een Telegram-bot voor micro-taken",
        "Dit is hoe ik mijn wachttijd nuttig besteed",
        "Simpele micro-taken op je telefoon? Ja, dat bestaat",
    ],

    # Section 2: Actions (3-8 sec)
    "actions": [
        "Het is simpel: je start de Telegram-bot, hij stuurt je korte video's. Jij bekijkt ze en geeft een korte beoordeling",
        "Open de bot in Telegram, bekijk de video's die hij stuurt en druk op de knop als je klaar bent. Dat is alles",
        "De bot stuurt je korte clips. Je bekijkt ze, geeft feedback en gaat door naar de volgende. Makkelijker kan niet",
        "Start de bot, ontvang video's, bekijk ze tot het einde en laat je beoordeling achter. Simpel als dat",
        "Je opent de bot, hij toont je een kort filmpje. Je kijkt het, drukt op een knop en krijgt de volgende",
        "Het werkt als een soort video-tester. De bot stuurt content, jij bekijkt en beoordeelt. Klaar",
        "Open Telegram, start de bot en begin met het bekijken en beoordelen van korte video's",
    ],

    # Section 3: Rewards (8-12 sec) — CAREFUL language!
    "rewards": [
        "Voor elke bekeken video krijg je een kleine beloning op je balans. Het vervangt geen baan, maar het is leuk als extra in je vrije tijd",
        "De bot geeft je een kleine vergoeding per bekeken video. Zie het als een micro-bijbaantje voor tussendoor",
        "Je ontvangt een kleine beloning voor elke voltooide taak. Ideaal als je toch al op je telefoon zit",
        "Per bekeken video ontvang je punten op je balans. Het vervangt geen baan, maar leuk als extra",
        "De bot beloont je activiteit met kleine bonussen. Perfect voor als je even niks te doen hebt",
        "Elke voltooide micro-taak levert een kleine beloning op. Leuk voor tussendoor, geen grote verwachtingen",
        "Je krijgt een klein bedrag per video. Het is bescheiden, maar het telt op als je het regelmatig doet",
    ],

    # Section 4: Safety (12-15 sec)
    "safety": [
        "Je hebt alleen een telefoon en Telegram nodig. Geen startkosten of verplichte betalingen. Het is volledig gratis",
        "Geen kosten nodig. Geen cursuskosten. Gewoon je telefoon en Telegram. Helemaal gratis",
        "Het kost je niks om te beginnen. Geen verborgen kosten, geen verplichtingen. Gewoon je telefoon",
        "Volledig gratis. Geen kosten, geen abonnement. Je hebt alleen Telegram nodig op je telefoon",
        "Niks te verliezen, geen kosten. Alles wat je nodig hebt is een telefoon met Telegram",
        "Gratis te gebruiken. Geen creditcard nodig, geen startkosten. Gewoon Telegram openen en beginnen",
    ],

    # Section 5: CTA (15-20 sec)
    "ctas": [
        "Klik op 'Meer info', lees de voorwaarden op onze site en doe mee!",
        "Tik op de link, bekijk de details en start met je eerste video!",
        "Druk op 'Meer info' om naar onze site te gaan en je aan te melden!",
        "Klik hieronder voor alle info en begin vandaag nog!",
        "Tap op de link, lees de voorwaarden en join het team!",
        "Link in bio! Bekijk de details en start direct!",
        "Druk op 'Meer info', lees alles op de site en ga aan de slag!",
    ],
}

# Registry of all templates
TEMPLATES = {
    "snell": SNELL,
    "tube": TUBE,
}
