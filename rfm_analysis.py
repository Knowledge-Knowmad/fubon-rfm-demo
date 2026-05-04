"""RFM 顧客分群分析

資料：customer_segmentation_cleaned.csv（已清理過的零售交易資料）
產出：
  - rfm_customers.csv：每位顧客的 R/F/M 數值、分數、分群
  - segment_summary.csv：每個分群的人數與貢獻指標
  - segment_counts.png：分群人數長條圖
  - rf_heatmap.png：R × F 熱圖（顏色=平均 Monetary）
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
CSV_PATH = HERE / "customer_segmentation_cleaned.csv"

# ----------------------------------------------------------------------
# 1. 讀取資料
# ----------------------------------------------------------------------
df = pd.read_csv(CSV_PATH, low_memory=False)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
print(f"原始資料：{len(df):,} 列，{df['CustomerID'].nunique():,} 位顧客")
print(f"日期區間：{df['InvoiceDate'].min().date()} ~ {df['InvoiceDate'].max().date()}")

# ----------------------------------------------------------------------
# 2. 過濾 — 標準 RFM 清理
#    - CustomerID 不可為空（無記名銷售無法歸屬）
#    - Quantity > 0（去掉退貨）
#    - UnitPrice > 0（去掉手調帳）
# ----------------------------------------------------------------------
clean = df[
    df["CustomerID"].notna()
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
].copy()
clean["CustomerID"] = clean["CustomerID"].astype(int)
clean["LineTotal"] = clean["Quantity"] * clean["UnitPrice"]
print(f"清理後：{len(clean):,} 列，{clean['CustomerID'].nunique():,} 位顧客")

# ----------------------------------------------------------------------
# 3. 計算 R / F / M
# ----------------------------------------------------------------------
snapshot = clean["InvoiceDate"].max() + pd.Timedelta(days=1)
print(f"快照日（snapshot）：{snapshot.date()}")

rfm = clean.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda s: (snapshot - s.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("LineTotal", "sum"),
).reset_index()
print(f"RFM 表：{len(rfm):,} 位顧客")
print(rfm.describe().round(2))

# ----------------------------------------------------------------------
# 4. 5 等分計分
#    - Recency 越小越好 → 反向給分
#    - Frequency / Monetary 越大越好 → 正向給分
#    用 rank(method='first') 避開 qcut 在大量重複值（特別是 Frequency=1）時失敗的坑
# ----------------------------------------------------------------------
def quintile(series: pd.Series, ascending: bool) -> pd.Series:
    """以 rank 切五等分，確保不會因 ties 變成空 bin。"""
    ranked = series.rank(method="first", ascending=ascending)
    return pd.qcut(ranked, q=5, labels=[1, 2, 3, 4, 5]).astype(int)

rfm["R_score"] = quintile(rfm["Recency"], ascending=False)   # 越近越高分
rfm["F_score"] = quintile(rfm["Frequency"], ascending=True)
rfm["M_score"] = quintile(rfm["Monetary"], ascending=True)
rfm["RFM_score"] = (
    rfm["R_score"].astype(str) + rfm["F_score"].astype(str) + rfm["M_score"].astype(str)
)

# ----------------------------------------------------------------------
# 5. 命名分群
# ----------------------------------------------------------------------
def segment(row) -> str:
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"          # 最近買、常買、貢獻高
    if r >= 3 and f >= 3:
        return "Loyal"              # 忠誠
    if r >= 4 and f <= 2:
        return "New"                # 新客（最近才出現）
    if r >= 3 and f <= 2:
        return "Promising"          # 潛力
    if r <= 2 and f >= 4:
        return "At Risk"            # 高價值但快流失
    if r <= 2 and f >= 3:
        return "Need Attention"     # 中等忠誠但變冷
    if r == 1 and f <= 2:
        return "Lost"               # 流失
    return "Hibernating"            # 沉睡

rfm["Segment"] = rfm.apply(segment, axis=1)

# ----------------------------------------------------------------------
# 6. 分群摘要
# ----------------------------------------------------------------------
summary = rfm.groupby("Segment").agg(
    Customers=("CustomerID", "count"),
    Avg_Recency=("Recency", "mean"),
    Avg_Frequency=("Frequency", "mean"),
    Avg_Monetary=("Monetary", "mean"),
    Total_Monetary=("Monetary", "sum"),
).round(2).sort_values("Total_Monetary", ascending=False)
summary["Customer_Pct"] = (summary["Customers"] / summary["Customers"].sum() * 100).round(1)
summary["Revenue_Pct"] = (summary["Total_Monetary"] / summary["Total_Monetary"].sum() * 100).round(1)
print("\n=== 分群摘要 ===")
print(summary)

# ----------------------------------------------------------------------
# 7. 輸出 CSV
# ----------------------------------------------------------------------
rfm.to_csv(HERE / "rfm_customers.csv", index=False)
summary.to_csv(HERE / "segment_summary.csv")
print(f"\n已輸出：rfm_customers.csv / segment_summary.csv")

# ----------------------------------------------------------------------
# 8. 視覺化
# ----------------------------------------------------------------------
plt.rcParams["font.family"] = ["Heiti TC", "PingFang TC", "Arial Unicode MS", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

# (a) 分群人數長條圖
fig, ax = plt.subplots(figsize=(10, 5))
ordered = summary.sort_values("Customers", ascending=True)
ax.barh(ordered.index, ordered["Customers"], color="#4C78A8")
for y, (count, pct) in enumerate(zip(ordered["Customers"], ordered["Customer_Pct"])):
    ax.text(count, y, f"  {count:,} ({pct}%)", va="center", fontsize=9)
ax.set_xlabel("Customers")
ax.set_title("RFM Segments — Customer Count")
fig.tight_layout()
fig.savefig(HERE / "segment_counts.png", dpi=120)
plt.close(fig)

# (b) R × F 熱圖（顏色=平均 Monetary，數字=人數）
pivot_count = rfm.pivot_table(index="R_score", columns="F_score", values="CustomerID", aggfunc="count").fillna(0)
pivot_money = rfm.pivot_table(index="R_score", columns="F_score", values="Monetary", aggfunc="mean").fillna(0)

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(pivot_money.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(pivot_money.columns)))
ax.set_xticklabels(pivot_money.columns)
ax.set_yticks(range(len(pivot_money.index)))
ax.set_yticklabels(pivot_money.index)
ax.set_xlabel("F score (low → high)")
ax.set_ylabel("R score (low → high)")
ax.set_title("R × F heatmap — color = avg Monetary, label = customers")
for i in range(pivot_count.shape[0]):
    for j in range(pivot_count.shape[1]):
        ax.text(j, i, f"{int(pivot_count.values[i, j])}", ha="center", va="center", fontsize=9)
fig.colorbar(im, ax=ax, label="Avg Monetary")
fig.tight_layout()
fig.savefig(HERE / "rf_heatmap.png", dpi=120)
plt.close(fig)
print("已輸出：segment_counts.png / rf_heatmap.png")
