# Phase 4 服务器部署排错与学习指南

> 本文档记录 2026-06-23 部署 `ai-demos` 到阿里云韩国首尔服务器过程中遇到的所有关键错误、排查思路和解决方法。内容从基础概念讲起，适合零基础逐步进阶。

---

## 0. 今天这整条链路到底是什么？

在动手排错前，先建立一张“地图”。本次 Phase 4 要做的就是：

```text
你本地电脑 (Windows + Git Bash)
    │
    │  1. 先写代码、提交到 GitHub
    │  2. 通过某种方式连上云服务器
    ▼
阿里云轻量应用服务器 (韩国首尔, Ubuntu 24.04 LTS)
    │
    │  3. 在服务器上安装 Docker、Node.js
    │  4. 拉取 GitHub 代码
    │  5. 构建前端、构建后端镜像
    │  6. Docker Compose 启动所有服务
    │  7. 申请 SSL 证书
    ▼
互联网用户
    访问 https://www.shiyuan-wreg.cloud
```

这条链路上任何一环出问题，最终表现都是“网站打不开”或“部署失败”。下面按时间线把每个错误拆开讲。

---

## 1. 基础概念：先搞懂这些名词

### 1.1 SSH 与端口 22

**SSH（Secure Shell）** 是一种远程登录协议。默认端口是 **22**。你在本地执行：

```bash
ssh root@8.213.145.110
```

本质上是：

1. 你的电脑向服务器 `8.213.145.110:22` 发起 TCP 连接。
2. 服务器上的 `sshd` 进程（SSH daemon）响应。
3. 双方验证身份（密钥或密码）。
4. 建立加密通道，你就可以在服务器上执行命令。

**关键点**：连接成功的前提是 **TCP 三层握手能完成**。如果 SYN 发出去、SYN+ACK 回不来，就会报 `Connection timed out`。

---

### 1.2 防火墙的层次

很多人一听到“连不上”就以为是防火墙。其实防火墙分好几层：

| 层级 | 位置 | 例子 | 管什么 |
|---|---|---|---|
| **云防火墙 / 安全组** | 云厂商控制台 | 阿里云轻量服务器“防火墙”页 | 公网 IP 的入站/出站 |
| **主机防火墙** | 操作系统内 | `ufw`、`firewalld` | 进入本机的流量 |
| **包过滤框架** | 操作系统内核 | `iptables`、`nftables` | 更底层的包过滤 |

今天遇到的 `ufw inactive` 属于第二层，`iptables -L -n` 为空，说明**本机没有拦截**。真正的拦截要么在云防火墙上，要么在网络运营商层面。

---

### 1.3 代理与 HTTP CONNECT 隧道

**代理（Proxy）** 就像一个“中转站”。你的请求先发给代理，再由代理转发出去。

常见两种：

- **HTTP 代理**：主要用于 HTTP/HTTPS 流量。浏览器、Git 都能用。
- **SOCKS5 代理**：更通用，几乎任何 TCP 流量都能走（包括 SSH）。

你本机开的代理是 **Clash / 类似工具**，监听 `127.0.0.1:7890`。它支持 **HTTP CONNECT** 方法——客户端向代理发送 `CONNECT 目标地址:端口`，代理建立一条 TCP 隧道，之后的数据原样转发。

```text
你 ── CONNECT 8.213.145.110:22 ──▶ 代理
你 ◀──────── 200 Connection established ──── 代理
你 ─────────── 原始 SSH 数据 ───────────▶ 代理 ────────▶ 服务器
```

这就是 `ssh` 能“借道”代理的原理。

---

### 1.4 Docker 与 Docker Compose

- **Docker**：把应用和它需要的运行环境打包成一个“容器镜像”，保证在任何机器上运行结果一致。
- **Docker Compose**：用一个 `docker-compose.yml` 文件定义多个容器怎么一起启动、网络怎么连、端口怎么映射。

今天的 `deploy/docker-compose.yml` 里定义了 6 个服务：`rag`、`fc`、`nexus`、`md_converter`、`nginx`、`certbot`。

---

### 1.5 Nginx 反向代理

**反向代理**是指 Nginx 站在用户和后端服务之间：

```text
用户 ──▶ Nginx(80/443) ──▶ 后端服务(8001/8002/...)
```

Nginx 根据路径决定转发给哪个后端：

