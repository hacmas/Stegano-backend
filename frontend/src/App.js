import React, { useState } from 'react';
import axios from 'axios';
import { BrowserRouter, Routes, Route, useParams, Link } from 'react-router-dom';
import './App.css';

// --- PAGE 1: THE CREATOR PAGE ---
function Home() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [shareLink, setShareLink] = useState('');

  // 1. ADD THIS NEW STATE:
  const [copied, setCopied] = useState(false); 

  // 2. ADD THIS NEW FUNCTION:
  const handleCopy = () => {
    navigator.clipboard.writeText(shareLink);
    setCopied(true); // Change the button text
    setTimeout(() => setCopied(false), 2000); // Change it back after 2 seconds
  };

  const handleEncode = async () => {
    setErrorMsg('');
    setShareLink('');
    if (!file || !text || !password) return setErrorMsg('⚠️ Please provide an image, message, and password.');

    setLoading(true);
    const formData = new FormData();
    formData.append('image', file);
    formData.append('text', text);
    formData.append('password', password);

    try {
      const response = await axios.post('https://stegano-backend-xlxd.onrender.com/api/generate_link', formData);
      const link = `${window.location.origin}/secret/${response.data.id}`;
      setShareLink(link);
    } catch (error) {
      setErrorMsg('❌ Error generating link. Check your server.');
    }
    setLoading(false);
  };

  return (
    <div className="card">
      <h2>🔒 Create a Secure Link</h2>
      {errorMsg && <div className="error-box">{errorMsg}</div>}
      
      <input type="file" accept="image/png, image/jpeg" onChange={(e) => setFile(e.target.files[0])} />
      <input 
        type="password" 
        placeholder="Set an AES Password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)} 
        className="password-input"
      />
      <textarea 
        placeholder="Type your secret message here..." 
        value={text} 
        onChange={(e) => setText(e.target.value)} 
      />

      <button className="action-btn" onClick={handleEncode} disabled={loading}>
        {loading ? 'Processing...' : 'Generate Secret Link'}
      </button>

      {shareLink && (
        <div className="result-card">
          <h3>✅ Link Generated!</h3>
          <p>Send this link to your friend. It will self-destruct after being read.</p>
          <div className="secret-text" style={{fontSize: '14px', wordBreak: 'break-all'}}>
            {shareLink}
          </div>

          <button 
            className="download-btn" 
            onClick={handleCopy} 
            style={{ 
              marginTop: '10px', 
              backgroundColor: copied ? '#00b894' : '', // Changes color to green when clicked
              transition: 'background-color 0.3s ease'  // Makes the color change smooth
            }}
          >
            {copied ? '✅ Copied!' : 'Copy to Clipboard'}
          </button>

        </div>
      )}
    </div>
  );
}

// --- PAGE 2: THE RECEIVER PAGE ---
function SecretView() {
  const { id } = useParams(); 
  const [password, setPassword] = useState('');
  const [decodedText, setDecodedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [imageError, setImageError] = useState(false); // Tracks if image is deleted

  const handleDecode = async () => {
    setErrorMsg('');
    if (!password) return setErrorMsg('⚠️ Please enter the password.');

    setLoading(true);
    const formData = new FormData();
    formData.append('id', id); 
    formData.append('password', password);

    try {
      const response = await axios.post('https://stegano-backend-xlxd.onrender.com/api/open_link', formData);
      setDecodedText(response.data.secret_message);
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        setErrorMsg("🔒 " + error.response.data.error);
      } else {
        setErrorMsg('❌ Connection error.');
      }
    }
    setLoading(false);
  };

  return (
    <div className="card">
      <h2>📩 Incoming Secret Message</h2>
      <p>This image contains encrypted data. Enter the password to unlock and destroy it.</p>
      
      {errorMsg && <div className="error-box">{errorMsg}</div>}

      {/* --- THE SPY ENVELOPE: Show the image if it hasn't been decoded/destroyed yet --- */}
      {!decodedText && !imageError && (
        <img 
          src={`https://stegano-backend-xlxd.onrender.com/api/image/${id}`} 
          alt="Secure Envelope" 
          onError={() => setImageError(true)} // If Flask returns 404, hide the broken image icon
          style={{ width: '100%', borderRadius: '8px', marginBottom: '15px', border: '2px solid #6c5ce7' }}
        />
      )}

      {/* If the image is already destroyed, show this warning instead of the password box */}
      {imageError && !decodedText ? (
        <div className="error-box" style={{textAlign: 'center', padding: '20px'}}>
          <h3>🔥 Message Destroyed</h3>
          <p>This image and its contents have already been read and permanently deleted from the server.</p>
        </div>
      ) : !decodedText ? (
        <>
          <input 
            type="password" 
            placeholder="Enter Password to Unlock" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            className="password-input"
          />
          <button className="action-btn" onClick={handleDecode} disabled={loading}>
            {loading ? 'Decrypting...' : 'Unlock & Destroy Image'}
          </button>
        </>
      ) : (
        <div className="result-card">
          <h3>🔓 Decrypted Message:</h3>
          <p className="secret-text">{decodedText}</p>
          <p style={{color: '#ff7675', marginTop: '15px', fontWeight: 'bold'}}>
            🔥 The cover image has been permanently deleted from the server.
          </p>
          <Link to="/">
            <button className="download-btn" style={{marginTop: '10px'}}>Create Your Own</button>
          </Link>
        </div>
      )}
    </div>
  );
}

// --- MAIN APP COMPONENT ---
function App() {
  return (
    <BrowserRouter>
      <div className="container">
        <h1>🕵️‍♂️ Stegano-Share Secure</h1>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/secret/:id" element={<SecretView />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;