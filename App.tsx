
import React from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import DriversPage from './pages/DriversPage';
import MonitorPage from './pages/MonitorPage';

const App: React.FC = () => {
  return (
    <HashRouter>
      <div className="min-h-screen bg-gray-50 text-brand-text-dark">
        <Header />
        <main className="p-4 sm:p-6 lg:p-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/drivers" element={<DriversPage />} />
            <Route path="/monitor/:driverId" element={<MonitorPage />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
};

export default App;
