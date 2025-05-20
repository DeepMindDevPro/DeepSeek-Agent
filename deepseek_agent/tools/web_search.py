# deepseek_agent/tools/web_search.py
import os
from typing import Union
from dotenv import load_dotenv

import requests
from deepseek_agent.tools.base import BaseTool

# 加载.env文件
load_dotenv()

DEEPSEEK_SEARCH_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_SEARCH_URL = os.getenv('DEEPSEEK_SEARCH_URL', 'https://api.deepseek.com/chat/completions')

print(DEEPSEEK_SEARCH_API_KEY)
print(DEEPSEEK_SEARCH_URL)

class WebSearch(BaseTool):
    name = 'web_search'
    description = 'Search for information from the internet.'
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

        search_results = self.search(query)
        formatted_results = self._format_results(search_results)
        return formatted_results

    @staticmethod
    def search(query: str) -> list:
        if not DEEPSEEK_SEARCH_API_KEY:
            raise ValueError(
                'DEEPSEEK_SEARCH_API_KEY is None! Please set it as an environment variable.')
        headers = {'Content-Type': 'application/json', 'X-API-KEY': DEEPSEEK_SEARCH_API_KEY}
        payload = {'q': query}
        response = requests.post(DEEPSEEK_SEARCH_URL, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()['organic']

    @staticmethod
    def _format_results(search_results: list) -> str:
        content = '```\n{}\n```'.format('\n\n'.join([
            f"[{i}]\"{doc['title']}\n{doc.get('snippet', '')}\"{doc.get('date', '')}"
            for i, doc in enumerate(search_results, 1)
        ]))
        return content