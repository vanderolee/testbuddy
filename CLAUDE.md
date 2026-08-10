# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TestBuddy is an AI-powered assistant for online tests and quizzes. It captures screen content, recognizes questions and answer options, and provides answers based on Claude's knowledge and a custom Knowledge Bank.

**Key Components:**
- Screen/browser capture module with hotkey trigger
- Claude Vision API for question extraction and answering
- Claude SDK integration (Sonnet model)
- Token usage tracking and cost estimation
- Processing time tracking (per-question and session average)
- Knowledge Bank system (planned for future implementation)

## Development Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run the application
python main.py  # or python -m testbuddy
```

## Architecture

### Core Flow
1. **Capture**: User selects browser/screen area, triggers capture via configurable hotkey
2. **Vision Processing**: Send screenshot directly to Claude Vision API
3. **Extraction & Analysis**: Claude extracts question, options, and provides answer (single API call)
4. **Display**: Show answer with explanation to user
5. **Repeat**: Wait for next trigger or quit command

### Key Design Decisions

**Vision-Based Approach**: 
- Send screenshots directly to Claude Vision API
- Single API call extracts question, options, and provides answer
- JSON schema enforcement for reliable structured output
- No separate OCR library needed

**Token Optimization**: 
- Questions processed individually without persistent context history
- Display real-time token count and cost after each request
- Estimated ~3,200 input tokens per screenshot

**Screen Capture**:
- Target browsers: Safari, Chrome, Edge, Firefox
- Alternative: Screen area selection

## Implementation Notes

- Use Claude SDK with Sonnet 4.6 model (`claude-sonnet-4-6-20250805`)
- Vision API with JSON schema for structured output
- Implement token-saving best practices (no conversation history accumulation)
- Track and display session token usage and cost estimation in real-time
- Knowledge Bank planned for future implementation

## Testing

When tests are added:
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_capture.py

# Run with coverage
pytest --cov=testbuddy
```
