import React, { useState, useEffect, useRef } from 'react';
import './Chat.css'; // Import the external CSS file


const Chat = () => {

  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = () => {
    if (userInput.trim() !== '') {
      const newUserMessage = { sender: 'You', text: userInput };
      setMessages((prevMessages) => [...prevMessages, newUserMessage]);

      fetch('http://localhost:5000/ask_openai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userInput }),
      })
        .then((response) => response.json())
        .then((data) => {
          const newBotMessage = { sender: 'PantherAI', text: data.answer };
          setMessages((prevMessages) => [...prevMessages, newBotMessage]);
        })
        .catch((error) => {
          console.error('Error:', error);
        });

      setUserInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender === 'You' ? 'user-message' : 'bot-message'}`}>
            <div className="message-bubble">
              <p>{message.text}</p>
              <span className="message-sender">{message.sender}</span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={handleKeyPress} // Listen for keypress event
          className="input-box"
          placeholder="Type your message..."
        />
        <button onClick={sendMessage} className="send-button">
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat;
