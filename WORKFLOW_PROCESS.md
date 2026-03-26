# 🔄 SQLMap 安全扫描平台 - 完整流程说明

## 📊 流程概览

```
开发者 Push 代码
    ↓
GitHub Actions 工作流触发
    ↓
Self-Hosted Runner 执行
    ↓
Docker 运行 SQLMap
    ↓
生成安全报告
    ↓
上传结果和通知
```

---

## 🚀 详细步骤分解

### Phase 1: 代码提交与事件触发

#### Step 1: 开发者 Push 代码
```bash
git add .
git commit -m "feat: update security scanner"
git push origin main
```

#### Step 2: GitHub 事件触发
```yaml
# 工作流配置 (.github/workflows/security-scan-runner.yml)
on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      target:
        description: '扫描目标 URL'
```

**触发条件：**
- ✅ 代码 Push 到 main 分支
- ✅ 修改 `security-scanner/` 目录
- ✅ 手动在 GitHub UI 触发

---

### Phase 2: Runner 初始化

#### Step 3: 检查 Runner 状态
```bash
# Runner 必须在线（Idle 状态）
# GitHub Settings → Actions → Runners 中验证
```

#### Step 4: 选择运行环境
```
两种方式：
├─ Docker 容器：myoung34/github-runner:latest
└─ 原生二进制：/opt/github-runner/run.sh
```

---

### Phase 3: 配置加载

#### Step 5: 加载环境变量
```bash
# Docker 方式
--env-file .env

# 或直接传递
-e GITHUB_URL=https://github.com/cpWhitecat/devops
-e GITHUB_TOKEN=ghp_xxxx...
```

#### Step 6: 验证配置
```python
# generate_report.py 中的验证
GITHUB_URL = os.getenv('GITHUB_URL')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
TARGET_URL = os.getenv('TARGET', secrets.SCAN_TARGET)
```

---

### Phase 4: 扫描执行

#### Step 7: 启动 SQLMap 容器
```bash
docker run --rm \
  -e TARGET="$TARGET" \
  -e LEVEL="$LEVEL" \
  -e RISK="$RISK" \
  -v "$WORKDIR/scans:/scans" \
  security-scanner:latest
```

#### Step 8: 执行 SQL 注入扫描
```bash
# run_scan.sh 中执行
sqlmap -u "$TARGET" \
  --batch \
  --output-dir="/scans" \
  --level="$LEVEL" \
  --risk="$RISK" \
  --threads="$THREADS"
```

**SQLMap 参数：**
| 参数 | 说明 | 值范围 |
|------|------|--------|
| `--level` | 扫描深度 | 1-5 |
| `--risk` | 风险等级 | 1-3 |
| `--threads` | 并发数 | 1-10 |

---

### Phase 5: 报告生成

#### Step 9: 分析扫描日志
```python
# generate_report.py 中的分析
def analyze(text):
    """分析 SQLMap 日志"""
    vuln_patterns = [
        r"is vulnerable",
        r"vulnerable parameter",
        r"SQL injection",
        r"payload:",
    ]
    findings = [p for p in vuln_patterns if re.search(p, text, re.I)]
    return findings
```

#### Step 10: 生成 HTML 报告
```python
# 生成内容包含：
├─ 扫描摘要
│  ├─ 目标地址
│  ├─ 检测到的数据库类型
│  └─ 风险评估等级
├─ 安全发现
│  └─ 检测到的漏洞列表
├─ 核心日志
│  └─ 关键词高亮显示
└─ 完整输出
   └─ 带行号的扫描日志
```

---

### Phase 6: 结果处理

#### Step 11: 打包结果
```bash
# 组织文件结构
scans/
├── run.log              # 原始扫描日志
├── report.html          # HTML 报告
└── [其他 SQLMap 输出]
```

#### Step 12: 上传 Artifact
```yaml
- name: Upload Scan Results
  uses: actions/upload-artifact@v4
  with:
    name: security-scan-results-${{ github.run_number }}
    path: ${{ github.workspace }}/scans/
    retention-days: 30
```

---

### Phase 7: 通知与反馈

#### Step 13: 工作流状态检查
```yaml
- name: Check Workflow Status
  if: always()
  run: |
    if [ $? -eq 0 ]; then
      echo "✅ 扫描成功"
    else
      echo "❌ 扫描失败"
    fi
```

#### Step 14: 创建 PR 评论（可选）
```bash
# 如果在 PR 中触发，自动评论
Comment: "🛡️ SQLMap 安全扫描完成
- ✅ 已执行 SQL 注入检测
- 📄 报告已生成
- 📦 结果已上传"
```

#### Step 15: 发送通知
```yaml
# Slack/邮件通知（可选）
- name: Notify Slack
  if: failure()
  run: |
    curl -X POST $SLACK_WEBHOOK \
      -d "SQLMap 扫描失败: ${{ github.repository }}"
```

