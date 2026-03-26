#!/bin/bash

# 🧪 SQLMap 安全扫描平台 - 完整系统测试脚本
# 用法: bash test-system.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((PASSED++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# ====================================
# 测试 1: 检查 Docker 安装
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 1: Docker 环境检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker 已安装: $DOCKER_VERSION"
else
    log_error "Docker 未安装"
    exit 1
fi

# ====================================
# 测试 2: 检查 Docker Daemon 运行
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 2: Docker Daemon 检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if docker info &> /dev/null; then
    log_success "Docker Daemon 正在运行"
else
    log_error "Docker Daemon 未运行或无权限"
    exit 1
fi

# ====================================
# 测试 3: 检查文件结构
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 3: 项目文件结构检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

FILES_TO_CHECK=(
    "security-scanner/Dockerfile"
    "security-scanner/run_scan.sh"
    "security-scanner/generate_report.py"
    ".github/workflows/security-scan-runner.yml"
    "README.md"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        log_success "文件存在: $file"
    else
        log_error "文件缺失: $file"
    fi
done

# ====================================
# 测试 4: 构建 Docker 镜像
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 4: 构建 SQLMap Docker 镜像${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

IMAGE_NAME="security-scanner:test"

log_info "开始构建镜像: $IMAGE_NAME"
if docker build -t "$IMAGE_NAME" ./security-scanner/ &>> /tmp/docker-build.log; then
    log_success "镜像构建成功"
    
    # 检查镜像大小
    IMAGE_SIZE=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
    log_info "镜像大小: $IMAGE_SIZE"
else
    log_error "镜像构建失败"
    cat /tmp/docker-build.log
    exit 1
fi

# ====================================
# 测试 5: 检查脚本权限
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 5: 脚本权限检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

SCRIPTS=(
    "security-scanner/run_scan.sh"
    "security-scanner/generate_report.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        log_success "脚本可执行: $script"
    else
        log_warning "脚本不可执行，尝试修复: $script"
        chmod +x "$script"
        log_success "已设置执行权限"
    fi
done

# ====================================
# 测试 6: Python 依赖检查（容器内）
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 6: Python 环境检查（容器内）${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

log_info "检查容器内 Python 环境..."
if docker run --rm "$IMAGE_NAME" python3 -c "import sys; print(f'Python {sys.version.split()[0]}')" &> /tmp/python-check.log; then
    PYTHON_VERSION=$(cat /tmp/python-check.log)
    log_success "Python 环境正常: $PYTHON_VERSION"
else
    log_error "Python 环境检查失败"
    cat /tmp/python-check.log
fi

# ====================================
# 测试 7: SQLMap 安装检查（容器内）
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 7: SQLMap 安装检查（容器内）${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

log_info "检查 SQLMap 版本..."
if docker run --rm "$IMAGE_NAME" sqlmap --version &> /tmp/sqlmap-check.log; then
    SQLMAP_VERSION=$(head -n 1 /tmp/sqlmap-check.log)
    log_success "SQLMap 已安装: $SQLMAP_VERSION"
else
    log_error "SQLMap 检查失败"
    cat /tmp/sqlmap-check.log
fi

# ====================================
# 测试 8: 环境变量检查
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 8: 环境变量检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

# 创建测试 env 文件
cat > /tmp/test.env << 'EOF'
TARGET=http://scanme.nmap.org
LEVEL=1
RISK=1
EOF

if docker run --rm --env-file /tmp/test.env "$IMAGE_NAME" env | grep -q "TARGET="; then
    log_success "环境变量加载成功"
else
    log_error "环境变量加载失败"
fi

# ====================================
# 测试 9: 模拟扫描（不执行真实扫描）
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 9: 容器启动和输出检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

SCANS_DIR="/tmp/test-scans"
mkdir -p "$SCANS_DIR"

log_info "运行测试容器..."
if docker run --rm \
    -e TARGET="http://httpbin.org/get" \
    -e LEVEL="1" \
    -e RISK="1" \
    -v "$SCANS_DIR:/scans" \
    "$IMAGE_NAME" bash -c "echo '[*] Test scan log' > /scans/run.log && exit 0" &> /tmp/container-test.log; then
    
    log_success "容器成功运行"
    
    if [ -f "$SCANS_DIR/run.log" ]; then
        log_success "输出文件成功生成"
    else
        log_error "输出文件未生成"
    fi
else
    log_error "容器运行失败"
    cat /tmp/container-test.log
fi

# ====================================
# 测试 10: GitHub 工作流语法检查
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 10: GitHub 工作流 YAML 检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if command -v yq &> /dev/null; then
    if yq eval '.jobs' .github/workflows/security-scan-runner.yml &> /dev/null; then
        log_success "工作流 YAML 语法正确"
    else
        log_error "工作流 YAML 语法错误"
    fi
else
    log_warning "yq 未安装，跳过 YAML 检查"
fi

# ====================================
# 测试 11: GitHub Runner 检查
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 11: GitHub Runner 状态检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

if command -v gh &> /dev/null; then
    log_info "GitHub CLI 已安装"
    
    if gh auth status &> /dev/null; then
        log_success "GitHub 认证成功"
    else
        log_warning "未认证，请运行: gh auth login"
    fi
else
    log_warning "GitHub CLI 未安装，跳过 Runner 检查"
fi

# ====================================
# 测试 12: 网络连接检查
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试 12: 网络连接检查${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

URLS=(
    "https://github.com"
    "https://api.github.com"
    "http://scanme.nmap.org"
)

for url in "${URLS[@]}"; do
    if timeout 5 curl -s -o /dev/null -w "%{http_code}" "$url" &> /dev/null; then
        log_success "可连接: $url"
    else
        log_warning "无法连接: $url（可能是网络问题）"
    fi
done

# ====================================
# 清理临时文件和镜像
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}清理临时文件${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

rm -f /tmp/docker-build.log /tmp/python-check.log /tmp/sqlmap-check.log /tmp/test.env /tmp/container-test.log
rm -rf "$SCANS_DIR"

log_info "临时文件已清理"

# ====================================
# 测试总结
# ====================================
echo ""
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}测试总结${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"

TOTAL=$((PASSED + FAILED))
echo ""
echo -e "总测试数: ${BLUE}$TOTAL${NC}"
echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ 所有测试通过！系统就绪。${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 部署 GitHub Runner: docker run -d --env-file .env myoung34/github-runner:latest"
    echo "  2. 在 GitHub Settings → Actions → Runners 中验证 Runner 在线"
    echo "  3. Push 代码或手动触发工作流进行测试"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}════════════════════════════════════════${NC}"
    echo -e "${RED}✗ 有 $FAILED 个测试失败${NC}"
    echo -e "${RED}════════════════════════════════════════${NC}"
    exit 1
fi
