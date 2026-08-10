"""
Claude API client module.
"""
import json
import base64
from pathlib import Path
from typing import Dict, Optional
from anthropic import Anthropic


class ClaudeClient:
    """Client for interacting with Claude API."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096, temperature: float = 0.3):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key
            model: Model identifier
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def answer_question_from_image(self, image_path: str, knowledge_context: str = "") -> Dict:
        """
        Send screenshot to Claude with vision and get structured answer.

        Args:
            image_path: Path to screenshot image
            knowledge_context: Optional context from Knowledge Bank

        Returns:
            Dictionary with:
            {
                "question": "Extracted question text",
                "options": [{"label": "A", "text": "..."}, ...],
                "correct_options": ["A", "C"],
                "explanation": "...",
                "input_tokens": 1234,
                "output_tokens": 567
            }
        """
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')

        # Determine media type
        suffix = Path(image_path).suffix.lower()
        media_type = "image/png" if suffix == ".png" else "image/jpeg"

        # Build message content
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data
                }
            },
            {
                "type": "text",
                "text": self._build_vision_prompt(knowledge_context)
            }
        ]

        # Define JSON schema for structured output
        response_schema = {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The full question text extracted from the image"
                },
                "options": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Option label (A, B, C, D, etc.)"
                            },
                            "text": {
                                "type": "string",
                                "description": "Full text of the option"
                            }
                        },
                        "required": ["label", "text"],
                        "additionalProperties": False
                    },
                    "description": "Array of answer options"
                },
                "correct_options": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Array of correct option labels (e.g., ['A'] or ['A', 'C'])"
                },
                "explanation": {
                    "type": "string",
                    "description": "Brief explanation of why the answer is correct"
                }
            },
            "required": ["question", "options", "correct_options", "explanation"],
            "additionalProperties": False
        }

        # Call Claude API with vision and structured output
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "user", "content": content}
            ],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": response_schema,
                }
            }
        )

        # Extract token usage
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Parse response (guaranteed valid JSON with schema)
        response_text = response.content[0].text
        answer_data = json.loads(response_text)

        # Add token usage
        answer_data["input_tokens"] = input_tokens
        answer_data["output_tokens"] = output_tokens

        return answer_data

    def _build_vision_prompt(self, knowledge_context: str = "") -> str:
        """Build prompt for vision-based question extraction."""
        prompt_parts = [
            "You are an expert test-taking assistant. Analyze this test question screenshot.",
            "",
            "INSTRUCTIONS:",
            "1. Extract the question text (ignore browser UI and navigation)",
            "2. Extract all answer options with their labels (A, B, C, D, etc.)",
            "3. Identify which option(s) are correct based on your knowledge",
            "4. Provide a brief explanation",
            ""
        ]

        if knowledge_context:
            prompt_parts.append(f"RELEVANT CONTEXT:\n{knowledge_context}\n")

        prompt_parts.append("Focus on the main question content. Extract complete option text, not just keywords.")

        return "\n".join(prompt_parts)
