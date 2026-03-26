# 📊 部署方案对比 & 快速命令

## 🎯 选择你的部署方式

| 特性 | 🐳 Docker 容器 | 📦 二进制部署 |
|-----|-----------|---------|
| **部署时间** | 💨 3-5 分钟 | ⏱️ 10-15 分钟 |
| **学习难度** | ⭐ 简单 | ⭐⭐ 中等 |
| **系统隔离** | ✅ 完全隔离 | ❌ 共享系统 |
| **管理复杂度** | ✅ 简单（一条命令） | ⚠️ 需要 systemd |
| **升级难度** | ✅ 极简（重新拉取镜像） | ⚠️ 需要手动更新 |
| **资源占用** | ⚠️ 额外的容器开销 | ✅ 最小化开销 |
| **适合场景** | 快速部署、多实例 | 生产环境、定制化 |
| **推荐指数** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🚀 快速命令参考

### 方案 A：Docker 容器（推荐）

#### 一行命令启动

```bash
# 前提: .env 文件已配置
bash start-docker-runner.sh
```

#### 完整步骤

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件（最重要！）
nano .env
# 需要填写：
#   GITHUB_URL=https://github.com/cpWhitecat/devops
#   GITHUB_TOKEN=ghp_xxxxxxxxxxxx
#   RUNNER_NAME=centos-runner-01

# 3. 启动容器
bash start-docker-runner.sh

# 4. 验证
docker ps -f name=github-runner
```

#### 常见操作

```bash
# 查看日志
docker logs -f github-runner-centos-runner-01

# 停止
docker stop github-runner-centos-runner-01

# 重启
docker restart github-runner-centos-runner-01

# 删除
docker stop github-runner-centos-runner-01 && docker rm github-runner-centos-runner-01

# 进入容器
docker exec -it github-runner-centos-runner-01 bash

# 资源使用情况
docker stats github-runner-centos-runner-01

# 更新镜像
docker pull myoung34/github-runner:latest
bash start-docker-runner.sh
```

---

### 方案 B：二进制部署

#### 自动化脚本启动

```bash
# 需要 root 权限
sudo bash setup-runner.sh

# 按提示输入：
#   GitHub Token
#   Runner 名称
```

#### 完整步骤

```bash
# 1. 进入 GitHub → Settings → Actions → Runners → New self-hosted runner
# 2. 复制提供的命令并在 CentOS 执行

# 大致流程：
mkdir -p /opt/github-runner
cd /opt/github-runner
curl -o actions-runner-linux-x64-2.x.tar.gz -L https://github.com/actions/runner/releases/download/v2.x/actions-runner-linux-x64-2.x.tar.gz
tar xzf ./actions-runner-linux-x64-2.x.tar.gz
./config.sh --url https://github.com/cpWhitecat/devops --token GXXXXXX --name centos-runner-01 --unattended
sudo ./svc.sh install runner
sudo systemctl start actions.runner.cpWhitecat-devops.centos-runner-01.service
```

#### 常见操作

```bash
# 查看状态
sudo systemctl status actions.runner.cpWhitecat-devops.*.service

# 查看日志
sudo journalctl -u actions.runner.cpWhitecat-devops.*.service -f

# 重启
sudo systemctl restart actions.runner.cpWhitecat-devops.*.service

# 停止
sudo systemctl stop actions.runner.cpWhitecat-devops.*.service

# 查看进程
ps aux | grep runner

# 进入 runner 目录
cd /opt/github-runner

# 卸载服务
sudo ./svc.sh uninstall
```

---

## 🔧 故障排除快速命令

### Docker 容器方案

```bash
# Runner 是否运行
docker ps -f name=github-runner

# 为什么容器退出了
docker logs github-runner-centos-runner-01 | tail -50

# Token 是否有效
grep GITHUB_TOKEN .env

# Docker 权限问题
docker run hello-world

# 查看容器网络
docker inspect github-runner-centos-runner-01 | grep -i network

# 重新拉取镜像
docker pull myoung34/github-runner:latest && bash start-docker-runner.sh
```

### 二进制部署方案

```bash
# Runner 进程是否存活
ps aux | grep actions-runner

# Runner 是否在线
systemctl status actions.runner.cpWhitecat-devops.*.service

