#!/usr/bin/env python3
import sys
import os
import re
import html
from datetime import datetime  # 添加时间处理模块


def find_runlog(outdir):
    path = os.path.join(outdir, 'run.log')
    return path if os.path.exists(path) else None


def analyze(text):
    findings = []
    # simple heuristics for sqlmap outputs
    vuln_patterns = [r"is vulnerable", r"vulnerable parameter", r"SQL injection", r"payload:", r"parameter.*is injectable"]
    for pat in vuln_patterns:
        if re.search(pat, text, re.I):
            findings.append(pat)

    # extract lines mentioning 'parameter' or 'payload' or 'interesting'
    lines = [l for l in text.splitlines() if re.search(r'parameter|payload|vulnerab|sql injection|notice', l, re.I)]

    return findings, lines


def render_html(outdir, findings, lines, full_log):
    vulnerable = len(findings) > 0
    title = f"SQLMap Scan Report - {'VULNERABLE' if vulnerable else 'NO VULNERABILITY FOUND'}"
    safe_log = html.escape(full_log)
    
    # 处理相关行，为关键词添加高亮
    highlighted_lines = []
    keywords = ['parameter', 'payload', 'vulnerable', 'SQL injection', 'notice', 'injectable']
    for line in lines:
        highlighted_line = html.escape(line)
        for keyword in keywords:
            # 不区分大小写高亮关键词
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            highlighted_line = pattern.sub(f'<span class="highlight">{keyword}</span>', highlighted_line)
        highlighted_lines.append(highlighted_line)
    
    # 处理完整日志，添加行号
    log_lines = safe_log.split('\n')
    numbered_log = []
    for i, line in enumerate(log_lines, 1):
        numbered_log.append(f'<span class="line-num">{i}</span>{line}')
    numbered_log = '\n'.join(numbered_log)

    # 生成检测项HTML
    findings_html = ""
    if findings:
        for f in findings:
            findings_html += f'        <li><strong>⚠️</strong> {html.escape(f)}</li>\n'
    else:
        findings_html += '        <li>No security vulnerabilities detected</li>\n'
    
    # 获取当前时间（替代os.popen方式，更可靠）
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 风险等级
    risk_level = "HIGH" if vulnerable else "LOW"

    html_content = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    :root {{
      --color-danger: #dc2626;
      --color-success: #059669;
      --color-warning: #f59e0b;
      --color-primary: #2563eb;
      --color-dark: #1e293b;
      --color-light: #f8fafc;
      --color-gray: #64748b;
      --color-gray-light: #e2e8f0;
      --color-highlight: #fef3c7;
      --font-mono: 'Consolas', 'Monaco', monospace;
    }}
    
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    
    body {{ 
      font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif; 
      line-height: 1.6;
      margin: 0;
      padding: 0;
      background-color: #f8fafc;
      color: var(--color-dark);
    }}
    
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
    }}
    
    header {{
      background: linear-gradient(135deg, var(--color-primary), #3b82f6);
      color: white;
      padding: 2rem 0;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      margin-bottom: 2rem;
    }}
    
    .header-content {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 2rem;
    }}
    
    .status {{ 
      padding: 0.75rem 1.5rem; 
      border-radius: 8px; 
      color: #fff; 
      font-weight: 600;
      display: inline-block;
      margin: 1rem 0;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .vuln {{ 
      background: var(--color-danger); 
      border-left: 4px solid #991b1b;
    }}
    
    .ok {{ 
      background: var(--color-success); 
      border-left: 4px solid #065f46;
    }}
    
    .card {{
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
      padding: 1.5rem;
      margin-bottom: 2rem;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }}
    
    .card-title {{
      color: var(--color-primary);
      border-bottom: 2px solid var(--color-gray-light);
      padding-bottom: 0.75rem;
      margin-bottom: 1rem;
      font-size: 1.25rem;
    }}
    
    pre {{ 
      background: #1e293b; 
      color: #e2e8f0;
      padding: 1.5rem; 
      white-space: pre-wrap; 
      overflow-x: auto; 
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.9rem;
      line-height: 1.5;
    }}
    
    code {{
      font-family: var(--font-mono);
    }}
    
    ul {{ 
      margin-top: 0; 
      padding-left: 1.5rem;
    }}
    
    li {{
      margin-bottom: 0.5rem;
      padding: 0.25rem 0;
    }}
    
    .summary-stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin: 1rem 0 2rem;
    }}
    
    .stat-card {{
      background: var(--color-light);
      border-radius: 8px;
      padding: 1rem;
      border-left: 4px solid var(--color-primary);
    }}
    
    .stat-value {{
      font-size: 2rem;
      font-weight: 700;
      color: var(--color-primary);
    }}
    
    .stat-label {{
      color: var(--color-gray);
      font-size: 0.9rem;
    }}
    
    .highlight {{
      background-color: var(--color-highlight);
      color: #92400e;
      padding: 0 4px;
      border-radius: 3px;
      font-weight: 600;
    }}
    
    .line-num {{
      display: inline-block;
      width: 45px;
      color: var(--color-gray);
      text-align: right;
      padding-right: 10px;
      border-right: 1px solid #475569;
      margin-right: 10px;
      user-select: none;
    }}
    
    .tabs {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      border-bottom: 1px solid var(--color-gray-light);
      padding-bottom: 0.5rem;
    }}
    
    .tab {{
      padding: 0.5rem 1rem;
      cursor: pointer;
      border-radius: 6px 6px 0 0;
      background: var(--color-gray-light);
      border: none;
      font-weight: 600;
      transition: all 0.2s ease;
    }}
    
    .tab.active {{
      background: var(--color-primary);
      color: white;
    }}
    
    .tab-content {{
      display: none;
    }}
    
    .tab-content.active {{
      display: block;
    }}
    
    .relevant-lines {{
      max-height: 400px;
      overflow-y: auto;
    }}
    
    footer {{
      text-align: center;
      padding: 2rem;
      color: var(--color-gray);
      font-size: 0.9rem;
      border-top: 1px solid var(--color-gray-light);
      margin-top: 2rem;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
      .container {{
        padding: 1rem;
      }}
      
      .header-content {{
        padding: 0 1rem;
      }}
      
      .summary-stats {{
        grid-template-columns: 1fr;
      }}
      
      pre {{
        font-size: 0.8rem;
        padding: 1rem;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-content">
      <h1>SQLMap Security Scan Report</h1>
      <p class="status { 'vuln' if vulnerable else 'ok' }">{ 'VULNERABLE - SECURITY ISSUES DETECTED' if vulnerable else 'NO VULNERABILITY FOUND - SCAN COMPLETED SUCCESSFULLY' }</p>
    </div>
  </header>
  
  <div class="container">
    <section class="card">
      <h2 class="card-title">Scan Summary</h2>
      <div class="summary-stats">
        <div class="stat-card">
          <div class="stat-value">{len(findings)}</div>
          <div class="stat-label">Security Detections</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{len(lines)}</div>
          <div class="stat-label">Relevant Log Lines</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{len(full_log.splitlines())}</div>
          <div class="stat-label">Total Log Lines</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{risk_level}</div>
          <div class="stat-label">Risk Level</div>
        </div>
      </div>
      
      <h3>Detected Security Issues:</h3>
      <ul>
{findings_html}
      </ul>
    </section>

    <section class="card">
      <h2 class="card-title">Detailed Results</h2>
      
      <div class="tabs">
        <button class="tab active" onclick="showTab('relevant', event)">Relevant Lines</button>
        <button class="tab" onclick="showTab('full', event)">Full Log</button>
      </div>
      
      <div id="relevant" class="tab-content active">
        <div class="relevant-lines">
          <pre>
{chr(10).join(highlighted_lines)}
          </pre>
        </div>
      </div>
      
      <div id="full" class="tab-content">
        <pre>
{numbered_log}
        </pre>
      </div>
    </section>
  </div>
  
  <footer>
    <p>Generated by SQLMap Report Generator • {current_time}</p>
    <p>⚠️ This report is for security assessment purposes only. Handle with care.</p>
  </footer>

  <script>
    // Tab switching functionality
    function showTab(tabId, evt) {{
      // Hide all tab contents
      document.querySelectorAll('.tab-content').forEach(tab => {{
        tab.classList.remove('active');
      }});
      
      // Deactivate all tabs
      document.querySelectorAll('.tab').forEach(tab => {{
        tab.classList.remove('active');
      }});
      
      // Activate selected tab and content
      document.getElementById(tabId).classList.add('active');
      if (evt && evt.target) {{
        evt.target.classList.add('active');
      }}
      
      // Smooth scroll to tab content
      document.getElementById(tabId).scrollIntoView({{ behavior: 'smooth' }});
    }}
    
    // Add copy to clipboard functionality
    document.addEventListener('DOMContentLoaded', function() {{
      // Create copy buttons for code blocks
      const preElements = document.querySelectorAll('pre');
      preElements.forEach((pre, index) => {{
        const copyBtn = document.createElement('button');
        copyBtn.textContent = 'Copy';
        copyBtn.style.position = 'sticky';
        copyBtn.style.top = '10px';
        copyBtn.style.left = 'calc(100% - 70px)';
        copyBtn.style.padding = '5px 10px';
        copyBtn.style.border = 'none';
        copyBtn.style.borderRadius = '4px';
        copyBtn.style.backgroundColor = 'var(--color-primary)';
        copyBtn.style.color = 'white';
        copyBtn.style.cursor = 'pointer';
        copyBtn.style.marginBottom = '10px';
        
        copyBtn.addEventListener('click', function() {{
          const text = pre.textContent;
          navigator.clipboard.writeText(text).then(() => {{
            copyBtn.textContent = 'Copied!';
            setTimeout(() => copyBtn.textContent = 'Copy', 2000);
          }});
        }});
        
        pre.parentNode.insertBefore(copyBtn, pre);
      }});
    }});
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
        print('No run.log found in', outdir)
        sys.exit(0)
    with open(runlog, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    findings, lines = analyze(content)
    report = render_html(outdir, findings, lines, content)
    print('Report generated:', report)z 