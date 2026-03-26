# 🛡️ SQLMap 安全扫描平台

> 一个完整的开源 DevOps 自动化平台，集成 GitHub Actions 和 SQLMap，为您的 Web 应用提供持续的 SQL 注入漏洞检测。

## 🎯 项目概览

```
开发者 Push 代码
        ↓
GitHub Actions 触发
        ↓
Self-Hosted Runner 执行
        ↓
Docker 运行 SQLMap
        ↓
生成安全报告
        ↓
自动上传和通知
```

**核心特性**:
- ✅ **完全自动化**: 代码 Push 自动触发安全扫描
- 🐳 **容器化**: Docker 隔离环境，避免污染主机
- 📊 **精美报告**: HTML 格式安全扫描报告
- 🚀 **高效部署**: 5 分钟内完成端到端设置
- 📈 **可对标**: 支持参数化扫描深度和风险等级
- 🔒 **企业级**: 支持私有部署和自定义配置

---

## 🚀 快速开始（5 分钟）

### 1️⃣ 克隆项目
```bash
git clone https://github.com/cpWhitecat/devops.git
cd devops
```

### 2️⃣ 构建和测试
```bash
# 运行系统测试
bash test-system.sh

# 本地测试扫描
mkdir -p ./scans
docker run --rm \
  -e TARGET="http://scanme.nmap.org" \
  -e LEVEL="1" \
  -e RISK="1" \
  -v $(pwd)/scans:/scans \
  security-scanner:latest
```

### 3️⃣ 部署 GitHub Runner
```bash
# Docker 方式（推荐快速）
mkdir -p /opt/github-runner
cat > /opt/github-runner/.env << 'EOF'
REPO_URL=https://github.com/cpWhitecat/devops
GITHUB_TOKEN=ghp_your_token_here
RUNNER_NAME=centos-runner-01
RUNNER_LABELS=linux,docker,sqlmap
EOF

docker run -d \
  --name github-runner \
  --restart always \
  --env-file /opt/github-runner/.env \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest
```

### 4️⃣ 验证并触发
```bash
# 在 GitHub 验证 Runner 在线
# GitHub Settings → Actions → Runners → 检查 "centos-runner-01" 状态

# 触发工作流
git add .
git commit -m "test: trigger security scan"
git push origin main
```

🎉 完成！查看 GitHub Actions 中的扫描结果

---

## 📚 完整文档

选择你最需要的部分开始：

### 🎓 新手指南
- **[QUICK_START.md](./QUICK_START.md)** - 超快速 5 分钟启动 
- **[IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)** - 从零到一的完整检查列表

### 🔍 详细文档

| 文档 | 用途 | 适合 |
|------|------|------|
| [WORKFLOW_PROCESS.md](./WORKFLOW_PROCESS.md) | 🔄 完整流程分解 | 想了解系统工作原理的人 |
| [QUICK_COMMANDS.md](./QUICK_COMMANDS.md) | ⚡ 常用命令速查 | 需要快速参考命令的人 |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | 🔧 故障排查指南 | 遇到问题需要诊断的人 |
| [DOCKER_RUNNER_GUIDE.md](./DOCKER_RUNNER_GUIDE.md) | 🐳 Docker 部署详解 | 选择 Docker 部署方式的人 |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | 🚀 部署方案对比 | 需要选择部署方式的人 |
| [GITHUB_RUNNER_SETUP.md](./GITHUB_RUNNER_SETUP.md) | 📦 原生部署详解 | 选择原生二进制部署的人 |

### 🧪 测试和诊断
- 运行 `bash test-system.sh` - 自动检查整个系统就绪情况
- 查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 遇到问题时参考

---

