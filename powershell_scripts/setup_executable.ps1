try{

    Start-Sleep -s 3

    cd 'C:\Users\nick\Code\Python_Projects\bachelorarbeit_tom'

    Start-Sleep -s 3

    . 'C:\Users\nick\Code\Python_Projects\bachelorarbeit_tom\venv\Scripts\activate.ps1'

    Start-Sleep -s 3

    pyinstaller --onefile 'web_app/app.py' --paths='C:\Users\nick\Code\Python_Projects\bachelorarbeit_tom\modules' --paths='C:\Users\nick\Code\Python_Projects\bachelorarbeit_tom\web_app\templates' --collect-data='web_app.templates'
} catch {
    Read-Host -Prompt "The above error occurred. Press Enter to exit."
}