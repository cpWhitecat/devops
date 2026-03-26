# 📋 实施检查清单 - 全流程指南

## Checklist 用法

按照下面的流程，逐项完成：
- `[ ]` = 未完成
- `[x]` = 已完成
- `[!]` = 可选但推荐
- `[-]` = 跳过

---

## 第一阶段: 环境准备

### 前置条件检查
- [ ] 有 GitHub 账户和 Personal Access Token（ghp_开头）
- [ ] CentOS 服务器有 Docker 已安装
- [ ] 有对 `https://github.com/cpWhitecat/devops` 仓库的写入权限
- [ ] 服务器可访问互联网（或有代理配置）

### 本地环境配置
- [ ] 在 CentOS 服务器上克隆仓库
  ```bash
  git clone https://github.com/cpWhitecat/devops.git
  cd devops
  ```
- [ ] 确认项目文件完整
  ```bash
  ls -la security-scanner/
  ls -la .github/workflows/
  ```
- [ ] 配置 Git（可选）
  ```bash
  git config user.name "Your Name"
  git config user.email "your@email.com"
  git config --global core.autocrlf input
  ```

### Docker 环境验证
- [ ] Docker 正常运行
  ```bash
  docker info
  ```
- [ ] 可以拉取镜像
  ```bash
  docker pull hello-world
  docker run hello-world
  ```
- [ ] Docker socket 可访问
  ```bash
  ls -la /var/run/docker.sock
  ```

---

## 第二阶段: 系统测试

### 运行综合测试
- [ ] 执行系统测试脚本
  ```bash
  chmod +x test-system.sh
  bash test-system.sh
  ```
- [ ] 所有测试都通过（`✓ 所有测试通过！系统就绪。`）
- [ ] 查看测试日志并记录任何警告
  ```bash
  tail -50 test-system.sh  # 查看脚本输出
  ```

### 构建 SQLMap Docker 镜像
- [ ] 构建镜像
  ```bash
  docker build -t security-scanner:latest ./security-scanner/
  ```
- [ ] 验证镜像存在
  ```bash
  docker images | grep security-scanner
  ```
- [ ] 获取镜像大小和信息
  ```bash
  docker inspect security-scanner:latest | grep -A 5 '"Size"'
  ```

### 本地扫描测试
- [ ] 创建扫描输出目录
  ```bash
  mkdir -p ./scans
  ```
- [ ] 运行本地测试扫描
  ```bash
  docker run --rm \
    -e TARGET="http://scanme.nmap.org" \
    -e LEVEL="1" \
    -e RISK="1" \
    -v $(pwd)/scans:/scans \
    security-scanner:latest
  ```
- [ ] 验证输出文件已生成
  ```bash
  ls -la ./scans/
  cat ./scans/report.html  # 或用浏览器打开
  ```
- [ ] 检查报告质量
  - [ ] HTML 文件有内容（不是空文件）
  - [ ] 包含扫描摘要信息
  - [ ] 包含所有出现的漏洞列表

---

## 第三阶段: GitHub Runner 部署

### 选择部署方式

**选项 A: Docker 容器（推荐）**

- [ ] 创建 Runner 专用目录
  ```bash
  mkdir -p /opt/github-runner
  cd /opt/github-runner
  ```

- [ ] 创建 `.env` 配置文件
  ```bash
  cat > .env << 'EOF'
  REPO_URL=https://github.com/cpWhitecat/devops
  GITHUB_TOKEN=ghp_your_token_here_replace_with_real_token
  RUNNER_NAME=centos-runner-01
  RUNNER_LABELS=linux,docker,sqlmap
  EOF
  ```

- [ ] 验证 `.env` 文件
  ```bash
  cat .env
  # 确认 GITHUB_TOKEN 值正确
  grep "^GITHUB_TOKEN=" .env | grep "^GITHUB_TOKEN=ghp_"
  ```

- [ ] 启动 Runner 容器
  ```bash
  docker run -d \
    --name github-runner \
    --restart always \
    --env-file /opt/github-runner/.env \
    -v /var/run/docker.sock:/var/run/docker.sock \
    myoung34/github-runner:latest
  ```

- [ ] 验证容器正在运行
  ```bash
  docker ps | grep github-runner
  docker logs github-runner | tail -20
  ```

**选项 B: 原生二进制**

- [ ] 从 GitHub 获取下载链接
  ```
  GitHub → Settings → Actions → Runners → New self-hosted runner
  (获取 Linux x64 的下载链接)
  ```

