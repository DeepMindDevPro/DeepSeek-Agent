# deepseek_agent/tools/web_browser.py（新增浏览器工具）
from deepseek_agent.tools.base import BaseTool
from playwright.sync_api import sync_playwright

# 浏览器助手
class WebBrowserTool(BaseTool):
    name = 'web_browser'
    description = '操作浏览器执行网页导航、数据提取等任务'
    parameters = {
        'type': 'object',
        'properties': {
            'url': {'type': 'string'},
            'query': {'type': 'string'}
        },
        'required': ['url']
    }

    def call(self, params: dict) -> str:
        url = params['url']
        query = params.get('query', '')
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            # 提取页面内容（示例）
            content = page.query_selector("body").inner_text()
            browser.close()
            return f"页面内容摘要：{content[:500]}..."