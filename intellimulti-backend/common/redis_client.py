import json
import pickle
import base64
import logging
import redis
from typing import Any, Optional, Union, Dict, List, Tuple
from config.settings import settings

# 配置日志
logger = logging.getLogger("redis_client")
logger.setLevel(logging.INFO)


class RedisSerializer:
    """Redis数据序列化器"""

    @staticmethod
    def serialize(value: Any) -> str:
        """序列化任意类型的数据为字符串"""
        try:
            if isinstance(value, (str, int, float, bool)) or value is None:
                # 基础类型直接JSON序列化
                return json.dumps({
                    "type": "basic",
                    "data": value
                })
            elif isinstance(value, (dict, list, tuple, set)):
                # 容器类型使用JSON
                return json.dumps({
                    "type": "json",
                    "data": value
                })
            else:
                # 复杂对象使用pickle序列化
                pickled = pickle.dumps(value)
                encoded = base64.b64encode(pickled).decode('utf-8')
                return json.dumps({
                    "type": "pickle",
                    "data": encoded
                })
        except Exception as e:
            logger.error(f"序列化失败: {str(e)}", exc_info=True)
            raise ValueError(f"无法序列化对象: {e}")

    @staticmethod
    def deserialize(value_str: str) -> Any:
        """反序列化字符串为原始对象"""
        try:
            # 尝试解析为JSON
            data = json.loads(value_str)

            if isinstance(data, dict) and "type" in data and "data" in data:
                data_type = data["type"]
                data_value = data["data"]

                if data_type == "basic":
                    return data_value
                elif data_type == "json":
                    return data_value
                elif data_type == "pickle":
                    # 解码pickle序列化的对象
                    decoded = base64.b64decode(data_value.encode('utf-8'))
                    return pickle.loads(decoded)

            # 如果不是我们的格式，直接返回
            return data
        except json.JSONDecodeError:
            # 如果不是JSON，直接返回字符串
            return value_str
        except Exception as e:
            logger.error(f"反序列化失败: {str(e)}", exc_info=True)
            raise ValueError(f"无法反序列化数据: {e}")