- `/rag/` → `rag:8001`
- `/fc/` → `fc:8002`
- `/nexus/` → `nexus:8003`

---

### 1.6 SSL/TLS 与 Let's Encrypt

- **SSL/TLS**：给 HTTP 加上加密，变成 HTTPS，防止中间人窃听。
- **证书**：由受信任的证书颁发机构（CA）签发，浏览器看到证书有效才会显示“小锁”。
- **Let's Encrypt**：免费的 CA。`certbot` 是它的官方客户端。

`certbot --standalone` 会临时占用 80 端口，完成域名验证后签发证书。

---

## 2. 错误时间线：每个问题怎么出现的、怎么解决的

### 2.1 SSH 22 端口连接超时

#### 现象

```text
ssh: connect to host 8.213.145.110 port 22: Connection timed out
ping 也 100% 丢包
```

#### 排查过程

1. **服务器内部检查 SSH 服务**：`systemctl status ssh` 显示正常，`ss -tlnp` 显示 22 端口在监听。
2. **检查本机防火墙**：`ufw inactive`，`iptables`/`nftables` 空。
3. **tcpdump 抓包**：在服务器上运行 `sudo tcpdump -i any port 22 -n`，同时从本地发 SSH 请求。
4. **发现**：本地 SYN 能到达服务器，服务器也回了 SYN+ACK，但**本地收不到 SYN+ACK**。

#### 根因

不是服务器拒绝，而是**本地网络到韩国这个公网 IP 的回程流量被丢弃或路由黑洞**。你用的日本代理也连不上，说明不是你一家网络的问题。

#### 解决

让 SSH 走本机代理的 HTTP CONNECT 隧道：

```bash
# 1. 安装/确认有 connect 工具（Git Bash 自带 /mingw64/bin/connect）
which /mingw64/bin/connect

# 2. 测试
ssh -i "C:\Users\hzs17\Downloads\ssh.pem" \
    -o ProxyCommand="/mingw64/bin/connect -H 127.0.0.1:7890 %h %p" \
    root@8.213.145.110
```

为了方便，创建了 `ai-demos/.claude/ssh_config`：

```text
Host ai-demos
    HostName 8.213.145.110
    User root
    IdentityFile C:/Users/hzs17/Downloads/ssh.pem
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ProxyCommand /mingw64/bin/connect -H 127.0.0.1:7890 %h %p
```

以后登录：

```bash
ssh -F C:/Users/hzs17/Desktop/ai-demos/.claude/ssh_config ai-demos
```

#### 进阶思考

- 如果代理不支持 CONNECT，可以用 `nc` 或 Python 脚本做 SOCKS5 中转。
- 生产环境不应依赖本地代理；可以考虑跳板机、WireGuard、Cloudflare Tunnel 等更稳定的方案。

---

### 2.2 ufw inactive 是不是没开防火墙的原因？

#### 现象

用户发现 `sudo ufw status` 显示 `inactive`，问是不是这个原因导致 SSH 不通。

#### 解释

**不是**。`ufw inactive` 表示 Ubuntu 自带的简单防火墙没有启用，等价于“本机不额外拦截”。如果它启用且默认拒绝，那才是它的问题。

真正的防火墙在云控制台：阿里云轻量服务器的“防火墙”页。

#### 建议

部署完成后可以开启 ufw 做加固，但只放行必要端口：

```bash
sudo ufw default deny incoming
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

### 2.3 服务器 443 端口被占用

#### 现象

启动 nginx 容器时报错：

```text
failed to bind host port 0.0.0.0:443/tcp: address already in use
```

#### 排查

```bash
ss -tlnp | grep :443
```

发现 `sshd` 也在监听 443。

#### 根因

之前为了绕过 22 端口不通的问题，我们在 `/etc/ssh/sshd_config` 里加了 `Port 443`，让 SSH 同时监听 443。但 HTTPS 也需要 443，冲突了。

更隐蔽的是：Ubuntu 24.04 默认使用 `ssh.socket` 来监听端口，配置文件里的 `Port` 改动会被 `sshd-socket-generator` 重新生成到 `/run/systemd/generator/ssh.socket.d/addresses.conf`。所以即使改回 `Port 22`，443 还在监听，需要 `systemctl daemon-reload` 才能刷新。

#### 解决

```bash
# 1. 去掉 /etc/ssh/sshd_config 里的 Port 443
sudo sed -i '/^Port 443/d' /etc/ssh/sshd_config

