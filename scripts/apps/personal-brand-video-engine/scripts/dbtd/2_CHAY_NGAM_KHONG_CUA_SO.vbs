Set WshShell = CreateObject("WScript.Shell")
strDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strDir
' Tham số 0 = vbHide: Ẩn hoàn toàn cửa sổ dòng lệnh (CMD) và chạy Chrome ở chế độ Headless ngầm 100%
WshShell.Run "cmd /c node """ & strDir & "\bot_autopost.mjs"" --run", 0, False
Set WshShell = Nothing