class RedisClient:
    """企业级Redis客户端（单例模式+连接池）支持所有数据类型"""
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
        """初始化Redis连接池"""
        try:
            cls._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                encoding=settings.REDIS_ENCODING,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS
            )
            logger.info("Redis连接池初始化成功")
        except Exception as e:
            logger.error(f"Redis连接池初始化失败: {str(e)}", exc_info=True)
            raise e

    @property
    def client(self):
        """获取Redis客户端（自动从连接池获取连接）"""
        try:
            return redis.Redis(connection_pool=self._pool)
        except Exception as e:
            logger.error(f"获取Redis客户端失败: {str(e)}", exc_info=True)
            raise e

    # ===== 基础字符串操作（保持原样）=====
    def get(self, key: str) -> Optional[str]:
        """获取字符串值"""
        try:
            result = self.client.get(key)
            logger.debug(f"Redis GET {key} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Redis GET {key} 失败: {str(e)}", exc_info=True)
            return None

    def set(self, key: str, value: str, ex: int = None, px: int = None,
            nx: bool = False, xx: bool = False) -> bool:
        """设置字符串值（支持过期时间）"""
        try:
            if not isinstance(value, str):
                logger.warning(f"set方法只接收字符串类型，请使用set_object存储其他类型")
                value = str(value)

            result = self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            logger.debug(f"Redis SET {key} -> {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis SET {key} 失败: {str(e)}", exc_info=True)
            return False

    # ===== 通用对象操作方法 =====
    def set_object(self, key: str, value: Any, ex: int = None, px: int = None,
                   nx: bool = False, xx: bool = False) -> bool:
        """
        存储任意Python对象到Redis

        Args:
            key: 键名
            value: 任意Python对象（字符串、数字、列表、字典、类实例等）
            ex: 过期时间（秒）
            px: 过期时间（毫秒）
            nx: 仅当键不存在时设置
            xx: 仅当键存在时设置

        Returns:
            bool: 是否设置成功
        """
        try:
            # 序列化对象
            serialized_value = RedisSerializer.serialize(value)

            # 存储到Redis
            result = self.client.set(key, serialized_value, ex=ex, px=px, nx=nx, xx=xx)

            if result:
                logger.debug(f"Redis SET_OBJECT {key} 成功 (类型: {type(value).__name__})")
            else:
                logger.warning(f"Redis SET_OBJECT {key} 失败")

            return bool(result)
        except Exception as e:
            logger.error(f"Redis SET_OBJECT {key} 失败: {str(e)}", exc_info=True)
            return False

    def get_object(self, key: str, default: Any = None) -> Any:
        """
        从Redis获取任意Python对象

        Args:
            key: 键名
            default: 默认值（当键不存在时返回）

        Returns:
            Any: 存储的对象或默认值
        """
        try:
            # 获取数据
            value_str = self.client.get(key)

            if value_str is None:
                logger.debug(f"Redis GET_OBJECT {key} -> 键不存在")
                return default

            # 反序列化对象
            result = RedisSerializer.deserialize(value_str)

            logger.debug(f"Redis GET_OBJECT {key} -> {type(result).__name__}")
            return result
        except Exception as e:
            logger.error(f"Redis GET_OBJECT {key} 失败: {str(e)}", exc_info=True)
            return default

    # ===== 类型特定的便捷方法 =====
    def set_dict(self, key: str, value: dict, ex: int = None, **kwargs) -> bool:
        """存储字典"""
        return self.set_object(key, value, ex=ex, **kwargs)

    def get_dict(self, key: str, default: dict = None) -> dict:
        """获取字典"""
        result = self.get_object(key, default)
        if result is None:
            return default or {}
        return result if isinstance(result, dict) else default or {}

    def set_list(self, key: str, value: list, ex: int = None, **kwargs) -> bool:
        """存储列表"""
        return self.set_object(key, value, ex=ex, **kwargs)

    def get_list(self, key: str, default: list = None) -> list:
        """获取列表"""
        result = self.get_object(key, default)
        if result is None:
            return default or []
        return result if isinstance(result, list) else default or []

    def set_int(self, key: str, value: int, ex: int = None, **kwargs) -> bool:
        """存储整数"""
        return self.set_object(key, value, ex=ex, **kwargs)

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数"""
        result = self.get_object(key, default)
        try:
            return int(result)
        except (ValueError, TypeError):
            return default

    def set_bool(self, key: str, value: bool, ex: int = None, **kwargs) -> bool:
        """存储布尔值"""
        return self.set_object(key, value, ex=ex, **kwargs)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔值"""
        result = self.get_object(key, default)
        if isinstance(result, bool):
            return result
        return default

    # ===== 批量操作 =====
    def mset_object(self, mapping: dict, ex: int = None) -> bool:
        """批量设置对象"""
        try:
            pipe = self.client.pipeline()

            for key, value in mapping.items():
                serialized_value = RedisSerializer.serialize(value)
                pipe.set(key, serialized_value, ex=ex)

            results = pipe.execute()
            success = all(results)

            logger.debug(f"Redis MSET_OBJECT 批量设置 {len(mapping)} 个键 -> {success}")
            return success
        except Exception as e:
            logger.error(f"Redis MSET_OBJECT 失败: {str(e)}", exc_info=True)
            return False

    # ===== 保持原有的其他方法 =====
    def delete(self, *keys) -> int:
        """删除键"""
        try:
            count = self.client.delete(*keys)
            logger.debug(f"Redis DELETE {keys} -> 成功删除{count}个键")
            return count
        except Exception as e:
            logger.error(f"Redis DELETE {keys} 失败: {str(e)}", exc_info=True)
            return 0

    def exists(self, *keys) -> int:
        """检查键是否存在"""
        try:
            return self.client.exists(*keys)
        except Exception as e:
            logger.error(f"Redis EXISTS {keys} 失败: {str(e)}", exc_info=True)
            return 0

    def expire(self, key: str, time: int) -> bool:
        """设置键的过期时间（秒）"""
        try:
            result = self.client.expire(key, time)
            logger.debug(f"Redis EXPIRE {key} {time}s -> {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis EXPIRE {key} 失败: {str(e)}", exc_info=True)
            return False

    def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL {key} 失败: {str(e)}", exc_info=True)
            return -2

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """自增操作"""
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR {key} 失败: {str(e)}", exc_info=True)
            return None

    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """自减操作"""
        try:
            return self.client.decr(key, amount)
        except Exception as e:
            logger.error(f"Redis DECR {key} 失败: {str(e)}", exc_info=True)
            return None

    def hgetall(self, key: str) -> dict:
        """获取哈希所有字段"""
        try:
            result = self.client.hgetall(key)
            logger.debug(f"Redis HGETALL {key} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL {key} 失败: {str(e)}", exc_info=True)
            return {}

    def hmset(self, key: str, mapping: dict) -> bool:
        """设置哈希多个字段"""
        try:
            result = self.client.hmset(key, mapping)
            logger.debug(f"Redis HMSET {key} -> {result}")
            return result
        except Exception as e:
            logger.error(f"Redis HMSET {key} 失败: {str(e)}", exc_info=True)
            return False

    def hget(self, key: str, field: str) -> Optional[str]:
        """获取哈希字段值"""
        try:
            return self.client.hget(key, field)
        except Exception as e:
            logger.error(f"Redis HGET {key}.{field} 失败: {str(e)}", exc_info=True)
            return None

    # ===== 高级功能 =====
    def set_with_lock(self, key: str, value: Any, ex: int = 30,
                      lock_timeout: int = 10) -> bool:
        """带分布式锁的设置操作"""
        lock_key = f"lock:{key}"

        try:
            # 尝试获取锁
            lock_acquired = self.client.set(
                lock_key, "1", ex=lock_timeout, nx=True
            )

            if not lock_acquired:
                logger.warning(f"获取锁失败: {lock_key}")
                return False

            # 执行设置操作
            result = self.set_object(key, value, ex=ex)

            # 释放锁
            self.client.delete(lock_key)

            return result
        except Exception as e:
            logger.error(f"带锁设置失败 {key}: {str(e)}", exc_info=True)
            # 确保锁被释放
            try:
                self.client.delete(lock_key)
            except:
                pass
            return False

    def cacheable(self, key: str, func: callable, ex: int = 3600,
                  force_refresh: bool = False) -> Any:
        """
        缓存装饰器功能

        Args:
            key: 缓存键
            func: 获取数据的函数
            ex: 缓存过期时间
            force_refresh: 是否强制刷新

        Returns:
            Any: 缓存或函数返回的数据
        """
        # 如果不强制刷新，尝试从缓存获取
        if not force_refresh:
            cached = self.get_object(key)
            if cached is not None:
                logger.debug(f"缓存命中: {key}")
                return cached

        # 执行函数获取数据
        try:
            data = func()
            if data is not None:
                self.set_object(key, data, ex=ex)
                logger.debug(f"缓存设置: {key}")
            return data
        except Exception as e:
            logger.error(f"缓存函数执行失败 {key}: {str(e)}", exc_info=True)
            raise e

    def close(self):
        """关闭连接"""
        try:
            self.client.close()
            logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接失败: {str(e)}")


