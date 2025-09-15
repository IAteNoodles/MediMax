import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Header = ({ isLoggedIn, handleLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <>
      <header className="fixed top-0 w-full z-50 px-6 lg:px-8 bg-white/80 backdrop-blur-sm shadow-md">
        <div className="flex justify-between items-center h-20">
          <div className="flex gap-6 items-center">
            <a className="w-32 relative h-12 md:w-24 md:h-8 block" href="/">
              <div className="text-blue-500 font-bold text-2xl flex items-center h-full">MedAssist</div>
            </a>
          </div>
          <div className="hidden lg:flex items-center gap-6">
            <nav className="flex gap-6 text-gray-700 font-medium">
              <a href="#about" className="hover:text-blue-500 transition-colors">About</a>
              <a href="#services" className="hover:text-blue-500 transition-colors">Services</a>
              <a href="#contact" className="hover:text-blue-500 transition-colors">Contact</a>
            </nav>
            <div className="h-6 border-l border-gray-300"></div>
            {isLoggedIn ? (
              <div className="flex items-center gap-4">
                <Link to="/dashboard">
                  <button className="bg-green-500 text-white px-6 py-2 rounded-full hover:bg-green-600 transition-colors font-semibold">
                    Dashboard
                  </button>
                </Link>
                <button onClick={handleLogout} className="bg-red-500 text-white px-6 py-2 rounded-full hover:bg-red-600 transition-colors font-semibold">
                  Logout
                </button>
              </div>
            ) : (
              <Link to="/login">
                <button className="bg-blue-500 text-white px-6 py-2 rounded-full hover:bg-blue-600 transition-colors font-semibold">
                  Login
                </button>
              </Link>
            )}
          </div>
          <div className="lg:hidden">
            <button onClick={toggleMenu} className="outline-none">
              <div className="w-6 h-6 flex flex-col justify-center space-y-1">
                <span className={`block h-0.5 w-6 bg-gray-800 transition-transform duration-300 ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
                <span className={`block h-0.5 w-6 bg-gray-800 transition-opacity duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
                <span className={`block h-0.5 w-6 bg-gray-800 transition-transform duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
              </div>
            </button>
          </div>
        </div>
      </header>
      {isMenuOpen && (
        <div className="lg:hidden fixed top-20 left-0 w-full bg-white z-40 shadow-md">
          <nav className="flex flex-col items-center p-4 space-y-4">
            <a href="#about" className="text-gray-700 hover:text-blue-500" onClick={toggleMenu}>About</a>
            <a href="#services" className="text-gray-700 hover:text-blue-500" onClick={toggleMenu}>Services</a>
            <a href="#contact" className="text-gray-700 hover:text-blue-500" onClick={toggleMenu}>Contact</a>
            <div className="w-full border-t border-gray-200 pt-4 flex justify-center">
              {isLoggedIn ? (
                <div className="space-y-3 w-full">
                  <Link to="/dashboard" onClick={toggleMenu}>
                    <button className="w-full bg-green-500 text-white px-6 py-3 rounded-full hover:bg-green-600 transition-colors font-semibold">
                      Dashboard
                    </button>
                  </Link>
                  <button 
                    onClick={() => { handleLogout(); toggleMenu(); }} 
                    className="w-full bg-red-500 text-white px-6 py-3 rounded-full hover:bg-red-600 transition-colors font-semibold"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <Link to="/login">
                  <button onClick={toggleMenu} className="bg-blue-500 text-white px-6 py-2 rounded-full hover:bg-blue-600 transition-colors font-semibold">
                    Login
                  </button>
                </Link>
              )}
            </div>
          </nav>
        </div>
      )}
    </>
  );
};

export default Header;
