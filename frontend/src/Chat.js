import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input) return;
    setMessages([...messages, { text: input, sender: 'user' }]);
    setInput('');
    setLoading(true);

    try {
      const eventSource = new EventSource(`http://localhost:8000/chat?message=${encodeURIComponent(input)}`);
      let responseText = '';

      eventSource.onmessage = (event) => {
        responseText += event.data;
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last.sender === 'bot') {
            last.text = responseText;
            return [...prev.slice(0, -1), last];
          }
          return [...prev, { text: responseText, sender: 'bot' }];
        });
      };

      eventSource.onerror = () => {
        eventSource.close();
        setLoading(false);
      };
    } catch (error) {
      setMessages([...messages, { text: 'Error: ' + error.message, sender: 'bot' }]);
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ height: '400px', overflowY: 'scroll' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <ReactMarkdown>{msg.text}</ReactMarkdown>  {/* For citations/previews */}
          </div>
        ))}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} disabled={loading} />
      <button onClick={sendMessage} disabled={loading}>Send</button>
    </div>
  );
};

export default Chat;
