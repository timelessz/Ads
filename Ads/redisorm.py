import redis


def get_redis():
    try:
        # host is the redis host,the redis server and client are required to open, and the redis default port is 6379
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1)
        r = redis.Redis(connection_pool=pool)
        return r
    except:
        return None
