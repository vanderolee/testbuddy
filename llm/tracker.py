"""
Token usage and cost tracking module.
"""


class TokenTracker:
    """Track token usage, costs, and processing times for Claude API calls."""

    def __init__(self, input_price_per_million: float, output_price_per_million: float):
        """
        Initialize token tracker.

        Args:
            input_price_per_million: Cost per million input tokens (USD)
            output_price_per_million: Cost per million output tokens (USD)
        """
        self.input_price = input_price_per_million
        self.output_price = output_price_per_million

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.request_count = 0

        # Timing tracking
        self.total_processing_time = 0.0
        self.processing_times = []  # Store individual times for average calculation

    def add_request(self, input_tokens: int, output_tokens: int, processing_time: float = 0.0) -> None:
        """
        Record a new API request.

        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            processing_time: Time taken for API request in seconds
        """
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.request_count += 1

        if processing_time > 0:
            self.total_processing_time += processing_time
            self.processing_times.append(processing_time)

    def get_summary(self) -> dict:
        """
        Get usage summary.

        Returns:
            Dictionary with token counts, costs, and timing info
        """
        input_cost = (self.total_input_tokens / 1_000_000) * self.input_price
        output_cost = (self.total_output_tokens / 1_000_000) * self.output_price
        total_cost = input_cost + output_cost

        avg_processing_time = (
            self.total_processing_time / len(self.processing_times)
            if self.processing_times else 0.0
        )

        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "requests": self.request_count,
            "total_processing_time": self.total_processing_time,
            "avg_processing_time": avg_processing_time,
            "processing_times": self.processing_times
        }

    def get_formatted_summary(self) -> str:
        """
        Get formatted summary string for display.

        Returns:
            Human-readable summary string
        """
        summary = self.get_summary()

        return (
            f"Tokens: {summary['total_tokens']:,} "
            f"(In: {summary['input_tokens']:,} | Out: {summary['output_tokens']:,}) | "
            f"Cost: ${summary['total_cost']:.4f} | "
            f"Requests: {summary['requests']}"
        )

    def reset(self) -> None:
        """Reset all counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.request_count = 0
        self.total_processing_time = 0.0
        self.processing_times = []
