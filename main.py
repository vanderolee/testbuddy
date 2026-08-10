#!/usr/bin/env python3
"""
TestBuddy - AI-powered test assistant
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from capture.window_capture import capture_browser
from capture.hotkey_listener import HotkeyManager
from llm.client import ClaudeClient
from llm.tracker import TokenTracker
from utils.logger import create_run_folder, setup_logger, save_combined
from ui.terminal import (
    print_welcome,
    print_processing,
    print_answer,
    print_token_summary,
    print_waiting_message,
    print_error,
    clear_screen
)


class TestBuddy:
    """Main application class."""

    def __init__(self):
        """Initialize TestBuddy application."""
        # Load environment variables
        load_dotenv()

        # Validate API key
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            print_error("ANTHROPIC_API_KEY not found in .env file")
            sys.exit(1)

        # Create run folder
        self.run_folder = create_run_folder(config.RUNS_DIR)

        # Setup logger
        self.logger = setup_logger(self.run_folder)
        self.logger.info(f"Starting TestBuddy session in {self.run_folder}")

        # Initialize components
        self.claude = ClaudeClient(
            api_key=self.api_key,
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE
        )

        self.tracker = TokenTracker(
            input_price_per_million=config.INPUT_TOKEN_PRICE,
            output_price_per_million=config.OUTPUT_TOKEN_PRICE
        )

        self.hotkey_manager = HotkeyManager()

        # State
        self.capture_count = 0
        self.is_running = True

    def handle_capture(self):
        """Handle screenshot capture and processing."""
        try:
            self.capture_count += 1
            self.logger.info(f"Capture #{self.capture_count} triggered")

            # Show processing message
            print_processing()

            # Capture screenshot
            capture_path = self.run_folder / "captures" / f"capture_{self.capture_count:03d}.png"
            success = capture_browser(
                browser_name=config.TARGET_BROWSER,
                output_path=str(capture_path),
                delay_ms=config.CAPTURE_DELAY_MS
            )

            if not success:
                print_error(f"Failed to capture {config.TARGET_BROWSER} window. Make sure it's open.")
                self.logger.error("Capture failed")
                print_waiting_message(config.TRIGGER_HOTKEY, config.QUIT_HOTKEY)
                return

            self.logger.info(f"Screenshot saved: {capture_path}")

            # Send image directly to Claude with vision
            # This extracts question, options, and answer in one step
            answer_data = self.claude.answer_question_from_image(str(capture_path))
            self.logger.info(f"Got answer: {answer_data}")

            # Extract question data for display
            question_data = {
                'question': answer_data.get('question', ''),
                'options': answer_data.get('options', [])
            }

            if not question_data.get('question'):
                print_error("Could not extract question from image. Try capturing again.")
                self.logger.warning("No question extracted")
                print_waiting_message(config.TRIGGER_HOTKEY, config.QUIT_HOTKEY)
                return

            # Track tokens
            self.tracker.add_request(
                answer_data.get('input_tokens', 0),
                answer_data.get('output_tokens', 0)
            )

            # Save data
            save_combined(self.run_folder, question_data, answer_data, self.capture_count)

            # Display results
            if config.OUTPUT_CLEAR_SCREEN:
                clear_screen()

            print_answer(question_data, answer_data)

            # Show token summary
            summary = self.tracker.get_summary()
            request_tokens = {
                'input_tokens': answer_data.get('input_tokens', 0),
                'output_tokens': answer_data.get('output_tokens', 0)
            }
            print_token_summary(summary, request_tokens)

            # Show waiting message
            print_waiting_message(config.TRIGGER_HOTKEY, config.QUIT_HOTKEY)

        except Exception as e:
            self.logger.exception(f"Error processing capture: {e}")
            print_error(f"Processing failed: {str(e)}")
            print_waiting_message(config.TRIGGER_HOTKEY, config.QUIT_HOTKEY)

    def handle_quit(self):
        """Handle quit command."""
        self.logger.info("Quit command received")
        self.is_running = False
        self.hotkey_manager.stop()

        # Print session summary
        summary = self.tracker.get_summary()
        print("\n" + "=" * 80)
        print(f"Session ended: {self.capture_count} questions processed")
        print(f"Total tokens: {summary['total_tokens']:,}")
        print(f"Total cost: ${summary['total_cost']:.4f}")
        print(f"Session saved to: {self.run_folder}")
        print("=" * 80)

    def run(self):
        """Start the application."""
        # Print welcome
        print_welcome(config.TRIGGER_HOTKEY, config.QUIT_HOTKEY, config.TARGET_BROWSER)

        # Register hotkeys
        self.hotkey_manager.register(config.TRIGGER_HOTKEY, self.handle_capture)
        self.hotkey_manager.register(config.QUIT_HOTKEY, self.handle_quit)

        # Start listening
        self.hotkey_manager.start()
        self.logger.info("Hotkey listener started")

        # Wait until quit
        try:
            self.hotkey_manager.wait()
        except KeyboardInterrupt:
            self.handle_quit()


def main():
    """Entry point."""
    app = TestBuddy()
    app.run()


if __name__ == "__main__":
    main()
