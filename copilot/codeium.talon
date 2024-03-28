app: vscode
-

## Commands for https://codeium.com/ extension

codeium chat:               user.vscode("codeium.openChatView")

codeium toggle:             user.vscode("codeium.toggleEnabledForCurrentLanguage")

codeium submit:             key(ctrl-shift-enter)

codeium command:            user.vscode("codeium.openCodeiumCommand")

codeium search:             user.vscode("codeium.openSearchView")

codeium explain:            user.vscode("codeium.explainCodeBlock")

codeium debug:              user.vscode("codeium.explainProblem")

codeium editor:             user.vscode("codeium.openChatInPane")

codeium jest:               user.vscode("editor.action.inlineSuggest.trigger")
codeium next:               user.vscode("editor.action.inlineSuggest.showNext")
codeium (previous | last):  user.vscode("editor.action.inlineSuggest.showPrevious")
codeium yes:                user.vscode("editor.action.inlineSuggest.commit")
codium nope:                user.vscode("editor.action.inlineSuggest.undo")
codeium cancel:             user.vscode("editor.action.inlineSuggest.hide")

codeium refactor:           user.vscode("codeium.refactorCodeBlock")
