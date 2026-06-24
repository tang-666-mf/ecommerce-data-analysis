# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os

def generate_pdf(processor, metrics, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
        topMargin=15*mm, bottomMargin=15*mm, leftMargin=15*mm, rightMargin=15*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=20, spaceAfter=10,
        textColor=HexColor("#1E3A5F"))
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=14, spaceBefore=12, spaceAfter=6,
        textColor=HexColor("#2563EB"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=4,
        textColor=HexColor("#475569"))
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=14, spaceAfter=4)
    
    story = []
    story.append(Paragraph("电商数据分析报告", title_style))
    story.append(Spacer(1, 6*mm))
    
    # Overview
    story.append(Paragraph("一、核心指标概览", h1))
    data = [
        ["总GMV", f"{metrics['total_gmv']:,.2f}元", "总订单数", str(metrics['total_orders'])],
        ["已完成订单", str(metrics['completed_orders']), "总用户数", str(metrics['total_users'])],
        ["客单价(AOV)", f"{metrics['aov']:.2f}元", "复购率", f"{metrics['repeat_purchase_rate']}%"],
        ["转化率", f"{metrics['conversion_rate']}%", "购买用户", str(metrics['buying_users'])],
    ]
    t = Table(data, colWidths=[60*mm, 50*mm, 50*mm, 50*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HexColor("#2563EB")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#F1F5F9"), colors.white]),
    ]))
    story.append(t)
    story.append(Spacer(1, 4*mm))
    
    # Charts
    chart_dir = os.path.join(os.path.dirname(output_path), "static", "images")
    charts = [
        ("二、销量趋势分析", "daily_sales.png"),
        ("三、品类 GMV 排名", "category_gmv.png"),
        ("四、支付方式分布", "payment_dist.png"),
        ("五、用户年龄分布", "age_dist.png"),
        ("六、RFM 用户分层", "rfm_segments.png"),
    ]
    for title, chart_name in charts:
        story.append(Paragraph(title, h1))
        img_path = os.path.join(chart_dir, chart_name)
        if os.path.exists(img_path):
            img = Image(img_path, width=160*mm, height=70*mm)
            story.append(img)
        story.append(Spacer(1, 3*mm))
    
    doc.build(story)
    print(f"[PDF] 报告已生成: {output_path}")
