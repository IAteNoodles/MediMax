import React from 'react';

const LogoCarousel = () => {
  const logoRows = [
    [
      { name: 'HeartFlow', width: 'w-32' },
      { name: 'Optimize Health', width: 'w-36' },
      { name: 'Medbridge', width: 'w-36' },
      { name: 'Laudio', width: 'w-24' },
      { name: 'Linus Health', width: 'w-36' }
    ],
    [
      { name: 'CareCloud', width: 'w-28' },
      { name: 'DNAnexus', width: 'w-28' },
      { name: 'Aris Global', width: 'w-28' },
      { name: 'Endear Health', width: 'w-36' },
      { name: 'Butterfly', width: 'w-36' }
    ],
    [
      { name: 'H1', width: 'w-16' },
      { name: 'Patina', width: 'w-28' },
      { name: 'LifeSphere', width: 'w-36' },
      { name: 'Paseva', width: 'w-20' },
      { name: 'DNAnexus', width: 'w-28' }
    ]
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Logo Grid */}
        <div className="mb-16">
          <div className="text-center mb-12">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Built on Trusted Medical Data
            </h3>
          </div>
          
          <div className="space-y-8">
            {logoRows.map((row, rowIndex) => (
              <div key={rowIndex} className="flex justify-center items-center space-x-8 opacity-40 hover:opacity-70 transition-opacity duration-300">
                {row.map((logo, logoIndex) => (
                  <div key={logoIndex} className={`${logo.width} h-12 bg-gray-200 rounded-lg flex items-center justify-center hover:bg-gray-300 transition-colors duration-200`}>
                    <span className="text-sm font-medium text-gray-600">{logo.name}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Testimonial Section */}
        <div className="text-center max-w-4xl mx-auto">
          <blockquote className="text-2xl md:text-3xl font-light text-gray-800 mb-8 leading-relaxed">
            "MedAssist transforms complex patient data into clear, actionable insights, moving healthcare from reactive to preventative."
          </blockquote>
          
          <cite className="text-gray-600 font-medium">
            Clinical Decision Support System
          </cite>
        </div>

        {/* Technical Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 pt-16 border-t border-gray-100">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">MIMIC-IV</div>
            <div className="text-sm text-gray-600">Dataset Integration</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">HIPAA</div>
            <div className="text-sm text-gray-600">Ready Foundation</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">Real-time</div>
            <div className="text-sm text-gray-600">Clinical Insights</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">AI-Powered</div>
            <div className="text-sm text-gray-600">Decision Support</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LogoCarousel;
