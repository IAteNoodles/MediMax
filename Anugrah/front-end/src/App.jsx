import React from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import About from './components/About';
import LogoCarousel from './components/LogoCarousel';
import Services from './components/Services';
import ProjectsCarousel from './components/ProjectsCarousel';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <Header />
      <main>
        <Hero />
        <About />
        <LogoCarousel />
        <Services />
        <ProjectsCarousel />
      </main>
      <Footer />
    </div>
  );
}

export default App;
