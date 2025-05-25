import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaperPlane } from '@fortawesome/free-solid-svg-icons';
import remarkGfm from 'remark-gfm';

// 自定义Markdown渲染组件，处理样式和格式
const MarkdownContent = ({ children }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="mb-2 text-gray-800">{children}</p>,
        h1: ({ children }) => <h1 className="text-xl font-bold mb-3 text-gray-900">{children}</h1>,
        h2: ({ children }) => <h2 className="text-lg font-bold mb-2 text-gray-900">{children}</h2>,
        ul: ({ children }) => <ul className="list-disc pl-5 mb-2 text-gray-800">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 text-gray-800">{children}</ol>,
        code: ({ inline, className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          return inline ? (
            <code className="bg-gray-100 px-1 py-0.5 rounded text-sm text-red-600" {...props}>
              {children}
            </code>
          ) : (
            <div className="bg-gray-800 text-white p-3 rounded mb-2 overflow-x-auto">
              <pre className="m-0">
                <code className={match ? `language-${match[1]}` : ''} {...props}>
                  {children}
                </code>
              </pre>
            </div>
          );
        },
      }}
    >
      {children}
    </ReactMarkdown>
  );
};

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isSending) return;

    setIsSending(true);
    const newMessage = { role: 'user', content: inputValue };
    setMessages([...messages, newMessage]);
    setInputValue('');

    try {
      const response = await axios.post('http://localhost:5000/api/chat', { messages: [newMessage] });
      response.data.forEach(res => {
        const botMessage = { role: 'assistant', content: res.choices[0].message.content };
        const thinkContent = res.choices[0].think_content;
        setMessages(prev => [
          ...prev,
          ...(thinkContent ? [{ role: 'think', content: thinkContent }, botMessage] : [botMessage])
        ]);
      });
    } catch (error) {
      console.error('发送失败:', error);
      setMessages(prev => [
        ...prev,
        { role: 'error', content: '⚠️ 消息发送失败，请检查网络' }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans">
      {/* 顶部导航栏 */}
      <div className="bg-white shadow-md py-3 px-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white">
            <FontAwesomeIcon icon={faPaperPlane} size="lg" />
          </div>
          <h1 className="text-lg font-semibold text-gray-800">智能对话助手</h1>
        </div>
        <div className="text-xs text-gray-500">{new Date().toLocaleString()}</div>
      </div>

      {/* 消息列表区域 */}
      <div className="flex-1 overflow-y-auto p-4 pb-24">
        {messages.map((msg, idx) => {
          const { role, content } = msg;
          const styles = {
            user: {
              container: 'bg-blue-50 border-blue-200',
              icon: '👤',
              title: '用户提问消息'
            },
            assistant: {
              container: 'bg-green-50 border-green-200',
              icon: '🤖',
              title: '智能助手回复'
            },
            think: {
              container: 'bg-yellow-50 border-yellow-200',
              icon: '💡',
              title: 'DeepSeek思考过程'
            },
            error: {
              container: 'bg-red-50 border-red-200',
              icon: '⚠️',
              title: '错误提示'
            }
          }[role] || { container: 'bg-gray-50 border-gray-200', icon: 'ℹ️', title: '系统消息' };

          return (
            <div
              key={idx}
              className={`mb-4 p-4 rounded-lg border-2 ${styles.container} max-w-4xl mx-auto transition-shadow hover:shadow-md`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1 text-sm font-medium text-gray-600">
                  {styles.icon} {styles.title}
                </div>
                <div className="text-xs text-gray-500">{new Date().toLocaleTimeString()}</div>
              </div>
              <MarkdownContent>{content}</MarkdownContent>
            </div>
          );
        })}
      </div>

      {/* 底部输入区域（居中处理） */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white shadow-lg">
        <div className="max-w-4xl mx-auto w-full">
          <div className="relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              className="w-full p-4 pr-14 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400/30 transition-all duration-300 resize-none min-h-[100px] shadow-sm"
              placeholder="输入消息（按Enter发送，Shift+Enter换行）..."
              maxLength={2000}
            />
            <button
              onClick={handleSendMessage}
              className="absolute right-3 bottom-3 bg-blue-500 hover:bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSending || !inputValue.trim()}
            >
              {isSending ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <FontAwesomeIcon icon={faPaperPlane} size="lg" />
              )}
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-1 text-right">
            {inputValue.length}/2000 字符
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;