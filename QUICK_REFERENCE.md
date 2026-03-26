# 🎯 GitHub Runner Docker 部署 - 快速参考卡

打印或收藏此卡，快速查阅常用命令。

---

## 🐳 启动 Runner（Docker）

```bash
# 1. 配置
cp .env.example .env
nano .env

# 2. 启动
bash start-docker-runner.sh

# 3. 验证
docker ps -f name=github-runner
```

---

## 🔍 日常操作

| 需求 | 命令 |
|------|------|
| 查看日志 | `docker logs -f github-runner-centos-runner-01` |
| 查看状态 | `docker ps -f name=github-runner` |
| 进入容器 | `docker exec -it github-runner-centos-runner-01 bash` |
| 重启容器 | `docker restart github-runner-centos-runner-01` |
| 停止容器 | `docker stop github-runner-centos-runner-01` |
| 删除容器 | `docker rm github-runner-centos-runner-01` |
| 查看资源 | `docker stats github-runner-centos-runner-01` |
| 更新镜像 | `docker pull myoung34/github-runner:latest` |

---

## 🚨 故障排除

### Runner 显示 Offline

```bash
# 查看日志
docker logs github-runner-centos-runner-01 | tail -20

# 重启容器
docker restart github-runner-centos-runner-01

# 等待 1-2 分钟，然后在 GitHub 刷新页面
```

### 容器无法启动

```bash
# 查看错误
docker logs github-runner-centos-runner-01

# 常见原因：
# 1. .env 文件未配置
# 2. GITHUB_TOKEN 无效
# 3. Docker Socket 权限问题

# 解决：
# - 编辑 .env，确认 GITHUB_TOKEN 正确
# - 检查: ls -la /var/run/docker.sock
```

### Docker Socket 权限错误

```bash
# 查看权限
ls -la /var/run/docker.sock

# 如果不是 root 可访问，需要调整 Docker daemon 配置
# 或者容器内使用 docker.sock 需要特殊权限

# 临时解决：
sudo chmod 666 /var/run/docker.sock

# 永久解决：将用户加入 docker 组
sudo usermod -aG docker $USER
```

---

## 📋 .env 文件配置

```bash
# 必需项
GITHUB_URL=https://github.com/cpWhitecat/devops
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 基本配置
RUNNER_NAME=centos-runner-01
RUNNER_GROUP=Default
RUNNER_LABELS=linux,docker,sqlmap

# 工作目录（可选）
RUNNER_WORKDIR=/tmp/runner-work

# 扫描目标（可选，供 workflows 使用）
SCAN_TARGET=http://your-target.com
```

---

## 📊 验证 Runner 在线

1. 进入 GitHub 仓库
2. **Settings** → **Actions** → **Runners**
3. 查找你的 Runner 名称
4. 应显示 **Idle** ✅（不是 Offline）

**如果显示 Offline：**
```bash
docker logs -f github-runner-centos-runner-01
# 查看错误信息，等待 1-2 分钟
# 刷新 GitHub 页面
```

---

## 🎮 运行工作流

1. **Actions** → **Security Scan with SQLMap**
2. **Run workflow**
3. 输入参数（或留空使用默认）
4. 点击 **Run workflow**
5. 等待完成 → 下载 artifact 查看报告

---

## 📚 完整文档

| 场景 | 文档 |
|------|------|
| Docker 详细指南 | [DOCKER_RUNNER_GUIDE.md](./DOCKER_RUNNER_GUIDE.md) |
| 部署方案对比 | [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) |
| 5 分钟快速入门 | [QUICK_START.md](./QUICK_START.md) |
| 完整项目说明 | [README.md](./README.md) |
| 诊断和检查 | `bash diagnose-runner.sh` |

---

## 💾 备份和恢复

### 备份 Runner 配置

```bash
docker inspect github-runner-centos-runner-01 > runner-backup.json
cp .env .env-backup
```

### 恢复

```bash
# 重新部署容器
bash start-docker-runner.sh
```

---

## 🔐 安全提示

- ✅ Token 保存在 `.env` 文件（不要提交到 Git）
- ✅ 使用 Fine-grained Personal Access Token
- ✅ 定期轮换 Token（建议每季度）
- ✅ 将 `.env` 添加到 `.gitignore`

```bash
# 检查 .env 是否在 .gitignore 中
cat .gitignore | grep .env
```

---

## 🚀 快速脚本集合

### 启动和停止

```bash
#!/bin/bash
# save as runner-control.sh

ACTION=${1:-help}

case $ACTION in
  start)
    bash start-docker-runner.sh
    ;;
  stop)
    docker stop github-runner-centos-runner-01
    ;;
  restart)
    docker restart github-runner-centos-runner-01
    ;;
  logs)
    docker logs -f github-runner-centos-runner-01
    ;;
  status)
    docker ps -f name=github-runner
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|logs|status}"
    ;;
esac
```

使用：
```bash
bash runner-control.sh start
bash runner-control.sh logs
bash runner-control.sh status
```

---

## 🔗 相关项目和资源

- **GitHub Actions 官方**: https://docs.github.com/en/actions
- **myoung34/github-runner**: https://github.com/myoung34/docker-github-actions-runner
- **Docker Hub 镜像**: https://hub.docker.com/r/myoung34/github-runner

---

## 📞 获取帮助

```bash
# 系统诊断
bash diagnose-runner.sh

# Docker 日志
docker logs github-runner-centos-runner-01

# 系统日志
sudo journalctl -xe

# GitHub 状态检查
curl -I https://api.github.com
```

---

**最后更新**: 2026-03-26  
**推荐**: 使用 Docker 部署 🐳 - 最简单、最可靠

---

💡 **提示**: 将此卡添加到书签或打印保存！

