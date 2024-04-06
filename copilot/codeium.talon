app: vscode
# You must manually enable this. By default we use Github Copilot for pilot commands
tag: user.codeium
-

## Commands for https://codeium.com/ extension

pilot (previous | last): user.vscode("editor.action.inlineSuggest.showPrevious")
pilot next: user.vscode("editor.action.inlineSuggest.showNext")

pilot yes: user.vscode("editor.action.inlineSuggest.commit")
pilot nope: user.vscode("editor.action.inlineSuggest.undo")

pilot chat [<user.prose>]:
    user.vscode("codeium.openChatView")
    sleep(2)
    user.paste(user.prose or "")

pilot toggle: user.vscode("codeium.toggleEnabledForCurrentLanguage")

# Submit the request from within a codeium request window
pilot submit: key(ctrl-shift-enter)

pilot make [<user.prose>]:
    user.vscode("codeium.openCodeiumCommand")
    sleep(0.7)
    user.paste(user.prose or "")

pilot search: user.vscode("codeium.openSearchView")
pilot explain: user.vscode("codeium.explainCodeBlock")
pilot debug: user.vscode("codeium.explainProblem")
pilot editor: user.vscode("codeium.openChatInPane")

pilot cancel: user.vscode("editor.action.inlineSuggest.hide")
pilot refactor: user.vscode("codeium.refactorCodeBlock")
