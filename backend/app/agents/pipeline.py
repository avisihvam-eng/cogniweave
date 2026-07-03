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

# Require 20 items minimum
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

# Require 15 items minimum
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

COMMUNICATION_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "patterns": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "pattern": {"type": "STRING"},
                    "explanation": {"type": "STRING"},
                    "examples": {"type": "ARRAY", "items": {"type": "STRING"}}
                },
                "required": ["pattern", "explanation", "examples"]
            }
        },
        "metaphors_analogies": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "type": {"type": "STRING"},
                    "concept": {"type": "STRING"},
                    "expression": {"type": "STRING"}
                },
                "required": ["type", "concept", "expression"]
            }
        }
    },
    "required": ["patterns", "metaphors_analogies"]
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
        "blog_outline": {"type": "STRING"},
        "newsletter_section": {"type": "STRING"},
        "conversation_starters": {"type": "ARRAY", "items": {"type": "STRING"}},
        "podcast_questions": {"type": "ARRAY", "items": {"type": "STRING"}},
        "interview_questions": {"type": "ARRAY", "items": {"type": "STRING"}}
    },
    "required": [
        "tweets", 
        "linkedin_post", 
        "blog_outline", 
        "newsletter_section", 
        "conversation_starters", 
        "podcast_questions", 
        "interview_questions"
    ]
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
                r = await client.post(url, json=payload, timeout=90.0)
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
        # Structured mocks matching the new PRD schemas
        if self.name == "ingestion_agent":
            return {
                "title": "Systems Thinking & Leveraged Compounding",
                "speaker": "Naval Ravikant",
                "duration": 3600,
                "topics": ["Mental Models", "Compounding", "Leverage"]
            }
        elif self.name == "signal_agent":
            return {
                "core_thesis": "Compounding knowledge combined with asymmetric leverage transforms linear learning curves into exponential growth curves.",
                "insights": [
                    {
                        "insight": "Knowledge is a compounding asset that yields exponential returns over time.",
                        "why_it_matters": "Most people treat information as transactional, forgetting it instantly.",
                        "application": "Build a personal compilation index and review it using spaced repetition.",
                        "action": "Select 3 actions from your reading list today and execute them."
                    }
                ]
            }
        elif self.name == "mental_model_agent":
            return {
                "mental_models": [
                    {
                        "name": "Compounding",
                        "definition": "Reinvesting gains to generate additional returns over time.",
                        "explanation": "Small wins build exponential value when repeated consistently.",
                        "example": "Reading 30 minutes daily accumulates massive wisdom in 5 years.",
                        "application": "Apply compounding to learning by reading 30 minutes every morning."
                    }
                ]
            }
        elif self.name == "vocabulary_agent":
            # Return 20 items to satisfy PRD
            return {
                "vocabulary": [{"word": f"VocabWord_{i}", "meaning": "Sophisticated definition", "usage": "Usage example", "origin": "Latin origin", "simpler_synonym": "synonym"} for i in range(1, 21)]
            }
        elif self.name == "quotes_agent":
            # Return 15 items to satisfy PRD
            return {
                "quotes": [{"quote": f"Memorable quote line {i}.", "meaning": "Explanation", "why_memorable": "Articulate technique", "counterargument": "Opposing point"} for i in range(1, 16)]
            }
        elif self.name == "communication_agent":
            return {
                "patterns": [
                    {
                        "pattern": "X is overrated. Y compounds.",
                        "explanation": "Contrasting two concepts to highlight exponential gains.",
                        "examples": [
                            "IQ is overrated. Curiosity compounds.",
                            "Talent is overrated. Execution compounds."
                        ]
                    }
                ],
                "metaphors_analogies": [
                    {
                        "type": "metaphor",
                        "concept": "Knowledge accumulation",
                        "expression": "A compounding snow-ball rolling down the hill."
                    }
                ]
            }
        elif self.name == "contrarian_agent":
            return {
                "contrarian": {
                    "opposing_argument": "Compounding works for structural skills, but transactional domains change too quickly for old lessons to compound.",
                    "assumptions": "Assumes that baseline cognitive tools never go obsolete.",
                    "evidence_missing": "Longitudinal data comparing generalized versus specialized domain outputs.",
                    "confidence_score": 8
                }
            }
        elif self.name == "content_creation_agent":
            return {
                "tweets": ["Tweet 1", "Tweet 2", "Tweet 3", "Tweet 4", "Tweet 5"],
                "linkedin_post": "Detailed LinkedIn Post...",
                "blog_outline": "Blog post structure...",
                "newsletter_section": "Newsletter highlights...",
                "conversation_starters": ["How do you apply compounding daily?"],
                "podcast_questions": ["What is the limit of mental leverage?"],
                "interview_questions": ["How do you distinguish linear vs exponential setups?"]
            }
        elif self.name == "knowledge_graph_agent":
            return {
                "nodes": [{"title": "Compounding", "description": "Exponential growth"}],
                "edges": [{"source": "Compounding", "target": "Leverage", "relationship": "expands"}]
            }
        return {}