# 2. 重新加载 systemd 配置并重启 ssh
sudo systemctl daemon-reload
sudo systemctl restart ssh

# 3. 确认只有 22
ss -tlnp | grep sshd
```

#### 进阶思考

- `sshd.socket` 是 systemd 的 socket 激活机制，比传统 `sshd.service` 直接监听更灵活，但也更复杂。
- 改 SSH 端口后记得在云防火墙放行新端口，否则会被锁在外面。

---

### 2.4 Node.js 下载失败（npmmirror.com 连不上）

#### 现象

部署脚本里执行：

```bash
curl -fsSL "https://npmmirror.com/mirrors/node/v20.14.0/..."
```

报错：

```text
Failed to connect to npmmirror.com port 443 after 134792 ms
```

#### 根因

`npmmirror.com` 是**中国国内镜像**。服务器在韩国，从韩国访问国内镜像反而慢或不通。

#### 解决

改用 Node.js 官方分发地址：

```bash
curl -fsSL --retry 3 --retry-delay 5 \
    "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
    -o /tmp/node.tar.xz
```

#### 进阶思考

- 选镜像要看服务器位置：国内服务器用 npmmirror/USTC/163，海外服务器用官方源或当地镜像。
- `npm config set registry` 同理，海外用默认 `registry.npmjs.org` 通常最快。

---

### 2.5 certbot 申请证书报 TTY 错误

#### 现象

```text
cannot attach stdin to a TTY-enabled container because stdin is not a terminal
```

#### 根因

原脚本 `deploy/init-ssl.sh` 使用 `docker run -it ...`。`-t` 表示分配伪终端（TTY），但在自动化脚本/非交互 SSH 中不存在 TTY。

#### 解决

去掉 `-t`，保留 `-i`（非交互式 stdin）：

```bash
docker run -i --rm \
    -p 80:80 \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    certbot/certbot certonly --standalone \
    -d "$DOMAIN" --agree-tos --non-interactive -m "$EMAIL"
```

#### 进阶思考

- `-it` 只适合人工在终端里执行。
- CI/CD、自动化脚本里统一用 `-i` 或干脆不用 `-i`（如果命令不需要 stdin）。

---

### 2.6 nginx 启动失败：host not found in upstream "rag"

#### 现象

nginx 容器反复重启，日志：

```text
nginx: [emerg] host not found in upstream "rag" in /etc/nginx/conf.d/default.conf:30
```

#### 根因

Nginx 在**启动时**就解析 `proxy_pass http://rag:8001/` 里的 `rag`。但 Docker Compose 启动顺序并不能保证 nginx 启动时 `rag` 容器已经注册到 Docker DNS，所以解析失败。

#### 解决

让 nginx 在**请求时**再解析上游，而不是启动时：

```nginx
resolver 127.0.0.11 valid=30s;

location /rag/ {
    set $rag http://rag:8001;
    proxy_pass $rag/;
    ...
}
```

`127.0.0.11` 是 Docker 内置 DNS 服务器地址。`valid=30s` 表示缓存解析结果 30 秒。

#### 进阶思考

- `depends_on` 只能控制容器启动顺序，不能控制服务是否就绪。
- 更健壮的做法是加 `healthcheck`，等后端真正 Ready 再启动 nginx。

---

### 2.7 POST /rag/clear 返回 405 Method Not Allowed

#### 现象

- `GET /rag/` 正常返回 200。
- `POST /rag/clear` 返回 405，响应头 `allow: GET`。

#### 根因

当 `proxy_pass` 使用变量时，Nginx **不会自动去掉 location 前缀**。请求 `/rag/clear` 被原样转发到后端，但 `rag` 后端只有 `/clear` 路由。

更糟的是，如果后端没有 `/rag/clear`，Nginx 会把这个请求交给 `location /` 的静态文件处理；静态文件对 POST 请求返回 405。

#### 解决

在 `location` 里加 `rewrite`，手动去掉前缀：

```nginx
location /rag/ {
    set $rag http://rag:8001;
    rewrite ^/rag/(.*) /$1 break;
    proxy_pass $rag;
    ...
}
```

`break` 表示不再继续匹配其他 rewrite 规则，并把改写后的 URI 传给 `proxy_pass`。

#### 进阶思考

