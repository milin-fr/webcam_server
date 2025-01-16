call .\flask\virtual_env\Scripts\activate.bat
git pull
pip install -r .\flask\requirements.txt
python .\flask\app.py
pause