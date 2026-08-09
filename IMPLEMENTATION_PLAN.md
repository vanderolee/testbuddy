# TestBuddy Implementation Plan

## Overview
TestBuddy is a stealth AI assistant for online tests. It captures browser content, extracts questions via OCR, queries Claude with Knowledge Bank context, and displays answers in terminal on a second monitor.

## Detection Avoidance Strategy

### ✅ Undetectable Components
- macOS command-line screen capture (`screencapture`)
- Background Python processes
- Global hotkeys registered at OS level (via `pynput`)
- External API calls to Claude
- Terminal output on second monitor

### Implementation Principles
- Use OS-level capture (no screen recording permission needed)
- No window focus switching
- Generic process naming
- All output to terminal (second monitor)

## Project Structure

```
testbuddy/
├── .env                       # ANTHROPIC_API_KEY
├── config.py                  # Settings & hotkeys
├── main.py                    # Main loop
├── requirements.txt           # Dependencies
├── runs/                      # Session folders (YYYY_MM_DD_HH_MM_SS)
│   └── YYYY_MM_DD_HH_MM_SS/
│       ├── captures/          # Screenshot images
│       ├── questions.txt      # Extracted questions
│       ├── answers.txt        # LLM responses
│       └── session.log        # Debug logs
├── capture/
│   ├── __init__.py
│   ├── window_capture.py      # macOS window detection + screencapture
│   └── hotkey_listener.py     # Global hotkey management
├── ocr/
│   ├── __init__.py
│   └── extractor.py           # EasyOCR wrapper
├── llm/
│   ├── __init__.py
│   ├── client.py              # Claude SDK integration
│   └── tracker.py             # Token usage & cost tracking
├── knowledge_bank/
│   ├── __init__.py
│   ├── store.py               # ChromaDB wrapper
│   ├── retriever.py           # Semantic search
│   ├── data/                  # Raw KB files (PDF, DOCX, TXT, URLs)
│   ├── chroma_db/             # ChromaDB storage
│   └── converter/
│       ├── __init__.py
│       ├── base.py            # Base converter class
│       ├── pdf.py             # PyPDF2 + Claude summarization
│       ├── docx.py            # python-docx + Claude
│       ├── txt.py             # Direct text + Claude chunking
│       └── url.py             # BeautifulSoup + Claude
├── ui/
│   ├── __init__.py
│   └── terminal.py            # Colored terminal output
└── utils/
    ├── __init__.py
    └── logger.py              # Run folder creation & logging
```

## Dependencies

### Core Dependencies
```bash
pip install anthropic          # Claude SDK
pip install easyocr            # OCR library
pip install chromadb           # Vector database for Knowledge Bank
pip install pillow             # Image processing
pip install pyobjc-framework-Quartz  # macOS window detection
pip install pynput             # Global hotkey listener
pip install python-dotenv      # Environment variable management
```

### Knowledge Bank Dependencies
```bash
pip install pypdf2             # PDF processing
pip install python-docx        # DOCX processing
pip install beautifulsoup4     # Web scraping
pip install requests           # HTTP requests
```

### UI Dependencies
```bash
pip install rich               # Terminal formatting (or colorama)
```

## Configuration

### config.py
```python
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent
RUNS_DIR = PROJECT_ROOT / "runs"
KB_DIR = PROJECT_ROOT / "knowledge_bank" / "data"
KB_CHROMA_DIR = PROJECT_ROOT / "knowledge_bank" / "chroma_db"

# Hotkeys
TRIGGER_HOTKEY = "<cmd>+<shift>+<f1>"  # Capture screenshot
QUIT_HOTKEY = "<cmd>+<shift>+q"        # Exit application

# Capture Settings
CAPTURE_DELAY_MS = 500                 # Wait after hotkey before capture
TARGET_BROWSER = "Safari"              # "Safari", "Google Chrome", "Firefox", "Microsoft Edge"

# LLM Settings
MODEL = "claude-sonnet-4-20250514"     # Default model
MAX_TOKENS = 4096                      # Max response tokens
TEMPERATURE = 0.3                      # Lower = more deterministic

# Token Pricing (USD per million tokens)
INPUT_TOKEN_PRICE = 3.0
OUTPUT_TOKEN_PRICE = 15.0

# Knowledge Bank Settings
KB_ENABLED = True                      # Enable/disable Knowledge Bank
KB_TOP_K = 3                           # Number of relevant chunks to retrieve
KB_CHUNK_SIZE = 1000                   # Tokens per chunk for document conversion
KB_SUMMARIZATION_PROMPT = """
Extract and summarize ONLY the key information, important facts, and main concepts from this text.
Focus on information that would be relevant for answering test questions.
Remove fluff, examples, and redundant explanations.
Format as concise bullet points.
"""

# OCR Settings
OCR_LANGUAGES = ['en']                 # Language codes for EasyOCR
OCR_GPU = False                        # Use GPU acceleration (requires CUDA)

# Output Settings
OUTPUT_CLEAR_SCREEN = True             # Clear terminal before each answer
OUTPUT_WIDTH = 80                      # Terminal width for formatting
```

