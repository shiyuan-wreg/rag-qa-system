# Kairos 生产部署检查单

本检查单用于防止重复犯错。每次执行生产部署前，逐项确认。

## 部署前

- [ ] 本地 `git status --short` 干净，无未提交改动。
- [ ] 本地 `git log origin/master..HEAD` 为空，或已推送。
- [ ] 所有相关测试已通过（至少 RAG/FC/Nexus 相关单元测试）。
- [ ] 如果修改了前端，已运行 `bash deploy/build-frontends.sh`。
- [ ] 如果修改了 `.env.example`，已同步到生产服务器 `.env`。

## 部署命令（必须包含 git pull）

```bash
ssh shiyuan-prod 'cd /opt/kairos && nohup bash -c "git pull origin master && bash deploy/build-frontends.sh && docker compose -f deploy/docker-compose.yml up -d --build; echo DONE_\$?" > /tmp/deploy.log 2>&1 & echo started'
```

注意：**必须包含 `git pull origin master &&`**，否则服务器会在旧代码上重建。

## 部署后验证

- [ ] 轮询日志直到出现 `DONE_0`。
- [ ] 8 路由 HTTPS 200：
  ```bash
  ssh shiyuan-prod 'D=www.shiyuan-wreg.cloud; for p in "" rag fc nexus doctomd learn iconforge; do curl -s -k -o /dev/null -w "/$p/ %{http_code}\n" --resolve $D:443:127.0.0.1 "https://$D/$p/"; done'
  ```
- [ ] RAG 端到端 smoke 测试：
  ```bash
  ssh shiyuan-prod 'curl -s -k -X POST --resolve www.shiyuan-wreg.cloud:443:127.0.0.1 https://www.shiyuan-wreg.cloud/rag/chat -H "Content-Type: application/x-www-form-urlencoded" -d "query=What is the difference between Python list and tuple?"'
  ```
- [ ] 如果修改了容器初始化逻辑，检查对应容器日志无启动错误。
- [ ] 如果用户反馈页面未更新，提示强制刷新（Ctrl+Shift+R / Cmd+Shift+R）或无痕窗口。

## 回滚

如果验证失败：

```bash
ssh shiyuan-prod 'cd /opt/kairos && git reset --hard <旧HEAD> && docker compose -f deploy/docker-compose.yml up -d --build'
```

## 历史教训

- 2026-07-08：部署命令漏写 `git pull`，导致服务器重建旧代码，用户看不到改动。
- 2026-07-09：RAG 新 pipeline 上线后，O(n²) 相似度计算导致启动卡死；Chroma 不接受空 list metadata 导致入库失败。必须在生产容器做端到端验证。
