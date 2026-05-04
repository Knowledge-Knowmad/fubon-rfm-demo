"""產生 RFM 分析的單頁 HTML 報告，採用知識遊牧 (Knowmad) brand 設計系統。
所有圖片以 base64 內嵌，產出單一 index.html 可直接部署。
"""

import base64
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
SUMMARY = pd.read_csv(HERE / "segment_summary.csv")


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


SEGMENT_DESC = {
    "Champions":      ("VIP 維繫、口碑大使",     "#233363"),
    "Loyal":          ("升級至 Champions",        "#2E7EA6"),
    "At Risk":        ("高價值喚回（重點！）",   "#E85444"),
    "Need Attention": ("個人化優惠刺激",          "#0e78a4"),
    "Promising":      ("引導第二次購買",          "#4A9CBF"),
    "New":            ("歡迎旅程、首單追加",      "#888888"),
    "Hibernating":    ("低成本喚醒",              "#5a5a5a"),
    "Lost":           ("多半放生",                "#494949"),
}

# KPIs
total_customers = int(SUMMARY["Customers"].sum())
total_revenue = float(SUMMARY["Total_Monetary"].sum())
champ = SUMMARY[SUMMARY["Segment"] == "Champions"].iloc[0]
champ_rev_pct = float(champ["Revenue_Pct"])
champ_cust_pct = float(champ["Customer_Pct"])
date_min, date_max = "2010-12-01", "2011-12-09"

rows_html = ""
for _, r in SUMMARY.iterrows():
    seg = r["Segment"]
    desc, color = SEGMENT_DESC.get(seg, ("—", "#888"))
    rows_html += f"""
    <tr>
      <td><span class="dot" style="background:{color}"></span><b>{seg}</b></td>
      <td class="num">{int(r['Customers']):,}</td>
      <td class="num">{r['Customer_Pct']:.1f}%</td>
      <td class="num">{r['Avg_Recency']:.0f} 天</td>
      <td class="num">{r['Avg_Frequency']:.1f}</td>
      <td class="num">${r['Avg_Monetary']:,.0f}</td>
      <td class="num">${r['Total_Monetary']:,.0f}</td>
      <td class="num"><b>{r['Revenue_Pct']:.1f}%</b></td>
      <td>{desc}</td>
    </tr>"""

logo_h_b64 = b64(HERE / "logo-horizontal.png")
logo_sq_b64 = b64(HERE / "logo-square.png")
seg_counts_b64 = b64(HERE / "segment_counts.png")
heatmap_b64 = b64(HERE / "rf_heatmap.png")

