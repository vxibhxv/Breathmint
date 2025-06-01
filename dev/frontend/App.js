import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const LOCAL_STORAGE_CHAT_KEY = 'savedChatHistoryApp'; // Unique key for localStorage

// Define the paths to your background images with fallbacks
const backgroundImages = [
  '/images/bg1.jpg',
  '/images/bg2.jpg', 
  '/images/bg3.jpg',
  '/images/bg4.jpg',
  '/images/bg5.jpg',
];

const buttonLabels = ['Seoul Streets', 'Ranger HQ', 'Monument', 'Hotel Bar', 'Combat Zone'];

function App() {
  const [inputValue, setInputValue] = useState('');
  const [currentBackground, setCurrentBackground] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [gameConnected, setGameConnected] = useState(false);
  const chatWindowRef = useRef(null);

  // Initialize background with fallback
  useEffect(() => {
    const testImage = new Image();
    testImage.onload = () => {
      setCurrentBackground(process.env.PUBLIC_URL + backgroundImages[0]);
    };
    testImage.onerror = () => {
      // Fallback to solid color if images don't exist
      setCurrentBackground('linear-gradient(135deg, #667eea 0%, #764ba2 100%)');
    };
    testImage.src = process.env.PUBLIC_URL + backgroundImages[0];
  }, []);

  // Load chat: Try localStorage first, then fallback to chatData.json
  useEffect(() => {
    const storedChat = localStorage.getItem(LOCAL_STORAGE_CHAT_KEY);
    if (storedChat) {
      try {
        setChatMessages(JSON.parse(storedChat));
        console.log('Loaded chat from localStorage.');
      } catch (error) {
        console.error('Error parsing chat from localStorage:', error);
        // Fallback to fetching from JSON if localStorage data is corrupt
        fetchInitialChatData();
      }
    } else {
      fetchInitialChatData();
    }

    // Check if game backend is running
    checkGameConnection();
  }, []);

  const checkGameConnection = async () => {
    try {
      const response = await fetch(process.env.PUBLIC_URL + '/response.json');
      if (response.ok) {
        setGameConnected(true);
        console.log('Game backend connected.');
      }
    } catch (error) {
      console.log('Game backend not connected, using static mode.');
      setGameConnected(false);
    }
  };

  const fetchInitialChatData = () => {
    fetch(process.env.PUBLIC_URL + '/chatData.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok for chatData.json');
        }
        return response.json();
      })
      .then(data => {
        if (data && data.chat_history) {
          setChatMessages(data.chat_history);
          console.log('Loaded initial chat from chatData.json.');
        } else {
          console.error('Chat history not found in JSON data');
          setChatMessages([]);
        }
      })
      .catch(error => {
        console.error('Failed to fetch chat data:', error);
        // Provide fallback chat data
        setChatMessages([
          { game: "Welcome to the Power Rangers text adventure! The system is initializing..." },
          { game: "Type your commands to interact with the game world." }
        ]);
      });
  };

  // Scroll chat window to bottom when new messages are added
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleClearInput = () => {
    setInputValue('');
  };

  const handleSubmitChatMessage = async () => {
    if (inputValue.trim() === '') {
      return;
    }
    
    const newUserMessage = { user: inputValue.trim() };
    setChatMessages(prevMessages => [...prevMessages, newUserMessage]);
    
    // If game backend is connected, try to get response
    if (gameConnected) {
      try {
        // Here you would make an API call to your Python backend
        // For now, add a placeholder response
        setTimeout(() => {
          setChatMessages(prevMessages => [...prevMessages, { 
            game: `Processing command: "${inputValue.trim()}"...` 
          }]);
        }, 500);
      } catch (error) {
        console.error('Error communicating with game backend:', error);
      }
    }
    
    setInputValue('');
  };

  const handleSelectBackground = (bgUrl) => {
    const testImage = new Image();
    testImage.onload = () => {
      setCurrentBackground(process.env.PUBLIC_URL + bgUrl);
    };
    testImage.onerror = () => {
      // Fallback to gradient if image doesn't exist
      const gradients = [
        'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
      ];
      const index = backgroundImages.indexOf(bgUrl);
      setCurrentBackground(gradients[index] || gradients[0]);
    };
    testImage.src = process.env.PUBLIC_URL + bgUrl;
  };

  const handleAddGameNextMessage = () => {
    setChatMessages(prevMessages => [...prevMessages, { game: "next" }]);
  };

  const handleSaveChat = () => {
    try {
      localStorage.setItem(LOCAL_STORAGE_CHAT_KEY, JSON.stringify(chatMessages));
      alert('Chat history saved to your browser!');
      console.log('Chat history saved to localStorage.');
    } catch (error) {
      console.error('Error saving chat to localStorage:', error);
      alert('Failed to save chat history.');
    }
  };

  // Function to reset chat to default from JSON
  const handleResetChatToDefault = () => {
    localStorage.removeItem(LOCAL_STORAGE_CHAT_KEY); // Clear saved version
    fetchInitialChatData(); // Fetch and set from chatData.json
    alert('Chat reset to default from chatData.json!');
    console.log('Chat reset to default. Loaded from chatData.json.');
  };

  const backgroundStyle = currentBackground.startsWith('linear-gradient') 
    ? { background: currentBackground }
    : { backgroundImage: `url(${currentBackground})` };

  return (
    <div className="app-container" style={backgroundStyle}>
      <div className="main-content-area">
        <div className="chat-section-wrapper">
          <div className="chat-controls-buttons">
            <button onClick={handleAddGameNextMessage} className="control-button next-button" title="Add 'next' game message">
              Next
            </button>
            <button onClick={handleSaveChat} className="control-button save-button" title="Save chat history to browser">
              Save
            </button>
            <button onClick={handleResetChatToDefault} className="control-button reset-button" title="Reset chat to default from file">
              Reset
            </button>
            {gameConnected && (
              <span className="control-button" style={{backgroundColor: '#28a745', cursor: 'default'}}>
                🟢 Game Connected
              </span>
            )}
          </div>
          <div className="chat-window" ref={chatWindowRef}>
            {chatMessages.length === 0 && <p className="chat-placeholder">Loading chat or no messages...</p>}
            {chatMessages.map((msg, index) => (
              <div
                key={index}
                className={`chat-message ${msg.user ? 'user-message' : 'game-message'}`}
              >
                <span className="message-sender">{msg.user ? 'You' : 'Game'}: </span>
                {msg.user || msg.game}
              </div>
            ))}
          </div>
        </div>

        <div className="controls-wrapper">
          <div className="input-container">
            <div className="input-field-wrapper">
              <input
                type="text"
                value={inputValue}
                onChange={handleInputChange}
                className="text-input"
                placeholder="Type your message..."
                onKeyPress={(event) => {
                  if (event.key === 'Enter') {
                    handleSubmitChatMessage();
                  }
                }}
              />
              {inputValue && (
                <button onClick={handleClearInput} className="clear-button" aria-label="Clear input">
                  ×
                </button>
              )}
            </div>
            <button onClick={handleSubmitChatMessage} className="action-button green-button">
              Submit
            </button>
          </div>

          <div className="button-selector-row">
            {backgroundImages.map((bgUrl, index) => (
              <button
                key={index}
                onClick={() => handleSelectBackground(bgUrl)}
                className="dark-button"
              >
                {buttonLabels[index]}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;