@echo off
REM Simple script to create virtualenv and launch Gradio interface
if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python gradio_app.py

