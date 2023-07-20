@echo off
start "User managament Service" "users\users.py"
start "Template and Phishsite Service" "templates_phishsite\controllers.py"
start "MailFunction Service" "mailfunc\mailfunc.py"
start "Phishing Service" "phishs\phishing.py" 
start "Worker:1" "_worker\main.py" 0.0.0.0 8080 helloworld 1