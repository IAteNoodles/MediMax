import React, { useState, useEffect } from 'react';

const API_URL = '/api';

const Chatbot = ({ patientId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
          setIsHealthy(true);
          setMessages(prev => [...prev, { text: "Backend is healthy. Ready to chat.", sender: 'bot' }]);
        } else {
          setMessages(prev => [...prev, { text: "Backend is not responding.", sender: 'bot' }]);
        }
      } catch (error) {
        console.error('Health check failed:', error);
        setMessages(prev => [...prev, { text: "Failed to connect to the backend.", sender: 'bot' }]);
      }
    };
    checkHealth();
  }, []);

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = { text: input, sender: 'user' };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      
      const requestBody = {
        patient_text: input,
      };

      setInput('');

      try {
        const response = await fetch(`${API_URL}/assess`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: data.response, sender: 'bot' }, // Assuming the response has a 'response' field
        ]);

      } catch (error) {
        console.error("Failed to send message:", error);
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: "Sorry, something went wrong.", sender: 'bot' },
        ]);
      }
    }
  };

  return (
    <div className="fixed bottom-0 right-0 m-8 w-96 bg-white rounded-lg shadow-lg flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold">Patient Chat</h2>
      </div>
      <div className="flex-1 p-4 overflow-y-auto h-64">
        {messages.map((msg, index) => (
          <div key={index} className={`my-2 p-2 rounded-lg ${
            msg.sender === 'user' ? 'bg-blue-500 text-white self-end' : 'bg-gray-200 text-gray-800 self-start'
          }`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="p-4 border-t flex">
        <input
          type="text"
          className="flex-1 border rounded-l-lg p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend} className="bg-blue-500 text-white p-2 rounded-r-lg">
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