- [ ] 下载并提取 Runner
  ```bash
  mkdir -p /opt/github-runner
  cd /opt/github-runner
  curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.x.x/actions-runner-linux-x64-2.x.x.tar.gz
  tar xzf runner.tar.gz
  ```

- [ ] 配置 Runner
  ```bash
  ./config.sh --url https://github.com/cpWhitecat/devops \
    --token GHXXX_token_from_github \
    --name centos-runner-01 \
    --labels linux,docker,sqlmap \
    --unattended \
    --runasservice
  ```

- [ ] 启动 Runner 服务
  ```bash
  sudo systemctl start actions.runner.cpWhitecat-devops.centos-runner-01.service
  sudo systemctl enable actions.runner.cpWhitecat-devops.centos-runner-01.service
  ```

- [ ] 验证服务运行
  ```bash
  systemctl status actions.runner.cpWhitecat-devops.centos-runner-01.service
  journalctl -u actions.runner.cpWhitecat-devops.centos-runner-01.service -n 20
  ```

### 验证 Runner 在线

- [ ] 在 GitHub 中检查 Runner 状态
  ```
  GitHub → Settings → Actions → Runners
  → 查看 "centos-runner-01" 状态是否为 "Idle"
  ```
- [ ] 如果显示离线，查看日志并排查
  ```bash
  docker logs github-runner -n 100  # Docker 方式
  journalctl -xe  # 原生二进制方式
  ```
- [ ] Runner 成功连接后显示"✓ Idle"

---

## 第四阶段: 工作流验证

### 手动触发工作流

- [ ] 在 GitHub 网页界面触发
  ```
  GitHub → Actions → 选择 "Security Scan with SQLMap"
  → "Run workflow" → 选择分支: main → 点击 "Run"
  ```

- [ ] 或使用命令行（需要安装 GitHub CLI）
  ```bash
  gh workflow run security-scan-runner.yml --ref main
  ```

### 监控工作流执行

- [ ] 在 GitHub Actions 中查看运行
  ```
  GitHub → Actions → 选择正在运行的工作流
  ```

- [ ] 等待工作流完成（通常 2-5 分钟）
  ```
  等待所有步骤完成，查看是否有红色 ✗ 错误
  ```

- [ ] 查看完整日志
  ```
  点击具体的 Job → 查看每个步骤的详细输出
  ```

### 工作流结果验证

要让工作流成功，需要验证：

- [ ] "Build Docker Image" 步骤成功
  - 日志显示 "Successfully tagged security-scanner:latest"

- [ ] "Run SQLMap Scan" 步骤成功
  - 日志显示 SQLMap 命令执行
  - 看到"Starting scan"或类似消息

- [ ] "Generate Report" 步骤成功
  - 日志显示 Python 脚本执行
  - 没有 Python 错误

- [ ] "Upload Artifacts" 步骤成功
  - 日志显示"Uploaded artifact"
  - 可以下载 artifact

---

## 第五阶段: 结果查看与验证

### 下载扫描结果

- [ ] 在 GitHub 中找到 Artifact
  ```
  GitHub → Actions → 选择工作流运行
  → 向下滚动找到 "Artifacts" 部分
  → 点击 "security-scan-results-xxx"
  ```

- [ ] 或使用命令行下载
  ```bash
  gh run download <run-id> -n security-scan-results-xxx
  ```

### 检查扫描报告

- [ ] 解析下载的 artifact
  ```bash
  unzip security-scan-results-xxx.zip
  cd security-scan-results-xxx/
  ls -la
  ```

- [ ] 查看 HTML 报告
  ```bash
  # 在浏览器中打开
  open report.html
  # 或在 Linux 上使用
  firefox report.html
  ```

- [ ] 验证报告内容
  - [ ] 包含"扫描摘要"部分
  - [ ] 显示目标 URL
  - [ ] 显示检测结果（即使是"未发现漏洞"）
  - [ ] 包含"完整输出"日志

- [ ] 查看完整日志
  ```bash
  cat run.log | head -50  # 查看前 50 行
  cat run.log | tail -50  # 查看后 50 行
  grep -i "vulnerability" run.log  # 搜索漏洞
  ```

---

## 第六阶段: 代码提交与自动化触发

### 提交更新到 Git

- [ ] 检查修改状态
  ```bash
  git status
  ```

- [ ] 添加新文件（如果有）
  ```bash
  git add test-system.sh WORKFLOW_PROCESS.md QUICK_COMMANDS.md TROUBLESHOOTING.md
  git add .gitignore  # 如果更新了
  ```

