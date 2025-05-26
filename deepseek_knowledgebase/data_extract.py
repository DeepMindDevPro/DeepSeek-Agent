from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModel
import torch

# 连接 Milvus
connections.connect(alias="default", host='localhost', port='19530')

# 定义集合字段
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768)
]

# 定义集合模式
schema = CollectionSchema(fields=fields, description="Knowledge base collection")

# 创建集合
collection_name = "knowledge_base"
collection = Collection(name=collection_name, schema=schema)

# 加载预训练的模型和分词器
tokenizer = AutoTokenizer.from_pretrained('bert-base-chinese')
model = AutoModel.from_pretrained('bert-base-chinese')

def parse_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        print(f"解析 HTML 文件时出错: {e}")
        return None

def get_embedding(text):
    try:
        inputs = tokenizer(text, return_tensors='pt')
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
        return embedding
    except Exception as e:
        print(f"生成嵌入向量时出错: {e}")
        return None

file_path = '/Users/gechunfa1/Documents/ai/DeepSeek-Agent/deepseek_knowledgebase/对话补全.html'
html_text = parse_html_file(file_path)
print(html_text)

# if html_text:
#     vector = get_embedding(html_text)
#     if vector is not None:
#         data = [
#             [html_text],
#             [vector.tolist()]
#         ]
#         # 插入数据
#         collection.insert(data)
#         # 刷新集合
#         collection.flush()
#         print("数据已成功存入 Milvus 数据库。")
#     else:
#         print("未能生成嵌入向量，数据未存入 Milvus 数据库。")
# else:
#     print("未能解析 HTML 文件，数据未存入 Milvus 数据库。")