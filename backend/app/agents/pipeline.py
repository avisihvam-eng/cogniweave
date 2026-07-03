import os
import json
import httpx
from app.config import settings

# Schemas for Gemini Structured JSON Outputs
INGESTION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "speaker": {"type": "STRING"},
        "duration": {"type": "INTEGER"},
        "topics": {"type": "ARRAY", "items": {"type": "STRING"}}
    },
    "required": ["title", "speaker", "duration", "topics"]
}

SIGNAL_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "core_thesis": {"type": "STRING"},
        "insights": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "insight": {"type": "STRING"},
                    "why_it_matters": {"type": "STRING"},
                    "application": {"type": "STRING"},
                    "action": {"type": "STRING"}
                },
                "required": ["insight", "why_it_matters", "application", "action"]
            }
        }
    },
    "required": ["core_thesis", "insights"]
}

MENTAL_MODEL_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "mental_models": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "definition": {"type": "STRING"},
                    "explanation": {"type": "STRING"},
                    "example": {"type": "STRING"},
                    "application": {"type": "STRING"}
                },
                "required": ["name", "definition", "explanation", "example", "application"]
            }
        }
    },
    "required": ["mental_models"]
}

VOCABULARY_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "vocabulary": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "word": {"type": "STRING"},
                    "meaning": {"type": "STRING"},
                    "usage": {"type": "STRING"},
                    "origin": {"type": "STRING"},
                    "simpler_synonym": {"type": "STRING"}
                },
                "required": ["word", "meaning", "usage", "origin", "simpler_synonym"]
            }
        }
    },
    "required": ["vocabulary"]
}

QUOTES_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "quotes": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "quote": {"type": "STRING"},
                    "meaning": {"type": "STRING"},
                    "why_memorable": {"type": "STRING"},
                    "counterargument": {"type": "STRING"}
                },
                "required": ["quote", "meaning", "why_memorable", "counterargument"]
            }
        }
    },
    "required": ["quotes"]
}

CONTRARIAN_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "contrarian": {
            "type": "OBJECT",
            "properties": {
                "opposing_argument": {"type": "STRING"},
                "assumptions": {"type": "STRING"},
                "evidence_missing": {"type": "STRING"},
                "confidence_score": {"type": "INTEGER"}
            },
            "required": ["opposing_argument", "assumptions", "evidence_missing", "confidence_score"]
        }
    },
    "required": ["contrarian"]
}

CONTENT_ASSETS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "tweets": {"type": "ARRAY", "items": {"type": "STRING"}},
        "linkedin_post": {"type": "STRING"},
        "newsletter_outline": {"type": "STRING"}
    },
    "required": ["tweets", "linkedin_post", "newsletter_outline"]
}

KNOWLEDGE_GRAPH_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "nodes": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"},
                    "description": {"type": "STRING"}
                },
                "required": ["title", "description"]
            }
        },
        "edges": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "source": {"type": "STRING"},
                    "target": {"type": "STRING"},
                    "relationship": {"type": "STRING"}
                },
                "required": ["source", "target", "relationship"]
            }
        }
    },
    "required": ["nodes", "edges"]
}

