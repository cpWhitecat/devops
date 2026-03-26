# 🔧 故障排查指南

## 快速诊断流程

```
系统启动失败?
    ↓
[选择问题类型]
    ├── Runner 问题 → Section A
    ├── Docker 问题 → Section B
    ├── SQLMap 问题 → Section C
    ├── 工作流问题 → Section D
    └── 网络问题 → Section E
```

---

## Section A: Runner 相关问题

### A1: Runner 显示 "Offline" 或 "Unknown"

**症状**:
- GitHub Settings → Actions → Runners 中显示离线
- 工作流任务一直等待

**诊断步骤**:
```bash
# 1. 检查 Runner 进程
docker ps | grep github-runner
systemctl status actions.runner.cpWhitecat-devops.* 2>/dev/null

# 2. 查看 Runner 日志
docker logs github-runner -n 50
journalctl -u actions.runner.cpWhitecat-devops.* -n 50
```

**常见原因和解决方案**:

| 原因 | 症状 | 解决方案 |
|------|------|--------|
| 容器停止 | `docker ps` 看不到容器 | `docker restart github-runner` |
| Token 过期 | 日志显示 "Invalid token" | 生成新 Token 并重启 Runner |
| 网络断连 | 日志显示 "Connection refused" | `ping github.com` 检查网络 |
| 权限错误 | 日志显示 "Permission denied" | 使用 `--user root` 运行 |
| 配置错误 | 日志显示 "Invalid configuration" | 验证 `.env` 文件中的 REPO_URL 和 TOKEN |

**修复步骤**:
```bash
# 方案 1: 重启 Runner（快速）
docker restart github-runner
sleep 10
docker logs github-runner | grep -i "listening"

# 方案 2: 完全重新部署
docker rm -f github-runner
docker run -d \
  --name github-runner \
  --restart always \
  --env-file /opt/github-runner/.env \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest

# 方案 3: 更新 Token 并重启
NEW_TOKEN="ghp_your_new_token"
sed -i "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$NEW_TOKEN/" /opt/github-runner/.env
docker restart github-runner
```

---

### A2: Runner 进程崩溃（循环重启）

**症状**:
- `docker ps` 显示 Restarting
- 日志中错误堆积

**诊断**:
```bash
# 检查崩溃日志
docker logs github-runner --tail 100

# 查看重启历史
docker inspect github-runner | grep -A 20 "RestartCount"
```

**解决方案**:
```bash
# 1. 停止自动重启
docker update --restart=no github-runner

# 2. 手动调试
docker rm github-runner
docker run -it --rm \
  --env-file /opt/github-runner/.env \
  myoung34/github-runner:latest \
  bash

# 3. 检查环境变量
env | grep -E "GITHUB|REPO"

# 4. 确认 /var/run/docker.sock 可用
ls -la /var/run/docker.sock

# 5. 重新启动（带调试日志）
docker run -d \
  --name github-runner-debug \
  -e DEBUG=true \
  --env-file /opt/github-runner/.env \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest
docker logs -f github-runner-debug
```

---

### A3: Runner 不能执行 Docker 命令

**症状**:
- 工作流中 `docker` 命令失败
- 错误: "Cannot connect to Docker daemon"

**根本原因**:
- `/var/run/docker.sock` 权限不足
- 或者 Docker socket 路径不正确

**修复**:
```bash
# 1. 检查文件权限
ls -la /var/run/docker.sock

# 2. 调整权限（不推荐生产环境）
sudo chmod 666 /var/run/docker.sock

# 3. 或添加 Runner 用户到 docker 组
getent group docker || groupadd docker
usermod -aG docker runner  # 如果是原生部署

# 4. 重启 Docker 服务
sudo systemctl restart docker

# 5. 重启 Runner
docker restart github-runner
```

---

## Section B: Docker 相关问题

### B1: Docker 镜像构建失败

**症状**:
- `docker build` 返回非零错误码
- 工作流停止在构建阶段

