import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import CollaborativeSession from './pages/CollaborativeSession';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/session/:sessionId" element={<CollaborativeSession />} />
      </Routes>
    </Router>
  );
}

export default App;
