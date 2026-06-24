# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os, json

class DataProcessor:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.users = None
        self.orders = None
        self.products = None
        self.behaviors = None
        self.metrics = {}
        self.rfm_df = None
        
    def load_data(self):
        self.users = pd.read_csv(os.path.join(self.data_dir, "users.csv"))
        self.orders = pd.read_csv(os.path.join(self.data_dir, "orders.csv"))
        self.products = pd.read_csv(os.path.join(self.data_dir, "products.csv"))
        self.behaviors = pd.read_csv(os.path.join(self.data_dir, "behaviors.csv"))
        self._clean()
        return self
    
    def _clean(self):
        # Fill missing ages with median
        self.users["age"] = self.users["age"].fillna(self.users["age"].median()).astype(int)
        # Remove negative prices
        self.products = self.products[self.products["price"] > 0]
        # Filter valid orders only
        self.orders = self.orders[self.orders["order_status"].isin(["已完成","已取消","已退款"])]
        # Parse dates
        self.orders["order_date_dt"] = pd.to_datetime(self.orders["order_date"])
        self.orders["order_date"] = self.orders["order_date_dt"].dt.date
        self.orders["order_month"] = self.orders["order_date_dt"].dt.to_period("M").astype(str)
        print("[OK] 数据清洗完成")

    def compute_metrics(self):
        df = self.orders.copy()
        # GMV
        total_gmv = df["total_amount"].sum()
        avg_order_value = df["total_amount"].mean()
        
        # By status
        completed = df[df["order_status"] == "已完成"]
        total_revenue = completed["total_amount"].sum()
        
        # 复购率 = 多次购买用户 / 总购买用户
        buy_counts = df[df["order_status"]=="已完成"].groupby("user_id")["order_id"].nunique()
        repeat_ratio = (buy_counts > 1).sum() / len(buy_counts) if len(buy_counts) > 0 else 0
        
        # 客单价
        aov = completed["total_amount"].mean()
        
        # 流量转化率 = 购买行为 / 总行为
        if len(self.behaviors) > 0:
            conv = len(self.behaviors[self.behaviors["behavior_type"]=="购买"]) / len(self.behaviors)
        else:
            conv = 0
        
        self.metrics = {
            "total_orders": int(len(df)),
            "completed_orders": int(len(completed)),
            "total_gmv": round(total_gmv, 2),
            "total_revenue": round(total_revenue, 2),
            "avg_order_value": round(avg_order_value, 2),
            "aov": round(aov, 2),
            "repeat_purchase_rate": round(repeat_ratio * 100, 2),
            "conversion_rate": round(conv * 100, 2),
            "total_users": int(self.users["user_id"].nunique()),
            "buying_users": int(buy_counts.shape[0]),
            "total_products": int(len(self.products))
        }
        return self.metrics

    def compute_rfm(self):
        """RFM用户分层"""
        now = pd.to_datetime("today")
        df = self.orders[self.orders["order_status"]=="已完成"].copy()
        if len(df) == 0:
            return None
        df["order_dt"] = pd.to_datetime(df["order_date"])
        
        rfm = df.groupby("user_id").agg(
            recency=("order_dt", lambda x: (now - x.max()).days),
            frequency=("order_id", "count"),
            monetary=("total_amount", "sum")
        ).reset_index()
        
        # 分箱打分 (1-5)
        rfm["R"] = pd.qcut(rfm["recency"], 5, labels=[5,4,3,2,1]).astype(int)
        rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
        rfm["M"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
        rfm["RFM_Score"] = rfm["R"] + rfm["F"] + rfm["M"]
        
        # 分层
        def segment(row):
            s = row["RFM_Score"]
            if s >= 13: return "高价值客户"
            elif s >= 10: return "重要发展客户"
            elif s >= 7: return "一般价值客户"
            elif s >= 4: return "一般发展客户"
            else: return "流失客户"
        rfm["segment"] = rfm.apply(segment, axis=1)
        
        # 合并用户信息
        rfm = rfm.merge(self.users[["user_id","gender","age","city","vip_level"]], on="user_id", how="left")
        self.rfm_df = rfm
        return rfm

    def get_daily_sales(self):
        df = self.orders[self.orders["order_status"]=="已完成"].copy()
        df["date"] = pd.to_datetime(df["order_date"])
        daily = df.groupby("date").agg(gmv=("total_amount","sum"), orders=("order_id","count")).reset_index()
        daily = daily.sort_values("date")
        return daily
    
    def get_category_sales(self):
        df = self.orders[self.orders["order_status"]=="已完成"].copy()
        # Explode products
        rows = []
        for _, row in df.iterrows():
            for pid in map(int, str(row["products"]).split(",")):
                rows.append({"order_id":row["order_id"],"product_id":pid,"total_amount":row["total_amount"]})
        exploded = pd.DataFrame(rows)
        merged = exploded.merge(self.products[["product_id","category"]], on="product_id", how="left")
        cat_stats = merged.groupby("category").agg(gmv=("total_amount","sum"), orders=("order_id","nunique")).reset_index()
        return cat_stats.sort_values("gmv", ascending=False)
    
    def get_payment_stats(self):
        return self.orders["payment_method"].value_counts().reset_index()
    
    def get_device_stats(self):
        return self.behaviors["device"].value_counts().reset_index()
    
    def get_monthly_trend(self):
        df = self.orders[self.orders["order_status"]=="已完成"].copy()
        monthly = df.groupby("order_month").agg(gmv=("total_amount","sum"), orders=("order_id","count")).reset_index()
        monthly = monthly.sort_values("order_month")
        return monthly

    def get_rfm_segment_summary(self):
        if self.rfm_df is None:
            return None
        return self.rfm_df.groupby("segment").agg(
            count=("user_id","count"),
            avg_recency=("recency","mean"),
            avg_frequency=("frequency","mean"),
            avg_monetary=("monetary","mean")
        ).round(2).reset_index()
