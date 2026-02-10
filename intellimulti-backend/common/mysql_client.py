import logging
import pymysql
from dbutils.pooled_db import PooledDB

from config.settings import settings

# 配置日志（企业级必备）
logger = logging.getLogger("mysql_client")
logger.setLevel(logging.INFO)

class MySQLClient:
    """企业级MySQL连接池客户端（单例模式）"""
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化连接池
            cls._init_pool()
        return cls._instance

    @classmethod
    def _init_pool(cls):
        """初始化MySQL连接池"""
        try:
            cls._pool = PooledDB(
                creator=pymysql,
                maxconnections=settings.MYSQL_POOL_SIZE,
                mincached=2,          # 最小空闲连接数
                maxcached=5,          # 最大空闲连接数
                maxshared=3,          # 最大共享连接数
                blocking=True,        # 连接耗尽时是否阻塞
                maxusage=None,        # 单个连接最大使用次数
                setsession=[],        # 会话初始化语句
                ping=1,               # 检查连接可用性（1=每次都检查）
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB,
                charset=settings.MYSQL_CHARSET
            )
            logger.info("MySQL连接池初始化成功")
        except Exception as e:
            logger.error(f"MySQL连接池初始化失败: {str(e)}", exc_info=True)
            raise e

    def get_connection(self):
        """获取数据库连接（自动从连接池获取）"""
        try:
            conn = self._pool.connection()
            # 设置自动提交（可选，根据业务调整）
            conn.autocommit(True)
            return conn
        except Exception as e:
            logger.error(f"获取MySQL连接失败: {str(e)}", exc_info=True)
            raise e

    def execute_query(self, sql, params=None):
        """执行查询语句（返回结果列表）"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)  # 返回字典格式
            cursor.execute(sql, params or ())
            result = cursor.fetchall()
            logger.info(f"执行SQL成功: {sql[:100]}... 影响行数: {cursor.rowcount}")
            return result
        except Exception as e:
            logger.error(f"执行查询SQL失败: {sql[:100]}... 错误: {str(e)}", exc_info=True)
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()  # 归还到连接池，不是真正关闭

    def execute_modify(self, sql, params=None):
        """执行增删改语句（返回受影响行数）"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            affected_rows = cursor.rowcount
            logger.info(f"执行修改SQL成功: {sql[:100]}... 影响行数: {affected_rows}")
            return affected_rows
        except Exception as e:
            conn.rollback()  # 异常回滚
            logger.error(f"执行修改SQL失败: {sql[:100]}... 错误: {str(e)}", exc_info=True)
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# 单例实例（全局唯一）
mysql_client = MySQLClient()