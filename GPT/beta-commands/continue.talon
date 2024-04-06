app: vscode
tag: user.gpt_beta
-

## Commands to interact with https://continue.dev/ extension

tin you new: user.vscode("continue.newSession")
tin you file select: user.vscode("continue.selectFilesAsContext")
tin you history: user.vscode("continue.viewHistory")
tin you (accept | yes): user.vscode("continue.acceptDiff")
tin you reject: user.vscode("continue.rejectDiff")
tin you toggle fullscreen: user.vscode("continue.toggleFullScreen")
tin you cancel: key("escape")
tin you debug terminal: user.vscode("continue.debugTerminal")
tin you add <user.cursorless_target>:
    user.cursorless_command("setSelection", cursorless_target)
    user.vscode("continue.focusContinueInput")
tin you edit <user.cursorless_target>:
    user.cursorless_command("setSelection", cursorless_target)
    user.vscode("continue.quickEdit")

bar tin you: user.vscode("continue.continueGUIView.focus")