## 📋 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   GitHub Repository                      │
├─────────────────────────────────────────────────────────┤
│  .github/workflows/                                      │
│  ├─ security-scan-runner.yml    ← SQLMap 扫描工作流    │
│  └─ docker-build-and-scan.yml   ← Docker 构建工作流    │
│                                                          │
│  security-scanner/                                      │
│  ├─ Dockerfile                  ← SQLMap 容器定义      │
│  ├─ run_scan.sh                 ← 扫描执行脚本        │
│  └─ generate_report.py          ← 报告生成器          │
└─────────────────────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────────────────────┐
│            GitHub Actions Triggers                       │
│  • Push to main 分支                                     │
│  • 手动 workflow_dispatch                                 │
│  • 定时 schedule（可选）                                  │
└─────────────────────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────────────────────┐
│         Self-Hosted Runner (CentOS Server)              │
│  ├─ Docker 容器方式:                                     │
│  │  myoung34/github-runner:latest                       │
│  │                                                       │
│  └─ 原生二进制方式:                                      │
│     /opt/github-runner/run.sh                           │
└─────────────────────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────────────────────┐
│          Docker: security-scanner:latest                 │
│  ├─ SQLMap 工具库                                        │
│  ├─ Python 运行时                                        │
│  └─ 扫描脚本和报告生成器                                 │
└─────────────────────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────────────────────┐
│         SQL Injection 扫描执行                           │
│  ├─ 参数化扫描: LEVEL, RISK, THREADS                    │
│  ├─ 自动报告生成                                        │
│  └─ 日志收集                                            │
└─────────────────────────────────────────────────────────┘
            ▼
┌─────────────────────────────────────────────────────────┐
│           Artifact 上传至 GitHub                         │
│  ├─ report.html              ← 美化的 HTML 报告        │
│  ├─ run.log                  ← 完整的扫描日志          │
│  └─ 其他 SQLMap 输出文件                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技术栈

| 组件 | 用途 | 版本 |
|------|------|------|
| **GitHub Actions** | CI/CD 流程编排 | ✅ 已内置 |
| **SQLMap** | SQL 注入检测工具 | Latest |
| **Docker** | 容器化环境 | 20.10+ |
| **Python** | 报告生成 | 3.11+ |
| **CentOS** | 服务器操作系统 | 7/8+ |
| **GitHub Runner** | 任务执行器 | Latest |

---

## 📊 使用示例

### 场景 1: 自动化扫描
```bash
# 开发者进行普通开发
git add .
git commit -m "feature: add new API endpoint"
git push origin main

# 自动触发 → SQLMap 扫描 → HTML 报告生成 → 结果上传
# 无需任何手动操作！
```

### 场景 2: 手动触发特定目标扫描
```
GitHub → Actions → "Security Scan with SQLMap"
→ "Run workflow" → 输入扫描参数
→ 执行 → 获取报告
```

### 场景 3: 定期定时扫描
```yaml
# 可选配置在工作流文件中
schedule:
  - cron: '0 2 * * *'  # 每天凌晨 2 点
```

---

## ⚙️ 配置选项

### 扫描参数调优

| 参数 | 默认值 | 说明 | 范围 |
|------|--------|------|------|
| `LEVEL` | 1 | 扫描深度 | 1-5 |
| `RISK` | 1 | 风险等级 | 1-3 |
| `THREADS` | 1 | 并发线程数 | 1-10 |
| `TIMEOUT` | 30 | 单个请求超时(秒) | 10-300 |

**速度 vs 全面性**:
- 快速扫描: `LEVEL=1, RISK=1` (2-3 分钟)
- 标准扫描: `LEVEL=3, RISK=2` (5-8 分钟)
- 深度扫描: `LEVEL=5, RISK=3` (10-30 分钟)

---

## 🔐 安全最佳实践

```
✅ DO:
  • 定期轮换 GitHub Token
  • 限制 Runner 权限（最小权限原则）
  • 使用私有 Runner 标签
  • 加密敏感的环境变量
  • 定期审查工作流日志

❌ DON'T:
  • 在代码中硬编码 Token
  • 使用公开的扫描目标生产环境
  • 在报告中存储敏感信息
  • 共享 Runner 配置凭证
```

---

## 📦 安装要求

### 最低系统要求
- **OS**: CentOS 7+ 或任何 Linux 发行版
- **内存**: 2GB RAM
- **磁盘**: 10GB 可用空间
- **网络**: 互联网连接

### 必要组件
- Docker 20.10+
- Git 2.23+
- curl (用于下载)
- 有效的 GitHub Personal Access Token

### 可选组件
- GitHub CLI (用于命令行操作)
- yq (用于 YAML 验证)
- 代理配置 (如果位于公司网络后)

---

## 🚀 部署选项