**诊断**:
```bash
# 1. 重新构建并查看详细日志
docker build -t security-scanner:latest ./security-scanner/ 2>&1 | tee build.log

# 2. 检查 Dockerfile 语法
docker run --rm -i hadolint/hadolint < ./security-scanner/Dockerfile

# 3. 检查依赖包
head -20 ./security-scanner/Dockerfile
```

**常见原因**:

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| `Cannot find package` | pip install 失败 | 检查网络，或改用国内源 |
| `base image not found` | FROM 镜像不存在 | 运行 `docker pull python:3.11-slim` |
| `permission denied` | 文件权限问题 | 在 Dockerfile 中添加 `RUN chmod +x` |
| `disk space` | 磁盘满 | 运行 `docker system prune` |

**修复步骤**:
```bash
# 1. 清理 Docker 缓存
docker system prune -a --volumes -f

# 2. 使用国内源（如果网络慢）
# 编辑 ./security-scanner/Dockerfile
# 在 FROM 后面添加:
# RUN pip install -i https://pypi.tsinghua.edu.cn/simple sqlmap

# 3. 重新构建
docker build --no-cache -t security-scanner:latest ./security-scanner/

# 4. 验证镜像
docker images | grep security-scanner
docker inspect security-scanner:latest
```

---

### B2: 容器启动失败

**症状**:
- `docker run` 立即退出
- 无法 exec 到容器

**诊断**:
```bash
# 1. 查看启动日志
docker run --rm security-scanner:latest bash -x 2>&1

# 2. 交互式测试
docker run -it --rm security-scanner:latest /bin/bash
```

**常见原因**:

```bash
# 原因 1: 环境变量缺失
docker run --rm -e TARGET="http://example.com" security-scanner:latest

# 原因 2: 脚本权限问题
docker run --rm security-scanner:latest stat /app/run_scan.sh

# 原因 3: Python 导入错误
docker run --rm security-scanner:latest python3 -c "import sqlmap"
```

---

### B3: 容器内网络问题

**症状**:
- 容器内无法访问外部网址
- SQLMap 扫描超时

**诊断和修复**:
```bash
# 1. 检查容器网络
docker run --rm security-scanner:latest curl -I http://google.com

# 2. 检查 DNS
docker run --rm security-scanner:latest nslookup github.com

# 3. 检查主机网络
ping -c 4 github.com
curl -I https://github.com

# 4. 重启 Docker（在主机上）
sudo systemctl restart docker

# 5. 使用主机网络运行（仅限 Linux）
docker run --rm --network host \
  -e TARGET="http://example.com" \
  security-scanner:latest
```

---

## Section C: SQLMap 相关问题

### C1: SQLMap 命令无效或超时

**症状**:
- `sqlmap: command not found`
- 或扫描一直运行不结束

**诊断**:
```bash
# 1. 检查 SQLMap 安装
docker run --rm security-scanner:latest which sqlmap
docker run --rm security-scanner:latest sqlmap --version

# 2. 检查扫描过程
docker run --rm security-scanner:latest sqlmap -u "http://target.com" --batch --verbose 3

# 3. 添加超时和日志
timeout 60 docker run --rm security-scanner:latest \
  sqlmap -u "$TARGET" --batch --timeout=30 -v 3
```

**解决方案**:
```bash
# 1. 增加超时时间（工作流中）
jobs:
  scan:
    timeout-minutes: 30
    
# 2. 在脚本中添加超时
timeout --signal=TERM 300 sqlmap -u "$TARGET" --batch

# 3. 启用详细日志调试
sqlmap -u "$TARGET" --batch -v 3 > /tmp/sqlmap-debug.log 2>&1
```

---

### C2: 报告生成失败

**症状**:
- `report.html` 文件不存在
- 或内容为空

**诊断**:
```bash
# 1. 检查日志文件
docker run --rm -v $(pwd)/scans:/scans security-scanner:latest \
  bash -c "ls -la /scans/"

# 2. 测试报告生成
docker run --rm -v $(pwd)/scans:/scans security-scanner:latest \
  python3 /app/generate_report.py

# 3. 查看 Python 错误
docker run --rm -v $(pwd)/scans:/scans security-scanner:latest \
  python3 -c "from generate_report import *; print('Import OK')"
```