### .env
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## Implementation Phases

### Phase 1: Core Infrastructure
**Goal:** Basic capture → OCR → Claude pipeline (no Knowledge Bank)

#### Step 1.1: Project Setup
1. Create virtual environment
2. Install core dependencies
3. Create .env file with API key
4. Create basic config.py
5. Initialize git repository (add .env to .gitignore)

#### Step 1.2: Window Capture Module
**File:** `capture/window_capture.py`

**Functions:**
- `get_browser_window_bounds(browser_name: str) -> tuple[int, int, int, int]`
  - Uses `pyobjc` to find browser window without activating it
  - Returns (x, y, width, height)
  
- `capture_window(bounds: tuple, output_path: str) -> bool`
  - Uses `screencapture -R x,y,w,h output_path` command
  - Returns success status

**Testing:**
- Manually call function to capture browser window
- Verify screenshot saved correctly

#### Step 1.3: Hotkey Listener Module
**File:** `capture/hotkey_listener.py`

**Classes:**
- `HotkeyManager`
  - Registers global hotkeys with callbacks
  - Runs listener in background thread
  - Provides stop() method for cleanup

**Testing:**
- Register test hotkey, verify callback fires
- Verify browser remains focused during hotkey press

#### Step 1.4: OCR Module
**File:** `ocr/extractor.py`

**Functions:**
- `initialize_reader(languages: list) -> easyocr.Reader`
  - Initialize EasyOCR reader (cached)
  
- `extract_text(image_path: str) -> str`
  - Extract text from image
  - Return formatted text with confidence filtering

- `parse_question_and_options(text: str) -> dict`
  - Parse extracted text into structured format:
    ```python
    {
        "question": "What is...",
        "options": [
            {"label": "A", "text": "Paris"},
            {"label": "B", "text": "London"},
            ...
        ]
    }
    ```

**Testing:**
- Test on sample quiz screenshots
- Verify question/option parsing accuracy

#### Step 1.5: Claude Client Module
**File:** `llm/client.py`

**Classes:**
- `ClaudeClient`
  - Initialize with API key and model
  - `answer_question(question: dict, knowledge_context: str = "") -> dict`
    - Send question to Claude
    - Return structured answer:
      ```python
      {
          "correct_options": ["A", "C"],  # Multiple choice
          "explanation": "...",
          "input_tokens": 1234,
          "output_tokens": 567
      }
      ```

**Prompt Structure:**
```
You are an expert test-taking assistant. Analyze the question and options, then identify which option(s) are correct.

{knowledge_context}

Question: {question}

Options:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

Respond in JSON format:
{
  "correct_options": ["A"],
  "explanation": "Brief explanation"
}
```

**Testing:**
- Test with sample questions
- Verify JSON response parsing

#### Step 1.6: Token Tracker Module
**File:** `llm/tracker.py`

**Classes:**
- `TokenTracker`
  - Track session usage
  - Calculate costs
  - `add_request(input_tokens: int, output_tokens: int)`
  - `get_summary() -> dict` - returns total tokens and cost
  - `get_formatted_summary() -> str` - returns formatted string for terminal

**Testing:**
- Verify cost calculations
- Test reset functionality

#### Step 1.7: Logger & Run Management
**File:** `utils/logger.py`

**Functions:**
- `create_run_folder() -> Path`
  - Create timestamped folder in runs/
  - Create subfolders: captures/, logs/
  
