# 🐳 myoung34/github-runner Docker 部署指南

使用预制的 Docker 镜像 `myoung34/github-runner:latest` 快速部署 GitHub Actions Self-Hosted Runner。

## 📋 前置条件

- ✅ CentOS 服务器
- ✅ Docker 已安装
- ✅ GitHub 仓库访问权限
- ✅ GitHub Personal Access Token

---

## 🚀 快速开始（3 步）

### ① 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env
```

编辑内容：
```bash
GITHUB_URL=https://github.com/cpWhitecat/devops
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx  # 从 GitHub 获取
RUNNER_NAME=centos-runner-01
RUNNER_LABELS=linux,docker,sqlmap
SCAN_TARGET=http://your-target.com
```

### ② 获取 GitHub Token

1. 进入 GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. 点击 **Generate new token**
3. 选择 **Fine-grained personal access tokens**
4. 配置权限：
   - ✅ `repo` (完整权限)
   - ✅ `workflow`
   - ✅ `admin:org_hook`
5. 复制 Token 到 `.env` 文件中的 `GITHUB_TOKEN`

### ③ 启动 Runner

```bash
# 添加执行权限
chmod +x start-docker-runner.sh

# 运行启动脚本
bash start-docker-runner.sh
```

脚本会自动：
- 检查 Docker 环境
- 拉取（如需要）`myoung34/github-runner:latest` 镜像
- 创建并启动容器
- 验证容器状态

---

## ✅ 验证 Runner 在线

1. 进入 GitHub 仓库 → **Settings** → **Actions** → **Runners**
2. 应该看到 `centos-runner-01` 显示为 **Idle** 状态（1-2 分钟后）

---

## 🔧 配置文件详解

### `.env` 环境变量

| 变量 | 说明 | 示例 |
|-----|------|------|
| `GITHUB_URL` | 仓库 URL | `https://github.com/cpWhitecat/devops` |
| `GITHUB_TOKEN` | GitHub 令牌 | `ghp_xxxx...` |
| `RUNNER_NAME` | Runner 名称 | `centos-runner-01` |
| `RUNNER_GROUP` | Runner 组别 | `Default` |
| `RUNNER_LABELS` | 标签（逗号分隔） | `linux,docker,sqlmap` |
| `RUNNER_WORKDIR` | 工作目录 | `/tmp/runner-work` |
| `DOCKER_HOST` | Docker Socket | `unix:///var/run/docker.sock` |

### myoung34/github-runner 镜像特性

- ✅ 预装 Docker CLI（支持容器内运行 Docker）
- ✅ 支持 Docker-in-Docker（DinD）
- ✅ 自动注册和注销
- ✅ 自动更新 Runner 版本
- ✅ 完整的 GitHub CLI 工具

---

## 🎮 常用命令

### 查看容器状态

```bash
# 查看运行中的容器
docker ps -f name=github-runner

# 查看所有容器（包括停止的）
docker ps -a | grep github-runner

# 查看容器详细信息
docker inspect github-runner-centos-runner-01
```

### 查看日志

```bash
# 查看最后 20 行日志
docker logs github-runner-centos-runner-01 | tail -20

# 实时查看日志
docker logs -f github-runner-centos-runner-01

# 查看特定时间段的日志
docker logs --since 10m github-runner-centos-runner-01
```

### 容器管理

```bash
# 停止容器
docker stop github-runner-centos-runner-01

# 重新启动容器
docker restart github-runner-centos-runner-01

# 删除容器（会注销 Runner）
docker stop github-runner-centos-runner-01
docker rm github-runner-centos-runner-01

# 进入容器交互式 shell
docker exec -it github-runner-centos-runner-01 bash

# 在容器内执行命令
docker exec github-runner-centos-runner-01 docker ps
```

### 手动注册/注销 Runner

```bash
# 进入容器
docker exec -it github-runner-centos-runner-01 bash

# 注销 Runner（容器内）
cd /actions-runner
./config.sh remove --token <TOKEN>

# 重新注册
./config.sh --url https://github.com/cpWhitecat/devops --token <NEW_TOKEN> --name centos-runner-01 --unattended
```

---

## 🐳 Docker 容器启动详解

### 启动脚本做了什么

```bash
docker run -d \
    --name github-runner-centos-runner-01 \           # 容器名称
    --restart always \                                 # 政策：总是重启
    -e GITHUB_URL="..." \                              # 环境变量
    -e GITHUB_TOKEN="..." \
    -e RUNNER_NAME="..." \
    -e RUNNER_WORKDIR="/tmp/runner-work" \
    -v /tmp/runner-work:/tmp/runner-work \             # 工作目录挂载
    -v /var/run/docker.sock:/var/run/docker.sock \     # Docker Socket（允许容器内调用 docker）
    myoung34/github-runner:latest
```

### 参数说明

