# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, send_file
import os, sys, json, io

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from data_processor import DataProcessor
from visualizer import Visualizer

app = Flask(__name__)



# Init
processor = DataProcessor(os.path.join(BASE, "data")).load_data()
metrics = processor.compute_metrics()
processor.compute_rfm()
os.makedirs(os.path.join(BASE, "static", "images"), exist_ok=True)
viz = Visualizer(processor, os.path.join(BASE, "static", "images"))
viz.generate_all()

@app.route("/")
def index():
    return render_template("dashboard.html", metrics=metrics)

@app.route("/api/metrics")
def api_metrics():
    return jsonify(metrics)

@app.route("/api/rfm")
def api_rfm():
    rfm = processor.rfm_df
    if rfm is None:
        return jsonify([])
    return jsonify(rfm.head(100).to_dict(orient="records"))

@app.route("/api/daily_sales")
def api_daily_sales():
    daily = processor.get_daily_sales()
    return jsonify(daily.to_dict(orient="records"))

@app.route("/api/category_sales")
def api_category_sales():
    cat = processor.get_category_sales()
    return jsonify(cat.to_dict(orient="records"))

@app.route("/api/segment_summary")
def api_segment_summary():
    seg = processor.get_rfm_segment_summary()
    if seg is None:
        return jsonify([])
    return jsonify(seg.to_dict(orient="records"))

@app.route("/charts/<name>")
def chart(name):
    return send_file(os.path.join(BASE, "static", "images", name))

@app.route("/report/pdf")
def report_pdf():
    """Generate and download PDF report"""
    try:
        from pdf_report import generate_pdf
        pdf_path = os.path.join(BASE, "report.pdf")
        generate_pdf(processor, metrics, pdf_path)
        return send_file(pdf_path, as_attachment=True, download_name="电商分析报告.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"[启动] 访问 http://127.0.0.1:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)





