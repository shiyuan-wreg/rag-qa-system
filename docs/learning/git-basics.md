# Git 零基础入门

> 目标：理解 Git 是什么，能在 Windows + Git Bash 里完成最基本的版本控制操作。

## 1. 一句话定义

Git 是一个**分布式版本控制系统**，帮你保存代码每一次修改的历史，并支持多人协作。

## 2. 为什么存在

没有 Git 时，你想保存代码的旧版本，只能手动复制文件夹：

```
project_v1/
project_v2_final/
project_v2_final_really/
```

问题：
- 不知道每个版本改了什么
- 改错了无法快速回退
- 多人同时改一个文件会互相覆盖

Git 解决方式：每次修改都生成一个"快照"（commit），记录修改内容、作者、时间和说明；多个开发者各自在本地工作，最后把修改合并到一起。

## 3. 安装与准备

1. 下载 Git for Windows：https://git-scm.com/download/win
2. 安装时保持默认选项即可。
3. 安装完成后，在开始菜单找到 **Git Bash** 并打开。
4. 验证安装：

```bash
git --version
```

Expected: 输出类似 `git version 2.45.0.windows.1`

5. 配置你的名字和邮箱（会出现在每次提交里）：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

## 4. 最小动手示例

在桌面上创建一个练习目录：

```bash
cd /c/Users/$USER/Desktop
mkdir git-practice
cd git-practice
git init
```

Expected: `Initialized empty Git repository in ...`

创建一个文件并提交：

```bash
echo "hello git" > readme.txt
git status
```

Expected: `readme.txt` 显示为 `Untracked files`。

把文件加入暂存区并提交：

```bash
git add readme.txt
git commit -m "first commit: add readme"
git log --oneline
```

Expected: 输出一条提交记录，包含短 SHA 和提交信息。

修改文件再提交一次：

```bash
echo "another line" >> readme.txt
git add readme.txt
git commit -m "second commit: append line"
git log --oneline
```

Expected: 现在有两条提交记录。

## 5. 在 Kairos 项目里哪里用了它

- 整个 Kairos 仓库就是一个 Git 仓库，根目录下的 `.git/` 文件夹保存所有历史。
- 远程仓库地址在仓库根目录运行 `git remote -v` 可看到：`https://github.com/shiyuan-wreg/rag-qa-system.git`
- `deploy/PRODUCTION.md` 中的生产部署流程包含服务器执行 `git pull origin master`。
- 品牌重塑分支 `feat/kairos-rebrand` 已合并到 `master`，通过 `git log --oneline` 可以看到这段历史。

## 6. 常见错误与排查

**错误 1：提交时提示 `Please tell me who you are`**
- 原因：没有配置 `user.name` 和 `user.email`
- 解决：见 Step 3 的配置命令

**错误 2：Windows 下 Git 提示 `LF will be replaced by CRLF`**
- 原因：Windows 换行符是 CRLF，Linux/macOS 是 LF，Git 自动转换时提示
- 解决：通常是无害警告；Kairos 仓库已有 `.gitattributes` 处理，可忽略

**错误 3：改完文件后 `git status` 没变化**
- 原因：可能改完没有保存文件，或者不在 Git 仓库目录下
- 解决：确认保存文件，并确认当前目录下有 `.git/` 文件夹

## 7. 自检清单

- [ ] 我能解释 Git 是什么、和手动复制文件夹备份的区别
- [ ] 我能用 `git init` 创建仓库
- [ ] 我能用 `git add` + `git commit` 提交修改
- [ ] 我能用 `git log --oneline` 查看提交历史
- [ ] 我能在 Kairos 仓库里找到 `.git/` 和远程仓库地址

## 8. 下一步

- 学习 `git status`、`git diff`、`git restore` 等日常命令
- 尝试 `git branch` 和 `git merge` 理解分支合并
- 阅读 Pro Git 官方中文版
