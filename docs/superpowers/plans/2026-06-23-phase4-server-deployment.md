# Phase 4 服务器部署计划

> 目标：把 ai-demos 完整部署到韩国首尔云服务器，通过 `https://www.shiyuan-wreg.cloud` 对外提供统一作品集门户。
> 计划日期：2026-06-23
> 阻塞项：服务器 SSH 登录凭证（私钥 `.pem` 路径或 root 密码）尚未拿到。

---

## 1. 目标与范围

- **生产域名**：`www.shiyuan-wreg.cloud`
- **服务器 IP**：`8.213.145.110`（阿里云韩国首尔）
- **部署路径**：`/opt/ai-demos`
- **对外服务**：统一门户 `/`、RAG `/rag/`、FC `/fc/`、Nexus `/nexus/`、DocHub `/doctomd/`、学习站 `/learn/`
- **安全**：全站 HTTPS（Let's Encrypt）、HTTP 自动跳转 HTTPS、Docker 容器不直接暴露后端端口

---

## 2. 前置条件

| 条件 | 状态 | 备注 |
|---|---|---|
| 云服务器已购 | 已购 | 阿里云韩国首尔 |
| 域名已购 + A 记录 | 待确认 | 域名 `shiyuan-wreg.cloud`，A 记录需指向 `8.213.145.110` |
| SSH 登录凭证 | 阻塞 | 需私钥 `.pem` 文件路径或 root 密码 |
| 邮箱用于 Let's Encrypt | 已确认 | `hzs1716775963@126.com` |
| 本地代码已合并/推送 | 已推送 | `master` 已推送到 `origin/master` |

**需要你提供**：SSH 私钥文件路径（如 `C:\Users\hzs17\.ssh\ai-demos-key.pem`）或 root 密码。拿到后可直接执行后续步骤。

---

## 3. 服务器初始化

SSH 登录后执行：

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl vim htop ufw

# 配置 swap（2GB，避免内存不足）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 安装 Docker（官方脚本）
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 验证
sudo docker --version
sudo docker compose version
```

---

## 4. 代码与配置部署

### 4.1 拉取代码

```bash
sudo mkdir -p /opt
sudo git clone https://github.com/shiyuan-wreg/rag-qa-system.git /opt/ai-demos
cd /opt/ai-demos
# 后续更新只需：sudo git pull
```

### 4.2 上传 `.env`

从本地仓库根上传 `.env` 到服务器 `/opt/ai-demos/.env`。当前 `.env` 已包含：

```bash
DASHSCOPE_API_KEY=***
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
DOCHUB_PASSWORD=test-password
DOCHUB_ALLOW_PATH_CONVERT=false
DOCHUB_SECRET_KEY=local-dev-secret-key-do-not-use-in-production
```

> 生产环境建议把 `DOCHUB_PASSWORD` 和 `DOCHUB_SECRET_KEY` 改为强密码/随机密钥。

---

## 5. 构建与启动

```bash
cd /opt/ai-demos

# 构建前端
bash deploy/build-frontends.sh

# 首次启动（会构建镜像）
sudo docker compose -f deploy/docker-compose.yml up -d --build
```

---

## 6. SSL 证书申请

确保域名 A 记录已解析到服务器 IP，然后执行：

```bash
cd /opt/ai-demos
bash deploy/init-ssl.sh hzs1716775963@126.com
```

该脚本使用 certbot standalone 申请证书，会临时占用 80 端口。申请成功后证书写入 `/etc/letsencrypt/live/www.shiyuan-wreg.cloud/`。

证书申请完成后重启 nginx：

```bash
sudo docker compose -f deploy/docker-compose.yml restart nginx
```

certbot 容器会自动每 12 小时检查续期。

---

## 7. 验证清单

| 检查项 | 命令/URL |
|---|---|
| HTTP 跳转 HTTPS | `curl -I http://www.shiyuan-wreg.cloud/` 应返回 301 |
| HTTPS 首页 | `curl -I https://www.shiyuan-wreg.cloud/` 应返回 200 |
| RAG | `https://www.shiyuan-wreg.cloud/rag/` |
| FC | `https://www.shiyuan-wreg.cloud/fc/` |
| Nexus | `https://www.shiyuan-wreg.cloud/nexus/` |
| DocHub | `https://www.shiyuan-wreg.cloud/doctomd/` |
| 学习站 | `https://www.shiyuan-wreg.cloud/learn/` |
| 后端代理 | `POST https://www.shiyuan-wreg.cloud/rag/clear` 返回 200 |
| SSL 证书有效期 | 浏览器锁标 + `openssl s_client -connect www.shiyuan-wreg.cloud:443` |

---

## 8. 本次本地验证已修复的问题

在本地 Docker 验证阶段发现并修复了以下问题，生产部署会直接受益：

1. **`backends/md_converter_app/requirements.txt`**：`python-markdown==3.6` 改为 `Markdown==3.6`（PyPI 正确包名）。
2. **`backends/md_converter_app/Dockerfile`**：保持复制到 `/app/` 根目录，与代码内相对导入一致。
3. **`backends/md_converter_app/main.py`**：static / templates 路径改为基于 `APP_DIR`，避免 Docker 内路径硬编码问题。
4. **`backends/nexus_app/Dockerfile`**：新增 `COPY core/ ./core/`，修复 `ModuleNotFoundError: No module named 'core'`。
5. **本地验证配置**：新增 `deploy/docker-compose.local.yml` + `deploy/nginx/nginx.local.conf`，生产配置 `deploy/docker-compose.yml` 已恢复为 80/443 + HTTPS。

---

## 9. 回滚方案

如果部署失败，最快回滚：

```bash
cd /opt/ai-demos
sudo docker compose -f deploy/docker-compose.yml down
# 如需回退代码：sudo git reset --hard <上一个稳定 commit>
sudo docker compose -f deploy/docker-compose.yml up -d --build
```

---

## 10. 后续维护

- **更新代码**：`sudo git pull` + `bash deploy/build-frontends.sh` + `sudo docker compose -f deploy/docker-compose.yml up -d --build`
- **查看日志**：`sudo docker compose -f deploy/docker-compose.yml logs -f`
- **监控资源**：`htop`、`sudo docker stats`
- **SSL 续期**：certbot 容器自动处理，可手动测试：`sudo docker compose -f deploy/docker-compose.yml exec certbot certbot renew --dry-run`

---

## 11. 下一步需要你提供

请提供以下任一方式，我立即开始执行服务器部署：

1. **SSH 私钥文件路径**（推荐）：例如 `C:\Users\hzs17\.ssh\ai-demos-key.pem`
2. **root 密码**：阿里云控制台重置后的 root 密码

拿到凭证后，我会按本计划逐步执行，并在每步汇报结果。
