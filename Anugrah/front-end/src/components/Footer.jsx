import React from 'react';

const Footer = () => {
  const navItems = [
    { name: 'About', href: '#about', active: false },
    { name: 'Projects', href: '#work', active: false },
    { name: 'Services', href: '#services', active: false },
    { name: 'Contact', href: '#contact', active: false }
  ];

  const socialLinks = [
    { name: 'Twitter', href: 'https://x.com/medassist', icon: '𝕏' },
    { name: 'LinkedIn', href: 'https://www.linkedin.com/company/medassist/', icon: 'in' },
    { name: 'Instagram', href: 'https://www.instagram.com/medassist/', icon: '📷' }
  ];

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Company Info */}
          <div className="col-span-1 lg:col-span-2">
            <div className="mb-6">
              <div className="text-white font-bold text-3xl">MedAssist</div>
            </div>
            <p className="text-gray-300 text-lg leading-relaxed mb-6 max-w-md">
              An AI-powered clinical co-pilot designed to combat physician burnout and diagnostic errors 
              through intelligent decision support and evidence-based recommendations.
            </p>
            <div className="flex space-x-4">
              {socialLinks.map((social, index) => (
                <a 
                  key={index}
                  href={social.href} 
                  className="text-gray-400 hover:text-white transition-colors duration-200"
                  target="_blank"
                  rel="noreferrer"
                  title={social.name}
                >
                  <span className="text-xl">{social.icon}</span>
                </a>
              ))}
            </div>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Resources</h3>
            <ul className="space-y-3">
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors duration-200">Blog</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors duration-200">Case Studies</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors duration-200">Help Center</a></li>
              <li><a href="#" className="text-gray-300 hover:text-white transition-colors duration-200">Privacy Policy</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Company</h3>
            <ul className="space-y-3">
              {navItems.map((item, index) => (
                <li key={index}>
                  <a 
                    href={item.href} 
                    className={`transition-colors duration-200 ${
                      item.active 
                        ? 'text-blue-400 pointer-events-none' 
                        : 'text-gray-300 hover:text-white'
                    }`}
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gray-800 rounded-2xl p-8 mb-12 text-center">
          <h3 className="text-2xl md:text-3xl font-bold mb-4">
            Ready to see MedAssist in action?
          </h3>
          <p className="text-gray-300 mb-8 text-lg max-w-2xl mx-auto">
            Request a personalized demo to see how our AI co-pilot can empower your clinical practice.
          </p>
          <a 
            href="/contact" 
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-all duration-300 transform hover:-translate-y-1"
          >
            Request a Demo
            <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm">
            © MedAssist 2025 All Rights Reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="/privacy-policy" className="text-gray-400 hover:text-white text-sm transition-colors duration-200">
              Privacy Policy
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors duration-200">
              Terms of Service
            </a>
            <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors duration-200">
              HIPAA Compliance
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
