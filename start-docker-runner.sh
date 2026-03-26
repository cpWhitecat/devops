#!/bin/bash

# GitHub Runner Docker 容器启动脚本
# 用法: bash start-docker-runner.sh

set -euo pipefail

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}GitHub Runner Docker 启动脚本${NC}"
echo -e "${BLUE}================================${NC}\n"

# ============== 检查 .env 文件 ==============
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ 找不到 .env 文件${NC}"
    echo "请首先复制 .env.example 为 .env 文件:"
    echo "  cp .env.example .env"
    echo "然后编辑 .env 文件，填入实际的 GitHub Token"
    exit 1
fi

echo -e "${YELLOW}📋 加载配置文件: $ENV_FILE${NC}"
# 载入环境变量，但排除注释和空行
set -a
source <(grep -v '^#' "$ENV_FILE" | grep -v '^$')
set +a

# ============== 验证必需变量 ==============
echo -e "\n${BLUE}🔍 验证必需配置...${NC}"

MISSING_VARS=0

if [ -z "${GITHUB_TOKEN:-}" ] || [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
    echo -e "${RED}❌ GITHUB_TOKEN 未设置或为默认值${NC}"
    MISSING_VARS=1
else
    echo -e "${GREEN}✅ GITHUB_TOKEN 已配置${NC}"
fi

if [ -z "${GITHUB_URL:-}" ]; then
    echo -e "${RED}❌ GITHUB_URL 未设置${NC}"
    MISSING_VARS=1
else
    echo -e "${GREEN}✅ GITHUB_URL: ${GITHUB_URL}${NC}"
fi

if [ -z "${RUNNER_NAME:-}" ]; then
    echo -e "${RED}❌ RUNNER_NAME 未设置${NC}"
    MISSING_VARS=1
else
    echo -e "${GREEN}✅ RUNNER_NAME: ${RUNNER_NAME}${NC}"
fi

if [ $MISSING_VARS -eq 1 ]; then
    echo -e "\n${RED}请先编辑 .env 文件，填入必需的配置项${NC}"
    exit 1
fi

# ============== 检查 Docker ==============
echo -e "\n${BLUE}🐳 检查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

if ! docker ps &>/dev/null; then
    echo -e "${RED}❌ Docker 守护进程未运行或无权限${NC}"
    echo "请确保运行此脚本时有足够的权限（或使用 sudo）"
    exit 1
fi

echo -e "${GREEN}✅ Docker 已安装并运行中${NC}"

# ============== 检查镜像 ==============
echo -e "\n${BLUE}🔍 检查 GitHub Runner 镜像...${NC}"
if ! docker images | grep -q myoung34/github-runner; then
    echo -e "${YELLOW}⚠️  镜像不存在，开始拉取...${NC}"
    docker pull myoung34/github-runner:latest
    echo -e "${GREEN}✅ 镜像拉取完成${NC}"
else
    echo -e "${GREEN}✅ 镜像已存在${NC}"
    docker images | grep myoung34/github-runner | head -1
fi

# ============== 清理旧容器 ==============
echo -e "\n${BLUE}🧹 检查旧容器...${NC}"
CONTAINER_NAME="github-runner-${RUNNER_NAME}"
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${YELLOW}⚠️  发现旧容器 $CONTAINER_NAME，正在移除...${NC}"
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo -e "${GREEN}✅ 旧容器已清理${NC}"
fi

# ============== 创建工作目录 ==============
echo -e "\n${BLUE}📁 创建工作目录...${NC}"
WORKDIR="${RUNNER_WORKDIR:-/tmp/runner-work}"
mkdir -p "$WORKDIR"
chmod 777 "$WORKDIR"
echo -e "${GREEN}✅ 工作目录: $WORKDIR${NC}"

# ============== 启动容器 ==============
echo -e "\n${BLUE}🚀 启动 GitHub Runner 容器...${NC}"
echo "Container Name: $CONTAINER_NAME"
echo "GitHub URL: $GITHUB_URL"
echo "Runner Name: $RUNNER_NAME"
echo ""

docker run -d \
    --name "$CONTAINER_NAME" \
    --restart always \
    -e GITHUB_URL="$GITHUB_URL" \
    -e GITHUB_TOKEN="$GITHUB_TOKEN" \
    -e RUNNER_NAME="$RUNNER_NAME" \
    -e RUNNER_WORKDIR="$WORKDIR" \
    -e RUNNER_GROUP="${RUNNER_GROUP:-Default}" \
    -e RUNNER_LABELS="${RUNNER_LABELS:-linux,docker}" \
    -e DOCKER_HOST="unix:///var/run/docker.sock" \
    -v "$WORKDIR:$WORKDIR" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    myoung34/github-runner:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 容器启动成功${NC}"
else
    echo -e "${RED}❌ 容器启动失败${NC}"
    exit 1
fi

# ============== 等待并验证 ==============
echo -e "\n${YELLOW}⏳ 等待容器初始化... (5 秒)${NC}"
sleep 5

if docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${GREEN}✅ 容器运行中${NC}"
else
    echo -e "${RED}❌ 容器未运行${NC}"
    echo "查看日志:"
    docker logs "$CONTAINER_NAME" | tail -20
    exit 1
fi

# ============== 显示容器信息 ==============
echo -e "\n${BLUE}📊 容器信息:${NC}"
docker ps -f "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# ============== 显示日志 ==============
echo -e "\n${BLUE}📋 容器启动日志（最后 20 行）:${NC}"
docker logs "$CONTAINER_NAME" | tail -20

# ============== 完成提示 ==============
echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}✅ GitHub Runner 已启动${NC}"
echo -e "${GREEN}================================${NC}\n"

echo -e "${BLUE}📌 后续步骤:${NC}"
echo "1. 进入 GitHub 仓库 Settings → Actions → Runners"
echo "   验证 '$RUNNER_NAME' 显示为 'Idle' 状态（约 1-2 分钟）"
echo ""
echo "2. 查看实时日志:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "3. 停止容器:"
echo "   docker stop $CONTAINER_NAME"
echo ""
echo "4. 重新启动容器:"
echo "   docker restart $CONTAINER_NAME"
echo ""
echo "5. 删除容器:"
echo "   docker stop $CONTAINER_NAME && docker rm $CONTAINER_NAME"
echo ""

echo -e "${BLUE}🔧 常用命令:${NC}"
echo "查看容器状态:"
echo "  docker ps -f name=$CONTAINER_NAME"
echo ""
echo "进入容器:"
echo "  docker exec -it $CONTAINER_NAME bash"
echo ""
echo "查看完整日志:"
echo "  docker logs $CONTAINER_NAME"
echo ""

echo -e "${GREEN}🚀 Ready to run workflows!${NC}\n"
