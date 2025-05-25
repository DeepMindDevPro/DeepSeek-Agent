import React, { useState } from 'react';
import axios from 'axios';

const ChatWindow = () => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');

    const handleSendMessage = async () => {
        if (inputValue.trim() === '') return;
        const newMessage = { role: 'user', content: inputValue };
        setMessages([...messages, newMessage]);
        setInputValue('');

        try {
            const response = await axios.post('http://localhost:5000/api/chat', { messages: [newMessage] });
            response.data.forEach(res => {
                const botMessage = { role: 'assistant', content: res.choices[0].message.content };
                const thinkContent = res.choices[0].think_content;
                if (thinkContent) {
                    const thinkMessage = { role: 'think', content: thinkContent };
                    setMessages(prevMessages => [...prevMessages, thinkMessage, botMessage]); // 不再重复添加用户消息
                } else {
                    setMessages(prevMessages => [...prevMessages, botMessage]); // 不再重复添加用户消息
                }
            });
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <div className="flex-grow overflow-y-auto p-4">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`mb-2 p-3 rounded-md ${
                            message.role === 'user' ? 'bg-blue-100 self-end' :
                            message.role === 'think' ? 'bg-yellow-100 self-start' : 'bg-gray-200 self-start'
                        }`}
                    >
                        {message.content}
                    </div>
                ))}
            </div>
            <div className="flex p-4 border-t border-gray-300">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    className="flex-grow p-2 border border-gray-300 rounded-md mr-2"
                    placeholder="输入你的消息"
                />
                <button
                    onClick={handleSendMessage}
                    className="px-4 py-2 bg-blue-500 text-white rounded-md"
                >
                    发送你的消息
                </button>
            </div>
        </div>
    );
};

export default ChatWindow;