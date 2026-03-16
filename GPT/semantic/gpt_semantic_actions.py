"""Public Talon actions for semantic planning and execution.

Purpose:
- Exposes `user.gpt_semantic_*` actions used by Talon voice commands.

Called from:
- `GPT/semantic/gpt_semantic.talon`
- `GPT/semantic/gpt_semantic_preview.talon`
"""

from talon import Module

from .gpt_semantic_runtime import GptSemanticRuntime

mod = Module()


@mod.action_class
class UserActions:
    def gpt_semantic_generate(text: str, model: str) -> None:
        """Generate a semantic plan from spoken text and open preview."""
        GptSemanticRuntime.generate(text, model)

    def gpt_semantic_run_pending() -> None:
        """Execute the currently previewed semantic plan."""
        GptSemanticRuntime.run_pending()

    def gpt_semantic_cancel_pending() -> None:
        """Cancel and discard the currently previewed semantic plan."""
        GptSemanticRuntime.cancel_pending()

    def gpt_semantic_copy_pending() -> None:
        """Copy the currently previewed semantic plan JSON to clipboard."""
        GptSemanticRuntime.copy_pending()

    def gpt_semantic_repeat_last() -> None:
        """Re-open the last confirmed semantic plan in preview mode."""
        GptSemanticRuntime.repeat_last()
