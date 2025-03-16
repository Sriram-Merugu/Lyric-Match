import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Simplified Typewriter Component
const Typewriter = ({ text, speed = 50, className = '' }) => {
  const [displayText, setDisplayText] = useState('');

  React.useEffect(() => {
    let index = 0;
    setDisplayText('');
    const interval = setInterval(() => {
      setDisplayText((prev) => prev + text.charAt(index));
      index++;
      if (index >= text.length) {
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);

  return <div className={className}>{displayText}</div>;
};

function App() {
  const [lyricSnippet, setLyricSnippet] = useState('');
  const [songTitle, setSongTitle] = useState('');
  const [userGuess, setUserGuess] = useState('');
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const generateLyric = async () => {
    // Clear previous data
    setError('');
    setResult('');
    setUserGuess('');
    setLyricSnippet('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/generate-lyric');
      if (!response.ok) {
        throw new Error('Error generating lyric snippet');
      }
      const data = await response.json();
      setLyricSnippet(data.lyric_snippet);
      setSongTitle(data.song_title);
    } catch (err) {
      setError('Failed to generate lyrics. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const checkAnswer = async () => {
    if (!userGuess) {
      setError('Please enter your guess');
      return;
    }

    setError('');
    setResult('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/check-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_guess: userGuess, correct_title: songTitle })
      });

      if (!response.ok) {
        throw new Error('Error checking answer');
      }

      const data = await response.json();

      if (data.result === 'correct') {
        setResult('Correct! Well done.');
      } else {
        setResult(`Incorrect. The correct song title was: ${data.correct_title}`);
      }
    } catch (err) {
      setError('Failed to check your answer. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && userGuess && lyricSnippet) {
      checkAnswer();
    }
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="card main-card">
          <div className="card-header text-center">
            <h1 className="app-title">Lyric Match</h1>
          </div>

          <div className="card-body">
            {/* Generate Button */}
            <div className="text-center mb-4">
              <button
                className="btn btn-primary generate-btn"
                onClick={generateLyric}
                disabled={isLoading}
              >
                {isLoading ? 'Loading...' : 'Generate Lyric Snippet'}
              </button>
            </div>

            {/* Lyric Display Area */}
            {lyricSnippet && (
              <div className="mb-4 lyric-section">
                <h4>Lyric Snippet:</h4>
                <div className="lyric-display">
                  <Typewriter text={lyricSnippet} speed={40} className="lyric-text" />
                </div>
              </div>
            )}

            {/* User Input Area */}
            {lyricSnippet && (
              <div className="mb-4 guess-section">
                <label htmlFor="userGuess" className="form-label">
                  Enter your guess for the song title:
                </label>
                <input
                  type="text"
                  id="userGuess"
                  className="form-control user-input"
                  value={userGuess}
                  onChange={(e) => setUserGuess(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type song title here"
                />
                <button
                  className="btn btn-success check-btn mt-2"
                  onClick={checkAnswer}
                  disabled={isLoading || !userGuess}
                >
                  Check Answer
                </button>
              </div>
            )}

            {/* Result Display Area */}
            {result && (
              <div className="mb-4 result-section">
                <h4>Result:</h4>
                <div className="result-display">
                  {result}
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;