---

## 🔍 关键代码文件

### 1. [run_scan.sh](./security-scanner/run_scan.sh)
**职责**：执行 SQLMap 扫描
```bash
├─ 验证 TARGET 环境变量
├─ 创建输出目录
├─ 运行 SQLMap
├─ 记录日志
└─ 调用报告生成器
```

### 2. [generate_report.py](./security-scanner/generate_report.py)
**职责**：分析日志并生成 HTML 报告
```python
├─ find_runlog()     # 递归查找日志文件
├─ analyze()         # 提取漏洞特征
└─ render_html()     # 生成 HTML 报告
```

### 3. [Dockerfile](./security-scanner/Dockerfile)
**职责**：打包扫描工具
```dockerfile
├─ FROM python:3.11-slim
├─ 安装 SQLMap
├─ 复制脚本
└─ 设置入口点
```

### 4. 工作流文件
**文件**：[.github/workflows/security-scan-runner.yml](./.github/workflows/security-scan-runner.yml)
```yaml
├─ 触发条件定义
├─ Runner 选择
├─ 环境变量配置
├─ Docker 构建和运行
└─ 结果处理
```

---

## 📈 工作流执行时间

| 阶段 | 时间 | 说明 |
|------|------|------|
| 初始化 | ~10s | 检查 Runner，准备环境 |
| 构建镜像 | ~30s | Docker 构建（首次较长） |
| SQLMap 扫描 | 1-5 分钟 | 取决于目标和参数 |
| 报告生成 | ~5s | 分析日志，生成 HTML |
| 上传 Artifact | ~10s | 压缩并上传结果 |
| **总计** | **2-6 分钟** | 通常 3-4 分钟 |

---

## 🎯 使用场景

### 场景 1：自动化扫描
```bash
# 每次 Push 时自动扫描
git add .
git commit -m "feature update"
git push origin main
# → 工作流自动触发 → SQLMap 扫描 → 报告生成
```

### 场景 2：手动触发扫描
```
GitHub UI → Actions → Security Scan with SQLMap
→ Run workflow → 输入参数 → 执行扫描
```

### 场景 3：定期扫描
```yaml
# 添加到工作流配置
schedule:
  - cron: '0 2 * * *'  # 每天凌晨 2 点
```

---

## ✅ 验证流程

### 检查清单

- [ ] Runner 在线（GitHub Settings 显示 Idle）
- [ ] Dockerfile 能成功构建
- [ ] SQLMap 容器能正常运行
- [ ] 扫描日志能被正确解析
- [ ] HTML 报告能成功生成
- [ ] Artifact 能上传到 GitHub

### 测试命令

```bash
# 1. 验证 Docker 镜像
docker build -t security-scanner:latest ./security-scanner/
docker images | grep security-scanner

# 2. 验证容器运行
mkdir -p ./scans
docker run --rm -e TARGET="http://scanme.nmap.org" \
  -v $(pwd)/scans:/scans \
  security-scanner:latest

# 3. 验证报告生成
ls -la ./scans/report.html
```

---

## 📊 监控和调试

### 查看工作流日志

```bash
# GitHub UI 方式
Actions → 选择工作流运行 → 点击 Job 查看详细日志

# 命令行方式（需要 GitHub CLI）
gh workflow run security-scan-runner.yml -f target=http://example.com
gh run list --workflow=security-scan-runner.yml
gh run view <run-id> --log
```

### 常见问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| Runner Offline | 容器/进程未运行 | 重启 Runner |
| Token 无效 | Token 过期或权限不足 | 生成新 Token |
| 扫描超时 | 目标不可达或 SQLMap 卡住 | 增加超时时间 |
| 报告为空 | 日志格式不匹配 | 检查 analyze() 函数 |

---

## 🚀 优化建议

1. **缓存 Docker 层**
   ```yaml
   - uses: docker/build-push-action@v5
     with:
       cache-from: type=gha
       cache-to: type=gha,mode=max
   ```

2. **并行运行多个扫描**
   ```bash
   # 同时扫描多个目标
   TARGET1=... TARGET2=... docker-compose up
   ```

3. **定期清理 Artifact**
   ```yaml
   retention-days: 30  # 保留 30 天
   ```

4. **增加通知功能**
   ```bash
   # Slack、钉钉、企业微信通知
   ```

---

## 📚 相关文档

- [README.md](./README.md) - 项目总览
- [QUICK_START.md](./QUICK_START.md) - 快速开始
- [DOCKER_RUNNER_GUIDE.md](./DOCKER_RUNNER_GUIDE.md) - Docker Runner 部署
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 部署方案对比

---

**最后更新**: 2026-03-26 | **维护者**: cpWhitecat
