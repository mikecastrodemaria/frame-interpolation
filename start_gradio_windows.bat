@echo off
REM Simple script to create virtualenv and launch Gradio interface
REM Requires Python 3.10 or newer (see WINDOWS_INSTALLATION.md)

if not exist .venv (
    py -3.10 -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python gradio_app.py

