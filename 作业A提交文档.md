# 作业 A：基础改造（基础版）

## 1. 作业说明

本次作业选取了 `lesson5` 中的英雄胜率统计脚本作为改造对象，并在 `lesson6` 目录下完成重构与提交。

- 改造前脚本：
  [hero_winrate_analysis_before.py](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_analysis_before.py)
- 改造后脚本：
  [hero_winrate_analysis_refactored.py](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_analysis_refactored.py)
- 环境变量模板：
  [.env.example](F:\code\ClaudeCode\pythonhomework\lesson6\.env.example)
- 定时任务入口：
  [run_hero_winrate_task.ps1](F:\code\ClaudeCode\pythonhomework\lesson6\run_hero_winrate_task.ps1)
- 日志文件：
  [task.log](F:\code\ClaudeCode\pythonhomework\lesson6\task.log)
- 结果文件：
  [hero_winrate_refactored.xlsx](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_refactored.xlsx)

---

## 2. 改造前 vs 改造后代码对比

### 改造前存在的问题

- 配置项分散，导出文件名和筛选条件直接写在逻辑里，不方便改。
- `print` 和业务逻辑混在一起，后续不利于统一记录运行信息。
- 主流程虽有 `main()`，但整体还是偏脚本式，缺少清晰的“配置区 + 功能函数 + 主流程”结构。
- 脚本依赖手动输入分析人姓名，不适合定时任务自动执行。

### 改造后完成的优化

- 增加了脚本顶部“配置区”，把这些内容统一集中：
  - Excel 输出路径
  - 日志文件路径
  - 最低场次筛选条件
  - 分析人名称
  - 是否写入 `analysis_log`
- 将主要逻辑拆成多个命名函数，并补充中文注释：
  - `setup_logger()`
  - `connect_to_database()`
  - `fetch_hero_statistics()`
  - `build_export_dataframe()`
  - `log_statistics_summary()`
  - `export_to_excel()`
  - `write_analysis_log()`
  - `main()`
- 用 `logging` 替换 `print`，并同时输出到屏幕和 `task.log`
- 去掉人工输入，改为配置项驱动，更适合无人值守执行
- 数据库敏感配置改成 `.env` / 环境变量读取，适合上传 GitHub

### 关键改造点示例

#### 1. 配置区抽离

改造前：

```python
DB_CONFIG = {
    'host': '<请在环境变量中配置 DB_HOST>',
    'port': 3306,
    'user': '<请在环境变量中配置 DB_USER>',
    'password': '<请在环境变量中配置 DB_PASSWORD>',
    'database': '<请在环境变量中配置 DB_NAME>',
    'charset': 'utf8mb4'
}
```

改造后：

```python
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_EXCEL = BASE_DIR / "hero_winrate_refactored.xlsx"
LOG_FILE = BASE_DIR / "task.log"
MIN_TOTAL_GAMES = 30
ANALYST_NAME = "lesson6_auto_task"
WRITE_ANALYSIS_LOG = True
```

#### 2. print 改成 logging

改造前：

```python
print(f"✓ 查询成功！共获取 {len(df)} 个英雄的数据")
```

改造后：

```python
logger.info("查询完成，共获取 %s 个英雄的数据", len(df))
```

#### 3. 手动输入改成可自动执行

改造前：

```python
analyst_name = input("\n请输入分析人姓名（用于日志记录）：").strip()
if analyst_name:
    insert_analysis_log(connection, df, analyst_name)
```

改造后：

```python
if WRITE_ANALYSIS_LOG:
    write_analysis_log(connection, df, logger)
```

---

## 3. 日志截图说明

本次作业要求日志中能看到时间戳。改造后的日志格式如下：

```text
2026-03-29 19:56:46 | INFO | 任务开始执行
2026-03-29 19:56:46 | INFO | 数据库连接成功
2026-03-29 19:56:46 | INFO | 查询完成，共获取 20 个英雄的数据
2026-03-29 19:56:46 | INFO | Excel 导出成功: F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_refactored.xlsx
```

对应日志文件：
[task.log](F:\code\ClaudeCode\pythonhomework\lesson6\task.log)

---

## 4. 定时任务自动触发说明

已为本作业创建 Windows 定时任务：

- 任务名：`lesson6_hero_winrate_auto`
- 触发方式：一次性触发
- 运行脚本：
  [hero_winrate_analysis_refactored.py](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_analysis_refactored.py)

触发后的验证方式：

- 查看 `task.log` 中新增的带时间戳日志
- 查看任务调度器中的 `Last Run Time` 和 `Last Result`

本次最终验证结果：

- `Last Run Time`: `2026/3/29 20:09:11`
- `Last Result`: `0`

---

## 5. 运行结果

手动运行已验证通过，结果如下：

- 查询到英雄数：20
- 平均胜率：51.5%
- 胜率最高英雄：阿鲁卡多（59.0%，288 场）
- Excel 文件已生成：
  [hero_winrate_refactored.xlsx](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_refactored.xlsx)
- 日志文件已生成：
  [task.log](F:\code\ClaudeCode\pythonhomework\lesson6\task.log)

---

## 6. 本次基础改造总结

这次改造主要完成了 3 件事：

1. 把原来的脚本式代码整理成了更清晰的函数化结构
2. 把输出方式升级为标准日志，便于排查和留痕
3. 把脚本改造成可以直接被定时任务调用的自动化版本

整体上，这份作业已经从“手动运行的小脚本”提升成了“可定时执行、可追踪日志、可重复使用”的基础自动化脚本。
