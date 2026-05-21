import os
import json
import ast

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return False

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


class _Response:
    def __init__(self, content):
        self.content = content


class MockLLM:
    """Deterministic quota-safe fallback used for smoke tests and demos without keys."""

    def _extract_user_brief(self, prompt):
        if "USER BRIEF:" not in prompt:
            return {}
        brief_text = prompt.split("USER BRIEF:", 1)[1].split("TONE PROFILE:", 1)[0].split("CHAPTER:", 1)[0].strip()
        try:
            return ast.literal_eval(brief_text)
        except Exception:
            try:
                return json.loads(brief_text)
            except Exception:
                return {}

    def invoke(self, prompt):
        lower = prompt.lower()

        if "planner agent" in lower:
            brief_text = prompt.split("USER BRIEF:", 1)[-1]
            brief = self._extract_user_brief(prompt)
            count = 3
            for token in ("'chapters':", '"chapters":'):
                if token in brief_text:
                    try:
                        count = int(brief_text.split(token, 1)[1].split(",", 1)[0].strip(" }"))
                    except Exception:
                        count = 3
            genre = str(brief.get("genre", "")).lower()
            characters = brief.get("characters", [])
            if genre in {"novella", "fiction"} and len(characters) >= 2:
                first, second = characters[0], characters[1]
                titles = [
                    "The House That Faced the Tide",
                    "A Letter Beneath the Floorboards",
                    "What the Harbor Refused to Say",
                    "The Night the Lantern Went Out",
                    "What Mira and Jonah Chose to Keep",
                ]
                chapters = [
                    {
                        "chapter_number": i,
                        "title": titles[i - 1] if i <= len(titles) else f"The Secret Turns {i}",
                        "summary": (
                            f"{first} and {second} follow the family secret through the coastal town, "
                            f"with chapter {i} deepening their friendship and the danger around the truth."
                        ),
                        "callback_candidates": ["the brass key", "the tide at midnight", f"{first} and {second}'s promise"],
                    }
                    for i in range(1, max(1, min(count, 10)) + 1)
                ]
                return _Response(json.dumps({"book_title": "The Tide Beneath the Door", "chapters": chapters}))
            chapters = [
                {
                    "chapter_number": i,
                    "title": f"Chapter {i} Turning Point",
                    "summary": f"A practical chapter that develops idea {i} and prepares callbacks for later sections.",
                    "callback_candidates": [f"turning point {i}", "small choices compound"],
                }
                for i in range(1, max(1, min(count, 10)) + 1)
            ]
            return _Response(json.dumps({"book_title": "AIuthor Sample Book", "chapters": chapters}))

        if "writer agent" in lower:
            chapter_number = 1
            title = "A Useful Beginning"
            brief = self._extract_user_brief(prompt)
            characters = brief.get("characters", [])
            genre = str(brief.get("genre", "")).lower()
            try:
                chapter_blob = prompt.split("CHAPTER:", 1)[1]
                if "'chapter_number':" in chapter_blob:
                    chapter_number = int(chapter_blob.split("'chapter_number':", 1)[1].split(",", 1)[0].strip())
                if "'title':" in chapter_blob:
                    title = chapter_blob.split("'title':", 1)[1].split(",", 1)[0].strip(" '\"")
            except Exception:
                pass
            if genre in {"novella", "fiction"} and len(characters) >= 2:
                first, second = characters[0], characters[1]
                story_beats = [
                    (
                        f"{first} reached the old harbor steps before sunrise, where the town smelled of rain, rope, and secrets. "
                        f"{second} was already there, holding the brass key they had promised never to use alone.",
                        f"{first} recognized a mark from her grandmother's locked notebook; {second} recognized it from stories his father stopped telling.",
                        "The key did not open a door. It opened a question."
                    ),
                    (
                        f"The letter beneath the floorboards was addressed to {first}, though it had been written before she was born. "
                        f"{second} read the date twice and went pale.",
                        f"Every line tied their families together more tightly, and every silence in town began to look deliberate.",
                        "By nightfall, the secret had a handwriting."
                    ),
                    (
                        f"{first} and {second} followed the harbor bell to the abandoned net shed, where gulls nested in the rafters and old maps curled from damp.",
                        "The map showed a room below the chapel and a passage that vanished under the tide.",
                        "The town had not forgotten the secret. It had built streets around it."
                    ),
                    (
                        f"When the lantern went out, {second} caught {first}'s sleeve before she stepped into the flooded stairwell.",
                        "Below them, voices moved through the dark, speaking their surnames as if both families owed the sea a debt.",
                        "For the first time, running felt easier than knowing."
                    ),
                    (
                        f"At dawn, {first} and {second} carried the truth back through town together, no longer sure whether it would heal anyone.",
                        "They chose what to reveal, what to forgive, and what the sea could keep for one more generation.",
                        "The secret had changed them, but it had not taken them from each other."
                    ),
                ]
                opening, clue, ending = story_beats[(chapter_number - 1) % len(story_beats)]
                content = (
                    f"{opening}\n\n"
                    "## The clue by the water\n"
                    f"{clue} Neither said they were afraid, which meant both of them were.\n\n"
                    "## The promise that followed\n"
                    f"By dusk, {first} and {second} understood that the family secret was not buried in one house. "
                    f"{ending}"
                )
                return _Response(json.dumps({
                    "chapter_number": chapter_number,
                    "title": title,
                    "content": content,
                    "callbacks_used": ["the brass key", f"{first} and {second}'s promise"],
                }))
            content = (
                f"You begin chapter {chapter_number} with one manageable decision, not a grand performance.\n\n"
                "## The first useful move\n"
                "The idea is simple: choose a habit small enough that it can survive an ordinary Tuesday. "
                "That rhythm gives the book a living thread, because every later chapter can look back at this first choice.\n\n"
                "## What carries forward\n"
                "When the next chapter returns to small choices compounding, the callback should feel earned rather than pasted in."
            )
            return _Response(json.dumps({
                "chapter_number": chapter_number,
                "title": title,
                "content": content,
                "callbacks_used": ["small choices compound"],
            }))

        if "fact checker agent" in lower:
            content = prompt.split("CHAPTER:", 1)[-1].strip()
            try:
                chapter_obj = ast.literal_eval(content)
                content = chapter_obj.get("content", content)
            except Exception:
                pass
            return _Response(json.dumps({
                "chapter_number": 1,
                "corrected_content": content,
                "flagged_claims": [],
                "softened_claims": [],
            }))

        if "humanizer agent" in lower:
            return _Response(json.dumps({
                "chapter_number": 1,
                "humanized_content": prompt.split("CONTENT:", 1)[-1].strip(),
            }))

        if "glossary agent" in lower:
            return _Response(json.dumps({"terms": [
                {"term": "Callback", "definition": "A deliberate return to an earlier idea so the book feels remembered."},
                {"term": "Tone fingerprint", "definition": "The practical voice rules that keep every page sounding like the same book."},
            ]}))

        if "references agent" in lower:
            return _Response(json.dumps({"references": [
                "Introductory personal finance education",
                "Behavioral habit formation research",
                "Plain-language nonfiction craft",
            ]}))

        if "front matter agent" in lower:
            return _Response(json.dumps({
                "dedication": "For readers building a sturdier next page.",
                "epigraph": "Small choices become a map when you keep returning to them.",
                "foreword": "This book was assembled to be useful before it tries to be impressive.",
                "preface": "The pages ahead treat the reader as a person with limited time and real decisions.",
                "acknowledgments": "Thanks to the early reviewers, tools, and test runs that made the system more honest.",
                "introduction": "Start here: the book will build through callbacks, careful claims, and a voice chosen for its reader.",
                "afterword": "The ending is a handoff. Carry the smallest useful practice into the next ordinary day.",
                "about_author": "AIuthor is an agentic writing system built around planning, memory, critique, and assembly.",
                "back_cover_copy": "A practical book generated by an auditable multi-agent pipeline, shaped for readers who want clarity without boilerplate.",
            }))

        return _Response("{}")


def _get_groq_llm(temperature):
    if not GROQ_API_KEY or os.getenv("AIUTHOR_OFFLINE", "").lower() in {"1", "true", "yes"}:
        return MockLLM()
    try:
        from langchain_groq import ChatGroq
    except Exception:
        return MockLLM()
    return ChatGroq(
        model=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=temperature,
    )


def get_writer_llm():
    return _get_groq_llm(0.7)


def get_fast_llm():
    return _get_groq_llm(0.3)
