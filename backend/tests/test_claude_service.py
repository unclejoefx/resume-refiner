"""Tests for Claude API service."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from app.services.claude_service import ClaudeService, ClaudeConfig
from app.models.resume import ResumeContent, Experience, ContactInfo, Skill
from app.models.analysis import ContentSuggestion


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client."""
    with patch('app.services.claude_service.AsyncAnthropic') as mock_client:
        yield mock_client


@pytest.fixture
def sample_resume_content():
    """Create sample resume content for testing."""
    return ResumeContent(
        contact_info=ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890"
        ),
        summary="Experienced software engineer with 5 years of experience.",
        experience=[
            Experience(
                company="Tech Corp",
                position="Software Engineer",
                is_current=False,
                bullets=[
                    "Worked on projects",
                    "Fixed bugs",
                    "Attended meetings"
                ]
            )
        ],
        skills=[
            Skill(category="Programming", skills=["Python", "JavaScript", "Java"])
        ],
        raw_text="Resume text content"
    )


class TestClaudeServiceInitialization:
    """Test Claude service initialization."""

    def test_initialization_without_api_key(self):
        """Test that service handles missing API key gracefully."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = ""
            service = ClaudeService()
            assert service.client is None
            assert not service._is_available()

    def test_initialization_with_api_key(self, mock_anthropic_client):
        """Test that service initializes with API key."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"
            service = ClaudeService()
            assert service._is_available()


class TestAnalyzeContent:
    """Test content analysis functionality."""

    @pytest.mark.asyncio
    async def test_analyze_content_without_api_key(self, sample_resume_content):
        """Test that analyze_content returns empty list without API key."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = ""
            service = ClaudeService()
            suggestions = await service.analyze_content(sample_resume_content)
            assert suggestions == []

    @pytest.mark.asyncio
    async def test_analyze_content_with_summary(self, mock_anthropic_client, sample_resume_content):
        """Test content analysis with summary section."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            # Mock the API response
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps({
                "original_text": "Experienced software engineer with 5 years of experience.",
                "suggested_text": "Results-driven software engineer with 5 years of experience delivering scalable solutions that increased system performance by 40%.",
                "explanation": "Added specific metrics and impact",
                "impact": "high"
            })
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            suggestions = await service.analyze_content(sample_resume_content)

            assert len(suggestions) >= 1
            assert any(s.section == "summary" for s in suggestions)

    @pytest.mark.asyncio
    async def test_analyze_content_with_experience(self, mock_anthropic_client, sample_resume_content):
        """Test content analysis with experience section."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            # Mock multiple API responses (summary + experience)
            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps({
                "original_text": "Worked on projects",
                "suggested_text": "Architected and delivered 3 microservices handling 1M+ daily requests",
                "explanation": "Added specificity and metrics",
                "impact": "high"
            })
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            suggestions = await service.analyze_content(sample_resume_content)

            # Should have suggestions from experience
            assert len(suggestions) >= 1

    @pytest.mark.asyncio
    async def test_analyze_content_limits_suggestions(self, mock_anthropic_client, sample_resume_content):
        """Test that analyze_content limits total suggestions to 10."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            # Create content with many sections
            sample_resume_content.experience = [
                Experience(
                    company=f"Company {i}",
                    position="Engineer",
                    is_current=False,
                    bullets=["Did work"]
                )
                for i in range(15)
            ]

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = json.dumps({
                "original_text": "test",
                "suggested_text": "improved test",
                "explanation": "better",
                "impact": "high"
            })
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            suggestions = await service.analyze_content(sample_resume_content)

            # Should be limited to 10
            assert len(suggestions) <= 10

    @pytest.mark.asyncio
    async def test_analyze_content_handles_api_error(self, mock_anthropic_client, sample_resume_content):
        """Test that analyze_content handles API errors gracefully."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            suggestions = await service.analyze_content(sample_resume_content)

            # Should return empty list on error
            assert suggestions == []

    @pytest.mark.asyncio
    async def test_analyze_content_handles_json_parse_error(self, mock_anthropic_client, sample_resume_content):
        """Test that analyze_content handles malformed JSON responses."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Not valid JSON"
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            suggestions = await service.analyze_content(sample_resume_content)

            # Should handle gracefully
            assert isinstance(suggestions, list)


