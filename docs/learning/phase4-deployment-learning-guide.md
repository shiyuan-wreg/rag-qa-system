# Phase 4 服务器部署排错与学习指南

> 本文档记录 2026-06-23 部署 `ai-demos` 到阿里云韩国首尔服务器过程中遇到的所有关键错误、排查思路和解决方法。内容从基础概念讲起，适合零基础逐步进阶。**2026-06-24 增补：深入解释 SSH 直连失败、代理无效、HTTP CONNECT 隧道有效的三层原因。**

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

#### 1.3.1 “代理”到底是什么？

**代理（Proxy）** 就像一个“邮局中转站”：你不直接把信寄给收件人，而是先寄给邮局，再由邮局替你转发。

在网络世界里，你的电脑是客户端，服务器是目标地址。正常情况下：

```text
你的电脑 ────── TCP 直连 ──────▶ 服务器:22
```

走代理时变成：

```text
你的电脑 ──────▶ 代理服务器 ──────▶ 目标服务器:22
```

代理自己也有 IP 和端口。你本机开的代理（Clash / v2rayN / 类似工具）监听在 **本机回环地址** `127.0.0.1:7890` 上。也就是说，所有想走代理的流量，必须先送到你电脑自己的 7890 端口。

#### 1.3.2 代理分两种：HTTP 代理 vs SOCKS5 代理

| 类型 | 工作层级 | 能转发什么流量 | 典型用途 |
|---|---|---|---|
| **HTTP 代理** | 应用层（HTTP 协议） | HTTP、HTTPS；通过 CONNECT 方法可扩展为任意 TCP 隧道 | 浏览器、Git、`curl` |
| **SOCKS5 代理** | 会话层 | 几乎所有 TCP/UDP 流量 | 游戏、SSH、任意应用 |

关键点：**HTTP 代理本身不是为 SSH 设计的**。它只能直接转发 HTTP 请求。但是 HTTP 协议里有一个特殊方法叫 `CONNECT`，它允许客户端对代理说：“请你帮我建一条到 `目标IP:端口` 的裸 TCP 隧道，后面的数据我不解释，你原样搬运。”

这就是 **HTTP CONNECT 隧道**。

#### 1.3.3 HTTP CONNECT 隧道的工作原理（逐帧拆解）

假设你要通过代理访问 `8.213.145.110:22`：

**第 1 步：你的电脑向本机代理发 HTTP CONNECT 请求**

```text
CONNECT 8.213.145.110:22 HTTP/1.1
Host: 8.213.145.110:22

```

注意：这里用的是 HTTP/1.1 明文请求，目标地址是 `服务器IP:22`。

**第 2 步：代理回复**

如果代理允许并且成功连上目标：

```text
HTTP/1.1 200 Connection established

```

**第 3 步：隧道建立**

从这个字节开始，连接的两端仿佛直接连在了一起。你发给代理的数据，代理不再按 HTTP 解析，而是原样转发给 `8.213.145.110:22`。服务器回的数据也原样返回给你。

```text
你的 SSH 客户端
       │
       │  原始 SSH 协议数据（此时外面已经不套 HTTP 了）
       ▼
127.0.0.1:7890（本机代理）
       │
       │  同样的原始 SSH 数据
       ▼
8.213.145.110:22（阿里云服务器 sshd）
```

形象地说：CONNECT 隧道就是代理给你挖了一条“透明管道”。管道里面流的是什么协议，代理不关心；它只负责把字节从一端搬到另一端。

#### 1.3.4 为什么你“开了代理”SSH 还是连不上？

这是最常见的误区。你以为“开了 Clash，系统代理已启用”，SSH 就会走代理。其实不然。

**SSH 客户端默认完全不读取操作系统的代理设置。**

浏览器、Git、curl 等应用会读取系统代理环境变量（如 `HTTP_PROXY`、`HTTPS_PROXY`），但 OpenSSH 不会。它只按自己的配置行事，默认就是**直接 TCP 连接目标服务器**。

