# 作业 B：基础改造 + Git 上传（进阶版）

## 1. GitHub 仓库链接

- GitHub 仓库：
  [pythonhomework-lesson6-assignment](https://github.com/tianhaishun/pythonhomework-lesson6-assignment)

---

## 2. 完成内容

本作业在作业 A 的基础上继续完成了以下内容：

1. 完成基础改造
   - 配置集中到脚本顶部配置区
   - 主逻辑拆成多个具名函数
   - 主流程统一进入 `main()`
   - 使用 `logging` 替换 `print`
   - 日志同时输出到屏幕和 `task.log`
   - 定时任务自动触发验证通过

2. 完成 GitHub 上传
   - 创建独立仓库
   - 添加 `.gitignore`
   - 推送改造后的代码、文档、截图和 `requirements.txt`

3. 完成敏感信息治理
   - 仓库中不再包含数据库账号密码
   - 改成从环境变量或 `.env` 文件读取
   - `.env` 已加入忽略规则，不会被提交

---

## 3. 仓库关键文件

- 改造前代码：
  [hero_winrate_analysis_before.py](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_analysis_before.py)
- 改造后完整代码：
  [hero_winrate_analysis_refactored.py](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_analysis_refactored.py)
- 运行入口：
  [run_hero_winrate_task.ps1](F:\code\ClaudeCode\pythonhomework\lesson6\run_hero_winrate_task.ps1)
- 依赖文件：
  [requirements.txt](F:\code\ClaudeCode\pythonhomework\lesson6\requirements.txt)
- 忽略规则：
  [\.gitignore](F:\code\ClaudeCode\pythonhomework\lesson6\.gitignore)
- 环境变量模板：
  [.env.example](F:\code\ClaudeCode\pythonhomework\lesson6\.env.example)

---

## 4. 日志截图 + 定时任务截图

- 日志截图：
  [log_capture.png](F:\code\ClaudeCode\pythonhomework\lesson6\log_capture.png)
- 定时任务触发截图：
  [scheduled_task_capture.png](F:\code\ClaudeCode\pythonhomework\lesson6\scheduled_task_capture.png)

本次定时任务最终验证结果：

- `Last Run Time`: `2026/3/29 20:09:11`
- `Last Result`: `0`

---

## 5. requirements.txt 说明

本次依赖文件按作业要求通过以下命令生成：

```bash
pip freeze > requirements.txt
```

已一起提交到 GitHub 仓库。

---

## 6. 安全检查说明

已检查仓库内容，以下信息没有上传到 GitHub：

- 本地 `.env`
- `task.log`
- 明文数据库密码
- 其他运行期敏感配置

目前 GitHub 仓库中保留的是可公开分享的代码与说明文件。