**常见原因**:

```bash
# 原因 1: run.log 不存在
mkdir -p ./scans
echo "[*] Test" > ./scans/run.log
docker run --rm -v $(pwd)/scans:/scans security-scanner:latest \
  python3 /app/generate_report.py

# 原因 2: Python 脚本有 bug
# 查看脚本第一行的 shebang
head -1 ./security-scanner/generate_report.py

# 原因 3: 权限问题
docker run --rm --user 0 -v $(pwd)/scans:/scans security-scanner:latest \
  python3 /app/generate_report.py
```

---

## Section D: 工作流相关问题

### D1: 工作流任务一直挂起

**症状**:
- GitHub Actions 显示 "In progress" 但不动作
- 工作流任务在等待状态

**原因分析**:
```
在 GitHub UI 中检查:
1. 是否有可用的 Runner?
   Settings → Actions → Runners → 查看状态是否为 Idle
   
2. Runner labels 是否匹配?
   工作流文件: runs-on: [self-hosted, linux, docker]
   Runner 注册时的 labels 必须包含这些

3. 工作流语法是否正确?
   Actions → 查看错误信息
```

**修复步骤**:
```bash
# 1. 验证 Runner 在线
git clone ... && cd repo
gh run list --workflow=security-scan-runner.yml
gh runner list

# 2. 检查 Runner 标签配置
docker inspect github-runner | grep -i "label"
# 或编辑工作流文件改为通用标签:
runs-on: self-hosted

# 3. 手动触发工作流查看错误
gh workflow run security-scan-runner.yml --ref main
gh run view --log
```

---

### D2: 工作流执行失败

**症状**:
- 红色 ✗ 标记在 GitHub Actions
- 工作流中间某步骤失败

**诊断流程**:
```bash
# 1. 查看具体失败的步骤
# GitHub UI → Actions → 选择运行 → 查看详细日志

# 2. 本地重现问题
# 复制工作流中的命令本地运行
docker run --rm \
  -e TARGET="http://scanme.nmap.org" \
  security-scanner:latest

# 3. 查看 Runner 日志
docker logs github-runner | tail -100
```

**常见失败原因**:

| 失败步骤 | 原因 | 解决方案 |
|---------|------|--------|
| Build image | 网络能下载包 | 使用国内源，或本地预构建 |
| Run scan | 目标不可达 | 检查网络，使用公开目标测试 |
| Upload artifact | 磁盘满 | `docker system prune` |
| Post to GitHub | Token 无效 | 更新 GITHUB_TOKEN |

---

### D3: 工作流报错 "Workflow file not valid YAML"

**症状**:
- 工作流文件无法被 GitHub 识别
- 错误: "workflow is not valid"

**诊断**:
```bash
# 1. 本地验证 YAML 语法
# 使用 online YAML validator 或:
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/security-scan-runner.yml'))"

# 2. 检查缩进（YAML 严格要求）
cat .github/workflows/security-scan-runner.yml | od -c | head -50

# 3. 使用 yamllint 工具
yamllint .github/workflows/security-scan-runner.yml
```

**常见问题**:
```yaml
# ❌ 错误: 混合 Tab 和空格
jobs:
	scan:    # 这是 Tab，不是空格!
  
# ✅ 正确: 只用空格（通常 2 或 4）
jobs:
  scan:
    runs-on: self-hosted
```

---

## Section E: 网络相关问题

### E1: GitHub 连接超时

**症状**:
- 无法克隆 GitHub 仓库
- Runner 无法从 GitHub 拉取任务

**诊断**:
```bash
# 1. 基本网络测试
ping -c 4 github.com
curl -I https://github.com
nslookup github.com

# 2. SSH 连接测试（如果使用 SSH）
ssh -v git@github.com
ssh -T git@github.com  # 验证认证

# 3. HTTPS 连接测试
curl -v https://api.github.com/zen
```

