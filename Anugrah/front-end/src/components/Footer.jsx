import React from 'react';

const Footer = () => {
  const navItems = [
    { name: 'About', href: '#about' },
    { name: 'Services', href: '#services' },
    { name: 'Contact', href: '#contact' }
  ];

  const socialLinks = [
    { name: 'Twitter', href: 'https://x.com/medassist', icon: '𝕏' },
    { name: 'LinkedIn', href: 'https://www.linkedin.com/company/medassist/', icon: 'in' },
    { name: 'Instagram', href: 'https://www.instagram.com/medassist/', icon: '📷' }
  ];

  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 lg:col-span-2">
            <div className="mb-4">
              <div className="text-blue-400 font-bold text-3xl">MedAssist</div>
            </div>
            <p className="text-gray-300 leading-relaxed max-w-md">
              AI-powered clinical co-pilot for enhanced decision support and evidence-based recommendations.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              {navItems.map((item) => (
                <li key={item.name}>
                  <a href={item.href} className="text-gray-300 hover:text-blue-400 transition-colors">
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Social Media */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Follow Us</h3>
            <div className="flex space-x-4">
              {socialLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-blue-400 transition-colors"
                >
                  <span className="sr-only">{link.name}</span>
                  <div className="w-8 h-8 border border-gray-600 rounded-full flex items-center justify-center hover:border-blue-400">
                    {link.icon}
                  </div>
                </a>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-8 border-t border-gray-700 pt-6 text-center text-gray-400">
          <p>&copy; {new Date().getFullYear()} MedAssist. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