所以当时的情况可能是：

| 流量类型 | 是否走代理 | 结果 |
|---|---|---|
| 浏览器访问 Google | ✅ 系统自动走代理 | 能打开 |
| `git clone` | ✅ 你配了代理或 Git 读了环境变量 | 能拉 |
| `ssh root@8.213.145.110` | ❌ SSH 默认直连 | 超时 |

你之前提到的“日本代理也连不上”，更可能的原因是：

1. **那个代理是浏览器/Web 代理**，只能转发 HTTP/HTTPS，不支持 CONNECT 到 22 端口；或者你根本没告诉 SSH 要走它。
2. **代理到韩国阿里云的回程同样被黑洞**，因为问题的根源是“代理→目标服务器”这条路径不通，而不是你本地到目标服务器不通。
3. **SSH 配置里没有 ProxyCommand**，所以它仍然尝试直连，自然还是超时。

#### 1.3.5 为什么本地代理的 HTTP CONNECT 能成功？

这里要分清三条不同的网络路径：

```text
路径 A：你的电脑  ──直连──▶  8.213.145.110:22    （失败，SYN+ACK 回不来）
路径 B：你的电脑  ──日本代理──▶  8.213.145.110:22  （可能失败，回程路由同样被黑洞）
路径 C：你的电脑  ──本机代理 7890──▶  代理远端出口──▶  8.213.145.110:22  （成功）
```

**路径 C 成功的原因不是“用了 HTTP CONNECT 这个方法本身”，而是“本机代理的出口节点到韩国阿里云服务器是通的”。**

HTTP CONNECT 只是**一种机制**，让 SSH 客户端能把数据交给本地代理。真正解决连接问题的是：**本地代理的后端节点（Clash 订阅里的某个海外节点）到目标服务器的路由是健康的**。

换句话说：

- 如果你的本机代理节点也连不上 `8.213.145.110:22`，HTTP CONNECT 同样会失败。
- 如果直接连是通的，你根本不需要代理。

这也能解释为什么你换日本代理不行：那个代理的出口到韩国服务器之间网络也不通。而本机代理当前选用的节点到韩国服务器之间恰好是通的。

#### 1.3.6 `ProxyCommand` 在 SSH 里做了什么？

`ssh` 命令本身不知道如何走 HTTP 代理，但它提供了一个钩子：**`ProxyCommand`**。

```text
ProxyCommand /mingw64/bin/connect -H 127.0.0.1:7890 %h %p
```

这条命令的意思是：在建立 SSH 连接之前，先执行 `connect` 这个辅助程序。`connect` 会：

1. 连接到本机代理 `127.0.0.1:7890`。
2. 向代理发送 `CONNECT %h:%p`，其中 `%h` 是 SSH 目标主机，`%p` 是端口（这里就是 `8.213.145.110:22`）。
3. 等代理返回 `200 Connection established`。
4. 把它的标准输入/输出挂在 SSH 进程的网络上。

于是 `ssh` 不再直接连服务器，而是把 `connect` 当成一条“虚拟网线”。

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
ping 8.213.145.110 也 100% 丢包
```

注意：这里不是 `Connection refused`。`refused` 表示能到目标机器，只是端口没开；`timed out` 表示**网络层根本没把包送过去或者回不来**。

#### 排查过程

1. **服务器内部检查 SSH 服务**：`systemctl status ssh` 显示正常，`ss -tlnp` 显示 22 端口在监听。
2. **检查本机防火墙**：`ufw inactive`，`iptables`/`nftables` 空。
3. **tcpdump 抓包**：在服务器上运行 `sudo tcpdump -i any port 22 -n`，同时从本地发 SSH 请求。
4. **发现**：本地 SYN 能到达服务器，服务器也回了 SYN+ACK，但**本地收不到 SYN+ACK**。

这一步非常关键：它排除了“服务器没开 SSH”和“云防火墙拦截入站”两种可能。问题出在**回程路由**上。

#### 根因：不是服务器拒绝，而是运营商层面的路由黑洞

我们用 `mtr` 或 `traceroute` 看的话，会发现类似情况：

```text
你的电脑 ──▶ 国内运营商路由器 ──▶ 国际出口 ──▶ 韩国骨干网 ──▶ 阿里云首尔
       ▲___________________________________________________________│
                        回程 SYN+ACK 在这里丢失