# 查看完整日志
journalctl -u actions.runner.cpWhitecat-devops.*.service -n 100

# Runner 工作目录
ls -la /opt/github-runner/_work/

# 重启服务
sudo systemctl restart actions.runner.cpWhitecat-devops.*.service

# 检查 GitHub 连接
curl -I https://api.github.com

# Runner 配置文件
cat /opt/github-runner/.runner
```

---

## 📈 性能优化

### Docker 容器

```bash
# 限制内存使用
docker update --memory 4g github-runner-centos-runner-01

# 限制 CPU
docker update --cpus 2 github-runner-centos-runner-01

# 查看资源使用
docker stats --no-stream github-runner-centos-runner-01
```

### 二进制部署

```bash
# 增加 Runner 并发数（编辑配置文件）
# 这通常通过 GitHub UI 配置

# 清理旧的工作目录
sudo rm -rf /opt/github-runner/_work/*

# 监控系统资源
top -p $(pgrep -f actions-runner | tr '\n' ',')
```

---

## 🔐 安全建议

### 通用

- ✅ 使用 Fine-grained Personal Access Token（而非 Classic）
- ✅ 限制 Token 权限：仅选择必需的 scopes
- ✅ 定期轮换 Token（建议每季度）
- ✅ 使用环境变量文件（.env）存储敏感信息
- ✅ 将 `.env` 添加到 `.gitignore` 中

### Docker 容器

```bash
# 不要在 Dockerfile 中硬编码 Token
# 不要在容器日志中显示敏感信息

# 使用 secret 而非环境变量（如果使用 Swarm 或 K8s）
```

### 二进制部署

```bash
# 定期更新 Runner 版本
# 监控系统日志和安全补丁
```

---

## 📚 文档导航

| 需要 | 文档 |
|-----|------|
| 🐳 Docker 部署 | [DOCKER_RUNNER_GUIDE.md](./DOCKER_RUNNER_GUIDE.md) |
| 📦 二进制部署 | [GITHUB_RUNNER_SETUP.md](./GITHUB_RUNNER_SETUP.md) |
| ⚡ 5 分钟快速开始 | [QUICK_START.md](./QUICK_START.md) |
| ✅ 配置检查清单 | [SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md) |
| 🔍 诊断工具 | `bash diagnose-runner.sh` |
| 📖 完整项目说明 | [README.md](./README.md) |

---

## 💡 推荐方案

### 场景 1：快速测试和开发
**使用 Docker 容器** 🐳
```bash
cp .env.example .env && nano .env && bash start-docker-runner.sh
```

### 场景 2：多个 Runner 实例
**使用 Docker 容器**（易于水平扩展）
```bash
# 创建多个 .env 文件，每个配置不同的 RUNNER_NAME
# 分别运行 start-docker-runner.sh 脚本
```

### 场景 3：生产环境、深度定制
**使用二进制部署** 📦
```bash
sudo bash setup-runner.sh
# 或按照 GitHub 提供的详细步骤手动配置
```

### 场景 4：高可用、Kubernetes 环境
**使用 Docker + Orchestration**
```bash
# 考虑使用 Docker Compose 或 Kubernetes
# 参考: https://github.com/myoung34/docker-github-actions-runner
```

---

## 🔄 迁移步骤

### 从二进制迁移到 Docker

```bash
# 1. 获取旧 Runner 名称
systemctl list-units | grep actions.runner

# 2. 从 GitHub 中卸载旧 Runner
# Settings → Actions → Runners → 删除旧 Runner

# 3. 停止并卸载旧服务
sudo systemctl stop actions.runner.cpWhitecat-devops.*.service
sudo /opt/github-runner/svc.sh uninstall

# 4. 启动新的 Docker 容器
cp .env.example .env && nano .env && bash start-docker-runner.sh

# 5. 验证新 Runner 在线
# GitHub Settings → Actions → Runners
```

---

## 📞 获取帮助

```bash
# 快速诊断
bash diagnose-runner.sh

# Docker 帮助
docker help

# GitHub Actions 官方文档
# https://docs.github.com/en/actions/hosting-your-own-runners

# myoung34/github-runner 项目
# https://github.com/myoung34/docker-github-actions-runner
```

---

**最后更新**: 2026-03-26 | **建议**: 使用 Docker 容器方案 🐳
