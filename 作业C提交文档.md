# 作业 C：完整自动化改造（挑战版）

## 1. GitHub 仓库链接

- 仓库地址：
  [pythonhomework-lesson6-assignment](https://github.com/tianhaishun/pythonhomework-lesson6-assignment)

仓库中已包含：

- `Dockerfile`
- `docker-compose.yaml`
- 改造后的完整代码
- 日志截图与定时任务截图

仓库中不包含：

- `.env`
- `task.log`
- 其他本地敏感配置

---

## 2. 改造后的完整代码

- 主脚本：
  [hero_winrate_analysis_refactored.py](F:\code\ClaudeCode\pythonhomework\lesson6\hero_winrate_analysis_refactored.py)

这次容器化改造的重点是：

1. 数据库配置完全改成 `os.environ.get()` 读取
2. 运行目录、日志文件名、Excel 文件名、分析人、筛选条件也支持环境变量
3. 保留 `.env` 本地读取能力，便于本地和服务器共用同一套代码

---

## 3. Dockerfile 逐行解释

文件：
[Dockerfile](F:\code\ClaudeCode\pythonhomework\lesson6\Dockerfile)

```dockerfile
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN mkdir -p /app/runtime

CMD ["python", "hero_winrate_analysis_refactored.py"]
```

逐行解释：

1. `FROM python:3.12-slim`
   使用轻量版 Python 3.12 作为基础镜像。
2. `WORKDIR /app`
   指定容器内工作目录为 `/app`。
3. `ENV PYTHONDONTWRITEBYTECODE=1`
   禁止生成 `.pyc` 文件，减少无用缓存。
4. `ENV PYTHONUNBUFFERED=1`
   让日志实时输出，便于看容器日志。
5. `COPY requirements.txt /app/requirements.txt`
   先复制依赖文件，方便 Docker 利用缓存。
6. `RUN pip install --no-cache-dir -r /app/requirements.txt`
   安装项目依赖，不保留 pip 缓存。
7. `COPY . /app`
   把项目代码复制进容器。
8. `RUN mkdir -p /app/runtime`
   提前创建运行目录，用来放日志和 Excel 输出。
9. `CMD ["python", "hero_winrate_analysis_refactored.py"]`
   容器启动时默认运行主脚本。

---

## 4. docker-compose.yaml 逐行解释

文件：
[docker-compose.yaml](F:\code\ClaudeCode\pythonhomework\lesson6\docker-compose.yaml)

```yaml
services:
  lesson6-task:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: lesson6-task
    restart: unless-stopped
    env_file:
      - .env
    environment:
      APP_DATA_DIR: /app/runtime
    volumes:
      - ./runtime:/app/runtime
    command: ["python", "hero_winrate_analysis_refactored.py"]
```

逐行解释：

1. `services:`
   定义 Compose 中要运行的服务。
2. `lesson6-task:`
   这个服务的名称，代表英雄分析任务容器。
3. `build:`
   表示镜像由本地 Dockerfile 构建。
4. `context: .`
   以当前目录作为构建上下文。
5. `dockerfile: Dockerfile`
   明确使用当前目录下的 Dockerfile。
6. `container_name: lesson6-task`
   指定容器名字，方便查看和管理。
7. `restart: unless-stopped`
   容器异常退出时自动重启，手动停止除外。
8. `env_file:`
   指定从 `.env` 文件中读取环境变量。
9. `- .env`
   实际使用当前目录下的 `.env`。
10. `environment:`
    额外补充容器内部环境变量。
11. `APP_DATA_DIR: /app/runtime`
    让脚本把日志和 Excel 输出到容器的 `/app/runtime`。
12. `volumes:`
    定义宿主机和容器之间的目录映射。
13. `- ./runtime:/app/runtime`
    把宿主机 `runtime` 目录挂载到容器内，方便保留产物。
14. `command: ["python", "hero_winrate_analysis_refactored.py"]`
    指定容器启动后执行的命令。

---

## 5. 部署说明（150字以内）

本地改完后 push 到 GitHub，服务器执行 `git pull`，再跑 `docker compose up -d --build` 更新容器。`.env` 放在服务器项目根目录，由运维或项目负责人维护，不提交到仓库。

---

## 6. 日志截图 + 定时任务触发截图

- 日志截图：
  [log_capture.png](F:\code\ClaudeCode\pythonhomework\lesson6\log_capture.png)
- 定时任务截图：
  [scheduled_task_capture.png](F:\code\ClaudeCode\pythonhomework\lesson6\scheduled_task_capture.png)

最终一次定时任务验证结果：

- `Last Run Time`: `2026/3/29 20:09:11`
- `Last Result`: `0`

---

## 7. 验证说明

当前电脑未安装 Docker，因此我已完成 Docker 配置文件编写与静态检查，但无法在本机执行 `docker build` / `docker compose up` 做实机验证。

已完成的实际验证包括：

- Python 脚本可正常运行
- `.env` 本地读取正常
- 定时任务自动触发成功
- GitHub 仓库已推送成功