class GeminiAgent:
    def __init__(self, name: str, model: str, instruction: str, response_schema: dict = None):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.response_schema = response_schema

    async def run(self, prompt: str) -> dict:
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            print(f"Warning: GEMINI_API_KEY not set. Mocking output for agent '{self.name}'.")
            return self._generate_mock_response()

        # Check model and append prefix if needed
        model_name = self.model
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"

        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": self.instruction}]
            },
            "generationConfig": {
                "temperature": 0.2
            }
        }

        if self.response_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"
            payload["generationConfig"]["responseSchema"] = self.response_schema

        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, timeout=60.0)
                if r.status_code == 200:
                    res_json = r.json()
                    text = res_json['candidates'][0]['content']['parts'][0]['text']
                    if self.response_schema:
                        return json.loads(text)
                    return {"text": text}
                else:
                    print(f"Gemini API returned error {r.status_code}: {r.text}")
                    return self._generate_mock_response()
        except Exception as e:
            print(f"Error calling Gemini API for agent '{self.name}': {e}")
            return self._generate_mock_response()

    def _generate_mock_response(self) -> dict:
        if self.name == "ingestion_agent":
            return {
                "title": "Ingested Document Summary",
                "speaker": "Principal Thinker",
                "duration": 3600,
                "topics": ["Decision Making", "Mental Models", "Compounding"]
            }
        elif self.name == "signal_agent":
            return {
                "core_thesis": "True wisdom comes from building systems that compound value and enable second-order thinking.",
                "insights": [
                    {
                        "insight": "Knowledge is a compounding asset that yields exponential returns over time.",
                        "why_it_matters": "Most people treat information as transactional, forgetting it instantly.",
                        "application": "Build a personal compilation index and review it using spaced repetition.",
                        "action": "Select 3 actions from your reading list today and execute them."
                    },
                    {
                        "insight": "Optimize for optionality in early-stage career choices.",
                        "why_it_matters": "Committing too early limits potential upside variance.",
                        "application": "Say yes to diverse projects until you find a strong product-market fit.",
                        "action": "Allocate 2 hours this week to explore a completely new technical domain."
                    }
                ]
            }
        elif self.name == "mental_model_agent":
            return {
                "mental_models": [
                    {
                        "name": "Compounding",
                        "definition": "The process where earnings are reinvested to generate additional earnings over time.",
                        "explanation": "Small gains consistently repeated build massive divergence between linear and exponential curves.",
                        "example": "Writing one page of code daily results in a substantial library after 5 years.",
                        "application": "Apply compounding to learning by reading 30 minutes every morning."
                    },
                    {
                        "name": "Second-Order Thinking",
                        "definition": "Thinking about the consequences of consequences, not just the immediate effect.",
                        "explanation": "First-order thinking solves immediate problems. Second-order thinking looks at how that solution affects things down the line.",
                        "example": "Adding code fixes that reduce technical debt now but make future expansion impossible.",
                        "application": "When designing APIs, ask: how will this scale if we support 10x more features?"
                    }
                ]
            }
        elif self.name == "vocabulary_agent":
            return {
                "vocabulary": [
                    {
                        "word": "Mellifluous",
                        "meaning": "Sweet or musical; pleasant to hear.",
                        "usage": "His explanation of systems thinking was mellifluous.",
                        "origin": "Latin (mel - honey, fluere - to flow)",
                        "simpler_synonym": "Smooth"
                    },
                    {
                        "word": "Cognitive Surplus",
                        "meaning": "The free time and mental bandwidth available to society to collaborate on activities.",
                        "usage": "The internet allows us to pool cognitive surplus to build open source projects.",
                        "origin": "Modern sociology",
                        "simpler_synonym": "Free mental energy"
                    }
                ]
            }
        elif self.name == "quotes_agent":
            return {
                "quotes": [
                    {
                        "quote": "The best way to think is to write. Writing is thinking.",
                        "meaning": "Writing forces you to resolve logical inconsistencies in your mind.",
                        "why_memorable": "It is brief and links cognitive clarity directly to physical action.",
                        "counterargument": "Some writers overcomplicate ideas that would be clear in speech."
                    }
                ]
            }
        elif self.name == "contrarian_agent":
            return {
                "contrarian": {
                    "opposing_argument": "Compounding knowledge is overrated if you never execute on what you learn. Action is the only true signal.",
                    "assumptions": "Assumes that learning itself is the goal rather than output.",
                    "evidence_missing": "Case studies of highly successful individuals who don't keep organized notes.",
                    "confidence_score": 8
                }
            }
        elif self.name == "content_creation_agent":
            return {
                "tweets": [
                    "Knowledge isn't power. Compounding knowledge is. Build your personal compiler today.",
                    "First-order thinkers solve problems. Second-order thinkers prevent them. Optimize for downstream consequences."
                ],
                "linkedin_post": "Information is abundant, but structured insight is scarce. Here is how we build compounding knowledge bases using modern AI agents...",
                "newsletter_outline": "1. The Ingestion Dilemma\n2. Shifting from Summaries to Systems\n3. Actionable Takeaways for Founders"
            }
        elif self.name == "knowledge_graph_agent":
            return {
                "nodes": [
                    {"title": "Compounding Knowledge", "description": "The idea that information grows exponentially when compiled systematically."},
                    {"title": "Second-Order Thinking", "description": "Analyzing downstream effects of choices."}
                ],
                "edges": [
                    {"source": "Compounding Knowledge", "target": "Second-Order Thinking", "relationship": "expands"}
                ]
            }
        return {"result": "mock"}