- `setup_logger(run_folder: Path) -> logging.Logger`
  - Configure file and console logging
  
- `save_question(run_folder: Path, question_data: dict)`
  - Save question JSON to file
  
- `save_answer(run_folder: Path, answer_data: dict)`
  - Save answer JSON to file

#### Step 1.8: Terminal UI
**File:** `ui/terminal.py`

**Functions:**
- `clear_screen()`
- `print_header()`
- `print_question(question_data: dict)`
- `print_answer(question_data: dict, answer_data: dict)`
  - Format with ✓/✗ next to each option
- `print_token_summary(tracker: TokenTracker)`
- `print_waiting_message()`

**Output Format:**
```
═══════════════════════════════════════════════════════════
QUESTION:
What is the capital of France?

OPTIONS:
  ✓ A) Paris
  ✗ B) London
  ✗ C) Berlin
  ✗ D) Madrid

EXPLANATION:
Paris is the capital and largest city of France.

TOKENS: 1,234 | COST: $0.0123 | SESSION: $0.45
═══════════════════════════════════════════════════════════
Waiting for trigger... (Cmd+Shift+F1 to capture, Cmd+Shift+Q to quit)
```

#### Step 1.9: Main Application
**File:** `main.py`

**Flow:**
```python
1. Load configuration
2. Initialize components (OCR, Claude, Tracker, Logger)
3. Create run folder
4. Print welcome message with instructions
5. Setup hotkey listeners:
   - TRIGGER_HOTKEY: capture → ocr → claude → display → wait
   - QUIT_HOTKEY: cleanup and exit
6. Wait in loop
7. On exit: print session summary
```

**Testing:**
- Full end-to-end test with real browser
- Verify all files saved correctly
- Test quit functionality

### Phase 2: Knowledge Bank
**Goal:** Fast semantic search for relevant test materials

#### Step 2.1: ChromaDB Store
**File:** `knowledge_bank/store.py`

**Classes:**
- `KnowledgeStore`
  - Initialize ChromaDB collection
  - `add_document(text: str, metadata: dict, doc_id: str)`
  - `query(text: str, top_k: int) -> list[dict]`
    - Semantic search for relevant chunks
    - Return chunks with metadata and relevance scores
  - `clear()` - reset database
  - `count()` - return number of documents

**Testing:**
- Add sample documents
- Query and verify relevance ranking

#### Step 2.2: Retriever
**File:** `knowledge_bank/retriever.py`

**Classes:**
- `KnowledgeRetriever`
  - Wrapper around KnowledgeStore
  - `get_relevant_context(question: str, top_k: int) -> str`
    - Query store
    - Format results into context string for Claude
    - Include source metadata

**Context Format:**
```
Relevant information from Knowledge Bank:

[Source: study_guide.pdf, Topic: Geography]
- Paris is the capital of France, located in northern France on the Seine River
- France is divided into 18 administrative regions

[Source: lecture_notes.txt, Topic: European Capitals]
- Major European capitals include: Paris (France), London (UK), Berlin (Germany)
```

#### Step 2.3: Base Converter
**File:** `knowledge_bank/converter/base.py`

**Classes:**
- `BaseConverter` (abstract)
  - `extract_text(file_path: str) -> str`
  - `chunk_text(text: str, chunk_size: int) -> list[str]`
  - `summarize_chunk(chunk: str, claude_client: ClaudeClient) -> str`
    - Use Claude to extract key points from chunk
  - `process(file_path: str, claude_client: ClaudeClient) -> list[dict]`
    - Main pipeline: extract → chunk → summarize → return structured data

#### Step 2.4: Format-Specific Converters
**Files:** `knowledge_bank/converter/{pdf,docx,txt,url}.py`

Each implements `BaseConverter`:
- **PDFConverter**: Use PyPDF2 to extract text
- **DOCXConverter**: Use python-docx to extract text
- **TXTConverter**: Direct file read
- **URLConverter**: Use BeautifulSoup to scrape and extract main content

#### Step 2.5: CLI Tool for KB Management
**File:** `kb_manager.py` (separate script)

**Commands:**
```bash
# Add documents to Knowledge Bank
python kb_manager.py add --file study_guide.pdf --topic "Geography"
python kb_manager.py add --url https://example.com/notes --topic "History"

# List all documents
python kb_manager.py list

# Clear Knowledge Bank
python kb_manager.py clear

# Test query
python kb_manager.py query "What is the capital of France?"
```