```

`ping` 也丢包说明 ICMP（也就是 `ping` 用的协议）同样受影响，进一步证明这是**网络层路由/策略问题**，不是 TCP 层端口问题。

可能的具体原因：

- 你所在网络到该 IP 段的路由表中，某台上游路由器丢弃了回程包。
- 该 IP 段被某些网络策略临时或局部阻断。
- 国际链路拥塞或路由震荡导致特定路径不稳定。

注意：阿里云控制台的安全组/防火墙并没有拦截 22 端口，否则**本地 SYN 根本到不了服务器**，tcpdump 也就抓不到包了。

#### 为什么日本代理也失败？

你当时试过的日本代理，从现象上看也连不上。这里要区分两种情况：

1. **如果你只是“开着浏览器代理”然后执行 `ssh`**：那 SSH 根本不走代理，等同于直连，失败是必然的。
2. **如果你确实让 SSH 走了日本代理**：说明日本代理的出口节点到 `8.213.145.110:22` 的路径也不通。问题的根源在于“代理出口到目标服务器”这段回程被黑洞，而不是“你本地到代理”这段。

这也侧面验证了：不是某个特定网络的问题，而是**目标服务器在部分国际路径上的可达性有问题**。

#### 解决：让 SSH 走本机代理的 HTTP CONNECT 隧道

既然直连和日本代理都不行，我们换一条路径：让本地 Clash 代理作为中转。它当前的出口节点到韩国阿里云恰好是通的。

**第 1 步：确认 `connect` 工具存在**

Git Bash 自带 `connect`，路径是 `/mingw64/bin/connect`。如果没有，可以用 `corkscrew` 替代，或者自己写一个 Python 脚本。

```bash
which /mingw64/bin/connect
```

**第 2 步：命令行直接测试**

```bash
ssh -i "C:\Users\hzs17\Downloads\ssh.pem" \
    -o ProxyCommand="/mingw64/bin/connect -H 127.0.0.1:7890 %h %p" \
    root@8.213.145.110
