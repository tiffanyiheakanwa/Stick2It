import json
import logging
import google.generativeai as genai
from typing import List, Dict, Any, Optional

from backend.app.config import GEMINI_API_KEY
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configure the Gemini API client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. Task AI Breakdown will fallback to local mock logic.")

class SubtaskSchema(BaseModel):
    title: str
    estimated_minutes: int

class BreakdownSchema(BaseModel):
    subtasks: list[SubtaskSchema]

class TaskAIService:
    def __init__(self):
        # Using Gemini 1.5 because it natively supports structured JSON output
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def breakdown_task(self, title: str, description: Optional[str] = None, behavioral_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Calls Gemini to break down a larger task into 3-5 subtasks.
        """
        if not GEMINI_API_KEY:
            return self._mock_breakdown(title, description)
            
        system_instruction = (
            "You are an academic productivity coach. "
            "Your job is to break down the user's task into 3 to 5 actionable, specific subtasks. "
            "Return ONLY a strictly valid JSON object matching the requested schema."
        )

        prompt = f"Task Title: {title}\n"
        if description:
            prompt += f"Task Description: {description}\n"
            
        if behavioral_context:
            prompt += f"\nUser Context:\n"
            prompt += f"- Login Consistency: {behavioral_context.get('login_consistency', 'unknown')}\n"
            prompt += f"- Engagement Intensity: {behavioral_context.get('engagement_intensity', 'unknown')}\n"
            prompt += "Please take the user's engagement level and consistency into account to frame the subtasks appropriately (e.g., if engagement is low, make the first subtask extremely easy to start)."

        try:
            # Depending on google-generativeai > 0.8.0, we can enforce response_schema
            response = self.model.generate_content(
                contents=[
                    {"role": "user", "parts": [system_instruction + "\n\n" + prompt]}
                ],
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=BreakdownSchema,
                    temperature=0.7
                )
            )
            
            # The response text should be a valid JSON matching BreakdownSchema
            raw_json = response.text
            parsed = json.loads(raw_json)
            
            # Convert to list of dicts that the frontend expects
            if "subtasks" in parsed:
                return parsed["subtasks"]
            return self._mock_breakdown(title, description)

        except Exception as e:
            logger.error(f"Error calling Gemini API for task breakdown: {e}")
            return self._mock_breakdown(title, description)
            
    def _mock_breakdown(self, title: str, description: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fallback mock logic roughly mimicking task_breakdown.py"""
        return [
            {"title": f"Outline the main points for '{title}'", "estimated_minutes": 15},
            {"title": "Draft the initial sections", "estimated_minutes": 30},
            {"title": "Review and finalize", "estimated_minutes": 20}
        ]

task_ai_service = TaskAIService()
