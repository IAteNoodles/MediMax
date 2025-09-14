import React from 'react';
import Header from './Header';
import Hero from './Hero';
import About from './About';
import LogoCarousel from './LogoCarousel';
import Services from './Services';
import ProjectsCarousel from './ProjectsCarousel';
import Footer from './Footer';

const Home = ({ isLoggedIn, handleLogout }) => {
  return (
    <>
      <Header isLoggedIn={isLoggedIn} handleLogout={handleLogout} />
      <main>
        <Hero isLoggedIn={isLoggedIn} />
        <About />
        <LogoCarousel />
        <Services />
        <ProjectsCarousel />
      </main>
      <Footer />
    </>
  );
};

export default Home;
