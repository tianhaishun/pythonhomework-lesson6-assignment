"""
lesson6 作业 A：基础改造版
基于 lesson5 的英雄战绩查询脚本进行重构，补充日志与定时任务友好能力。
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
import warnings

import pandas as pd
import pymysql

# ==============================
# 配置区
# ==============================
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy connectable",
    category=UserWarning,
)


def get_bool_env(name: str, default: bool) -> bool:
    """把环境变量中的布尔值转成 Python 布尔类型。"""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_runtime_settings() -> dict:
    """读取运行期配置，统一返回给主流程使用。"""
    raw_data_dir = Path(os.environ.get("APP_DATA_DIR", str(BASE_DIR)))
    data_dir = raw_data_dir if raw_data_dir.is_absolute() else (BASE_DIR / raw_data_dir).resolve()
    output_excel_name = os.environ.get("OUTPUT_EXCEL_NAME", "hero_winrate_refactored.xlsx")
    log_file_name = os.environ.get("LOG_FILE_NAME", "task.log")

    return {
        "data_dir": data_dir,
        "output_excel": data_dir / output_excel_name,
        "log_file": data_dir / log_file_name,
        "min_total_games": int(os.environ.get("MIN_TOTAL_GAMES", "30")),
        "analyst_name": os.environ.get("ANALYST_NAME", "lesson6_auto_task"),
        "write_analysis_log": get_bool_env("WRITE_ANALYSIS_LOG", True),
    }


def setup_logger(log_file: Path) -> logging.Logger:
    """初始化日志，让日志同时输出到屏幕和 task.log。"""
    logger = logging.getLogger("hero_winrate_refactored")
    if logger.handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:
                pass

    log_file.parent.mkdir(parents=True, exist_ok=True)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def load_env_file() -> None:
    """读取本地 .env 文件，把数据库配置加载到环境变量。"""
    if not ENV_FILE.exists():
        return

    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        normalized_key = key.strip().lstrip("\ufeff")
        os.environ.setdefault(normalized_key, value.strip())


def build_db_config() -> dict:
    """从环境变量构建数据库配置，避免把敏感信息写入代码仓库。"""
    return {
        "host": os.environ.get("DB_HOST", ""),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", ""),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", ""),
        "charset": os.environ.get("DB_CHARSET", "utf8mb4"),
    }


def validate_db_config(db_config: dict) -> list[str]:
    """检查数据库关键配置是否已经完整提供。"""
    missing = []
    required_map = {
        "DB_HOST": db_config.get("host"),
        "DB_USER": db_config.get("user"),
        "DB_PASSWORD": db_config.get("password"),
        "DB_NAME": db_config.get("database"),
    }
    for env_name, value in required_map.items():
        if not value:
            missing.append(env_name)
    return missing


def connect_to_database(logger: logging.Logger):
    """连接数据库，失败时记录错误日志。"""
    db_config = build_db_config()
    missing_items = validate_db_config(db_config)
    if missing_items:
        logger.error("缺少数据库配置: %s", ", ".join(missing_items))
        logger.error("请在环境变量或 .env 文件中提供这些配置后再执行")
        return None

    try:
        connection = pymysql.connect(**db_config)
        logger.info("数据库连接成功")
        return connection
    except Exception as exc:
        logger.exception("数据库连接失败: %s", exc)
        return None


def fetch_hero_statistics(connection, logger: logging.Logger, min_total_games: int) -> pd.DataFrame:
    """查询英雄统计数据，并按胜率从高到低返回。"""
    sql = f"""
    SELECT
        h.hero_id,
        h.hero_name,
        h.role,
        h.attack_type,
        COUNT(br.record_id) AS total_games,
        SUM(br.is_win) AS win_games,
        ROUND(SUM(br.is_win) / COUNT(br.record_id), 3) AS win_rate
    FROM
        hero h
    INNER JOIN
        battle_record br ON h.hero_id = br.hero_id
    GROUP BY
        h.hero_id, h.hero_name, h.role, h.attack_type
    HAVING
        total_games >= %s
    ORDER BY
        win_rate DESC;
    """

    df = pd.read_sql(sql, connection, params=[min_total_games])
    logger.info("查询完成，共获取 %s 个英雄的数据", len(df))
    return df


def build_export_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """整理导出用的数据格式，并改成更易读的中文列名。"""
    export_df = df.copy()
    export_df["win_rate"] = (export_df["win_rate"] * 100).round(1)
    export_df.columns = [
        "英雄ID",
        "英雄名称",
        "职业",
        "普攻类型",
        "总场次",
        "胜场数",
        "胜率(%)",
    ]
    return export_df


def log_statistics_summary(df: pd.DataFrame, logger: logging.Logger) -> None:
    """输出核心统计摘要，方便从日志中直接查看结果。"""
    total_heroes = len(df)
    avg_win_rate = (df["win_rate"] * 100).mean()
    top_hero = df.iloc[0]

    logger.info("统计摘要开始")
    logger.info("总英雄数: %s", total_heroes)
    logger.info("平均胜率: %.1f%%", avg_win_rate)
    logger.info(
        "胜率最高英雄: %s | 职业: %s | 胜率: %.1f%% | 场次: %s",
        top_hero["hero_name"],
        top_hero["role"],
        top_hero["win_rate"] * 100,
        top_hero["total_games"],
    )

    for rank, (_, row) in enumerate(df.head(3).iterrows(), start=1):
        logger.info(
            "TOP%s: %s | 胜率: %.1f%% | 场次: %s",
            rank,
            row["hero_name"],
            row["win_rate"] * 100,
            row["total_games"],
        )


def export_to_excel(df: pd.DataFrame, logger: logging.Logger, output_excel: Path) -> None:
    """将分析结果导出成 Excel 文件。"""
    export_df = build_export_dataframe(df)
    output_excel.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_excel(output_excel, index=False, engine="openpyxl")
    logger.info("Excel 导出成功: %s", output_excel)


def write_analysis_log(connection, df: pd.DataFrame, logger: logging.Logger, analyst_name: str) -> None:
    """把分析结果写入 analysis_log 表，便于后续追踪。"""
    cursor = connection.cursor()
    run_sql = """
    INSERT INTO analysis_log
    (hero_id, hero_name, total_games, win_games, win_rate, analyst, run_time)
    VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """

    try:
        for _, row in df.iterrows():
            cursor.execute(
                run_sql,
                (
                    int(row["hero_id"]),
                    row["hero_name"],
                    int(row["total_games"]),
                    int(row["win_games"]),
                    float(row["win_rate"]),
                    analyst_name,
                ),
            )
        connection.commit()
        logger.info("analysis_log 写入成功，共写入 %s 条记录", len(df))
    except Exception as exc:
        connection.rollback()
        logger.exception("analysis_log 写入失败: %s", exc)
        raise
    finally:
        cursor.close()


def main() -> int:
    """主流程：连接数据库、查询数据、记录日志、导出结果。"""
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    load_env_file()
    settings = build_runtime_settings()
    logger = setup_logger(settings["log_file"])
    logger.info("任务开始执行")
    logger.info(
        "配置区: OUTPUT_EXCEL=%s, LOG_FILE=%s, MIN_TOTAL_GAMES=%s, ANALYST_NAME=%s",
        settings["output_excel"],
        settings["log_file"],
        settings["min_total_games"],
        settings["analyst_name"],
    )

    connection = connect_to_database(logger)
    if connection is None:
        return 1

    try:
        df = fetch_hero_statistics(connection, logger, settings["min_total_games"])
        if df.empty:
            logger.warning("没有查询到符合条件的数据")
            return 1

        log_statistics_summary(df, logger)
        export_to_excel(df, logger, settings["output_excel"])

        if settings["write_analysis_log"]:
            write_analysis_log(connection, df, logger, settings["analyst_name"])

        logger.info("任务执行完成")
        return 0
    except Exception as exc:
        logger.exception("任务执行失败: %s", exc)
        return 1
    finally:
        connection.close()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    raise SystemExit(main())
