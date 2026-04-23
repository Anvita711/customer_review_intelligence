"""
Application configuration and constants.
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Customer Review Intelligence Platform"
    version: str = "1.0.0"
    debug: bool = False

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    sample_data_dir: Path = base_dir / "sample_data"

    # Preprocessing
    min_review_length: int = 5
    duplicate_similarity_threshold: float = 0.85
    spam_similarity_threshold: float = 0.90
    spam_min_cluster_size: int = 3

    # Feature extraction
    feature_keywords: dict[str, list[str]] = {
        "battery": ["battery", "charge", "charging", "power", "mah", "battery life", "drain"],
        "display": ["display", "screen", "lcd", "amoled", "oled", "brightness", "resolution"],
        "camera": ["camera", "photo", "picture", "lens", "megapixel", "selfie", "zoom"],
        "performance": ["performance", "speed", "fast", "slow", "lag", "hang", "smooth", "processor", "ram"],
        "delivery": ["delivery", "shipping", "courier", "arrived", "dispatch", "delayed", "on time"],
        "packaging": ["packaging", "package", "box", "packed", "bubble wrap", "damaged", "broken"],
        "price": ["price", "cost", "expensive", "cheap", "value", "worth", "money", "affordable"],
        "build_quality": ["build", "quality", "material", "plastic", "metal", "sturdy", "flimsy", "premium"],
        "sound": ["sound", "audio", "speaker", "volume", "bass", "music", "earphone"],
        "software": ["software", "update", "os", "android", "ios", "app", "bloatware", "ui", "interface"],
        "customer_service": ["customer service", "support", "helpline", "warranty", "replacement", "return"],
    }

    # Sentiment
    positive_words: list[str] = [
        "good", "great", "excellent", "amazing", "awesome", "love", "best", "perfect",
        "wonderful", "fantastic", "superb", "happy", "pleased", "satisfied", "recommend",
        "impressive", "brilliant", "outstanding", "nice", "solid",
    ]
    negative_words: list[str] = [
        "bad", "worst", "terrible", "awful", "horrible", "hate", "poor", "waste",
        "disappointed", "useless", "broken", "defective", "pathetic", "rubbish",
        "trash", "regret", "annoying", "frustrating", "slow", "cheap",
    ]
    sarcasm_indicators: list[str] = [
        "yeah right", "sure thing", "oh great", "just wonderful", "fantastic luck",
        "wow amazing", "what a surprise", "clearly", "obviously", "totally",
    ]
    negation_words: list[str] = [
        "not", "no", "never", "neither", "nobody", "nothing", "nowhere",
        "nor", "cannot", "can't", "won't", "don't", "doesn't", "didn't",
        "wasn't", "weren't", "isn't", "aren't", "hardly", "barely",
    ]

    # Trend detection
    default_window_size: int = 50
    anomaly_z_threshold: float = 2.0
    systemic_issue_threshold: float = 0.15  # 15% of reviews mention the feature

    # Hindi-English common words mapping (for basic mixed-language support)
    hindi_keywords: dict[str, str] = {
        "accha": "good", "acha": "good", "bahut": "very", "kharab": "bad",
        "bekar": "useless", "bakwas": "nonsense", "paisa": "money",
        "vasool": "worth", "wahiyat": "terrible", "zabardast": "excellent",
        "mast": "awesome", "shandaar": "splendid", "ghatiya": "inferior",
        "dhokha": "fraud", "nakli": "fake", "asli": "genuine",
        "tikau": "durable", "majboot": "strong", "kamzor": "weak",
    }

    model_config = {"env_prefix": "CRIP_"}


settings = Settings()