**解决方案**:
```bash
# 1. 检查 DNS
cat /etc/resolv.conf
ping 8.8.8.8  # Google DNS

# 2. 更换 DNS（CentOS）
cat > /etc/resolv.conf << 'EOF'
nameserver 8.8.8.8
nameserver 1.1.1.1
EOF

# 3. 检查防火墙
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 4. 配置代理（如果需要）
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
git config --global http.proxy http://proxy:8080
```

---

### E2: npm/pip 包下载超时

**症状**:
- Docker build 中 `pip install` 超时
- 工作流中软件包下载缓慢

**解决方案**:
```bash
# 1. 使用国内源（临时）
pip install -i https://pypi.tsinghua.edu.cn/simple sqlmap

# 2. 修改 Dockerfile 使用国内源
# 编辑 ./security-scanner/Dockerfile
RUN pip install -i https://pypi.tsinghua.edu.cn/simple sqlmap

# 3. 或配置 pip 永久源（主机）
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tsinghua.edu.cn/simple
EOF

# 4. 增加超时时间
pip install --default-timeout=1000 sqlmap
```

---

### E3: 扫描目标不可达

**症状**:
- SQLMap 报错 "target URL content is empty"
- 或完全超时

**诊断路程**:
```bash
# 1. 从 Runner 机器测试连接
curl -I http://target.com
telnet target.com 80

# 2. 从容器内测试
docker run --rm security-scanner:latest curl -I http://target.com

# 3. 检查防火墙规则
sudo iptables -L -n | grep target-port

# 4. 检查 DNS 解析
docker run --rm security-scanner:latest nslookup target.com
```

**解决方案**:
```bash
# 1. 允许出站连接
sudo firewall-cmd --permanent --add-rich-rule \
  'rule family="ipv4" destination address="0.0.0.0/0" accept'
sudo firewall-cmd --reload

# 2. 使用公开目标测试
TARGET="http://scanme.nmap.org"

# 3. 增加 SQLMap 超时
sqlmap -u "$TARGET" --batch --timeout=30 --retries=3
```

---

## 快速排查流程表

```
问题: 系统无法工作

Step 1: 是否能 Docker?
  └─ 否 → 安装 Docker 并启动

Step 2: 是否能运行容器?
  docker run --rm hello-world
  └─ 否 → 检查 Docker daemon 和权限

Step 3: 能否构建镜像?
  docker build -t test ./security-scanner/
  └─ 否 → 查看构建日志，检查依赖

Step 4: 容器能否运行扫描?
  docker run --rm -e TARGET="..." security-scanner:latest
  └─ 否 → 检查环境变量和网络

Step 5: Runner 是否在线?
  GitHub Settings → Actions → Runners → 检查状态
  └─ 否 → 重启 Runner

Step 6: 工作流是否成功?
  GitHub Actions → 查看运行历史和日志
  └─ 否 → 查看工作流 YAML 和任务日志

✓ 所有通过 → 系统就绪！
```

---

## 日志收集命令

当需要寻求帮助时，收集这些日志信息:

```bash
#!/bin/bash
# 收集诊断信息

echo "=== 系统信息 ===" > diagnosis.log
uname -a >> diagnosis.log
docker --version >> diagnosis.log

echo -e "\n=== Docker 状态 ===" >> diagnosis.log
docker ps -a >> diagnosis.log
docker images >> diagnosis.log

echo -e "\n=== Runner 日志 ===" >> diagnosis.log
docker logs github-runner -n 100 >> diagnosis.log 2>&1

echo -e "\n=== 容器测试 ===" >> diagnosis.log
docker run --rm security-scanner:latest sqlmap --version >> diagnosis.log 2>&1

echo -e "\n=== 网络测试 ===" >> diagnosis.log
ping -c 3 github.com >> diagnosis.log 2>&1
curl -I https://api.github.com >> diagnosis.log 2>&1

echo -e "\n=== 文件检查 ===" >> diagnosis.log
ls -la .github/workflows/ >> diagnosis.log
ls -la security-scanner/ >> diagnosis.log

cat diagnosis.log
```

---

**最后更新**: 2026-03-26 | **维护者**: cpWhitecat
