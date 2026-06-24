# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import os, sys

# Find Chinese font
def _find_font():
    for f in fm.fontManager.ttflist:
        if "Microsoft YaHei" in f.name:
            return f.name
        if "SimHei" in f.name:
            return f.name
    return "sans-serif"
plt.rcParams["font.sans-serif"] = [_find_font()]
plt.rcParams["axes.unicode_minus"] = False

class Visualizer:
    def __init__(self, processor, output_dir):
        self.p = processor
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.charts = []
    
    def _save(self, fig, name):
        fp = os.path.join(self.output_dir, name)
        fig.savefig(fp, bbox_inches="tight", facecolor="white", dpi=130)
        plt.close(fig)
        self.charts.append(name)
        print(f"  Chart saved: {name}")
    
    def plot_daily_sales(self):
        daily = self.p.get_daily_sales()
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.plot(daily["date"], daily["gmv"], color="#2563EB", linewidth=1.5, alpha=0.85)
        ax.fill_between(daily["date"], daily["gmv"], alpha=0.1, color="#2563EB")
        ax.set_title("每日 GMV 趋势", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("日期"); ax.set_ylabel("GMV (元)")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        fig.autofmt_xdate()
        self._save(fig, "daily_sales.png")

    def plot_monthly_trend(self):
        monthly = self.p.get_monthly_trend()
        fig, ax1 = plt.subplots(figsize=(10, 4))
        bars = ax1.bar(monthly["order_month"], monthly["gmv"], color="#7C3AED", alpha=0.75, width=0.5, label="GMV")
        ax2 = ax1.twinx()
        ax2.plot(monthly["order_month"], monthly["orders"], "o-", color="#F59E0B", linewidth=2, label="订单量")
        ax1.set_title("月度 GMV 与订单量", fontsize=13, fontweight="bold", pad=10)
        ax1.set_ylabel("GMV (元)", color="#7C3AED"); ax2.set_ylabel("订单量", color="#F59E0B")
        ax1.tick_params(axis="y", labelcolor="#7C3AED"); ax2.tick_params(axis="y", labelcolor="#F59E0B")
        ax1.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
        lines1, labs1 = ax1.get_legend_handles_labels()
        lines2, labs2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2, labs1+labs2, loc="upper left", frameon=False)
        fig.autofmt_xdate()
        self._save(fig, "monthly_trend.png")

    def plot_category_gmv(self):
        cat = self.p.get_category_sales()
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Blues(np.linspace(0.3, 0.85, len(cat)))
        bars = ax.barh(cat["category"], cat["gmv"], color=colors, edgecolor="white")
        for bar, val in zip(bars, cat["gmv"]):
            ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2, f"{val:.0f}", va="center", fontsize=8)
        ax.set_title("各品类 GMV 排名", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("GMV (元)"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        self._save(fig, "category_gmv.png")

    def plot_payment_dist(self):
        pm = self.p.get_payment_stats()
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ["#2563EB","#7C3AED","#059669","#F59E0B"]
        wedges, texts, autotexts = ax.pie(pm["count"], labels=pm["payment_method"], autopct="%1.1f%%",
            colors=colors[:len(pm)], startangle=90, textprops={"fontsize":10})
        ax.set_title("支付方式分布", fontsize=13, fontweight="bold", pad=10)
        self._save(fig, "payment_dist.png")
    
    def plot_device_dist(self):
        dv = self.p.get_device_stats()
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ["#3B82F6","#8B5CF6","#10B981","#F59E0B"]
        wedges, texts, autotexts = ax.pie(dv["count"], labels=dv["device"], autopct="%1.1f%%",
            colors=colors[:len(dv)], startangle=90, textprops={"fontsize":10})
        ax.set_title("设备来源分布", fontsize=13, fontweight="bold", pad=10)
        self._save(fig, "device_dist.png")

    def plot_rfm_segments(self):
        seg = self.p.get_rfm_segment_summary()
        if seg is None:
            return
        fig, ax = plt.subplots(figsize=(8, 4))
        colors_map = {"高价值客户":"#DC2626","重要发展客户":"#2563EB","一般价值客户":"#059669","一般发展客户":"#F59E0B","流失客户":"#94A3B8"}
        bar_colors = [colors_map.get(s, "#94A3B8") for s in seg["segment"]]
        bars = ax.bar(seg["segment"], seg["count"], color=bar_colors, edgecolor="white", width=0.5)
        for bar, val in zip(bars, seg["count"]):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, str(val), ha="center", fontsize=10, fontweight="bold")
        ax.set_title("RFM 用户分层", fontsize=13, fontweight="bold", pad=10)
        ax.set_ylabel("用户数"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        fig.autofmt_xdate()
        self._save(fig, "rfm_segments.png")

    def plot_age_hist(self):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(self.p.users["age"], bins=15, color="#3B82F6", alpha=0.7, edgecolor="white")
        ax.axvline(x=self.p.users["age"].median(), color="#DC2626", linestyle="--", linewidth=1.5, label=f"中位年龄 {int(self.p.users['age'].median())}")
        ax.set_title("用户年龄分布", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("年龄"); ax.set_ylabel("人数"); ax.legend(frameon=False)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        self._save(fig, "age_dist.png")

    def generate_all(self):
        print("[Chart] 生成图表...")
        self.plot_daily_sales()
        self.plot_monthly_trend()
        self.plot_category_gmv()
        self.plot_payment_dist()
        self.plot_device_dist()
        self.plot_rfm_segments()
        self.plot_age_hist()
        return self.charts
