# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TestBuddy is an AI-powered assistant for online tests and quizzes. It captures screen content, recognizes questions and answer options, and provides answers based on Claude's knowledge and a custom Knowledge Bank.

**Key Components:**
- Screen/browser capture module with hotkey trigger
- OCR/image recognition for question extraction
- Claude SDK integration (default: Sonnet model)
- Knowledge Bank system for test-specific materials
- Answer generation with confidence scoring
- Token usage tracking and cost estimation

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
2. **Recognition**: Extract question and answer options from captured image
3. **Query**: Send to Claude with Knowledge Bank context
4. **Display**: Show answer with confidence level to user
5. **Repeat**: Wait for next trigger or quit command

### Key Design Decisions

**Token Optimization**: 
- Questions processed individually without persistent context history
- Minimize conversation history to reduce token usage
- Display real-time token count and cost after each request

**Knowledge Bank**:
- Store extracted key points, not full documents
- Support formats: PDF, DOCX, TXT, URLs
- Structure entries for efficient retrieval

**Screen Capture**:
- Target browsers: Safari, Chrome, Edge, Firefox
- Alternative: Screen area selection

## Implementation Notes

- Use Claude SDK with Sonnet as default model
- Implement token-saving best practices (no conversation history accumulation)
- Track and display session token usage and cost estimation in real-time
- Knowledge Bank module should extract and store only relevant information, not full content

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
