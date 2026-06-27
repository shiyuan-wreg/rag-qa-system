# 生产部署(增量重部署)

> 服务器已建好时的**增量更新**流程。首次建机(装 Docker/Node/swap/SSL)走 `phase4-workbench-deploy.sh`,**本文件不重复那些步骤**。

## 环境

- 生产 = 首尔阿里云轻量,`8.213.145.110`,Ubuntu 24.04,部署目录 `/opt/ai-demos`,域名 https://www.shiyuan-wreg.cloud
- 代码靠服务器 **`git pull origin master`** 更新(remote = GitHub `shiyuan-wreg/rag-qa-system`),所以本地改动**先合并 master + 推 GitHub**,服务器再 pull。
- `.env` 在**服务器**上、gitignored、含 DeepSeek(聊天)+ Jina(RAG embedding)密钥,**部署不碰它**。

## 连接服务器

- 通过本机已配的 **ssh 别名**(见个人 `~/.ssh/config`):`ssh <别名> '<cmd>'`。
- **前提:本机代理软件开着**。大陆裸连首尔 22/443 会被 GFW 挡(超时),别名经本地代理端口做 SSH 隧道(`connect.exe` 当 ProxyCommand)。代理关了 → 只能走**阿里云 Workbench 网页控制台**执行下面同样的命令。
- 接入密钥与代理端口属个人/机器信息,不入库;若别名丢失需重建,见本机 `~/.ssh/config` 或私有部署记忆。

## 增量重部署(一条命令)

```
ssh <别名> 'cd /opt/ai-demos && git pull origin master && bash deploy/build-frontends.sh && docker compose -f deploy/docker-compose.yml up -d --build'
```

大构建建议放服务器后台 + 写日志(防 ssh 断线 / 工具超时),再轮询:

```
ssh <别名> 'cd /opt/ai-demos && nohup bash -c "bash deploy/build-frontends.sh && docker compose -f deploy/docker-compose.yml up -d --build; echo DONE_\$?" > /tmp/deploy.log 2>&1 & echo started'
# 然后:ssh <别名> 'tail -20 /tmp/deploy.log'  直到出现 DONE_0
```

> `up -d --build` 会用仓库源重建所有镜像(rag/fc/nexus/iconforge/md + 前端),把新代码烤进生产。后端容器在同一 compose 网络内重建,nginx 经服务名 DNS 解析新 IP,通常**无需手动重启 nginx**;若个别路由 502,再 `docker compose -f deploy/docker-compose.yml restart nginx`。

## 验证(从服务器本机)

大陆本机连不到公网 443,验证在**服务器上**做,用 `--resolve` 指回本机带正确 Host/SNI:

```
ssh <别名> 'D=www.shiyuan-wreg.cloud; for p in "" rag fc nexus doctomd learn iconforge; do
  curl -s -k -o /dev/null -w "/$p/ %{http_code}\n" --resolve $D:443:127.0.0.1 "https://$D/$p/"; done'
```

期望全 **200**(直接 `curl http://localhost/` 会得 301 → HTTPS 跳转,属正常)。端到端可再 POST `/rag/chat`、`/fc/chat` 确认 DeepSeek+Jina 在线。

## 回滚

```
ssh <别名> 'cd /opt/ai-demos && git reset --hard <旧HEAD> && docker compose -f deploy/docker-compose.yml up -d --build'
```