**Testing:**
- Add various document formats
- Verify summarization quality
- Test retrieval accuracy

#### Step 2.6: Integration with Main Application
**Modifications to `main.py`:**
- Initialize KnowledgeRetriever if KB_ENABLED
- Before calling Claude, retrieve relevant context
- Pass context to `answer_question()`

**Testing:**
- Add test materials to KB
- Verify relevant context retrieved and used
- Compare answer quality with/without KB

### Phase 3: Polish & Error Handling
**Goal:** Production-ready error handling and UX improvements

#### Step 3.1: Error Handling
- Retry logic for OCR failures
- Handle Claude API errors (rate limits, network issues)
- Graceful degradation if KB unavailable
- Validate configuration on startup

#### Step 3.2: Performance Optimization
- Cache EasyOCR reader initialization
- Parallel processing (capture + previous question processing)
- Monitor and log processing time per step
- Target: <15s total per question

#### Step 3.3: Configuration Validation
- Verify API key on startup
- Check browser availability
- Validate hotkey format
- Check file permissions for runs/ folder

#### Step 3.4: Documentation
- Update README.md with setup instructions
- Document hotkey configuration
- Add troubleshooting guide
- Include example screenshots

## Implementation Order

### Sprint 1: Basic Pipeline (No KB)
1. Project setup + dependencies
2. window_capture.py
3. extractor.py
4. client.py + tracker.py
5. logger.py
6. terminal.py
7. main.py (basic loop)
8. **Milestone:** Can capture browser, extract question, get Claude answer

### Sprint 2: Knowledge Bank
1. store.py (ChromaDB)
2. retriever.py
3. base.py + txt.py (start with simplest format)
4. kb_manager.py CLI tool
5. Integrate with main.py
6. pdf.py, docx.py, url.py
7. **Milestone:** Can query KB and use context in answers

### Sprint 3: Polish
1. Error handling across all modules
2. Performance monitoring
3. Configuration validation
4. Documentation
5. **Milestone:** Production-ready MVP

## Testing Strategy

### Unit Tests
- OCR text parsing
- Question/option extraction
- Token cost calculations
- KB retrieval ranking

### Integration Tests
- Full pipeline with mock images
- KB query → Claude → answer flow
- Error scenarios (missing files, API failures)

### Manual Tests
- Real browser capture
- Various quiz formats
- KB with real study materials
- Performance under time pressure

## Success Criteria

- ✅ Undetectable by browser JavaScript
- ✅ <15s processing time per question
- ✅ Accurate OCR (>90% for clear text)
- ✅ Relevant KB context retrieved
- ✅ Clear terminal output with correct answers marked
- ✅ Session tracking and cost estimation
- ✅ Stable operation for full test duration (no crashes)

## Future Enhancements (Post-MVP)

### V1.1 Features
- Support for image-based questions (Claude Vision API)
- LaTeX/equation support
- Multiple KB profiles (switch between test subjects)
- Answer confidence scoring
- Statistics dashboard (accuracy tracking)

### V1.2 Features
- Prompt caching for frequently used KB content
- Cross-platform support (Windows, Linux)
- Web interface alternative to terminal
- Batch question mode (upload screenshot folder)

### V2.0 Features
- Real-time answer highlighting overlay (optional, higher risk)
- Voice output for answers
- Mobile device integration
- Cloud KB synchronization

## Risk Mitigation

### Technical Risks
- **OCR accuracy**: Test with multiple quiz formats early
- **API rate limits**: Implement exponential backoff
- **KB size**: Monitor ChromaDB performance with large datasets
- **Processing time**: Profile and optimize bottlenecks

### Detection Risks
- **Process enumeration**: Use generic naming
- **Screen recording API**: Use CLI capture only
- **Focus detection**: Never switch window focus
- **Timing patterns**: Add human-like delays (future)

## Notes

- All timestamps in filename format: YYYY_MM_DD_HH_MM_SS
- Session folders in runs/ preserved for manual review/debugging
- Configuration changes don't require code modifications
- KB can be completely disabled via config if not needed
- Terminal output designed for second monitor viewing
- No GUI dependencies for maximum compatibility
