import sys, os
sys.path.insert(0, r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统_FINAL")
os.chdir(r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统_FINAL")
from data_processor import DataProcessor
from visualizer import Visualizer
p = DataProcessor(r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统_FINAL\data").load_data()
p.compute_metrics()
p.compute_rfm()
v = Visualizer(p, r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统_FINAL\static\images")
v.generate_all()
from pdf_report import generate_pdf
generate_pdf(p, p.metrics, r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统_FINAL\report.pdf")
print("[OK] Initialization complete")