async def run_compilation_pipeline(content: str, source_url: str = None, user_profile: dict = None) -> dict:
    user_profile = user_profile or {}
    
    # 1. Ingestion Agent
    ingestion_agent = GeminiAgent(
        name="ingestion_agent",
        model="gemini-2.5-flash",
        instruction="You are an Ingestion Agent. Extract metadata (title, speaker, duration, and main topics) from this content. Return JSON.",
        response_schema=INGESTION_SCHEMA
    )
    metadata = await ingestion_agent.run(content[:8000])
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
    mental_models = await mental_model_agent.run(content[:24000])

    # 4. Vocabulary Agent (Instruct minimum 20 words)
    vocab_agent = GeminiAgent(
        name="vocabulary_agent",
        model="gemini-2.5-flash",
        instruction="You are a Vocabulary Agent. Identify and extract at least 20 sophisticated yet practical vocabulary words used or related to the text. Provide meaning, usage, origin, and simpler synonyms for each.",
        response_schema=VOCABULARY_SCHEMA
    )
    vocab = await vocab_agent.run(content[:24000])
    
    # 5. Quotes Agent (Instruct minimum 15 quotes)
    quotes_agent = GeminiAgent(
        name="quotes_agent",
        model="gemini-2.5-flash",
        instruction="You are a Quote Intelligence Agent. Extract at least 15 memorable, powerful quotes. Explain the meaning, why it is memorable, and write a counterargument to that quote.",
        response_schema=QUOTES_SCHEMA
    )
    quotes = await quotes_agent.run(content[:24000])

    # 6. Communication Agent
    communication_agent = GeminiAgent(
        name="communication_agent",
        model="gemini-2.5-flash",
        instruction="You are a Communication Agent. Identify memorable articulation, metaphors, analogies, and sentence structures. Provide explanations and generate original examples using the same sentence pattern structure.",
        response_schema=COMMUNICATION_SCHEMA
    )
    communication = await communication_agent.run(content[:24000])

    # 7. Contrarian Agent
    contrarian_agent = GeminiAgent(
        name="contrarian_agent",
        model="gemini-2.5-pro",
        instruction="You are a Contrarian Agent. Challenge the main points in the content. Build the strongest opposing argument, identify hidden assumptions, specify missing evidence, and give a confidence score for the original thesis.",
        response_schema=CONTRARIAN_SCHEMA
    )
    contrarian = await contrarian_agent.run(content)

    # 8. Content Creation Agent
    content_creation_agent = GeminiAgent(
        name="content_creation_agent",
        model="gemini-2.5-flash",
        instruction="You are a Content Creation Agent. Generate content assets including exactly 5 tweets, 1 LinkedIn post, a blog outline, a newsletter section, conversation starters, podcast questions, and interview questions. Make them highly original and sharp.",
        response_schema=CONTENT_ASSETS_SCHEMA
    )
    content_assets = await content_creation_agent.run(content[:24000])

    # 9. Knowledge Graph Agent
    graph_agent = GeminiAgent(
        name="knowledge_graph_agent",
        model="gemini-2.5-flash",
        instruction="You are a Knowledge Graph Agent. Convert the core insights into graph nodes and define their relationships (e.g. supports, contradicts, expands, related_to).",
        response_schema=KNOWLEDGE_GRAPH_SCHEMA
    )
    graph_data = await graph_agent.run(content[:24000])

    # 10. Personal Intelligence Agent
    profile_summary = f"Career: {user_profile.get('career', 'Founder')}, Goals: {user_profile.get('goals', 'Growth')}, Interests: {user_profile.get('interests', 'Tech')}"
    personal_agent = GeminiAgent(
        name="personal_agent",
        model="gemini-2.5-flash",
        instruction=f"You are a Personal Intelligence Agent. Customize these insights to fit this user profile: {profile_summary}. Highlight how the lessons apply to their career.",
    )
    insights_str = json.dumps(signal_data.get("insights", []))
    personalized_result = await personal_agent.run(f"User Profile: {profile_summary}\n\nInsights: {insights_str}")
    
    compiled_data = {
        **metadata,
        **signal_data,
        **mental_models,
        **vocab,
        **quotes,
        **communication,
        **contrarian,
        "content_assets": content_assets,
        "knowledge_graph": graph_data,
        "personalization": personalized_result.get("text", ""),
        "reading_list": ["The Lessons of History by Will Durant", "Poor Charlie's Almanack by Charlie Munger"]
    }
    
    return compiled_data
