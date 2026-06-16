import json
import logging
import time
import re
import google.generativeai as genai
from typing import List, Dict, Any, Optional

from backend.app.config import GEMINI_API_KEY
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configure the Gemini API client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. Task AI Breakdown will fallback to local logic.")

class SubtaskSchema(BaseModel):
    title: str
    estimated_minutes: int

class BreakdownSchema(BaseModel):
    subtasks: list[SubtaskSchema]


# ---------------------------------------------------------------------------
# Smart mock: generates task-specific subtasks from the title/description
# without hitting the API — used as fallback when quota is exhausted
# ---------------------------------------------------------------------------
_ACADEMIC_PATTERNS = [
    # (keyword_regex, subtask_templates)
    (r'essay|report|write|paper',
     [("Brainstorm and outline key arguments for '{title}'", 20),
      ("Research and gather sources for '{title}'", 45),
      ("Write the first draft", 60),
      ("Revise, proofread and format the final submission", 30)]),

    (r'code|program|implement|build|develop|project',
     [("Read the requirements and plan the architecture for '{title}'", 20),
      ("Set up the project structure and environment", 15),
      ("Implement the core logic / main features", 60),
      ("Write tests and fix bugs", 30),
      ("Review code and prepare submission", 15)]),

    (r'exam|test|quiz|study|revise',
     [("List all topics covered in '{title}'", 15),
      ("Study first half of topics using active recall", 45),
      ("Study second half of topics using active recall", 45),
      ("Do past questions / practice problems", 30),
      ("Final review of weak areas", 20)]),

    (r'presentation|slides|present',
     [("Outline the key points for '{title}'", 15),
      ("Create slide structure and draft content", 40),
      ("Design slides and add visuals", 30),
      ("Rehearse presentation twice", 20)]),

    (r'read|chapter|textbook|article',
     [("Skim the material to get the big picture", 10),
      ("Read actively and take notes", 40),
      ("Summarise key points in your own words", 15),
      ("Review notes and flag anything unclear", 10)]),

    (r'assignment|homework|task|exercise|lab',
     [("Read the assignment instructions carefully for '{title}'", 10),
      ("Break down each question / section", 15),
      ("Complete the main body of work", 50),
      ("Review answers and check requirements before submitting", 15)]),
]

_DEFAULT_TEMPLATES = [
    ("Understand the scope and requirements of '{title}'", 15),
    ("Plan your approach and gather any resources needed", 20),
    ("Complete the main work for '{title}'", 50),
    ("Review your work and make final adjustments", 15),
]


def _smart_mock(title: str, description: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generates plausible, task-specific subtasks from the title/description
    using pattern matching — no API call required.
    """
    text = (title + " " + (description or "")).lower()
    templates = _DEFAULT_TEMPLATES

    for pattern, tmpl_list in _ACADEMIC_PATTERNS:
        if re.search(pattern, text):
            templates = tmpl_list
            break

    return [
        {
            "title": t.format(title=title),
            "estimated_minutes": mins
        }
        for t, mins in templates
    ]


class TaskAIService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def breakdown_task(
        self,
        title: str,
        description: Optional[str] = None,
        behavioral_context: Optional[Dict[str, Any]] = None,
        max_retries: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Calls Gemini to break down a task into 3-5 actionable subtasks.
        Retries once on rate-limit (429) then falls back to smart local logic.
        """
        if not GEMINI_API_KEY:
            return _smart_mock(title, description)

        system_instruction = (
            "You are an academic productivity coach. "
            "Break down the user's task into 3 to 5 specific, actionable subtasks. "
            "Each subtask should be concrete and completable in one sitting. "
            "Return ONLY a strictly valid JSON object matching the requested schema."
        )

        prompt = f"Task Title: {title}\n"
        if description:
            prompt += f"Task Description: {description}\n"

        if behavioral_context:
            prompt += "\nUser Context:\n"
            prompt += f"- Login Consistency: {behavioral_context.get('login_consistency', 'unknown')}\n"
            prompt += f"- Engagement Intensity: {behavioral_context.get('engagement_intensity', 'unknown')}\n"
            prompt += (
                "Take the user's engagement level into account: "
                "if engagement is low, make the first subtask extremely easy to start."
            )

        for attempt in range(max_retries + 1):
            try:
                # Try with structured response_schema first (SDK >= 0.8.0)
                try:
                    response = self.model.generate_content(
                        contents=[{"role": "user", "parts": [system_instruction + "\n\n" + prompt]}],
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=BreakdownSchema,
                            temperature=0.7
                        )
                    )
                except Exception:
                    # Fallback: plain JSON prompt for older SDK versions
                    json_hint = (
                        '\n\nRespond with ONLY a JSON object like: '
                        '{"subtasks": [{"title": "...", "estimated_minutes": 20}, ...]}'
                    )
                    response = self.model.generate_content(
                        contents=[{"role": "user", "parts": [system_instruction + "\n\n" + prompt + json_hint]}],
                        generation_config=genai.types.GenerationConfig(
                            response_mime_type="application/json",
                            temperature=0.7
                        )
                    )

                raw = response.text.strip()
                # Strip markdown fences if present
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]

                parsed = json.loads(raw)

                if "subtasks" in parsed and isinstance(parsed["subtasks"], list):
                    return [
                        {
                            "title": st.get("title", f"Step {i+1}"),
                            "estimated_minutes": int(st.get("estimated_minutes", 20))
                        }
                        for i, st in enumerate(parsed["subtasks"])
                    ]

                # Unexpected structure — fall through to smart mock
                break

            except Exception as e:
                err_str = str(e)
                is_rate_limit = "429" in err_str or "quota" in err_str.lower()

                if is_rate_limit and attempt < max_retries:
                    # Extract retry delay from error message if available
                    delay_match = re.search(r'retry in (\d+)', err_str)
                    wait = int(delay_match.group(1)) if delay_match else 60
                    wait = min(wait, 65)  # cap at 65s so we don't block forever
                    logger.warning(
                        f"Gemini rate limit hit (attempt {attempt+1}/{max_retries+1}). "
                        f"Retrying in {wait}s..."
                    )
                    time.sleep(wait)
                    continue
                else:
                    logger.error(f"Error calling Gemini API for task breakdown: {e}")
                    break

        logger.info(f"Gemini unavailable — using smart local breakdown for '{title}'")
        return _smart_mock(title, description)


task_ai_service = TaskAIService()