- `-d`：后台运行
- `--name`：容器名称
- `--restart always`：容器退出时自动重启（CentOS 重启后也会重启）
- `-e`：环境变量
- `-v`：卷挂载
  - `/tmp/runner-work` → Runner 工作目录
  - `/var/run/docker.sock` → Docker Socket（Docker-in-Docker）

---

## 📊 监控和维护

### 监控容器资源使用

```bash
# 实时监控
docker stats github-runner-centos-runner-01

# 查看内存使用
docker stats --no-stream github-runner-centos-runner-01
```

### 检查 Runner 连接状态

```bash
# 在容器内检查
docker exec github-runner-centos-runner-01 cat /actions-runner/.runner

# 查看注册的 Runner 信息
docker exec github-runner-centos-runner-01 ls -la /actions-runner/
```

### 定期清理

```bash
# 清理未使用的 Docker 资源
docker system prune -a

# 清理容器工作目录（谨慎！）
sudo rm -rf /tmp/runner-work/*
```

---

## 🔄 更新和升级

### 更新 Docker 镜像

```bash
# 拉取最新镜像
docker pull myoung34/github-runner:latest

# 停止旧容器
docker stop github-runner-centos-runner-01
docker rm github-runner-centos-runner-01

# 运行新镜像
bash start-docker-runner.sh
```

### 使用特定版本

编辑 `start-docker-runner.sh`，将：
```bash
myoung34/github-runner:latest
```

改为：
```bash
myoung34/github-runner:ubuntu-focal  # 或其他版本
```

查看可用版本：https://hub.docker.com/r/myoung34/github-runner/tags

---

## 🛠️ 故障排除

### 问题：容器无法启动

```bash
# 查看错误日志
docker logs github-runner-centos-runner-01

# 常见原因：
# 1. Docker Socket 不存在
# 2. 权限不足
# 3. Token 无效
```

### 问题：Runner 显示 Offline

```bash
# 检查容器状态
docker ps -f name=github-runner-centos-runner-01

# 重启容器
docker restart github-runner-centos-runner-01

# 查看实时日志
docker logs -f github-runner-centos-runner-01

# 检查网络连接
docker exec github-runner-centos-runner-01 curl -I https://api.github.com
```

### 问题：容器退出或频繁重启

```bash
# 查看完整日志
docker logs github-runner-centos-runner-01

# 查看退出码
docker inspect github-runner-centos-runner-01 | grep -i exitcode

# 常见原因：
# 1. Token 过期
# 2. 网络问题
# 3. 磁盘满
```

### 问题：Docker-in-Docker 不工作

```bash
# 验证 Docker Socket 挂载
docker exec github-runner-centos-runner-01 docker ps

# 如果失败，检查：
# 1. Docker Socket 权限
# 2. SELinux 配置（CentOS）
sudo setenforce 0  # 临时关闭 SELinux（不推荐用于生产）
```

---

## ⚙️ 高级配置

### 使用多个 Runner

创建多个 `.env` 文件：

```bash
cp .env.example .env.runner1
cp .env.example .env.runner2

# 编辑每个文件，设置不同的 RUNNER_NAME
nano .env.runner1
nano .env.runner2

# 启动多个容器
RUNNER_NAME=centos-runner-01 bash start-docker-runner.sh
RUNNER_NAME=centos-runner-02 bash start-docker-runner.sh
```

或修改启动脚本以支持参数。

### 自定义工作目录

编辑 `.env`：
```bash
RUNNER_WORKDIR=/data/runner-work  # 使用高可用存储
```

### 日志持久化

创建日志卷：
```bash
docker volume create runner-logs

# 修改启动脚本，添加：
-v runner-logs:/runner-logs \
```

---

## 📚 相关文档

- **[GitHub Runners 官方文档](https://docs.github.com/en/actions/hosting-your-own-runners)**
- **[myoung34/github-runner GitHub](https://github.com/myoung34/docker-github-actions-runner)**
- **[Docker 官方文档](https://docs.docker.com/)**

---

## 📞 快速参考

| 需求 | 命令 |
|------|------|
| 启动 Runner | `bash start-docker-runner.sh` |
| 查看状态 | `docker ps -f name=github-runner` |
| 查看日志 | `docker logs -f github-runner-centos-runner-01` |
| 停止 Runner | `docker stop github-runner-centos-runner-01` |
| 重启 Runner | `docker restart github-runner-centos-runner-01` |
| 删除 Runner | `docker rm github-runner-centos-runner-01` |
| 进入容器 | `docker exec -it github-runner-centos-runner-01 bash` |
| 更新镜像 | `docker pull myoung34/github-runner:latest` |
| 查看资源 | `docker stats github-runner-centos-runner-01` |

---

**最后更新**: 2026-03-26 | **镜像**: myoung34/github-runner:latest
