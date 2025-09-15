import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import PatientDetail from './components/PatientDetail';
import AgenticInterface from './components/AgenticInterface';
import ScrollProgressBar from './components/ScrollProgressBar';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <Router>
      <div className="App">
        <ScrollProgressBar />
        <Routes>
          <Route path="/" element={<Home isLoggedIn={isLoggedIn} handleLogout={handleLogout} />} />
          <Route path="/login" element={isLoggedIn ? <Navigate to="/dashboard" /> : <Login handleLogin={handleLogin} />} />
          <Route path="/dashboard" element={isLoggedIn ? <Dashboard handleLogout={handleLogout} /> : <Navigate to="/login" />} />
          <Route path="/patient/:patientId" element={isLoggedIn ? <PatientDetail handleLogout={handleLogout} /> : <Navigate to="/login" />} />
          <Route path="/agentic-interface" element={isLoggedIn ? <AgenticInterface /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
