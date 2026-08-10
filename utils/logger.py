"""
Logging and run folder management utilities.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict


def create_run_folder(runs_dir: Path) -> Path:
    """
    Create a timestamped run folder with subfolders.

    Args:
        runs_dir: Base runs directory

    Returns:
        Path to created run folder
    """
    # Create timestamp
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    run_folder = runs_dir / timestamp

    # Create folder structure
    run_folder.mkdir(parents=True, exist_ok=True)
    (run_folder / "captures").mkdir(exist_ok=True)

    return run_folder


def setup_logger(run_folder: Path, name: str = "testbuddy") -> logging.Logger:
    """
    Configure logging to file and console.

    Args:
        run_folder: Run folder path
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # File handler
    log_file = run_folder / "session.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler (minimal output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def save_question(run_folder: Path, question_data: Dict, capture_num: int) -> None:
    """
    Save question data to file.

    Args:
        run_folder: Run folder path
        question_data: Question dictionary
        capture_num: Capture sequence number
    """
    output_file = run_folder / f"question_{capture_num:03d}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(question_data, f, indent=2, ensure_ascii=False)


def save_answer(run_folder: Path, answer_data: Dict, capture_num: int) -> None:
    """
    Save answer data to file.

    Args:
        run_folder: Run folder path
        answer_data: Answer dictionary
        capture_num: Capture sequence number
    """
    output_file = run_folder / f"answer_{capture_num:03d}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(answer_data, f, indent=2, ensure_ascii=False)


def save_combined(run_folder: Path, question_data: Dict, answer_data: Dict, capture_num: int) -> None:
    """
    Save combined question and answer to single file.

    Args:
        run_folder: Run folder path
        question_data: Question dictionary
        answer_data: Answer dictionary
        capture_num: Capture sequence number
    """
    combined = {
        "question": question_data,
        "answer": answer_data,
        "timestamp": datetime.now().isoformat()
    }

    output_file = run_folder / f"qa_{capture_num:03d}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
