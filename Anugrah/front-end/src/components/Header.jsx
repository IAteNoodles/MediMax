import React, { useState } from 'react';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <>
      <header className="fixed top-6 w-full z-50 px-6 lg:px-0 flex justify-between items-center pointer-events-none">
        <div className="flex gap-6 items-center">
          <div className="lg:flex hidden justify-center items-center w-16 pointer-events-auto h-full">
            <div id="menu-button" className="flex items-center justify-center" onClick={toggleMenu}>
              <button className={`outline-none block relative ${isMenuOpen ? 'is-active' : ''}`}>
                <div className="w-6 h-6 flex flex-col justify-center space-y-1">
                  <span className={`block h-0.5 w-6 bg-white transition-transform duration-300 ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
                  <span className={`block h-0.5 w-6 bg-white transition-opacity duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
                  <span className={`block h-0.5 w-6 bg-white transition-transform duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
                </div>
              </button>
            </div>
          </div>
          <a className="w-32 relative h-12 md:w-24 md:h-8 block pointer-events-auto" href="/">
            <div className="text-white font-bold text-2xl flex items-center h-full">MedAssist</div>
          </a>
        </div>
        <a className="hidden lg:block pointer-events-auto" href="/contact">
          <button className="relative group rounded-full overflow-hidden z-20 select-none inline-flex items-center border border-gray-300 text-white px-8 md:px-6 py-4 md:py-3 gap-2 hover:bg-white hover:text-black transition-all duration-300 lg:px-10">
            <span className="block overflow-hidden relative">
              <span className="block transition-transform duration-500 origin-top-left group-hover:-translate-y-full group-hover:rotate-12">Request Demo</span>
              <span className="block absolute top-0 translate-y-full transition-transform duration-500 origin-top-left group-hover:translate-y-0 group-hover:-rotate-12">Request Demo</span>
            </span>
          </button>
        </a>
        <div className="lg:hidden flex items-center justify-center shrink-0 pointer-events-auto" onClick={toggleMenu}>
          <button className="outline-none block relative">
            <div className="w-6 h-6 flex flex-col justify-center space-y-1">
              <span className={`block h-0.5 w-6 bg-white transition-transform duration-300 ${isMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`}></span>
              <span className={`block h-0.5 w-6 bg-white transition-opacity duration-300 ${isMenuOpen ? 'opacity-0' : ''}`}></span>
              <span className={`block h-0.5 w-6 bg-white transition-transform duration-300 ${isMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
            </div>
          </button>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {isMenuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={toggleMenu}></div>
          <div className="absolute top-0 right-0 w-80 h-full bg-white shadow-lg">
            <div className="p-8 pt-20">
              <nav className="space-y-8">
                <a href="#about" className="block text-2xl font-medium text-gray-800 hover:text-blue-600 transition-colors" onClick={toggleMenu}>
                  How It Works
                </a>
                <a href="#services" className="block text-2xl font-medium text-gray-800 hover:text-blue-600 transition-colors" onClick={toggleMenu}>
                  Features
                </a>
                <a href="#work" className="block text-2xl font-medium text-gray-800 hover:text-blue-600 transition-colors" onClick={toggleMenu}>
                  Technology
                </a>
                <a href="#contact" className="block text-2xl font-medium text-gray-800 hover:text-blue-600 transition-colors" onClick={toggleMenu}>
                  Demo
                </a>
              </nav>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Header;
