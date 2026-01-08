#!/usr/bin/env python3
import sys
import os
import re
import html
from datetime import datetime

def find_runlog(outdir):
    path = os.path.join(outdir, 'run.log')
    return path if os.path.exists(path) else None

def analyze(text):
    findings = []
    # 扩展漏洞匹配模式
    vuln_patterns = [
        (r"is vulnerable", "Critical: Verified SQL Injection"),
        (r"vulnerable parameter", "Critical: Injectable Parameter Found"),
        (r"SQL injection", "High: SQL Injection Evidence"),
        (r"payload:", "Medium: Testing Payload"),
        (r"parameter.*is injectable", "Critical: Confirmed Injection Point")
    ]
    for pat, desc in vuln_patterns:
        if re.search(pat, text, re.I):
            findings.append(desc)

    # 提取包含关键信息的行
    lines = [l for l in text.splitlines() if re.search(r'parameter|payload|vulnerab|sql injection|notice|DBMS|back-end', l, re.I)]
    
    # 提取扫描元数据 (从日志中寻找关键信息)
    metadata = {
        "url": re.search(r"testing URL '(.+?)'", text),
        "dbms": re.search(r"back-end DBMS: '(.+?)'", text),
        "os": re.search(r"operating system: '(.+?)'", text)
    }
    
    formatted_metadata = {k: (v.group(1) if v else "Unknown") for k, v in metadata.items()}
    return list(set(findings)), lines, formatted_metadata

def render_html(outdir, findings, lines, full_log, metadata):
    vulnerable = len(findings) > 0
    title = "SQLMap Professional Security Audit"
    safe_log = html.escape(full_log)
    
    # 关键词高亮
    highlighted_lines = []
    keywords = ['parameter', 'payload', 'vulnerable', 'SQL injection', 'notice', 'injectable', 'CRITICAL', 'WARNING']
    for line in lines:
        hl = html.escape(line)
        for kw in keywords:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            hl = pattern.sub(f'<span class="highlight">{kw}</span>', hl)
        highlighted_lines.append(hl)
    
    # 完整日志带行号
    numbered_log = "\n".join([f'<div class="log-line"><span class="line-num">{i}</span>{html.escape(l)}</div>' 
                              for i, l in enumerate(full_log.splitlines(), 1)])

    # 漏洞列表 HTML
    findings_html = "".join([f'<li><span class="tag tag-danger">⚠️</span> {f}</li>' for f in findings]) \
                    if findings else '<li><span class="tag tag-success">✅</span> No vulnerabilities detected.</li>'
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk_level = "CRITICAL" if vulnerable else "SECURE"
    risk_class = "risk-high" if vulnerable else "risk-low"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    :root {{
      --primary: #2563eb; --danger: #ef4444; --success: #10b981; --warning: #f59e0b;
      --dark: #0f172a; --gray: #64748b; --bg: #f1f5f9;
    }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--dark); margin: 0; line-height: 1.5; }}
    
    header {{ background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: white; padding: 3rem 2rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    .container {{ max-width: 1100px; margin: -2rem auto 2rem; padding: 0 1rem; }}
    
    .risk-badge {{ display: inline-block; padding: 0.5rem 2rem; border-radius: 50px; font-weight: 800; letter-spacing: 1px; margin-top: 1rem; text-transform: uppercase; border: 2px solid white; }}
    .risk-high {{ background: var(--danger); box-shadow: 0 0 20px rgba(239, 68, 68, 0.4); }}
    .risk-low {{ background: var(--success); }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
    .card {{ background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.05); }}
    .card-h2 {{ font-size: 1.1rem; color: var(--gray); text-transform: uppercase; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px; }}

    .meta-item {{ display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }}
    .meta-label {{ color: var(--gray); font-weight: 500; }}

    .code-box {{ background: #1e293b; color: #f8fafc; padding: 1.25rem; border-radius: 12px; font-family: 'Fira Code', monospace; font-size: 13px; overflow-x: auto; position: relative; }}
    .highlight {{ background: #fbbf24; color: #000; padding: 0 3px; border-radius: 3px; font-weight: bold; }}
    .line-num {{ color: #475569; padding-right: 1rem; border-right: 1px solid #334155; margin-right: 1rem; user-select: none; width: 35px; display: inline-block; text-align: right; }}
    .log-line:hover {{ background: #334155; }}

    .tab-nav {{ display: flex; gap: 1rem; margin-bottom: 1rem; }}
    .tab-btn {{ padding: 0.6rem 1.5rem; border: none; background: #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.3s; }}
    .tab-btn.active {{ background: var(--primary); color: white; }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}

    ul {{ list-style: none; padding: 0; }}
    li {{ padding: 0.8rem; background: #f8fafc; border-radius: 8px; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 10px; border-left: 4px solid var(--primary); }}
    
    footer {{ text-align: center; padding: 3rem; color: var(--gray); font-size: 0.85rem; }}
  </style>
</head>
<body>
  <header>
    <div style="max-width: 1100px; margin: 0 auto;">
      <h1 style="margin:0; font-size: 2.5rem;">🛡️ SQLMap Audit Report</h1>
      <div class="risk-badge {risk_class}">{risk_level}</div>
      <p style="opacity: 0.8; margin-top: 1rem;">Target: {metadata['url']}</p>
    </div>
  </header>
  
  <div class="container">
    <div class="grid">
      <div class="card">
        <h2 class="card-h2">📊 Scan Metadata</h2>
        <div class="meta-item"><span class="meta-label">DBMS</span><span>{metadata['dbms']}</span></div>
        <div class="meta-item"><span class="meta-label">OS</span><span>{metadata['os']}</span></div>
        <div class="meta-item"><span class="meta-label">Detections</span><span style="color:var(--danger); font-weight:bold;">{len(findings)}</span></div>
        <div class="meta-item"><span class="meta-label">Scan Date</span><span>{current_time}</span></div>
      </div>
      
      <div class="card">
        <h2 class="card-h2">🚨 Security Findings</h2>
        <ul>{findings_html}</ul>
      </div>
    </div>

    <section class="card">
      <h2 class="card-h2">🔍 Technical Logs</h2>
      <div class="tab-nav">
        <button class="tab-btn active" onclick="switchTab('relevant')">Critical Segments</button>
        <button class="tab-btn" onclick="switchTab('full')">Full Output</button>
      </div>
      
      <div id="relevant" class="tab-content active">
        <div class="code-box">
          {"<br>".join(highlighted_lines) if highlighted_lines else "No critical segments identified."}
        </div>
      </div>
      
      <div id="full" class="tab-content">
        <div class="code-box" style="max-height: 600px; overflow-y: auto;">
          {numbered_log}
        </div>
      </div>
    </section>
  </div>
  
  <footer>
    <p>Generated by Enhanced SQLMap Reporter &bull; {current_time}</p>
    <p>INTERNAL USE ONLY - PROPRIETARY INFORMATION</p>
  </footer>

  <script>
    function switchTab(id) {{
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.add('active');
      event.currentTarget.classList.add('active');
    }}
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
        print('Usage: generate_report.py <scan-output-dir>')
        sys.exit(2)
    
    outdir = sys.argv[1]
    runlog = find_runlog(outdir)
    if not runlog:
        print(f'Error: No run.log found in {{outdir}}')
        sys.exit(1)
        
    with open(runlog, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    findings, lines, metadata = analyze(content)
    report_path = render_html(outdir, findings, lines, content, metadata)
    print(f'Successfully generated report: {{report_path}}')