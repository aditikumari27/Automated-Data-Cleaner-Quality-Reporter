# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from cleaner import analyze_and_clean
from utils import allowed_file, make_unique_filename, ensure_dirs

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
OUTPUT_FOLDER = os.path.join(os.getcwd(), "outputs")
ensure_dirs(UPLOAD_FOLDER, OUTPUT_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.secret_key = "dev-secret-change-me"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if 'dataset' not in request.files:
        flash("No file part")
        return redirect(url_for('index'))
    file = request.files['dataset']
    if file.filename == '':
        flash("No selected file")
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        unique_name = make_unique_filename(file.filename)
        in_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(in_path)
        # chosen fill strategy from form
        fill_strategy = request.form.get('fill_strategy', 'auto')
        outdir_name = os.path.splitext(unique_name)[0]
        outdir = os.path.join(app.config['OUTPUT_FOLDER'], outdir_name)
        os.makedirs(outdir, exist_ok=True)
        result = analyze_and_clean(in_path, outdir, fill_strategy=fill_strategy)
        # provide links
        cleaned_rel = os.path.relpath(result['cleaned_csv'], start=os.getcwd())
        json_rel = os.path.relpath(result['json'], start=os.getcwd())
        txt_rel = os.path.relpath(result['txt'], start=os.getcwd())
        return render_template("index.html", success=True, cleaned=cleaned_rel, summary_json=json_rel, summary_txt=txt_rel, health=result['report'].get('health_score', None))
    else:
        flash("File type not allowed (use CSV)")
        return redirect(url_for('index'))

@app.route("/download/<path:filename>")
def download(filename):
    # filename is relative path from project root, e.g. outputs/<uid>_file/cleaned_data.csv
    fullpath = os.path.join(os.getcwd(), filename)
    folder = os.path.dirname(fullpath)
    fname = os.path.basename(fullpath)
    return send_from_directory(folder, fname, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
