@echo off
start "Flask 5000" cmd /k "python app.py --port 5000"
start "Flask 5001" cmd /k "python app.py --port 5001"
start "Flask 5002" cmd /k "python app.py --port 5002"
start "Flask 5003" cmd /k "python app.py --port 5003"