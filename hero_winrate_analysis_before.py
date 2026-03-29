"""
英雄战绩查询与统计脚本
作业 A：英雄战绩查询与统计（基础版）
功能：查询数据库，计算英雄胜率，导出Excel报表
"""

import pymysql
import pandas as pd
from datetime import datetime
import sys

# 设置Windows终端编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 数据库连接配置
DB_CONFIG = {
    'host': '<请在环境变量中配置 DB_HOST>',
    'port': 3306,
    'user': '<请在环境变量中配置 DB_USER>',
    'password': '<请在环境变量中配置 DB_PASSWORD>',
    'database': '<请在环境变量中配置 DB_NAME>',
    'charset': 'utf8mb4'
}


def connect_to_database():
    """连接到MySQL数据库"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✓ 数据库连接成功！")
        return connection
    except Exception as e:
        print(f"✗ 数据库连接失败：{e}")
        return None


def query_hero_data(connection):
    """
    查询并合并hero表和battle_record表的数据
    计算每个英雄的总场次、胜场数、胜率
    """
    try:
        # SQL查询：连接两张表，计算统计指标
        sql = """
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
            total_games >= 30
        ORDER BY
            win_rate DESC;
        """

        # 使用pandas读取数据
        df = pd.read_sql(sql, connection)
        print(f"✓ 查询成功！共获取 {len(df)} 个英雄的数据")
        return df

    except Exception as e:
        print(f"✗ 查询失败：{e}")
        return None


def export_to_excel(df, filename='hero_winrate.xlsx'):
    """
    导出数据到Excel文件
    """
    try:
        # 将胜率转换为百分比格式，保留一位小数
        df_export = df.copy()
        df_export['win_rate'] = (df_export['win_rate'] * 100).round(1)

        # 重命名列（中文列名）
        df_export.columns = [
            '英雄ID', '英雄名称', '职业', '普攻类型',
            '总场次', '胜场数', '胜率(%)'
        ]

        # 导出到Excel
        df_export.to_excel(filename, index=False, engine='openpyxl')
        print(f"✓ 成功导出文件：{filename}")
        return True

    except Exception as e:
        print(f"✗ 导出失败：{e}")
        return False


def print_statistics(df):
    """
    打印统计摘要
    """
    print("\n" + "="*50)
    print("📊 统计摘要")
    print("="*50)

    # 总英雄数
    total_heroes = len(df)
    print(f"总英雄数：{total_heroes}")

    # 平均胜率
    avg_win_rate = (df['win_rate'] * 100).mean()
    print(f"平均胜率：{avg_win_rate:.1f}%")

    # 胜率最高的英雄
    top_hero = df.iloc[0]
    print(f"\n🏆 胜率最高的英雄：")
    print(f"  - 名称：{top_hero['hero_name']}")
    print(f"  - 职业：{top_hero['role']}")
    print(f"  - 总场次：{top_hero['total_games']}")
    print(f"  - 胜场数：{top_hero['win_games']}")
    print(f"  - 胜率：{top_hero['win_rate'] * 100:.1f}%")

    # 胜率前3名
    print(f"\n🥇 胜率排行榜 TOP 3：")
    for i, (idx, row) in enumerate(df.head(3).iterrows(), 1):
        medal = ['🥇', '🥈', '🥉'][i-1]
        print(f"  {medal} {row['hero_name']} - {row['win_rate']*100:.1f}% ({row['total_games']}场)")

    print("="*50 + "\n")


def insert_analysis_log(connection, df, analyst_name="学员"):
    """
    将分析结果写入analysis_log表
    """
    try:
        cursor = connection.cursor()
        run_time = datetime.now()

        # 准备插入数据
        for _, row in df.iterrows():
            sql = """
            INSERT INTO analysis_log
            (hero_id, hero_name, total_games, win_games, win_rate, analyst, run_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                row['hero_id'],
                row['hero_name'],
                int(row['total_games']),
                int(row['win_games']),
                float(row['win_rate']),
                analyst_name,
                run_time
            )
            cursor.execute(sql, values)

        connection.commit()
        print(f"✓ 成功写入分析日志表，共 {len(df)} 条记录")

    except Exception as e:
        print(f"✗ 写入日志失败：{e}")
        connection.rollback()


def main():
    """主函数"""
    print("\n" + "="*50)
    print("🎮 英雄战绩分析系统")
    print("="*50 + "\n")

    # 1. 连接数据库
    connection = connect_to_database()
    if not connection:
        return

    try:
        # 2. 查询数据
        df = query_hero_data(connection)
        if df is None or df.empty:
            print("没有查询到数据！")
            return

        # 3. 打印统计摘要
        print_statistics(df)

        # 4. 导出Excel
        export_to_excel(df, 'hero_winrate.xlsx')

        # 5. 写入分析日志（可选，需要分析人姓名）
        analyst_name = input("\n请输入分析人姓名（用于日志记录）：").strip()
        if analyst_name:
            insert_analysis_log(connection, df, analyst_name)

        print("\n✅ 分析完成！")

    finally:
        connection.close()
        print("数据库连接已关闭")


if __name__ == "__main__":
    main()
