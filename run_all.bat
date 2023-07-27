@echo off
start "User managament Service" "cmd /k python users\users.py"
start "Template and Phishsite Service" "cmd /k python templates_phishsite\controllers.py"
start "MailFunction Service" "cmd /k python mailfunc\mailfunc.py"
start "Phishing Service" "cmd /k python phishs\phishing.py" 
start "Summary Service" "cmd /k python summary\summary.py"
start "Worker:1" "cmd /k python _worker\main.py 0.0.0.0 8080 helloworld 1"
@REM start "CloudFlared Tunnel" cmd /k cloudflared tunnel --url http://localhost:8080