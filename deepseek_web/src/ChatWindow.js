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
                    setMessages(prevMessages => [...prevMessages, thinkMessage, botMessage]);
                } else {
                    setMessages(prevMessages => [...prevMessages, botMessage]);
                }
            });
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <div className="flex-grow overflow-y-auto p-4">
                {messages.map((message, index) => {
                    if (message.role === 'think') {
                        return (
                            <div
                                key={index}
                                className="mb-2 p-3 rounded-md bg-yellow-100 self-start"
                            >
                                <div className="text-xs text-gray-600">思维链内容</div>
                                <div>{message.content}</div>
                            </div>
                        );
                    } else if (message.role === 'assistant') {
                        return (
                            <div
                                key={index}
                                className="mb-2 p-3 rounded-md bg-gray-200 self-start"
                            >
                                <div className="text-xs text-gray-600">实际答案内容</div>
                                <div>{message.content}</div>
                            </div>
                        );
                    } else {
                        return (
                            <div
                                key={index}
                                className="mb-2 p-3 rounded-md bg-blue-100 self-end"
                            >
                                {message.content}
                            </div>
                        );
                    }
                })}
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