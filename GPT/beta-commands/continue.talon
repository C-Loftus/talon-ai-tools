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
tin you share: user.vscode("continue.shareSession")
tin you select files: user.vscode("continue.selectFilesAsContext")
tin you add <user.cursorless_target>:
    user.cursorless_ide_command("continue.focusContinueInput", cursorless_target)
tin you edit <user.cursorless_target>:
    user.cursorless_ide_command("continue.quickEdit", cursorless_target)

tin you dock <user.cursorless_target>:
    user.cursorless_ide_command("continue.writeDocstringForCode", cursorless_target)

tin you comment <user.cursorless_target>:
    user.cursorless_ide_command("continue.writeCommentsForCode", cursorless_target)

tin you optimize <user.cursorless_target>:
    user.cursorless_ide_command("continue.optimizeCode", cursorless_target)

tin you fix code <user.cursorless_target>:
    user.cursorless_ide_command("continue.fixCode", cursorless_target)

tin you fix grammar <user.cursorless_target>:
    user.cursorless_ide_command("continue.fixGrammar", cursorless_target)

bar tin you: user.vscode("continue.continueGUIView.focus")