- [ ] 创建提交
  ```bash
  git commit -m "docs: add comprehensive workflow and testing documentation"
  ```

- [ ] 推送到 GitHub
  ```bash
  git push origin main
  ```

### 验证自动化触发

- [ ] 推送完成后，GitHub Action 自动触发
  ```
  GitHub → Actions → 查看新的工作流运行
  ```

- [ ] 等待工作流完成
  - [ ] Docker 镜像构建成功
  - [ ] SQLMap 扫描执行成功
  - [ ] 报告生成成功

- [ ] 验证结果
  - [ ] 可以下载 artifact
  - [ ] report.html 内容正常

---

## 第七阶段: 定期维护

### 每周检查

- [ ] Runner 状态是否在线
  ```bash
  GitHub Settings → Actions → Runners → 检查状态
  ```

- [ ] Docker 容器是否正常运行
  ```bash
  docker ps | grep github-runner
  ```

- [ ] 最近的工作流运行是否成功
  ```bash
  GitHub → Actions → 查看最近 5 个运行
  ```

### 每月维护

- [ ] 清理 Docker 缓存
  ```bash
  docker system prune -a --volumes
  ```

- [ ] 更新 GitHub Runner（如有新版本）
  ```bash
  docker pull myoung34/github-runner:latest
  docker restart github-runner
  ```

- [ ] 轮换 Personal Access Token（安全最佳实践）
  ```
  GitHub → Settings → Developer settings → Personal access tokens
  → 生成新 token → 更新 .env 或配置
  ```

- [ ] 检查工作流日志是否有错误模式
  ```bash
  GitHub → Actions → 查看失败的工作流
  ```

### 半年检查

- [ ] 审查并更新文档
  - [ ] WORKFLOW_PROCESS.md
  - [ ] TROUBLESHOOTING.md
  - [ ] QUICK_COMMANDS.md

- [ ] 测试灾难恢复流程
  - [ ] 停止 Runner
  - [ ] 清除所有容器
  - [ ] 重新部署（验证可以快速恢复）

---

## 常见问题快速参考

### 如果 Runner 离线

```bash
# Docker 方式
docker logs github-runner -n 50
docker restart github-runner

# 原生方式
journalctl -u actions.runner.* -n 50
systemctl restart actions.runner.cpWhitecat-devops.centos-runner-01.service
```

### 如果扫描超时

```bash
# 增加超时时间（在工作流文件中）
timeout-minutes: 30

# 或使用更快的扫描设置
-e LEVEL="1" -e RISK="1" -e THREADS="5"
```

### 如果报告为空

```bash
# 检查 run.log 是否存在
ls -la ./scans/run.log

# 重新运行报告生成脚本
docker run --rm -v $(pwd)/scans:/scans security-scanner:latest \
  python3 /app/generate_report.py
```

### 如果无法连接 GitHub

```bash
# 测试网络
ping github.com
curl -I https://api.github.com

# 检查 Token 有效性
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

---

## 完成标志

当以下所有项都打勾时，整个系统已成功部署:

```
□ 所有测试通过 (test-system.sh ✓)
□ SQLMap 镜像成功构建
□ 本地扫描测试成功
□ Runner 在线且状态为 Idle
□ 手动工作流运行成功
□ 能够下载并查看报告
□ 代码 Push 自动触发工作流
□ 最终报告包含所有预期信息
```

✅ **完成!** 你的 SQLMap 安全扫描平台已完全就绪。

---

## 下一步建议

1. **定义扫描目标列表**
   - 内部应用程序 URL
   - 定期扫描的客户端环境
   - 测试和生产环境分离

2. **配置通知**
   - Slack/钉钉集成
   - 邮件报告
   - 自动 PR 评论

3. **性能优化**
   - 缓存 Docker 层以加快构建
   - 并行运行多个扫描任务
   - 使用 workflow_dispatch 输入参数

4. **安全加固**
   - 定期轮换 Token
   - 限制 Runner 权限
   - 使用私有 Runner 标签

5. **扩展功能**
   - 集成其他安全工具（OWASP ZAP 等）
   - 生成趋势图表和历史报告
   - 自动化漏洞补救

---

**最后更新**: 2026-03-26 | **维护者**: cpWhitecat

**需要帮助?** 查看:
- [QUICK_COMMANDS.md](QUICK_COMMANDS.md) - 快速命令参考
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查指南
- [WORKFLOW_PROCESS.md](WORKFLOW_PROCESS.md) - 详细流程说明