# Orchestration Pipeline runner
async def run_compilation_pipeline(content: str, source_url: str = None, user_profile: dict = None) -> dict:
    user_profile = user_profile or {}
    
    # 1. Ingestion Agent
    ingestion_agent = GeminiAgent(
        name="ingestion_agent",
        model="gemini-2.5-flash",
        instruction="You are an Ingestion Agent. Extract metadata (title, speaker, duration, and main topics) from this content. Return JSON.",
        response_schema=INGESTION_SCHEMA
    )
    metadata = await ingestion_agent.run(content)
    if source_url:
        metadata["url"] = source_url
    
    # 2. Signal Agent (Using Gemini Pro for deep reasoning)
    signal_agent = GeminiAgent(
        name="signal_agent",
        model="gemini-2.5-pro",
        instruction="You are a Signal Extraction Agent. Identify the core thesis and extract highest-signal insights. Skip stories, introductions, and generic talk. For each insight, explain why it matters, how it applies, and one concrete action to take.",
        response_schema=SIGNAL_SCHEMA
    )
    signal_data = await signal_agent.run(content)
    
    # 3. Mental Model Agent
    mental_model_agent = GeminiAgent(
        name="mental_model_agent",
        model="gemini-2.5-flash",
        instruction="You are a Mental Model Agent. Scan the content and identify instances of mental models (e.g. Compounding, Incentives, Systems thinking, Inversion, Network effects). Provide definitions, explanation, example, and how to apply them.",
        response_schema=MENTAL_MODEL_SCHEMA
    )
    mental_models = await mental_model_agent.run(content)

    # 4. Vocabulary Agent
    vocab_agent = GeminiAgent(
        name="vocabulary_agent",
        model="gemini-2.5-flash",
        instruction="You are a Vocabulary Agent. Extract sophisticated yet practical vocabulary used in the text. Return a list of words, meanings, usage, origin, and simpler synonyms.",
        response_schema=VOCABULARY_SCHEMA
    )
    vocab = await vocab_agent.run(content)
    
    # 5. Quotes Agent
    quotes_agent = GeminiAgent(
        name="quotes_agent",
        model="gemini-2.5-flash",
        instruction="You are a Quote Intelligence Agent. Extract memorable, powerful quotes. Explain the meaning, why it is memorable, and write a counterargument to that quote.",
        response_schema=QUOTES_SCHEMA
    )
    quotes = await quotes_agent.run(content)

    # 6. Contrarian Agent
    contrarian_agent = GeminiAgent(
        name="contrarian_agent",
        model="gemini-2.5-pro",
        instruction="You are a Contrarian Agent. Challenge the main points in the content. Build the strongest opposing argument, identify hidden assumptions, specify missing evidence, and give a confidence score for the original thesis.",
        response_schema=CONTRARIAN_SCHEMA
    )
    contrarian = await contrarian_agent.run(content)

    # 7. Content Creation Agent
    content_creation_agent = GeminiAgent(
        name="content_creation_agent",
        model="gemini-2.5-flash",
        instruction="You are a Content Creation Agent. Generate content assets including 3 tweets, 1 LinkedIn post, and a newsletter outline. Make it sound highly original, sharp, and engaging.",
        response_schema=CONTENT_ASSETS_SCHEMA
    )
    content_assets = await content_creation_agent.run(content)

    # 8. Knowledge Graph Agent
    graph_agent = GeminiAgent(
        name="knowledge_graph_agent",
        model="gemini-2.5-flash",
        instruction="You are a Knowledge Graph Agent. Convert the core insights into graph nodes and define their relationships (e.g. supports, contradicts, expands, related_to).",
        response_schema=KNOWLEDGE_GRAPH_SCHEMA
    )
    graph_data = await graph_agent.run(content)

    # 9. Personal Intelligence Agent
    # We personalize the output structures based on the user's career/goals.
    profile_summary = f"Career: {user_profile.get('career', 'Founder')}, Goals: {user_profile.get('goals', 'Growth')}, Interests: {user_profile.get('interests', 'Tech')}"
    personal_agent = GeminiAgent(
        name="personal_agent",
        model="gemini-2.5-flash",
        instruction=f"You are a Personal Intelligence Agent. Customize these insights to fit this user profile: {profile_summary}. Filter out irrelevant areas, translate analogies to fit their industry, and highlight how the lessons apply to their career.",
    )
    
    insights_str = json.dumps(signal_data.get("insights", []))
    personalized_result = await personal_agent.run(f"User Profile: {profile_summary}\n\nInsights: {insights_str}")
    
    # 10. Compile final structure
    compiled_data = {
        **metadata,
        **signal_data,
        **mental_models,
        **vocab,
        **quotes,
        **contrarian,
        "content_assets": content_assets,
        "knowledge_graph": graph_data,
        "personalization": personalized_result.get("text", ""),
        "reading_list": ["The Lessons of History by Will Durant", "Poor Charlie's Almanack by Charlie Munger"]
    }
    
    return compiled_data
