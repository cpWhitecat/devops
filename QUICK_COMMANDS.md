# 🎯 关键命令速查表

## 🔧 Runner 部署

### 方式 A: Docker 容器（推荐快速）
```bash
# 1. 登录服务器
ssh root@centos-server

# 2. 创建 .env 文件
cat > /opt/github-runner/.env << 'EOF'
REPO_URL=https://github.com/cpWhitecat/devops
GITHUB_TOKEN=ghp_your_token_here
RUNNER_NAME=centos-runner-01
RUNNER_LABELS=linux,docker,sqlmap
EOF

# 3. 启动 Runner 容器
docker run -d \
  --name github-runner \
  --restart always \
  --env-file /opt/github-runner/.env \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest

# 4. 验证 Runner 在线
docker logs github-runner  # 查看日志
docker ps | grep github-runner  # 检查容器状态
```

### 方式 B: 原生二进制（推荐稳定）
```bash
# 1. 下载 Runner（在 GitHub Settings → Actions → Runners 中获取链接）
mkdir -p /opt/github-runner && cd /opt/github-runner
curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.x.x/actions-runner-linux-x64-2.x.x.tar.gz
tar xzf runner.tar.gz

# 2. 配置 Runner
./config.sh --url https://github.com/cpWhitecat/devops \
  --token GHXXX_your_token \
  --name centos-runner-01 \
  --unattended \
  --runasservice

# 3. 启动服务
sudo systemctl start actions.runner.cpWhitecat-devops.centos-runner-01.service
sudo systemctl enable actions.runner.cpWhitecat-devops.centos-runner-01.service

# 4. 验证 Runner 在线
# GitHub Settings → Actions → Runners → 检查 "Idle" 状态
```

---

## 🐳 SQLMap 容器

### 构建镜像
```bash
cd /path/to/devops
docker build -t security-scanner:latest ./security-scanner/
```

### 本地测试扫描
```bash
# 创建输出目录
mkdir -p ./scans

# 运行扫描容器（使用公共测试目标）
docker run --rm \
  -e TARGET="http://scanme.nmap.org" \
  -e LEVEL="1" \
  -e RISK="1" \
  -v $(pwd)/scans:/scans \
  security-scanner:latest

# 查看报告
cat ./scans/report.html  # 或用浏览器打开
```

### 扫描参数
```bash
# LEVEL: 1-5（深度）
# RISK: 1-3（风险等级）
# THREADS: 1-10（并发线程数）

# 快速扫描
docker run --rm -e TARGET="http://target.com" \
  -e LEVEL="1" -e RISK="1" \
  -v $(pwd)/scans:/scans \
  security-scanner:latest

# 深度扫描
docker run --rm -e TARGET="http://target.com" \
  -e LEVEL="5" -e RISK="3" \
  -v $(pwd)/scans:/scans \
  security-scanner:latest
```

---

## 📊 工作流触发

### 自动触发（代码 Push）
```bash
git add .
git commit -m "security update"
git push origin main
# → GitHub Actions 自动触发 security-scan-runner.yml
```

### 手动触发（GitHub UI）
```
GitHub → Actions → "Security Scan with SQLMap"
→ "Run workflow" → 选择分支 → 输入参数 → ✅ Run
```

### 查看工作流运行
```bash
# GitHub UI 方式
Actions → 查看运行历史 → 点击具体运行 → 查看日志

# 命令行方式（需要 GitHub CLI）
gh workflow run security-scan-runner.yml
gh run list --workflow=security-scan-runner.yml
gh run view <run-id> --log
```

---

## 📦 查看结果

### 下载 Artifact
```
GitHub UI:
Actions → 选择工作流运行 → 下载 "security-scan-results-xxx"

命令行:
gh run download <run-id> -n security-scan-results-xxx
```

### 查看报告
```bash
# 解析 artifact
unzip security-scan-results-xxx.zip
cd security-scan-results-xxx
cat report.html  # 在浏览器中打开
```

### 查看原始日志
```bash
cat run.log  # 完整的 SQLMap 输出
grep -i "vulnerable" run.log  # 搜索漏洞
```

---

## 🔍 诊断命令

### 检查 Runner 状态
```bash
# Docker 方式
docker logs github-runner | tail -20  # 查看最后 20 行日志
docker inspect github-runner  # 查看详细信息
docker stats github-runner  # 实时监控

# 原生方式
systemctl status actions.runner.cpWhitecat-devops.centos-runner-01.service
journalctl -u actions.runner.cpWhitecat-devops.centos-runner-01.service -n 50
```

