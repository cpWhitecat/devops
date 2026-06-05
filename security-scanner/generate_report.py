#!/usr/bin/env python3
import sys
import os
import re
import html
from datetime import datetime

def find_runlog(outdir):
    """
    递归查找 run.log 文件。
    
    """
    for root, dirs, files in os.walk(outdir):
        if 'run.log' in files:
            return os.path.join(root, 'run.log')
    return None

def analyze(text):
    """
    分析 SQLMap 日志并提取核心特征。
    """
    findings = []
    # 漏洞匹配
    vuln_patterns = [
        (r"is vulnerable", "确认存在 SQL 注入漏洞"),
        (r"vulnerable parameter", "发现可注入参数"),
        (r"SQL injection", "检测到 SQL 注入特征"),
        (r"payload:", "攻击载荷 (Payload) 详情"),
        (r"parameter.*is injectable", "注入点验证成功")
    ]
    
    detected_descriptions = []
    for pat, desc in vuln_patterns:
        if re.search(pat, text, re.I):
            detected_descriptions.append(desc)
            findings.append(pat)

    # 提取关键字
    lines = [l for l in text.splitlines() if re.search(r'parameter|payload|vulnerab|sql injection|notice|critical|error', l, re.I)]
    
    # 尝试提取扫描元数据
    metadata = {
        "target": "Unknown",
        "dbms": "Unknown"
    }
    url_match = re.search(r"testing URL '(.+?)'", text, re.I)
    if url_match:
        metadata["target"] = url_match.group(1)

    dbms_match = re.search(r"back-end DBMS: '(.+?)'", text, re.I)
    if dbms_match:
        metadata["dbms"] = dbms_match.group(1)

    # 提取Payload和HTTP响应码，供漏洞详情高亮
    payloads = [m.group(1).strip() for m in re.finditer(r"payload:\s*(.+)", text, re.I)]
    http_codes = [m.group(1) for m in re.finditer(r"(?:HTTP/\d\.\d\s+|response code[:\s]*)(\d{3})", text, re.I)]
    vuln_details = {
        "payloads": sorted(set(payloads)),
        "http_codes": sorted(set(http_codes))
    }

    return list(set(detected_descriptions)), lines, metadata, vuln_details

