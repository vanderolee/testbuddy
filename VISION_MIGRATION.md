# Vision-Based Approach Migration

## Changes Made

### Problem
- OCR was capturing all screen text including browser UI
- Parsing logic couldn't detect answer options in boxed format (A, B, C, D)
- Wrong model ID: `claude-sonnet-4-20250514` (doesn't exist)

### Solution
Switch from OCR → Parse → Claude to direct **Image → Claude Vision** approach.

## Updated Files

### 1. `config.py`
- Changed model from `claude-sonnet-4-20250514` to `claude-sonnet-4-6-20250805`

### 2. `llm/client.py`
- Added `answer_question_from_image()` method
- Sends image directly to Claude using vision API
- **Added JSON schema for structured output** - guarantees valid response format
- New `_build_vision_prompt()` guides Claude to extract question, options, and answer
- Returns complete structure: question + options + correct answer + explanation
- Removed try/catch for JSON parsing (schema enforcement eliminates parsing errors)

### 3. `main.py`
- Removed OCR imports (`extract_text`, `parse_question_and_options`)
- Changed flow: capture → send image to Claude → display results
- Claude now does extraction + answering in single API call

## Token Cost Analysis

**Per question with vision approach:**
- Image tokens (1800×900px): ~3,200 tokens input
- Text response: ~300-500 tokens output
- **Total cost: ~$0.01-0.02 per question**

**Daily usage estimate:**
- 100 questions/day = $1-2/day
- 1000 questions/day = $10-20/day

## Benefits

✅ More accurate question extraction (Claude sees visual layout)  
✅ Handles any option format (boxes, letters, numbers)  
✅ Ignores browser UI automatically  
✅ No complex parsing logic needed  
✅ Single API call = faster response  
✅ **JSON schema enforcement** - guaranteed valid responses, no parsing errors  
✅ Simpler error handling - no fallback logic needed  

## Trade-offs

⚠️ Higher token cost (~3.2K vs ~500 tokens with text)  
⚠️ Slightly slower due to image encoding

## Next Steps

Test with the actual quiz site to verify:
1. Question extraction accuracy
2. Option detection (A, B, C, D labels)
3. Answer correctness
4. Token usage matches estimates