### 选项 A: Docker 容器（推荐用于快速部署）
✅ 优点:
- 最快部署时间（< 5 分钟）
- 自动重启和更新
- 与主机隔离

❌ 缺点:
- 需要 Docker Socket 访问
- 容器开销

查看 [DOCKER_RUNNER_GUIDE.md](./DOCKER_RUNNER_GUIDE.md)

### 选项 B: 原生二进制（推荐用于稳定性）
✅ 优点:
- 更好的性能
- 更多控制
-系统集成度高

❌ 缺点:
- 部署步骤多
- 需要系统权限

查看 [GITHUB_RUNNER_SETUP.md](./GITHUB_RUNNER_SETUP.md)

---

## 📈 监控和维护

### 日常检查
```bash
# 检查 Runner 在线状态
docker logs github-runner | tail -10

# 查看工作流历史
gh run list --workflow=security-scan-runner.yml

# 下载最新报告
gh run download <run-id> -n security-scan-results-xxx
```

### 定期维护
```bash
# 每月清理一次 Docker
docker system prune -a --volumes

# 定期更新 Runner
docker pull myoung34/github-runner:latest
docker restart github-runner
```

---

## 🐛 常见问题

**Q: Runner 显示离线？**
A: 查看日志: `docker logs github-runner` 或 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

**Q: 扫描超时？**
A: 增加超时时间或调整参数: `LEVEL=1 RISK=1 TIMEOUT=60`

**Q: 报告生成失败？**
A: 检查 `run.log` 文件是否存在，查看 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

**Q: 如何定义多个扫描目标？**
A: 见 [WORKFLOW_PROCESS.md](./WORKFLOW_PROCESS.md) 中的扩展部分

---

## 🤝 贡献指南

欢迎提交 Issue 和 PR！

```bash
# 1. Fork 项目
# 2. 创建功能分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m 'Add amazing feature'

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 开启 Pull Request
```

---

## 📄 许可证

此项目采用 MIT 许可证。详见 [LICENSE](./LICENSE) 文件。

---

## 👨‍💼 作者

- **cpWhitecat** - 主要开发者

## 🙏 致谢

- SQLMap 团队
- GitHub Actions 社区
- 所有贡献者

---

## 📞 联系和支持

- 📸 GitHub Issues: [提交问题](https://github.com/cpWhitecat/devops/issues)
- 💬 Discussion: [讨论区](https://github.com/cpWhitecat/devops/discussions)

---

## 🎓 学习资源

- [SQLMap 中文文档](http://www.sqlmap.cn/)
- [GitHub Actions 官方文档](https://docs.github.com/actions)
- [Docker 官方文档](https://docs.docker.com/)
- [Self-Hosted Runner 指南](https://docs.github.com/en/actions/hosting-your-own-runners)

---

## 📋 功能路线图

- [x] 基础 SQLMap 集成
- [x] HTML 报告生成
- [x] GitHub Actions 工作流
- [x] Self-Hosted Runner 支持
- [ ] Slack 通知集成
- [ ] 邮件报告发送
- [ ] 漏洞趋势图表
- [ ] OWASP ZAP 支持
- [ ] 自动化补救建议

---

## 🌟 如果有帮助，请 Star ⭐

```
git clone https://github.com/cpWhitecat/devops.git
cd devops
# ⭐ 如果你觉得这个项目有用，请点击 GitHub 上的 Star 按钮！
```

---

## 🎯 快速导航

| 需求 | 文档 | 时间 |
|------|------|------|
| 快速开始 | [QUICK_START.md](./QUICK_START.md) | 5 分钟 |
| 完整部署 | [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md) | 30 分钟 |
| 遇到问题 | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | 10-20 分钟 |
| 学习系统 | [WORKFLOW_PROCESS.md](./WORKFLOW_PROCESS.md) | 15 分钟 |
| 日常使用 | [QUICK_COMMANDS.md](./QUICK_COMMANDS.md) | 随时查看 |

---

**最后更新**: 2026-03-26 | **版本**: 1.0.0

---

## 🎉 开始使用

ready? 现在就开始！

```bash
# 克隆项目
git clone https://github.com/cpWhitecat/devops.git
cd devops

# 运行系统测试
bash test-system.sh

# 查看完整指南
cat IMPLEMENTATION_CHECKLIST.md
```

🚀 祝你使用愉快！
