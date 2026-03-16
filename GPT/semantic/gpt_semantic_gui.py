"""Semantic plan preview UI.

Purpose:
- Renders the confirmation window with steps and Run/Copy/Cancel controls.
- Toggles the preview tag used by preview-only voice commands.

Called from:
- `GPT/semantic/gpt_semantic_runtime.py` via `show_preview()` / `hide_preview()`.
"""

import textwrap

from talon import Context, Module, actions, imgui, settings

from .gpt_semantic_state import GptSemanticState

mod = Module()
ctx = Context()


@imgui.open()
def semantic_preview(gui: imgui.GUI) -> None:
    _render_header(gui)
    _render_summary(gui)
    _render_steps(gui)
    _render_buttons(gui)


def show_preview() -> None:
    ctx.tags = ["user.gpt_semantic_preview_open"]
    semantic_preview.show()


def hide_preview() -> None:
    semantic_preview.hide()
    ctx.tags = []


def _render_header(gui: imgui.GUI) -> None:
    gui.text("Model semantic plan preview")
    gui.line()
    if GptSemanticState.pending_request:
        gui.text(f"Request: {GptSemanticState.pending_request}")


def _render_summary(gui: imgui.GUI) -> None:
    plan = GptSemanticState.pending_plan
    if plan is None or not plan.summary:
        return
    gui.spacer()
    gui.text(f"Summary: {plan.summary}")


def _render_steps(gui: imgui.GUI) -> None:
    plan = GptSemanticState.pending_plan
    if plan is None:
        return
    gui.spacer()
    width = settings.get("user.model_window_char_width")
    for index, step in enumerate(plan.steps, start=1):
        line = f"{index}. {step.action} {step.args}"
        for chunk in textwrap.wrap(line, width=width):
            gui.text(chunk)


def _render_buttons(gui: imgui.GUI) -> None:
    gui.spacer()
    if gui.button("Run plan"):
        actions.user.gpt_semantic_run_pending()
    gui.spacer()
    if gui.button("Copy plan"):
        actions.user.gpt_semantic_copy_pending()
    gui.spacer()
    if gui.button("Cancel plan"):
        actions.user.gpt_semantic_cancel_pending()
