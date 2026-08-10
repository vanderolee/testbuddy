# TestBuddy

AI-powered assistant for online tests. Captures browser content, recognizes questions, and provides answers using Claude AI.

## Features

- **Stealth Operation**: 100% undetectable by browsers (no extensions, no DOM access)
- **OCR Recognition**: Extracts questions and options from screenshots
- **Claude Integration**: Powered by Claude Sonnet 4 for accurate answers
- **Token Optimization**: Minimal token usage with no conversation history
- **Cost Tracking**: Real-time token and cost monitoring
- **Session Logging**: All captures and answers saved for review

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy example .env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_key_here
```

### 3. Configure Settings

Edit `config.py` to customize:
- Target browser (Safari, Chrome, Firefox, Edge)
- Hotkeys
- Model settings
- OCR language

## Usage

### Start TestBuddy

```bash
python main.py
```

### Controls

- **Cmd+Shift+F1**: Capture browser window and get answer
- **Cmd+Shift+Q**: Quit application

### Workflow

1. Open your test in the target browser
2. Start TestBuddy in a terminal (preferably on second monitor)
3. When you see a question, press **Cmd+Shift+F1**
4. TestBuddy will:
   - Capture the browser window
   - Extract question and options via OCR
   - Query Claude for the answer
   - Display marked options and explanation
5. Repeat for each question

## Configuration

### `config.py` Key Settings

```python
# Browser to capture
TARGET_BROWSER = "Safari"  # or "Google Chrome", "Firefox", "Microsoft Edge"

# Hotkeys
TRIGGER_HOTKEY = "<cmd>+<shift>+<f1>"  # Capture
QUIT_HOTKEY = "<cmd>+<shift>+q"        # Quit

# Model
MODEL = "claude-sonnet-4-20250514"     # Claude model
```

## Output

All session data is saved to timestamped folders in `runs/`:

```
runs/YYYY_MM_DD_HH_MM_SS/
├── captures/          # Screenshot images
│   ├── capture_001.png
│   ├── capture_002.png
│   └── ...
├── qa_001.json        # Question + Answer data
├── qa_002.json
└── session.log        # Debug logs
```

## Token Usage

TestBuddy is optimized for minimal token consumption:
- **No conversation history**: Each question is independent
- **Focused prompts**: Only question and options sent to Claude
- **Real-time tracking**: Cost displayed after each request

Example costs (Claude Sonnet 4):
- Simple question: ~$0.01-0.02 per answer
- With Knowledge Bank context: ~$0.02-0.04 per answer

## Requirements

- macOS (uses Quartz for window detection)
- Python 3.8+
- Anthropic API key
- Target browser installed

## Detection Avoidance

TestBuddy is designed to be completely undetectable:

✅ **Safe**:
- Uses macOS command-line screen capture
- No browser extensions or plugins
- No JavaScript injection
- No window focus changes
- All processing external to browser

❌ **Not detectable by**:
- Browser JavaScript
- Proctoring software (with proper setup)
- Window focus detection
- Process enumeration (generic Python process)

## Troubleshooting

### "Failed to capture window"
- Ensure target browser is open and visible
- Check browser name in `config.py` matches exactly
- Try different browsers

### "Could not extract question"
- Question might not be clearly visible in capture
- Try adjusting browser window size
- Check OCR language setting in `config.py`

### API Errors
- Verify `ANTHROPIC_API_KEY` in `.env` file
- Check API key has sufficient credits
- Ensure internet connection is stable

## Phase 1 Status

✅ **Implemented**:
- Window capture (macOS)
- Global hotkey listener
- OCR text extraction
- Question/option parsing
- Claude client integration
- Token tracking and cost estimation
- Terminal UI with colored output
- Session logging and data persistence

⏳ **Coming in Phase 2** (Knowledge Bank):
- Document ingestion (PDF, DOCX, TXT, URLs)
- Vector database storage (ChromaDB)
- Semantic search for relevant context
- Topic-based organization

## License

For educational purposes only.
