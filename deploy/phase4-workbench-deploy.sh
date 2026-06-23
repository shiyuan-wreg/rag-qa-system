#!/usr/bin/env bash
# Phase 4 生产部署脚本（Workbench / VNC 通道专用）
# 由于外部 SSH 暂时无法连入，通过阿里云 Workbench 登录后执行本脚本。
# 用法：
#   1. 用 Workbench 登录服务器
#   2. 把本脚本复制到服务器，例如 /tmp/phase4-workbench-deploy.sh
#   3. chmod +x /tmp/phase4-workbench-deploy.sh
#   4. /tmp/phase4-workbench-deploy.sh your-email@example.com
#
# 注意：
#   - 运行前请先在 /opt/ai-demos/.env 写入真实配置（含 DASHSCOPE_API_KEY）
#   - 建议在 tmux/screen 里执行，防止 Workbench 断开导致部署中断

set -e

DOMAIN="www.shiyuan-wreg.cloud"
EMAIL="${1:-}"
DEPLOY_DIR="/opt/ai-demos"
NODE_VERSION="20.14.0"

if [ -z "$EMAIL" ]; then
    echo "用法: $0 your-email@example.com"
    echo "该邮箱用于 Let's Encrypt 证书申请。"
    exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "本脚本需要 root 权限执行。当前不是 root，请使用 sudo。"
    exit 1
fi

# ------------------------------------------------------------------
# 0. 基础环境
# ------------------------------------------------------------------
echo "==> 更新系统并安装基础工具..."
export DEBIAN_FRONTEND=noninteractive
apt update && apt upgrade -y
apt install -y git curl vim htop ufw ca-certificates gnupg lsb-release

# ------------------------------------------------------------------
# 1. 配置 swap（2GB）
# ------------------------------------------------------------------
if ! swapon --show | grep -q /swapfile; then
    echo "==> 配置 2GB swap..."
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# ------------------------------------------------------------------
# 2. 安装 Docker
# ------------------------------------------------------------------
if ! command -v docker &>/dev/null; then
    echo "==> 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker "$SUDO_USER" 2>/dev/null || true
fi

# 配置国内镜像加速（写入 daemon.json，如果已存在则保留）
if [ ! -f /etc/docker/daemon.json ]; then
    echo "==> 配置 Docker 镜像加速..."
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
    systemctl restart docker
fi

echo "==> Docker 版本:"
docker --version
docker compose version

# ------------------------------------------------------------------
# 3. 安装 Node.js（用于构建前端）
# ------------------------------------------------------------------
if ! command -v node &>/dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" != "20" ]; then
    echo "==> 安装 Node.js ${NODE_VERSION}..."
    mkdir -p /usr/local/lib/nodejs
    curl -fsSL "https://npmmirror.com/mirrors/node/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
        -o /tmp/node.tar.xz
    tar -xJf /tmp/node.tar.xz -C /usr/local/lib/nodejs
    ln -sf "/usr/local/lib/nodejs/node-v${NODE_VERSION}-linux-x64/bin/node" /usr/local/bin/node
    ln -sf "/usr/local/lib/nodejs/node-v${NODE_VERSION}-linux-x64/bin/npm" /usr/local/bin/npm
fi

# 配置 npm 国内镜像
npm config set registry https://registry.npmmirror.com || true

echo "==> Node 版本:"
node -v
npm -v

# ------------------------------------------------------------------
# 4. 拉取代码
# ------------------------------------------------------------------
if [ -d "$DEPLOY_DIR/.git" ]; then
    echo "==> 更新代码..."
    cd "$DEPLOY_DIR"
    git pull origin master
else
    echo "==> 克隆代码到 ${DEPLOY_DIR}..."
    git clone https://github.com/shiyuan-wreg/rag-qa-system.git "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# ------------------------------------------------------------------
# 5. 检查 .env
# ------------------------------------------------------------------
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    echo "========================================"
    echo "错误：未找到 ${DEPLOY_DIR}/.env"
    echo "请在继续前创建该文件，内容示例："
    echo ""
    cat <<'EOF'
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
DOCHUB_PASSWORD=your-strong-password
DOCHUB_ALLOW_PATH_CONVERT=false
DOCHUB_SECRET_KEY=your-random-secret-key
EOF
    echo ""
    echo "可以用以下命令创建："
    echo "  nano ${DEPLOY_DIR}/.env"
    echo "========================================"
    exit 1
fi

echo "==> .env 已存在，检查关键变量..."
grep -E '^DASHSCOPE_API_KEY=' "$DEPLOY_DIR/.env" >/dev/null || {
    echo "错误：.env 中缺少 DASHSCOPE_API_KEY"
    exit 1
}

# ------------------------------------------------------------------
# 6. 构建前端
# ------------------------------------------------------------------
echo "==> 构建前端..."
cd "$DEPLOY_DIR"
bash deploy/build-frontends.sh

# ------------------------------------------------------------------
# 7. 预拉取基础镜像（减少首次 compose 构建失败概率）
# ------------------------------------------------------------------
echo "==> 预拉取 Docker 基础镜像..."
docker pull nginx:1.27-alpine || true
docker pull python:3.12-slim || true
docker pull certbot/certbot:latest || true

# ------------------------------------------------------------------
# 8. 启动服务
# ------------------------------------------------------------------
echo "==> 启动 Docker Compose..."
cd "$DEPLOY_DIR"
docker compose -f deploy/docker-compose.yml up -d --build

echo "==> 等待服务启动..."
sleep 10

# ------------------------------------------------------------------
# 9. 申请 SSL 证书
# ------------------------------------------------------------------
echo "==> 申请 Let's Encrypt SSL 证书..."
cd "$DEPLOY_DIR"

# certbot standalone 会临时占用 80 端口，先停止 nginx 容器避免冲突
docker compose -f deploy/docker-compose.yml stop nginx

bash deploy/init-ssl.sh "$EMAIL"

# 证书申请完成后重新启动 nginx，使其加载新证书
docker compose -f deploy/docker-compose.yml up -d nginx

# ------------------------------------------------------------------
# 10. 基础验证
# ------------------------------------------------------------------
echo ""
echo "==> 部署完成，开始基础验证..."
echo "HTTP 跳转 HTTPS:"
curl -I "http://${DOMAIN}/" || true

echo ""
echo "HTTPS 首页:"
curl -I "https://${DOMAIN}/" || true

echo ""
echo "==> 容器状态:"
docker compose -f deploy/docker-compose.yml ps

echo ""
echo "============================================"
echo "Phase 4 部署脚本执行完毕。"
echo "若验证失败，请检查："
echo "  1. 域名 A 记录是否指向本机公网 IP"
echo "  2. 防火墙是否放行 80/443 端口"
echo "  3. docker compose logs 查看具体错误"
echo "============================================"
