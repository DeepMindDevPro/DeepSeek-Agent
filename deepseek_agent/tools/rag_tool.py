import os
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
from deepseek_agent.tools.base import BaseTool
from typing import Union

# 连接到 Milvus
connections.connect(
    alias="default",
    host=os.getenv('MILVUS_HOST', 'localhost'),
    port=os.getenv('MILVUS_PORT', '19530')
)

# 创建或加载 Milvus 集合
collection_name = "my_collection"
dim = 384  # all-MiniLM-L6-v2 模型的向量维度
fields = [
    {"name": "id", "type": "VARCHAR", "params": {"max_length": 64}, "is_primary": True},
    {"name": "embedding", "type": "FLOAT_VECTOR", "params": {"dim": dim}},
    {"name": "document", "type": "VARCHAR", "params": {"max_length": 2048}}
]
schema = {
    "name": collection_name,
    "fields": fields
}
collection = Collection(name=collection_name, schema=schema)
collection.load()

# 加载预训练的嵌入模型
model = SentenceTransformer('all-MiniLM-L6-v2')

def add_document(text):
    """向数据存储模块添加文档"""
    embedding = model.encode(text).tolist()
    id = str(len(collection.query(expr="id >= '0'")))
    data = [
        [id],
        [embedding],
        [text]
    ]
    collection.insert(data)
    collection.flush()

def retrieve_documents(query, top_k=3):
    """从数据存储模块中检索与查询相关的文档"""
    query_embedding = model.encode(query).tolist()
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10}
    }
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["document"]
    )
    return [hit.entity.get("document") for hit in results[0]]

class RAGTool(BaseTool):
    name = 'rag_tool'
    description = 'Retrieve relevant documents using RAG.'
    parameters = {
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
            }
        },
        'required': ['query'],
    }

    def call(self, params: Union[str, dict], **kwargs) -> str:
        params = self._verify_json_format_args(params)
        query = params['query']
        # 检索相关文档
        relevant_docs = retrieve_documents(query)
        # 将检索到的文档与查询一起传递给生成模型
        messages = [
            {"role": "user", "content": f"查询: {query}\n相关文档: {' '.join(relevant_docs)}"}
        ]
        # 调用 DeepSeekChatModel 进行生成
        response = self.llm.chat(messages)
        result = ""
        for chunk in response:
            result += chunk["choices"][0]["message"]["content"]
        return result