class TestImproveSummary:
    """Test summary improvement functionality."""

    @pytest.mark.asyncio
    async def test_improve_summary_without_api_key(self):
        """Test that improve_summary returns original without API key."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = ""
            service = ClaudeService()

            original = "Software engineer with experience."
            result = await service.improve_summary(original)
            assert result == original

    @pytest.mark.asyncio
    async def test_improve_summary_with_valid_input(self, mock_anthropic_client):
        """Test summary improvement with valid input."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Improved professional summary with metrics and achievements."
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            original = "Software engineer with experience."
            result = await service.improve_summary(original)

            assert result != original
            assert "Improved" in result

    @pytest.mark.asyncio
    async def test_improve_summary_with_empty_input(self):
        """Test that improve_summary handles empty input."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"
            service = ClaudeService()

            result = await service.improve_summary("")
            assert result == ""

    @pytest.mark.asyncio
    async def test_improve_summary_with_short_input(self):
        """Test that improve_summary handles very short input."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"
            service = ClaudeService()

            short_text = "Hi"
            result = await service.improve_summary(short_text)
            assert result == short_text

    @pytest.mark.asyncio
    async def test_improve_summary_truncates_long_input(self, mock_anthropic_client):
        """Test that improve_summary truncates very long input."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "Improved summary"
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()

            # Create text longer than MAX_TEXT_LENGTH
            long_text = "a" * (ClaudeConfig.MAX_TEXT_LENGTH + 1000)
            result = await service.improve_summary(long_text)

            # Should call API (text is truncated internally)
            mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_improve_summary_handles_api_error(self, mock_anthropic_client):
        """Test that improve_summary handles API errors."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            original = "Software engineer with experience."
            result = await service.improve_summary(original)

            # Should return original on error
            assert result == original


class TestImproveBulletPoints:
    """Test bullet point improvement functionality."""

    @pytest.mark.asyncio
    async def test_improve_bullet_points_without_api_key(self):
        """Test that improve_bullet_points returns original without API key."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = ""
            service = ClaudeService()

            bullets = ["Did work", "Fixed bugs"]
            result = await service.improve_bullet_points(bullets)
            assert result == bullets

    @pytest.mark.asyncio
    async def test_improve_bullet_points_with_valid_input(self, mock_anthropic_client):
        """Test bullet point improvement with valid input."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = """1. Architected and delivered microservices handling 1M+ requests
2. Resolved critical bugs reducing downtime by 95%"""
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            bullets = ["Did work", "Fixed bugs"]
            result = await service.improve_bullet_points(bullets)

            assert len(result) == 2
            assert result != bullets

    @pytest.mark.asyncio
    async def test_improve_bullet_points_with_empty_input(self):
        """Test that improve_bullet_points handles empty input."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"
            service = ClaudeService()

            result = await service.improve_bullet_points([])
            assert result == []

    @pytest.mark.asyncio
    async def test_improve_bullet_points_limits_to_five(self, mock_anthropic_client):
        """Test that improve_bullet_points only processes first 5 bullets."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "\n".join([f"{i}. Improved bullet {i}" for i in range(1, 6)])
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            bullets = [f"Bullet {i}" for i in range(10)]
            result = await service.improve_bullet_points(bullets)

            # Should return all 10, but only first 5 are improved
            assert len(result) == 10

    @pytest.mark.asyncio
    async def test_improve_bullet_points_handles_mismatch(self, mock_anthropic_client):
        """Test handling when API returns wrong number of bullets."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_response = Mock()
            mock_content = Mock()
            mock_content.text = "1. Only one bullet"
            mock_response.content = [mock_content]

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            bullets = ["Bullet 1", "Bullet 2", "Bullet 3"]
            result = await service.improve_bullet_points(bullets)

            # Should return original on mismatch
            assert result == bullets

    @pytest.mark.asyncio
    async def test_improve_bullet_points_handles_api_error(self, mock_anthropic_client):
        """Test that improve_bullet_points handles API errors."""
        with patch('app.services.claude_service.settings') as mock_settings:
            mock_settings.CLAUDE_API_KEY = "test-api-key"

            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
            mock_anthropic_client.return_value = mock_client

            service = ClaudeService()
            bullets = ["Bullet 1", "Bullet 2"]
            result = await service.improve_bullet_points(bullets)

            # Should return original on error
            assert result == bullets


class TestClaudeConfig:
    """Test Claude configuration constants."""

    def test_config_values(self):
        """Test that config values are set correctly."""
        assert ClaudeConfig.MODEL == "claude-3-5-sonnet-20241022"
        assert ClaudeConfig.MAX_TOKENS == 4096
        assert ClaudeConfig.TEMPERATURE == 0.7
        assert ClaudeConfig.TIMEOUT == 60.0
        assert ClaudeConfig.MAX_TEXT_LENGTH == 100000