def render_html(outdir, findings, lines, full_log, metadata, vuln_details):
    """
    生成精致的 HTML 报告。
    """
    vulnerable = len(findings) > 0
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk_level = "HIGH" if vulnerable else "LOW"
    status_text = "发现安全风险" if vulnerable else "未发现明显漏洞"
    status_class = "vuln" if vulnerable else "ok"

    payloads = vuln_details.get('payloads', []) if vuln_details else []
    http_codes = vuln_details.get('http_codes', []) if vuln_details else []

    # 高亮关键词逻辑
    highlighted_lines = []
    keywords = ['parameter', 'payload', 'vulnerable', 'SQL injection', 'notice', 'injectable', 'critical']
    for line in lines:
        hl = html.escape(line)
        for kw in keywords:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            hl = pattern.sub(f'<span class="highlight">{kw}</span>', hl)
        highlighted_lines.append(hl)

    # 完整日志带行号
    numbered_log = "\n".join([f'<div class="log-line"><span class="line-num">{i}</span>{html.escape(l)}</div>' 
                              for i, l in enumerate(full_log.splitlines(), 1)])

    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SQLMap 扫描报告</title>
  <style>
    :root {{
      --primary: #2563eb; --danger: #dc2626; --success: #16a34a; --bg: #f8fafc; --dark: #1e293b;
    }}
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--dark); margin: 0; padding: 20px; }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    header {{ background: linear-gradient(135deg, var(--primary), #1d4ed8); color: white; padding: 2.5rem; border-radius: 16px; text-align: center; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-bottom: 30px; }}
    .status {{ display: inline-block; padding: 10px 25px; border-radius: 50px; font-weight: bold; border: 2px solid white; margin-top: 15px; text-transform: uppercase; }}
    .risk-meter {{ height: 14px; border-radius: 999px; margin-top: 8px; }}
    .risk-meter.high {{ background: linear-gradient(90deg, #dc2626 0%, #f97316 50%, #facc15 100%); }}
    .risk-meter.low {{ background: linear-gradient(90deg, #16a34a 0%, #4ade80 50%, #86efac 100%); }}
    .vuln {{ background: var(--danger); box-shadow: 0 0 15px rgba(220, 38, 38, 0.5); }}
    .ok {{ background: var(--success); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 25px; }}
    .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
    h2 {{ font-size: 1.25rem; color: var(--primary); margin-top: 0; border-bottom: 1px solid #edf2f7; padding-bottom: 10px; }}
    pre {{ background: #0f172a; color: #f8fafc; padding: 15px; border-radius: 8px; font-family: 'Consolas', monospace; font-size: 13px; line-height: 1.6; overflow-x: auto; }}
    .highlight {{ background: #fbbf24; color: #000; padding: 0 3px; border-radius: 3px; font-weight: bold; }}
    .line-num {{ color: #64748b; border-right: 1px solid #334155; padding-right: 10px; margin-right: 10px; display: inline-block; width: 40px; text-align: right; user-select: none; }}
    .log-line:hover {{ background: #1e293b; }}
    .footer {{ text-align: center; padding: 30px; color: #64748b; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1 style="margin:0">🛡️ SQLMap 自动化安全报告</h1>
      <div class="status {status_class}">{status_text}</div>
    </header>
    
    <div class="grid">
      <div class="card">
        <h2>扫描摘要</h2>
        <p><strong>目标地址:</strong> {metadata['target']}</p>
        <p><strong>检测到数据库:</strong> {metadata['dbms']}</p>
        <p><strong>风险评估:</strong> <span style="color: {'var(--danger)' if vulnerable else 'var(--success)'}; font-weight:bold;">{risk_level}</span></p>
        <div class="risk-meter {'high' if vulnerable else 'low'}" aria-label="风险仪表"></div>
        <p><strong>扫描时间:</strong> {current_time}</p>
      </div>
      <div class="card">
        <h2>🚨 安全发现</h2>
        <ul style="padding-left: 20px;">
          {"".join([f'<li style="margin-bottom:8px">️ {f}</li>' for f in findings]) if findings else '<li> 未发现 SQL 注入漏洞 (对于 Apache 初始页，这属于正常安全状态)。</li>'}
        </ul>
      </div>
    </div>

    <div class="card">
      <h2> 漏洞详情（Payload / HTTP 响应码）</h2>
      <p><strong>Payload</strong>：</p>
      <ul style="padding-left: 20px;">{''.join([f'<li><code class="highlight">{html.escape(p)}</code></li>' for p in payloads]) if payloads else '<li>未发现具体 payload</li>'}</ul>
      <p><strong>HTTP 响应码</strong>：</p>
      <ul style="padding-left: 20px;">{''.join([f'<li><span class="highlight">{c}</span></li>' for c in http_codes]) if http_codes else '<li>未发现 HTTP 响应码</li>'}</ul>
    </div>

    <div class="card">
      <h2>🔗 漏洞证链</h2>
      <p>已提取的 Payload 注入链路（基于已识别 payload）：</p>
      <p style="background: #fdf2f8; border: 1px solid #fecdd3; border-radius: 8px; padding: 10px; font-family: Consolas, monospace; overflow-x: auto;">{html.escape(' -> '.join(payloads)) if payloads else '无注入 Payload 链路'}</p>
      <p>已注入载荷关键信息（HTML Escape 保护）：</p>
      <ul style="padding-left: 20px;">{''.join([f'<li style="background:#fff7ed; padding:4px 8px; border-radius:4px; margin-bottom:4px;">{html.escape(p)}</li>' for p in payloads]) if payloads else '<li>无</li>'}</ul>
    </div>

    <div class="card">
      <h2>🔍 核心日志证据</h2>
      <pre>{"<br>".join(highlighted_lines) if highlighted_lines else "未提取到关键安全日志。"}</pre>
    </div>

    <div class="card">
      <h2>完整扫描输出</h2>
      <div class="log-scroll" style="max-height: 500px; overflow-y: auto; border-radius: 8px;">
        <pre style="margin:0">{numbered_log}</pre>
      </div>
    </div>

    <div class="footer">
      <p>生成的扫描报告仅供安全审计使用 &bull; {current_time}</p>
    </div>
  </div>
  <script>
    document.addEventListener('DOMContentLoaded', function () {
      const logBox = document.querySelector('.log-scroll');
      if (logBox) {
        logBox.scrollTop = logBox.scrollHeight;
      }
    });
  </script>
</body>
</html>
"""
    outpath = os.path.join(outdir, 'report.html')
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return outpath

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: generate_report.py <scans-directory>')
        sys.exit(2)
    
    # 1. 确定扫描根目录
    base_dir = sys.argv[1]
    
    # 2. 搜索 run.log
    runlog = find_runlog(base_dir)
    
    if not runlog:
        print(f"Error: No run.log found in {base_dir}. 生成说明性报告。")
        # 如果没扫到东西（例如网络不通），生成一个简易报告告知用户
        with open(os.path.join(base_dir, 'report.html'), 'w', encoding='utf-8') as f:
            f.write(f"<html><body><h1>扫描未正常执行</h1><p>未在 {base_dir} 中找到扫描日志，请检查目标连通性。</p></body></html>")
        sys.exit(0)

    # 3. 读取并分析日志
    with open(runlog, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    findings, lines, meta, vuln_details = analyze(content)
    
    # 4. 渲染 HTML
    report = render_html(base_dir, findings, lines, content, meta, vuln_details)
    print(f'Successfully generated report: {report}')