html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RFM 顧客分群分析 ｜ 知識遊牧 × 富邦 Fu+</title>
<link rel="icon" type="image/png" href="data:image/png;base64,{logo_sq_b64}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Roboto:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --primary: #233363;
    --primary-link: #0e78a4;
    --primary-mid: #2E7EA6;
    --primary-light: #4A9CBF;
    --text: #202220;
    --text-secondary: #5a5a5a;
    --bg: #FFFFFF;
    --bg-alt: rgba(0,0,0,0.05);
    --bg-inv: #494949;
    --fg-alt: #f6f6f6;
    --alert: #E85444;
    --gray-300: #BBBBBB;
    --line: rgba(0,0,0,0.08);

    --font-zh: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
    --font-en: "Roboto", system-ui, sans-serif;
    --font-mono: "JetBrains Mono", ui-monospace, monospace;

    --section-py: clamp(3rem, 7vw, 5rem);
    --container: 1120px;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-en), var(--font-zh);
    color: var(--text); background: var(--bg);
    font-size: 16px; line-height: 1.7;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{ max-width: var(--container); margin: 0 auto; padding: 0 24px; }}

  /* ===== Nav ===== */
  nav.top {{
    position: sticky; top: 0; z-index: 50;
    background: rgba(255,255,255,0.92);
    backdrop-filter: saturate(140%) blur(8px);
    border-bottom: 1px solid var(--line);
  }}
  nav.top .row {{ display:flex; align-items:center; justify-content: space-between; height: 64px; }}
  nav.top img {{ height: 32px; display:block; }}
  nav.top .links {{ display: flex; gap: 24px; font-size: 14px; color: var(--text-secondary); }}
  nav.top .links a {{ color: inherit; text-decoration: none; }}
  nav.top .links a:hover {{ color: var(--primary-link); }}

  /* ===== Hero (dark section per brand guideline) ===== */
  .hero {{
    position: relative; overflow: hidden; color: #fff;
    padding: clamp(4rem, 9vw, 7rem) 24px clamp(4rem, 9vw, 7rem);
    background:
      radial-gradient(ellipse 70% 60% at 50% 0%, rgba(74,156,191,0.35) 0%, transparent 65%),
      radial-gradient(ellipse 50% 40% at 50% 100%, rgba(46,126,166,0.28) 0%, transparent 70%),
      linear-gradient(180deg, #1a274a 0%, #233363 55%, #2a3d76 100%);
  }}
  .hero::before {{
    content: ""; position: absolute; inset: 0; pointer-events: none;
    background-image:
      linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
    background-size: 48px 48px;
    -webkit-mask-image: radial-gradient(ellipse at center, black 35%, transparent 78%);
            mask-image: radial-gradient(ellipse at center, black 35%, transparent 78%);
  }}
  .hero .inner {{ position: relative; max-width: var(--container); margin: 0 auto; text-align: center; }}
  .hero .logo-mark {{
    width: 72px; height: 72px; margin: 0 auto 20px;
    filter: drop-shadow(0 12px 32px rgba(0,0,0,0.35));
    border-radius: 8px; background: #fff; padding: 8px;
  }}
  .eyebrow {{
    font-family: var(--font-mono);
    font-size: 12px; font-weight: 500; letter-spacing: 3px; text-transform: uppercase;
    color: rgba(246,246,246,0.6); margin-bottom: 18px;
  }}
  h1.hero-title {{
    font-family: var(--font-zh); font-weight: 700;
    font-size: clamp(36px, 5.4vw, 60px); line-height: 1.1; letter-spacing: -0.5px;
    margin: 0 0 18px;
  }}
  .hero-sub {{
    font-size: clamp(17px, 2.1vw, 22px); line-height: 1.6;
    color: rgba(246,246,246,0.82); max-width: 680px; margin: 0 auto 24px;
  }}
  .chips {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 14px; }}
  .chip {{
    font-size: 14px; padding: 6px 14px; border-radius: 9999px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.16);
    backdrop-filter: blur(4px);
    color: rgba(246,246,246,0.85);
  }}

  /* ===== Sections ===== */
  section {{ padding: var(--section-py) 0; }}
  section.alt {{ background: var(--bg-alt); }}
  h2 {{
    font-family: var(--font-zh); font-weight: 600;
    font-size: 32px; line-height: 1.3;
    color: var(--text); margin: 0 0 24px;
  }}
  h2 .num {{
    display:inline-block; width:34px; height:34px; line-height:34px;
    text-align:center; border-radius: 9999px;
    background: var(--primary); color:#fff; font-size:16px;
    margin-right: 12px; vertical-align: 4px;
  }}
  .lead {{ font-size: 18px; color: var(--text-secondary); max-width: 720px; margin: 0 0 32px; }}

  /* ===== KPI cards ===== */
  .kpis {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
  .kpi {{
    background: #fff; border: 1px solid var(--line); border-radius: 8px;
    padding: 24px; transition: transform .15s ease, box-shadow .15s ease;
  }}
  .kpi:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(35,51,99,0.08); }}
  .kpi .label {{ font-size: 14px; color: var(--text-secondary); }}
  .kpi .value {{ font-size: 36px; font-weight: 700; color: var(--text); margin-top: 4px; line-height: 1.2; }}
  .kpi .value.accent {{ color: var(--primary); }}
  .kpi .delta {{ font-size: 13px; color: var(--text-secondary); margin-top: 6px; }}

  .callout {{
    background: #fff; border-left: 4px solid var(--primary);
    padding: 18px 22px; border-radius: 4px; margin: 24px 0 0;
    box-shadow: 0 4px 16px rgba(35,51,99,0.06);
  }}
  .callout b {{ color: var(--primary); }}

  /* ===== Table ===== */
  .table-wrap {{
    background: #fff; border: 1px solid var(--line); border-radius: 8px; overflow: hidden;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  thead th {{
    background: var(--primary); color: #fff;
    font-family: var(--font-zh); font-weight: 600;
    font-size: 13px; letter-spacing: 0.04em;
    padding: 14px 12px; text-align: left;
  }}
  tbody td {{ padding: 14px 12px; border-bottom: 1px solid var(--line); vertical-align: middle; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: rgba(35,51,99,0.03); }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; font-family: var(--font-en); }}
  .dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:10px; vertical-align: middle; }}

  /* ===== Charts ===== */
  .charts {{ display: grid; gap: 20px; grid-template-columns: 1fr; }}
  @media (min-width: 900px) {{ .charts {{ grid-template-columns: 1.1fr .9fr; }} }}
  .chart-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 20px;
  }}
  .chart-card img {{ width: 100%; height: auto; border-radius: 4px; }}
  .chart-card .cap {{ font-size: 14px; color: var(--text-secondary); margin-top: 10px; }}

  /* ===== Method ===== */
  .method-grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
  .method-card {{
    background: #fff; border: 1px solid var(--line); border-radius: 8px;
    padding: 22px;
  }}
  .method-card .step {{
    font-family: var(--font-mono); font-size: 12px; letter-spacing: 2px;
    text-transform: uppercase; color: var(--primary-link); margin-bottom: 8px;
  }}
  .method-card h3 {{
    font-family: var(--font-zh); font-weight: 600; font-size: 18px;
    margin: 0 0 8px; color: var(--text);
  }}
  .method-card p {{ font-size: 14px; color: var(--text-secondary); margin: 0; line-height: 1.7; }}
  code {{
    background: rgba(35,51,99,0.06); color: var(--primary);
    padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 13px;
  }}

  /* ===== CTA ===== */
  .cta-section {{
    background:
      radial-gradient(ellipse 70% 60% at 50% 0%, rgba(74,156,191,0.35) 0%, transparent 65%),
      linear-gradient(180deg, #1a274a 0%, #233363 100%);
    color: #fff; text-align: center; position: relative; overflow: hidden;
  }}
  .cta-section::before {{
    content: ""; position: absolute; inset: 0; pointer-events: none;
    background-image:
      linear-gradient(rgba(255,255,255,0.045) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.045) 1px, transparent 1px);
    background-size: 48px 48px;
    -webkit-mask-image: radial-gradient(ellipse at center, black 35%, transparent 78%);
            mask-image: radial-gradient(ellipse at center, black 35%, transparent 78%);
  }}
  .cta-section .inner {{ position: relative; }}
  .cta-section h2 {{ color: #fff; }}
  .cta-section p {{ color: rgba(246,246,246,0.82); max-width: 600px; margin: 0 auto 28px; }}
  .btn {{
    display: inline-block; height: 48px; line-height: 48px; padding: 0 28px;
    background: #fff; color: var(--primary); font-size: 16px; font-weight: 500;
    border-radius: 4px; text-decoration: none; border: none;
    transition: background .15s ease, transform .15s ease;
  }}
  .btn:hover {{ background: var(--fg-alt); transform: translateY(-1px); }}
  .btn.primary {{ background: var(--primary); color: #fff; }}
  .btn.primary:hover {{ background: #2a3d76; }}

  /* ===== Footer ===== */
  footer.site {{
    background: #f6f6f6; padding: 32px 24px; border-top: 1px solid var(--line);
    color: var(--text-secondary); font-size: 14px;
  }}
  footer.site .row {{
    max-width: var(--container); margin: 0 auto;
    display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
  }}
  footer.site img {{ height: 28px; opacity: 0.9; }}
  footer.site a {{ color: var(--primary-link); text-decoration: none; }}
  footer.site a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>

<nav class="top">
  <div class="container row">
    <a href="#"><img src="data:image/png;base64,{logo_h_b64}" alt="知識遊牧工作室"></a>
    <div class="links">
      <a href="#summary">摘要</a>
      <a href="#segments">分群</a>
      <a href="#charts">視覺化</a>
      <a href="#method">方法</a>
    </div>
  </div>
</nav>

<header class="hero">
  <div class="inner">
    <img class="logo-mark" src="data:image/png;base64,{logo_sq_b64}" alt="">
    <div class="eyebrow">Knowmad × Fubon Fu+ · Demo</div>
    <h1 class="hero-title">RFM 顧客分群分析</h1>
    <p class="hero-sub">用 53 萬筆零售交易，找出「誰是 VIP、誰快流失、誰可以喚回」<br>把 Excel 的客戶清單，變成可行動的營運決策。</p>
    <div class="chips">
      <span class="chip">資料 {date_min} ~ {date_max}</span>
      <span class="chip">{total_customers:,} 位顧客</span>
      <span class="chip">8 個分群</span>
      <span class="chip">Pareto 80/20</span>
    </div>
  </div>
</header>

<section id="summary">
  <div class="container">
    <h2><span class="num">1</span>關鍵指標</h2>
    <p class="lead">分析期間 12 個月，扣除無記名銷售、退貨與手調帳後，得到 4,338 位有效顧客。</p>
    <div class="kpis">
      <div class="kpi">
        <div class="label">有效顧客數</div>
        <div class="value">{total_customers:,}</div>
        <div class="delta">扣除無記名與退貨後</div>
      </div>
      <div class="kpi">
        <div class="label">總營收</div>
        <div class="value">${total_revenue/1e6:,.2f}M</div>
        <div class="delta">分析期間累計</div>
      </div>
      <div class="kpi">
        <div class="label">Champions 顧客</div>
        <div class="value">{int(champ['Customers']):,}</div>
        <div class="delta">{champ_cust_pct:.1f}% 的顧客</div>
      </div>
      <div class="kpi">
        <div class="label">Champions 營收貢獻</div>
        <div class="value accent">{champ_rev_pct:.1f}%</div>
        <div class="delta">經典 Pareto 80/20 現象</div>
      </div>
    </div>
    <div class="callout">
      <b>核心洞察：</b>不到 ¼ 的顧客（約 22%）貢獻了 65% 的營收。守住 Champions、喚回 At Risk 是 ROI 最高的兩件事；其餘分群依優先順序與成本投放對應行動。
    </div>
  </div>
</section>

<section id="segments" class="alt">
  <div class="container">
    <h2><span class="num">2</span>分群結果</h2>
    <p class="lead">以 R/F/M 三維分數（各 5 分）組合切分八個有意義的客群，並對應建議行動。</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>分群</th><th class="num">顧客數</th><th class="num">% 顧客</th>
            <th class="num">平均最近購買</th><th class="num">平均購買次數</th>
            <th class="num">平均消費</th><th class="num">總營收</th><th class="num">% 營收</th>
            <th>建議行動</th>
          </tr>
        </thead>
        <tbody>{rows_html}
        </tbody>
      </table>
    </div>
  </div>
</section>

<section id="charts">
  <div class="container">
    <h2><span class="num">3</span>視覺化</h2>
    <p class="lead">人數分布讓你看見規模；R×F 熱圖告訴你價值密度落在哪裡。</p>
    <div class="charts">
      <div class="chart-card">
        <img src="data:image/png;base64,{seg_counts_b64}" alt="Segment counts">
        <div class="cap">各分群人數分布。Champions 與 Loyal 合計約 45%，是穩定的營收基底。</div>
      </div>
      <div class="chart-card">
        <img src="data:image/png;base64,{heatmap_b64}" alt="R x F heatmap">
        <div class="cap">R × F 熱圖：顏色＝平均消費，數字＝顧客數。<b>右上角是金礦</b>（最近又常買，貢獻最高）。</div>
      </div>
    </div>
  </div>
</section>

<section id="method" class="alt">
  <div class="container">
    <h2><span class="num">4</span>方法論</h2>
    <p class="lead">RFM 是最經典也最容易上手的顧客分群法。三個維度都從交易紀錄就能算出來。</p>
    <div class="method-grid">
      <div class="method-card">
        <div class="step">Step 01 · Recency</div>
        <h3>最近一次購買距今幾天</h3>
        <p>快照日 <code>2011-12-10</code> 減去顧客最後一次購買日。<br>越小越好 → 反向給分。</p>
      </div>
      <div class="method-card">
        <div class="step">Step 02 · Frequency</div>
        <h3>分析期間內的不重複發票數</h3>
        <p>用 <code>InvoiceNo</code> 不重複計數，避免一張單多品項被重複計算。</p>
      </div>
      <div class="method-card">
        <div class="step">Step 03 · Monetary</div>
        <h3>累計消費金額</h3>
        <p>每筆 <code>Quantity × UnitPrice</code> 加總。負值（退貨）已在前置清理排除。</p>
      </div>
      <div class="method-card">
        <div class="step">Step 04 · Scoring</div>
        <h3>Rank → Quintile（五等分）</h3>
        <p>對 R/F/M 各別 <code>rank → qcut(5)</code>，避開大量重複值（例如多數人 F=1）造成的空 bin 問題。</p>
      </div>
      <div class="method-card">
        <div class="step">Step 05 · Segmentation</div>
        <h3>對應命名分群</h3>
        <p>以 R、F 為主軸（M 作為 tie-breaker）切八群：Champions / Loyal / At Risk / Need Attention / Promising / New / Hibernating / Lost。</p>
      </div>
      <div class="method-card">
        <div class="step">Step 06 · Action</div>
        <h3>對應行動建議</h3>
        <p>每群配上獲取 / 維繫 / 喚回 / 放棄四種策略意圖，把分析結果接到行銷與 CRM 操作。</p>
      </div>
    </div>
  </div>
</section>

<section class="cta-section">
  <div class="container inner">
    <h2 style="margin-bottom: 12px">想為自己的資料做一份？</h2>
    <p>這份 demo 從讀檔、清理、計算到產報告，總共不到 200 行 Python。<br>知識遊牧協助團隊把資料變成可行動的洞察。</p>
    <a class="btn" href="https://www.knowmad.tw" target="_blank" rel="noopener">了解知識遊牧 →</a>
  </div>
</section>

<footer class="site">
  <div class="row">
    <img src="data:image/png;base64,{logo_h_b64}" alt="知識遊牧工作室">
    <div>
      © 知識遊牧工作室 · Knowmad ｜ 富邦 Fu+ 2026.05 講座 Demo<br>
      <small>資料：UK Online Retail (公開資料集)，僅供教學示範。</small>
    </div>
  </div>
</footer>

</body>
</html>
"""

(HERE / "index.html").write_text(html, encoding="utf-8")
print(f"Wrote {(HERE/'index.html').stat().st_size:,} bytes to index.html")
