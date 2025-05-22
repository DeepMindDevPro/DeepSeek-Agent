import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from deepseek_agent.tools.base import BaseTool
from typing import Union

# 初始化 Chroma 客户端
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=".chromadb"
))

# 创建一个集合
collection = client.create_collection(name="my_collection")

# 加载预训练的嵌入模型
model = SentenceTransformer('all-MiniLM-L6-v2')

def add_document(text):
    """向数据存储模块添加文档"""
    embedding = model.encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(len(collection.get()['ids']))]
    )
    client.persist()

def retrieve_documents(query, top_k=3):
    """从数据存储模块中检索与查询相关的文档"""
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0]

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