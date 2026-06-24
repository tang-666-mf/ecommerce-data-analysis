import sys, os
sys.path.insert(0, r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统")
os.chdir(r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统")
from data_processor import DataProcessor
from visualizer import Visualizer
p = DataProcessor(r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统\data").load_data()
p.compute_metrics()
p.compute_rfm()
v = Visualizer(p, r"C:\Users\Y'T'L'~1\AppData\Local\Temp\电商数据分析系统\static\images")
v.generate_all()
print("All charts generated OK")
