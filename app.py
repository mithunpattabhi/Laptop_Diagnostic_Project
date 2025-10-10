import os
import io
import joblib
import pandas as pd
from flask import Flask, render_template, request, redirect, send_file, flash
from werkzeug.utils import secure_filename
from fpdf import FPDF
import matplotlib.pyplot as plt
import re

app = Flask(__name__)
app.secret_key = "diagnostic_secret"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"csv"}

model = joblib.load(open("model/hardware_health_model.pkl", "rb"))
scaler = joblib.load(open("model/scaler.pkl", "rb"))

healthy_df = pd.read_csv("Healthy.csv")
FEATURES = [
    "Core Temperatures (avg) [°C]",
    "CPU Core [°C]",
    "CPU Package Power [W]",
    "Total CPU Utility [%]",
    "GPU Temperature [°C]",
    "GPU Hot Spot Temperature [°C]",
    "GPU Power [W]",
    "GPU Utilization [%]",
    "GPU Memory Usage [%]",
    "Physical Memory Load [%]",
    "Virtual Memory Load [%]",
    "Charge Level [%]",
    "Wear Level [%]",
    "GPU Bus Load [%]",
    "Framerate Displayed (avg) [FPS]",
    "Frame Time Presented (avg) [ms]"
]

def extract_numeric(series):
    return pd.to_numeric(series.astype(str).str.extract(r'([-+]?\d*\.?\d+)')[0], errors='coerce')

for col in FEATURES:
    if col in healthy_df.columns:
        healthy_df[col] = extract_numeric(healthy_df[col])

baseline_mean = healthy_df.mean()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

def normalize_name(name):
    return re.sub(r'[^a-z0-9]', '', str(name).lower())

def create_summary_pdf(result_text, user_data, baseline_data, notes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Laptop Health Diagnostic Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=result_text)
    pdf.ln(10)

    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Key Metrics:", ln=True)
    pdf.set_font("Arial", size=11)
    for col, val in user_data.items():
        pdf.cell(0, 8, f"{col}: {val:.2f}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, "Analysis Notes:", ln=True)
    pdf.set_font("Arial", size=11)
    if notes:
        for note in notes:
            pdf.multi_cell(0, 8, f"- {note}")
    else:
        pdf.multi_cell(0, 8, "All metrics are within healthy ranges.")

    metrics_to_plot = ["CPU Core [°C]", "GPU Temperature [°C]", "Physical Memory Load [%]", "GPU Utilization [%]"]
    values = [user_data[m] for m in metrics_to_plot]
    baseline_values = [baseline_data[m] for m in metrics_to_plot]

    plt.figure(figsize=(6,4))
    x = range(len(metrics_to_plot))
    plt.bar([i-0.15 for i in x], baseline_values, width=0.3, label="Healthy")
    plt.bar([i+0.15 for i in x], values, width=0.3, label="Your System")
    plt.xticks(x, metrics_to_plot, rotation=15, fontsize=8)
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    graph_path = "graph.png"
    plt.savefig(graph_path)
    plt.close()

    pdf.image(graph_path, x=10, y=None, w=180)

    file = io.BytesIO(pdf.output(dest="S").encode("latin1"))
    return file

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file uploaded.", "danger")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("Please select a file.", "danger")
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash("Unsupported file format. Please upload CSV from HWInfo.", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath, encoding='latin1', skiprows=0)

            df_columns_norm = {normalize_name(c): c for c in df.columns}
            FEATURES_NORM = {normalize_name(f): f for f in FEATURES}

            predict_df = pd.DataFrame()
            for f_norm, f_orig in FEATURES_NORM.items():
                if f_norm in df_columns_norm:
                    col_name = df_columns_norm[f_norm]
                    predict_df[f_orig] = extract_numeric(df[col_name])
                else:
                    predict_df[f_orig] = 0  

            df_mean = predict_df.mean().to_frame().T.fillna(0)


            notes = []
            for feature in FEATURES:
                user_val = df_mean[feature].values[0]
                baseline_val = baseline_mean.get(feature, 0)
                if baseline_val > 0 and abs(user_val - baseline_val)/baseline_val > 0.1:
                    notes.append(f"{feature} deviates from healthy value ({baseline_val:.2f}). Current: {user_val:.2f}")

            scaled = scaler.transform(df_mean)
            pred = model.predict(scaled)[0]

            result_text = "Your laptop appears to be Healthy!" if pred == 0 else "Your laptop shows signs of abnormal performance!"
            summary = create_summary_pdf(result_text, df_mean.iloc[0], baseline_mean, notes)
            os.remove(filepath)

            flash(result_text, "success" if pred==0 else "danger")
            return send_file(summary, as_attachment=True, download_name="diagnostic_report.pdf")
        

        except Exception as e:
            flash(f"Error processing file: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
