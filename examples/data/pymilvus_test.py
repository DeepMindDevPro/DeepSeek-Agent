from pymilvus import connections

# 连接到Milvus服务
connections.connect(
    alias="default",
    host='localhost',
    port='19530'
)

# 检查连接状态
print("连接成功")