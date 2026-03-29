# lesson6 作业 B

这是基于 `lesson5` 英雄胜率分析脚本完成的基础改造 + Git 上传版本。

## 仓库内容

- `hero_winrate_analysis_before.py`：改造前代码留档
- `hero_winrate_analysis_refactored.py`：改造后完整代码
- `run_hero_winrate_task.ps1`：定时任务调用入口
- `requirements.txt`：通过 `pip freeze > requirements.txt` 生成
- `作业A提交文档.md`：基础改造说明
- `作业B提交文档.md`：Git 上传说明
- `log_capture.png`：日志截图
- `scheduled_task_capture.png`：定时任务触发截图

## 环境变量

本仓库不包含敏感信息。请复制 `.env.example` 为 `.env`，再填写以下配置：

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_CHARSET`

## 运行方式

```powershell
python hero_winrate_analysis_refactored.py
```

或使用定时任务入口：

```powershell
powershell -ExecutionPolicy Bypass -File .\run_hero_winrate_task.ps1
```
