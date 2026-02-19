# TikTok platform text requirements and optimization rules

# Caption length limits
CAPTION_MAX_LENGTH = 2200
CAPTION_OPTIMAL_MIN = 100
CAPTION_OPTIMAL_MAX = 300

# Sentence structure
SENTENCE_MAX_WORDS = 20
OPTIMAL_SENTENCES_PER_PARAGRAPH = 2

# Hashtags
HASHTAGS_MIN = 3
HASHTAGS_MAX = 5
HASHTAG_MAX_LENGTH = 30

# Readability
MAX_COMPLEX_WORD_RATIO = 0.15  # no more than 15% complex words
COMPLEX_WORD_MIN_SYLLABLES = 4

# Emoji density (per 100 characters)
EMOJI_DENSITY_MIN = 0.5
EMOJI_DENSITY_MAX = 3.0

# Hook (first line)
HOOK_MAX_LENGTH = 80

# Structure
LINE_BREAK_INTERVAL = 50  # characters between line breaks for readability

# Common TikTok hook patterns
HOOK_PATTERNS = [
    "POV:",
    "Wait for it...",
    "No one talks about this...",
    "Here's why...",
    "The truth about...",
    "Stop scrolling!",
    "You need to know this",
    "This changed everything",
    "Unpopular opinion:",
    "Fun fact:",
]

# Engagement CTA phrases
CTA_PHRASES = [
    "What do you think?",
    "Share your experience!",
    "Save this for later!",
    "Follow for more!",
    "Drop a comment!",
    "Tag someone who needs this!",
    "Do you agree?",
    "Like if you relate!",
]

# Topic-to-hashtag mapping for common categories
TOPIC_HASHTAGS = {
    "education": ["#LearnOnTikTok", "#EduTok", "#KnowledgeIsPower", "#DidYouKnow", "#Learning"],
    "motivation": ["#Motivation", "#Mindset", "#GrowthMindset", "#Inspiration", "#DailyMotivation"],
    "life": ["#LifeHacks", "#LifeLessons", "#RealTalk", "#Relatable", "#DailyLife"],
    "tech": ["#TechTok", "#Technology", "#TechTips", "#Digital", "#Innovation"],
    "business": ["#BusinessTips", "#Entrepreneur", "#SmallBusiness", "#Marketing", "#Success"],
    "health": ["#HealthTips", "#Wellness", "#HealthyLifestyle", "#Fitness", "#SelfCare"],
    "food": ["#FoodTok", "#Recipe", "#Cooking", "#FoodLover", "#Yummy"],
    "travel": ["#TravelTok", "#Travel", "#Wanderlust", "#TravelTips", "#Explore"],
    "default": ["#FYP", "#ForYou", "#Viral", "#Trending", "#TikTok"],
}

# Emoji mapping for emotional tone
TONE_EMOJIS = {
    "positive": ["🔥", "✨", "💯", "🙌", "❤️", "👏", "💪"],
    "negative": ["😤", "💔", "😢", "⚠️", "🚫"],
    "neutral": ["👀", "💡", "📌", "🎯", "📍"],
    "question": ["🤔", "❓", "👇", "💭"],
    "urgent": ["🚨", "⚡", "‼️", "🔴"],
}

# Words considered complex (Russian)
COMPLEX_WORD_INDICATORS_RU = [
    "вследствие", "нижеследующий", "вышеуказанный", "соответственно",
    "безусловно", "непосредственно", "обуславливает", "свидетельствует",
    "представляется", "осуществляется", "функционирование", "использование",
    "формирование", "обеспечение", "предполагается", "характеризуется",
]

# Simple replacements for common complex phrases (Russian)
SIMPLIFY_MAP_RU = {
    "в связи с тем что": "потому что",
    "в настоящее время": "сейчас",
    "в данный момент времени": "сейчас",
    "на сегодняшний день": "сегодня",
    "в целях": "чтобы",
    "в случае если": "если",
    "вследствие того что": "потому что",
    "по причине того что": "потому что",
    "несмотря на тот факт что": "хотя",
    "принимая во внимание": "учитывая",
    "осуществлять деятельность": "работать",
    "оказывать воздействие": "влиять",
    "является": "это",
    "представляет собой": "это",
    "характеризуется": "отличается",
    "обуславливается": "вызвано",
    "в том числе": "включая",
    "помимо этого": "также",
    "кроме того": "ещё",
    "тем не менее": "но",
    "однако же": "но",
    "таким образом": "так",
    "следовательно": "поэтому",
    "необходимо отметить": "важно",
    "следует подчеркнуть": "важно",
}

# Simple replacements for common complex phrases (English)
SIMPLIFY_MAP_EN = {
    "in order to": "to",
    "at this point in time": "now",
    "in the event that": "if",
    "due to the fact that": "because",
    "for the purpose of": "to",
    "in spite of the fact that": "although",
    "in the near future": "soon",
    "a large number of": "many",
    "the vast majority of": "most",
    "on the other hand": "but",
    "as a consequence of": "because of",
    "with regard to": "about",
    "in accordance with": "following",
    "take into consideration": "consider",
    "it is important to note that": "note that",
    "at the present time": "now",
    "in today's world": "today",
    "each and every": "every",
    "first and foremost": "first",
    "in my opinion": "I think",
}