### 检查 Docker 镜像
```bash
docker images | grep security-scanner
docker history security-scanner:latest
```

### 验证环境变量
```bash
# Docker 容器内
docker run -it --rm security-scanner:latest env | grep -E "GITHUB|REPO|TARGET"

# 或通过 Runner 工作流任务
env | grep -E "GITHUB|TARGET"
```

### 测试网络连接
```bash
# 从 Runner 机器
curl -I http://scanme.nmap.org
ping -c 4 github.com
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

---

## 🐛 常见问题快速修复

### ❌ Runner 显示 Offline
```bash
# Docker 方式
docker restart github-runner
docker logs github-runner  # 检查错误

# 原生方式
systemctl restart actions.runner.cpWhitecat-devops.centos-runner-01.service
journalctl -xe  # 查看系统日志
```

### ❌ Token 无效
```bash
# 1. 生成新 Token (GitHub Settings → Developer settings → Personal access tokens)
# 2. 确保权限: repo (完全), workflow, read:org

# 3. 更新 .env
sed -i 's/GITHUB_TOKEN=.*/GITHUB_TOKEN=ghp_new_token/' /opt/github-runner/.env

# 4. 重启 Runner
docker restart github-runner
# 或
systemctl restart actions.runner.cpWhitecat-devops.centos-runner-01.service
```

### ❌ CRLF 行结束错误
```bash
# 修复脚本文件
dos2unix security-scanner/run_scan.sh
dos2unix security-scanner/generate_report.py

# 或使用 sed
sed -i 's/\r$//' security-scanner/run_scan.sh

# 或全局配置 Git
git config --global core.autocrlf input
git config --global core.safecrlf warn
```

### ❌ Docker Socket 权限错误
```bash
# 运行 Runner 时添加权限
docker run -d \
  --name github-runner \
  --user root \  # 或运行 Runner 的用户组
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest

# 或调整 socket 权限
sudo chmod 666 /var/run/docker.sock
```

### ❌ 扫描超时
```bash
# 增加工作流超时时间
# .github/workflows/security-scan-runner.yml
jobs:
  scan:
    timeout-minutes: 30  # 从默认 6 小时改为 30 分钟
    
run: |
  # 增加 SQLMap 超时
  sqlmap -u "$TARGET" --batch --timeout=30 ...
```

---

## 📈 监控和日志

### 查看完整工作流日志
```bash
# GitHub Actions 最详细的日志
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/cpWhitecat/devops/actions/runs" \
  | jq '.workflow_runs[0]'
```

### 实时监控 Runner
```bash
# 终端分屏监控
# 终端 1: watch Docker
watch -n 2 'docker stats --no-stream github-runner'

# 终端 2: 查看日志
docker logs -f github-runner

# 终端 3: 推送代码触发工作流
git push origin main
```

---

## 💾 备份和恢复

### 备份 Runner 配置
```bash
# Docker 方式
docker inspect github-runner > runner-backup.json

# 原生方式
tar -czf github-runner-backup.tar.gz /opt/github-runner/
```

### 恢复 Runner
```bash
# 清除旧 Runner
docker rm -f github-runner  # Docker
systemctl stop actions.runner.* && systemctl disable actions.runner.*  # 原生

# 重新部署
# 使用上面的部署步骤
```

---

## 🎓 完整工作流示例

```bash
# 1️⃣ 准备环境（首次）
ssh root@centos-server
docker run -d --name github-runner --env-file .env myoung34/github-runner:latest

# 2️⃣ 克隆项目
git clone https://github.com/cpWhitecat/devops.git
cd devops

# 3️⃣ 构建 SQLMap 镜像
docker build -t security-scanner:latest ./security-scanner/

# 4️⃣ 本地测试
mkdir -p ./scans
docker run --rm -e TARGET="http://scanme.nmap.org" \
  -v $(pwd)/scans:/scans security-scanner:latest

# 5️⃣ 查看报告
cat ./scans/report.html

# 6️⃣ 提交代码触发工作流
git add .
git commit -m "test: trigger workflow"
git push origin main

# 7️⃣ 查看工作流运行
# GitHub → Actions → 选择运行 → 查看日志

# 8️⃣ 下载结果
gh run download <run-id> -n security-scan-results-xxx
unzip security-scan-results-xxx.zip
```

---

**快速导出为文本**:
```bash
# 将本文档复制到剪贴板（Mac/Linux）
cat QUICK_COMMANDS.md | xclip -selection clipboard

# 打印备用
cat QUICK_COMMANDS.md > commands.txt
```

**最后更新**: 2026-03-26
