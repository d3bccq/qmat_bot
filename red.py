import redis

r = redis.Redis(host='192.168.0.137', 
                           port=6379, 
                           db=0)