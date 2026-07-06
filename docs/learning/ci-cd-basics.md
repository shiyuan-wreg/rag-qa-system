# CI/CD 基础学习笔记

> 状态：待归档学习（Kairos 项目当前未使用，先作为独立笔记）  
> 目标：建立对 CI/CD 的最基础认知，知道它是什么、为什么存在、长什么样。

---

## 1. CI/CD 是什么

CI/CD 是 **Continuous Integration / Continuous Deployment** 的缩写，中文常译为**持续集成 / 持续部署**。

| 缩写 | 全称 | 一句话解释 |
|---|---|---|
| CI | Continuous Integration（持续集成） | 代码提交后，自动拉取、编译、跑测试，尽早发现集成问题 |
| CD | Continuous Delivery（持续交付） | 代码通过测试后，自动打包成可部署产物，随时能上线 |
| CD | Continuous Deployment（持续部署） | 代码通过测试后，**自动**部署到生产环境，无需人工干预 |

> 很多团队把后两者混称为 CD，区别只在于是否自动发布到线上。

---

## 2. 为什么需要 CI/CD

没有 CI/CD 时，软件发布通常是这样的：

```
本地开发 → 手动打包 → 手动上传服务器 → 手动改配置 → 祈祷别出问题 → 上线
```

问题：

1. **集成痛苦**：多个人各自开发，最后合并时冲突爆炸。
2. **测试滞后**：本地不跑全量测试，上线前才发现 bug。
3. **部署不一致**：不同人手动操作，环境差异导致"在我机器上能跑"。
4. **发布风险高**：一次性改很多内容，出问题难定位。

CI/CD 解决方式：

```
提交代码 → 自动拉取 → 自动构建 → 自动测试 → 自动部署
```

每次提交都做一遍，把小问题尽早暴露出来。

---

## 3. 核心概念

### 3.1 Pipeline（流水线）

CI/CD 的核心是**流水线**。一条流水线由多个**阶段（stage）**组成，每个阶段里可以有一个或多个**任务（job）**。

典型流水线：

```
构建（Build） → 测试（Test） → 部署（Deploy）
```

### 3.2 常见阶段

| 阶段 | 做什么 | 例子 |
|---|---|---|
| Build | 编译代码、安装依赖、打包 | `npm run build`、`docker build` |
| Test | 跑单元测试、集成测试、代码检查 | `pytest`、`eslint` |
| Deploy | 把产物部署到测试/生产环境 | `scp`、`kubectl apply`、`docker compose up` |

### 3.3 Runner / Agent

跑流水线的机器。可以是：

- 云服务商提供的托管 runner（如 GitHub Actions 的 runner）
- 自己搭建的服务器（如 Jenkins agent、GitLab runner）

### 3.4 Artifact（产物）

流水线中产生的可交付文件，比如：

- 编译后的 `dist/` 目录
- Docker 镜像
- 可执行文件

### 3.5 Trigger（触发器）

什么情况下启动流水线？常见触发条件：

- 代码推送到 `main` 分支
- 提交 Pull Request
- 定时触发（如每天凌晨跑备份任务）
- 手动触发

---

## 4. 一个最简单的例子（GitHub Actions）

GitHub Actions 是 GitHub 自带的 CI/CD 工具。下面是一个每次推代码到 `main` 分支时自动跑测试的例子：

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: 拉取代码
        uses: actions/checkout@v4

      - name: 安装 Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 安装依赖
        run: pip install -r requirements.txt

      - name: 运行测试
        run: pytest
```

这段配置文件做了什么：

1. `on`：触发条件，push 到 main 或提 PR 时触发。
2. `jobs`：定义任务。
3. `runs-on`：在 Ubuntu 虚拟机上运行。
4. `steps`：一步一步执行：拉代码 → 装 Python → 装依赖 → 跑测试。

---

## 5. CI/CD 和 Kairos 的关系（当前）

**Kairos 目前没有用 CI/CD**。它的部署流程是手动的：

```
本地修改 → git commit → git push → 登录服务器 → git pull → docker compose up -d
```

这个流程在项目早期是合理的，因为：

- 改动频率低
- 只有一个人部署
- 手动操作足够可控

但随着项目变大、demo 变多、部署变频繁，手动部署会暴露问题：

- 容易忘记跑测试就上线
- 服务器和本地环境可能不一致
- 回滚麻烦

所以 CI/CD 是 Kairos **未来可能引入**的工程化能力，但现在先理解概念即可。

---

## 6. 常见工具对比

| 工具 | 特点 | 适用场景 |
|---|---|---|
| GitHub Actions | 和 GitHub 集成最好，免费额度够用 | 项目放在 GitHub 上 |
| GitLab CI | 和 GitLab 集成好，自托管能力强 | 项目放在 GitLab 上 |
| Jenkins | 开源、插件多、可定制性强 | 企业内部、复杂流水线 |
| CircleCI / Travis CI | 老牌 CI 服务，配置简单 | 中小项目 |

---

## 7. 常见面试问法

- "什么是 CI/CD？和手动部署有什么区别？"
- "持续集成、持续交付、持续部署的区别是什么？"
- "你们项目为什么还没有 CI/CD？"
  - 答：项目早期手动部署足够，未来会随着规模引入。
- "CI/CD 流水线一般包含哪些阶段？"
- "如果测试失败，流水线应该怎么办？"
  - 答：应该阻止部署，通知开发者修复。

---

## 8. 学习资源

1. GitHub Actions 官方文档：https://docs.github.com/cn/actions
2. 《Continuous Delivery》—— Jez Humble（经典书）
3. 搜索关键词："GitHub Actions 入门教程"

---

## 9. 下一步

当你对 CI/CD 有基本理解后，可以思考：

1. Kairos 如果现在引入 CI/CD，第一步该做什么？
   - 建议：先做一个"提交代码后自动跑 pytest"的流水线。
2. 部署到生产环境这一步能不能自动化？
   - 可以，但需要先解决服务器访问权限、 secrets 管理、回滚策略等问题。

---

> 本笔记属于独立学习材料，不直接关联 Kairos 当前代码。未来 Kairos 引入 CI/CD 后，再把相关内容迁移到 `kairos-concept-map.md` 的对应层级。
