# RFM 顧客分群分析｜知識遊牧 × 富邦 Fu+ Demo

> 用 53 萬筆零售交易找出「誰是 VIP、誰快流失、誰可以喚回」。
> 富邦 Fu+ 2026.05「AI 實用技巧：Excel 也能自動化分析」講座 demo。

🌐 **線上 Demo**：https://knowledge-knowmad.github.io/fubon-rfm-demo/

## 內容

| 檔案 | 說明 |
|---|---|
| `index.html` | 單頁報告（圖片以 base64 內嵌，可離線開啟） |
| `rfm_analysis.py` | 從 CSV 讀檔 → 清理 → 計算 R/F/M → 分群 → 出圖 |
| `build_report.py` | 由分析結果產生 `index.html`（採用知識遊牧 brand 設計系統） |
| `segment_summary.csv` | 八個分群的人數、平均 RFM、營收貢獻 |
| `rfm_customers.csv` | 每位顧客的 R/F/M 數值、分數、所屬分群 |
| `segment_counts.png` / `rf_heatmap.png` | 分析輸出的圖表 |

## 重新跑

```bash
# 把 customer_segmentation_cleaned.csv 放在這個資料夾
python3 rfm_analysis.py    # 產生 segment_summary.csv / rfm_customers.csv / *.png
python3 build_report.py    # 產生 index.html
open index.html
```

## 資料來源

UK Online Retail 公開資料集（2010-12 ~ 2011-12，53 萬筆交易），原始 CSV 因尺寸與隱私因素**不收錄於此 repo**。

## 方法

1. **Recency** — 快照日 (2011-12-10) 減去最後購買日
2. **Frequency** — 不重複發票數
3. **Monetary** — Quantity × UnitPrice 加總
4. **Scoring** — 對 R/F/M 各別 `rank → qcut(5)`，避開大量 ties 造成空 bin
5. **Segmentation** — 以 R、F 為主軸切八群（Champions / Loyal / At Risk / Need Attention / Promising / New / Hibernating / Lost）

## 主要發現

不到 ¼ 的顧客（22%）貢獻了 65% 的營收 — 經典 Pareto 80/20。守住 Champions、喚回 At Risk 是 ROI 最高的兩件事。

---

© [知識遊牧工作室](https://www.knowmad.tw) ｜ Knowmad