# 单例实例（全局唯一）
redis_client = RedisClient()

# 使用示例
if __name__ == "__main__":
    # 示例类
    class User:
        def __init__(self, name: str, age: int):
            self.name = name
            self.age = age

        def __repr__(self):
            return f"User(name={self.name}, age={self.age})"


    # 测试各种数据类型
    # 1. 基础类型
    redis_client.set_object("test:int", 42)
    redis_client.set_object("test:str", "hello")
    redis_client.set_object("test:bool", True)
    redis_client.set_object("test:float", 3.14)

    # 2. 容器类型
    redis_client.set_object("test:list", [1, 2, 3, {"a": 1}])
    redis_client.set_object("test:dict", {"name": "张三", "age": 25})

    # 3. 类实例
    user = User("李四", 30)
    redis_client.set_object("test:user", user)

    # 4. 获取数据
    print("整数:", redis_client.get_object("test:int"))
    print("字符串:", redis_client.get_object("test:str"))
    print("布尔值:", redis_client.get_object("test:bool"))
    print("列表:", redis_client.get_object("test:list"))
    print("字典:", redis_client.get_object("test:dict"))

    retrieved_user = redis_client.get_object("test:user")
    print("用户对象:", retrieved_user)
    print("用户姓名:", retrieved_user.name)

    # 5. 使用便捷方法
    redis_client.set_dict("config", {"theme": "dark", "language": "zh"})
    config = redis_client.get_dict("config")
    print("配置:", config)


    # 6. 带缓存的方法
    def fetch_data_from_db():
        print("从数据库获取数据...")
        return {"data": [1, 2, 3, 4, 5]}


    # 第一次调用会执行函数
    data1 = redis_client.cacheable("cache:data", fetch_data_from_db, ex=60)
    print("第一次获取:", data1)

    # 第二次调用从缓存获取
    data2 = redis_client.cacheable("cache:data", fetch_data_from_db, ex=60)
    print("第二次获取:", data2)

    # 清理测试数据
    keys = ["test:int", "test:str", "test:bool", "test:float",
            "test:list", "test:dict", "test:user", "config", "cache:data"]
    redis_client.delete(*keys)

    # 关闭连接
    redis_client.close()