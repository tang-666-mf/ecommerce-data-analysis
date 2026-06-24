# 电商用户 & 销量数据分析可视化系统

## 技术栈
Python 3.12+ / Pandas / NumPy / Matplotlib / Flask / ReportLab

## 项目结构
- app.py — Flask Web 应用入口
- data_processor.py — 数据清洗 & 指标计算
- visualizer.py — 可视化模块 (7张图表)
- pdf_report.py — PDF 报告导出
- data/ — 数据集 (users, products, orders, behaviors)
- static/images/ — 图表文件
- templates/dashboard.html — Web 看板模板

## 启动方式
python app.py
## 访问 http://127.0.0.1:5000

## 核心功能
- 数据清洗：缺失值填充、异常数据剔除
- 指标计算：GMV、复购率、客单价、转化率
- RFM 用户分层：5级客户分类
- 7种可视化图表
- Web 看板 + PDF 一键导出

