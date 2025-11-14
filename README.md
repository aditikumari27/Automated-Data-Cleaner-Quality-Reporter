<img width="793" height="1122" alt="image" src="https://github.com/user-attachments/assets/99a9bb6c-f5fe-4bce-9697-34e3e133ad9c" /># Automated Data Cleaner & Quality Reporter

## Setup (VS Code)

1. Open this folder in VS Code.
2. Create a Python virtual environment:
   - Windows:
     > python -m venv .venv
     > .venv\Scripts\activate
   - macOS / Linux:
     > python3 -m venv .venv
     > source .venv/bin/activate

3. Install dependencies:
   > pip install -r requirements.txt

4. Run the app:
   > python app.py

5. Open browser at:
   http://127.0.0.1:5000

6. Upload a CSV (try `sample_data.csv`) and choose a fill strategy. The app will:
   - analyze missing values, duplicates, and simple outliers
   - save cleaned CSV to `outputs/<id>/cleaned_data.csv`
   - save `summary.json` and `report.txt` in same folder
   - show download links on the result page

## Files
- `cleaner.py` : core functionality (load, detect, clean, output)
- `app.py` : Flask app
- `templates/index.html` : web UI
- `static/*` : CSS & JS
- `uploads/` : uploaded CSV files
- `outputs/` : cleaned outputs & reports

## How it maps to learning topics
See README in project for details of where each Python topic is used.

<img width="1692" height="775" alt="image" src="https://github.com/user-attachments/assets/e3795177-d216-4717-90fe-a9084388d1ee" />