```

参数解释：

- `-i`：指定私钥文件。
- `-o ProxyCommand=...`：告诉 SSH 用哪个命令来建立底层连接。
- `/mingw64/bin/connect -H 127.0.0.1:7890 %h %p`：
  - `-H` 表示使用 HTTP CONNECT（还有 `-S` 表示 SOCKS5）。
  - `127.0.0.1:7890` 是你本机代理的地址和端口。
  - `%h` 是 SSH 自动替换的目标主机名。
  - `%p` 是 SSH 自动替换的目标端口（默认 22）。

**第 3 步：写成配置文件，避免每次敲长命令**

创建了 `ai-demos/.claude/ssh_config`：

```text
Host ai-demos
    HostName 8.213.145.110
    User root
    IdentityFile C:/Users/hzs17/Downloads/ssh.pem
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ProxyCommand /mingw64/bin/connect -H 127.0.0.1:7890 %h %p
```

字段解释：

- `Host ai-demos`：给这条配置起个别名，以后 `ssh ai-demos` 就会匹配。
- `HostName`：真实的服务器 IP。
- `IdentityFile`：私钥路径，注意在 Windows/Git Bash 中用正斜杠更稳。
- `StrictHostKeyChecking no` + `UserKnownHostsFile /dev/null`：测试阶段跳过主机密钥校验，避免每次 IP 不变但证书变化导致无法登录。**生产环境建议去掉这两行，使用正常 known_hosts。**
- `ProxyCommand`：核心，建立 HTTP CONNECT 隧道。

以后登录：

```bash
ssh -F C:/Users/hzs17/Desktop/ai-demos/.claude/ssh_config ai-demos
```

#### 进阶思考

- 如果代理只支持 SOCKS5 不支持 CONNECT，可以用 `nc -X 5 -x 127.0.0.1:7890 %h %p` 作为 ProxyCommand。
- 如果代理需要用户名密码认证，`connect` 本身不支持；可以用 `corkscrew` 或在 Python 脚本里手写 HTTP CONNECT 并加 `Proxy-Authorization` 头。
- 生产环境不应长期依赖本地代理登录服务器。更稳定的方案：
  - **跳板机（Bastion Host）**：买一台国内能稳定访问的轻量服务器，先 SSH 到跳板机，再从跳板机 SSH 到韩国服务器。
  - **WireGuard / Tailscale**：在服务器和你的设备之间建立私有网络，绕开公网路由问题。
  - **Cloudflare Tunnel**：让服务器主动 outbound 连 Cloudflare，你通过 Cloudflare 的私有入口访问，无需关心服务器公网可达性。

#### 常见误区再强调

1. **“我开了 Clash，为什么 SSH 不走？”** —— SSH 不读系统代理，必须显式配置 ProxyCommand。
2. **“HTTP 代理不是只能转发网页吗？”** —— 普通 HTTP 转发只能处理网页，但 CONNECT 方法可以把任意 TCP 包塞进去。
3. **“HTTP CONNECT 加密吗？”** —— CONNECT 请求本身是明文的（代理能看到你要连哪个 IP 和端口），但**隧道建立后，SSH 协议自己的加密会接管**，里面的数据代理看不到。
4. **“代理会不会看到我输入的 root 密码/私钥？”** —— 不会。私钥永远只在你的本地 SSH 客户端使用；密码/密钥交换发生在 SSH 加密隧道内部，代理只能看到加密后的字节流。

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
3. 为什么浏览器能翻墙，但 `ssh root@8.213.145.110` 仍然超时？
4. HTTP 代理为什么能转发 SSH 这种非 HTTP 协议？关键机制是什么？
5. `ProxyCommand` 中的 `%h` 和 `%p` 分别代表什么？
6. 为什么说 HTTP CONNECT 隧道里“代理看不到你输入的密码/私钥”？
7. 日本代理连不上、本机代理能连上，这说明了什么？问题的真正根源在哪里？
8. 为什么 `sshd` 监听 443 会导致 nginx 启动失败？怎么彻底关闭 sshd 的 443？
9. `docker run -it` 和 `docker run -i` 有什么区别？自动化脚本应该用什么？
10. 为什么 `proxy_pass $rag/;` 不能直接替代 `proxy_pass http://rag:8001/;`？会带来哪两个问题？
11. Let's Encrypt 验证域名时为什么要临时占用 80 端口？
12. RAG 后端第一次启动慢的根本原因是什么？怎么优化？

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
- [SSH 通过 HTTP 代理 (CONNECT 方法)](https://en.wikipedia.org/wiki/HTTP_tunnel#HTTP_CONNECT_method)
- [corkscrew: 通过 HTTP 代理转发 SSH](https://github.com/bryanpkc/corkscrew)
- [connect: Git for Windows 自带的 ProxyCommand 工具](https://github.com/git-for-windows/git/wiki/Proxy-configuration)
- [Nginx proxy_pass 指令](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass)
- [Docker Compose depends_on](https://docs.docker.com/compose/compose-file/05-services/#depends_on)
- [Let's Encrypt How It Works](https://letsencrypt.org/how-it-works/)
- [systemd.socket 文档](https://www.freedesktop.org/software/systemd/man/latest/systemd.socket.html)