- 不加变量时，`proxy_pass http://rag:8001/;` 会自动去掉 `/rag/` 前缀。
- 加变量时行为不同，这是 Nginx 容易踩的坑。需要同时理解“启动时解析”和“URI 替换”两个行为。

---

### 2.8 RAG 启动慢，/rag/ 先 502 后 200

#### 现象

部署刚完成时 `/rag/` 返回 502，等了几分钟后才变成 200。

#### 根因

RAG 后端在启动时会执行 `init_rag_tool()`，流程是：

1. 读取 `docs/python_guide.txt`
2. 切分文本
3. 调用 DashScope Embedding API 构建向量数据库
4. 存入 Chroma

第一次启动需要构建向量库，耗时较长；而且输出因为 Python 缓冲没有立即打印到 Docker 日志。

#### 解决

不需要特殊操作，等待即可。后续启动如果 `chroma_db/` 目录还在，会直接加载已有库，快很多。

#### 进阶思考

- 生产环境可以考虑把 `chroma_db` 持久化到 volume，避免每次重建。
- 也可以把向量库构建拆成独立的初始化命令，而不是每次启动都执行。

---

## 3. 学习路径：从基础到进阶

### 初级（先把命令跑通）

1. 用 `ssh -F .claude/ssh_config ai-demos` 登录服务器。
2. 执行 `docker compose -f deploy/docker-compose.yml ps`，看容器状态。
3. 用 `curl -I https://www.shiyuan-wreg.cloud/` 测试首页。
4. 用 `docker logs deploy-nginx-1` 看日志。

### 中级（理解原理）

1. 画一张图：从浏览器到 Nginx 到后端容器的完整请求路径。
2. 解释为什么 `proxy_pass` 用变量时需要 `rewrite`。
3. 解释 `resolver 127.0.0.11` 解决了什么问题。
4. 解释 certbot standalone 为什么需要临时占用 80 端口。

### 进阶（动手改造）

1. 给 `deploy/docker-compose.yml` 的每个后端服务加 `healthcheck`。
2. 把 RAG 向量库初始化拆成单独脚本，避免每次启动重建。
3. 写一个 `deploy/update.sh`：自动 `git pull`、`build-frontends.sh`、`docker compose up -d --build`。
4. 研究 Cloudflare Tunnel 或 WireGuard，替代本地代理登录方案。

---

## 4. 自测问题

1. SSH 报 `Connection timed out` 时，应该先怀疑服务器本身，还是先怀疑网络层？怎么验证？
2. `ufw inactive` 为什么不是 SSH 连不上的原因？
3. 为什么 `sshd` 监听 443 会导致 nginx 启动失败？怎么彻底关闭 sshd 的 443？
4. `docker run -it` 和 `docker run -i` 有什么区别？自动化脚本应该用什么？
5. 为什么 `proxy_pass $rag/;` 不能直接替代 `proxy_pass http://rag:8001/;`？会带来哪两个问题？
6. Let's Encrypt 验证域名时为什么要临时占用 80 端口？
7. RAG 后端第一次启动慢的根本原因是什么？怎么优化？

---

## 5. 关键命令速查

```bash
# 登录服务器
ssh -F C:/Users/hzs17/Desktop/ai-demos/.claude/ssh_config ai-demos

# 查看容器
sudo docker compose -f /opt/ai-demos/deploy/docker-compose.yml ps

# 查看 nginx 日志
sudo docker compose -f /opt/ai-demos/deploy/docker-compose.yml logs --tail 50 nginx

# 重启全部服务
sudo docker compose -f /opt/ai-demos/deploy/docker-compose.yml restart

# 更新代码并重新部署
cd /opt/ai-demos
sudo git pull
bash deploy/build-frontends.sh
sudo docker compose -f deploy/docker-compose.yml up -d --build

# 测试 SSL
openssl s_client -connect www.shiyuan-wreg.cloud:443 -servername www.shiyuan-wreg.cloud
```

---

## 6. 参考资料

- [SSH ProxyCommand 官方文档](https://man.openbsd.org/ssh_config.5#ProxyCommand)
- [Nginx proxy_pass 指令](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)
- [Docker Compose depends_on](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Let's Encrypt How It Works](https://letsencrypt.org/how-it-works/)
- [systemd.socket 文档](https://www.freedesktop.org/software/systemd/man/latest/systemd.socket.html)
