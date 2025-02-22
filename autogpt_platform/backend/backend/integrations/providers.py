from enum import Enum


# --8<-- [start:ProviderName]
class ProviderName(str, Enum):
    ANTHROPIC = "anthropic"
    APOLLO = "apollo"
    COMPASS = "compass"
    DISCORD = "discord"
    D_ID = "d_id"
    E2B = "e2b"
    EXA = "exa"
    FAL = "fal"
    GITHUB = "github"
    GOOGLE = "google"
    GOOGLE_MAPS = "google_maps"
    GROQ = "groq"
    HUBSPOT = "hubspot"
    IDEOGRAM = "ideogram"
    JINA = "jina"
    LINEAR = "linear"
    MEDIUM = "medium"
    MEM0 = "mem0"
    NOTION = "notion"
    NVIDIA = "nvidia"
    OLLAMA = "ollama"
    OPENAI = "openai"
    OPENWEATHERMAP = "openweathermap"
    OPEN_ROUTER = "open_router"
    PINECONE = "pinecone"
    REDDIT = "reddit"
    REPLICATE = "replicate"
    REVID = "revid"
    SCREENSHOTONE = "screenshotone"
    SLANT3D = "slant3d"
    SMARTLEAD = "smartlead"
    SMTP = "smtp"
    TWITTER = "twitter"
    TODOIST = "todoist"
    UNREAL_SPEECH = "unreal_speech"
    ZEROBOUNCE = "zerobounce"
    # --8<-- [end:ProviderName]
