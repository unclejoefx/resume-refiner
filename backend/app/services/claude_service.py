"""Claude API service for AI-powered analysis."""

import json
import logging
from typing import List, Optional, Dict, Any
from anthropic import AsyncAnthropic, APIError, APITimeoutError, RateLimitError
from app.config import settings
from app.models.resume import ResumeContent, Experience
from app.models.analysis import ContentSuggestion

logger = logging.getLogger(__name__)


class ClaudeConfig:
    """Configuration for Claude API service."""

    MODEL = "claude-3-5-sonnet-20241022"
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7
    MAX_RETRIES = 2
    TIMEOUT = 60.0  # seconds
    MAX_TEXT_LENGTH = 100000  # Max chars to send to Claude


class ClaudeService:
    """Service for interacting with Claude API."""

    def __init__(self):
        """Initialize Claude service."""
        self.api_key = settings.CLAUDE_API_KEY
        if not self.api_key:
            logger.warning("CLAUDE_API_KEY not configured - AI suggestions will be unavailable")
            self.client = None
        else:
            self.client = AsyncAnthropic(api_key=self.api_key)

    def _is_available(self) -> bool:
        """Check if Claude API is available."""
        return self.client is not None

    async def analyze_content(self, resume_content: ResumeContent) -> List[ContentSuggestion]:
        """
        Analyze resume content and provide suggestions.

        Args:
            resume_content: Parsed resume content

        Returns:
            List of content suggestions
        """
        if not self._is_available():
            logger.warning("Claude API not available - returning empty suggestions")
            return []

        try:
            suggestions = []

            # Analyze summary if present
            if resume_content.summary:
                summary_suggestions = await self._analyze_summary(resume_content.summary)
                suggestions.extend(summary_suggestions)

            # Analyze experience sections
            for idx, exp in enumerate(resume_content.experience):
                exp_suggestions = await self._analyze_experience(exp, idx)
                suggestions.extend(exp_suggestions)

            # Analyze skills if present
            if resume_content.skills:
                skills_suggestions = await self._analyze_skills(resume_content.skills)
                suggestions.extend(skills_suggestions)

            logger.info(f"Generated {len(suggestions)} content suggestions")
            return suggestions[:10]  # Limit to top 10 suggestions

        except RateLimitError as e:
            logger.error("Claude API rate limit exceeded", exc_info=True)
            return []
        except APITimeoutError as e:
            logger.error("Claude API timeout", exc_info=True)
            return []
        except APIError as e:
            logger.error(f"Claude API error: {str(e)}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error in analyze_content: {str(e)}", exc_info=True)
            return []

    async def _analyze_summary(self, summary: str) -> List[ContentSuggestion]:
        """Analyze professional summary and provide suggestions."""
        if len(summary) > ClaudeConfig.MAX_TEXT_LENGTH:
            summary = summary[:ClaudeConfig.MAX_TEXT_LENGTH]

        prompt = f"""Analyze this professional resume summary and provide ONE specific, actionable improvement suggestion.

Current Summary:
{summary}

Focus on:
1. Impact and achievements (use metrics/numbers)
2. Clear value proposition
3. Active voice and strong action verbs
4. Conciseness (2-3 sentences ideal)
5. Relevance to career goals

Return your response as a JSON object with this exact structure:
{{
  "original_text": "the original summary text",
  "suggested_text": "your improved version",
  "explanation": "brief explanation of what you improved and why",
  "impact": "high"
}}

Important: Return ONLY the JSON object, no additional text."""

        try:
            response = await self.client.messages.create(
                model=ClaudeConfig.MODEL,
                max_tokens=ClaudeConfig.MAX_TOKENS,
                temperature=ClaudeConfig.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            suggestion_data = json.loads(content)

            return [ContentSuggestion(
                section="summary",
                original_text=suggestion_data["original_text"],
                suggested_text=suggestion_data["suggested_text"],
                explanation=suggestion_data["explanation"],
                impact=suggestion_data.get("impact", "high")
            )]

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response for summary: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error analyzing summary: {str(e)}", exc_info=True)
            return []

    async def _analyze_experience(self, experience: Experience, index: int) -> List[ContentSuggestion]:
        """Analyze work experience and provide suggestions."""
        if not experience.bullets:
            return []

        # Analyze only the first 2-3 bullets to avoid overwhelming the response
        bullets_to_analyze = experience.bullets[:3]
        bullets_text = "\n".join(f"- {bullet}" for bullet in bullets_to_analyze)

        if len(bullets_text) > ClaudeConfig.MAX_TEXT_LENGTH:
            bullets_text = bullets_text[:ClaudeConfig.MAX_TEXT_LENGTH]

        prompt = f"""Analyze these resume bullet points for the position "{experience.position}" at "{experience.company}".

Current Bullet Points:
{bullets_text}

Provide ONE specific improvement for the weakest bullet point.

Best practices:
1. Start with strong action verbs
2. Include quantifiable metrics and results
3. Follow the format: "Action Verb + Task + Result/Impact"
4. Be specific and concrete
5. Focus on achievements, not just responsibilities

Return your response as a JSON object with this exact structure:
{{
  "original_text": "the original bullet point",
  "suggested_text": "your improved version",
  "explanation": "brief explanation of improvements",
  "impact": "high"
}}

Important: Return ONLY the JSON object, no additional text."""

        try:
            response = await self.client.messages.create(
                model=ClaudeConfig.MODEL,
                max_tokens=ClaudeConfig.MAX_TOKENS,
                temperature=ClaudeConfig.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            suggestion_data = json.loads(content)

            return [ContentSuggestion(
                section=f"experience_{index}",
                original_text=suggestion_data["original_text"],
                suggested_text=suggestion_data["suggested_text"],
                explanation=suggestion_data["explanation"],
                impact=suggestion_data.get("impact", "high")
            )]

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response for experience: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error analyzing experience: {str(e)}", exc_info=True)
            return []

    async def _analyze_skills(self, skills: List[Any]) -> List[ContentSuggestion]:
        """Analyze skills section and provide suggestions."""
        if not skills:
            return []

        # Format skills for analysis
        skills_text = []
        for skill_group in skills[:5]:  # Limit to first 5 skill groups
            if hasattr(skill_group, 'category') and hasattr(skill_group, 'skills'):
                category = skill_group.category or "General"
                skill_list = ", ".join(skill_group.skills[:10])  # Limit skills per category
                skills_text.append(f"{category}: {skill_list}")

        if not skills_text:
            return []

        skills_content = "\n".join(skills_text)

        if len(skills_content) > ClaudeConfig.MAX_TEXT_LENGTH:
            skills_content = skills_content[:ClaudeConfig.MAX_TEXT_LENGTH]

        prompt = f"""Analyze this resume skills section and provide ONE specific improvement suggestion.

Current Skills:
{skills_content}

Focus on:
1. Organization and categorization
2. Relevance and priority (put most important skills first)
3. Specificity (avoid vague terms)
4. Industry-standard terminology
5. Balance of technical and soft skills

Return your response as a JSON object with this exact structure:
{{
  "original_text": "describe current organization/issue",
  "suggested_text": "your specific recommendation",
  "explanation": "brief explanation of the improvement",
  "impact": "medium"
}}

Important: Return ONLY the JSON object, no additional text."""

        try:
            response = await self.client.messages.create(
                model=ClaudeConfig.MODEL,
                max_tokens=ClaudeConfig.MAX_TOKENS,
                temperature=ClaudeConfig.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            suggestion_data = json.loads(content)

            return [ContentSuggestion(
                section="skills",
                original_text=suggestion_data["original_text"],
                suggested_text=suggestion_data["suggested_text"],
                explanation=suggestion_data["explanation"],
                impact=suggestion_data.get("impact", "medium")
            )]

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response for skills: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error analyzing skills: {str(e)}", exc_info=True)
            return []

    async def improve_summary(self, summary: str) -> str:
        """
        Improve professional summary.

        Args:
            summary: Current professional summary

        Returns:
            Improved summary text
        """
        if not self._is_available():
            logger.warning("Claude API not available - returning original summary")
            return summary

        if not summary or len(summary.strip()) < 10:
            logger.warning("Summary too short or empty")
            return summary

        if len(summary) > ClaudeConfig.MAX_TEXT_LENGTH:
            summary = summary[:ClaudeConfig.MAX_TEXT_LENGTH]

        prompt = f"""Improve this professional resume summary. Make it more impactful, concise, and achievement-focused.

Current Summary:
{summary}

Requirements:
1. Keep it 2-3 sentences (50-80 words)
2. Start with your professional identity
3. Include 1-2 key achievements with metrics if possible
4. End with value proposition or career goals
5. Use active voice and strong action verbs
6. Make it compelling and specific

Return ONLY the improved summary text, nothing else."""

        try:
            response = await self.client.messages.create(
                model=ClaudeConfig.MODEL,
                max_tokens=500,
                temperature=ClaudeConfig.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            improved = response.content[0].text.strip()
            logger.info("Successfully improved summary")
            return improved

        except Exception as e:
            logger.error(f"Error improving summary: {str(e)}", exc_info=True)
            return summary

    async def improve_bullet_points(self, bullets: List[str]) -> List[str]:
        """
        Improve experience bullet points.

        Args:
            bullets: List of bullet points

        Returns:
            List of improved bullet points
        """
        if not self._is_available():
            logger.warning("Claude API not available - returning original bullets")
            return bullets

        if not bullets:
            return bullets

        # Limit to first 5 bullets to avoid token limits
        bullets_to_improve = bullets[:5]
        bullets_text = "\n".join(f"{i+1}. {bullet}" for i, bullet in enumerate(bullets_to_improve))

        if len(bullets_text) > ClaudeConfig.MAX_TEXT_LENGTH:
            bullets_text = bullets_text[:ClaudeConfig.MAX_TEXT_LENGTH]

        prompt = f"""Improve these resume bullet points. Make them more impactful and achievement-focused.

Current Bullet Points:
{bullets_text}

Requirements for each bullet:
1. Start with a strong action verb (past tense for previous roles)
2. Include specific metrics, percentages, or numbers
3. Follow format: "Action Verb + Task + Result/Impact"
4. Be concise (1-2 lines max)
5. Focus on achievements and outcomes, not just responsibilities

Return ONLY the improved bullet points as a numbered list (1., 2., 3., etc.), nothing else."""

        try:
            response = await self.client.messages.create(
                model=ClaudeConfig.MODEL,
                max_tokens=ClaudeConfig.MAX_TOKENS,
                temperature=ClaudeConfig.TEMPERATURE,
                messages=[{"role": "user", "content": prompt}]
            )

            improved_text = response.content[0].text.strip()

            # Parse the numbered list
            improved_bullets = []
            for line in improved_text.split('\n'):
                line = line.strip()
                if line:
                    # Remove numbering (1., 2., etc.) and bullet points (-, *, •)
                    cleaned = line
                    if line[0].isdigit() and '.' in line[:4]:
                        cleaned = line.split('.', 1)[1].strip()
                    elif line.startswith(('-', '*', '•')):
                        cleaned = line[1:].strip()

                    if cleaned:
                        improved_bullets.append(cleaned)

            # If we have improved bullets and they match the count, return them
            if improved_bullets and len(improved_bullets) == len(bullets_to_improve):
                logger.info(f"Successfully improved {len(improved_bullets)} bullet points")
                # If original had more bullets, append the remaining ones
                return improved_bullets + bullets[len(bullets_to_improve):]
            else:
                logger.warning("Bullet count mismatch, returning originals")
                return bullets

        except Exception as e:
            logger.error(f"Error improving bullet points: {str(e)}", exc_info=True)
            return bullets
