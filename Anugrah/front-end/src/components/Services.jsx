import React from 'react';

const Services = () => {
  const services = [
    {
      name: 'Proactive Risk Prediction',
      description: "Analyzes patient's long-term health history to identify potential future health issues, moving care from reactive to preventative.",
      icon: '📊',
      href: '/features?feature=risk-prediction'
    },
    {
      name: 'Intuitive User Experience',
      description: 'Clean, uncluttered interface using "Calm Technology" design principles to prevent cognitive overload and burnout.',
      icon: '🎯',
      href: '/features?feature=user-experience'
    },
    {
      name: 'Transparency and Trust',
      description: 'Every piece of information is explicitly linked to its source with "Trust-by-Citation" for complete transparency.',
      icon: '🔍',
      href: '/features?feature=transparency'
    },
    {
      name: 'Clinical Decision Support',
      description: 'Transforms complex patient data into clear, actionable insights without interrupting clinical workflows.',
      icon: '⚡',
      href: '/features?feature=decision-support'
    },
    {
        name: 'Predictive Analytics',
        description: 'Optimize hospital operations with our predictive analytics solutions. Forecast patient admission rates, manage bed occupancy, and allocate resources effectively to improve overall hospital efficiency.',
        icon: '📊',
        href: '/features?feature=predictive-analytics'
      },
      {
        name: 'AI-Powered Diagnostics',
        description: 'Enhance diagnostic accuracy with our AI algorithms that analyze medical images, lab results, and clinical notes to provide data-driven insights and support clinical decision-making.',
        icon: '🤖',
        href: '/features?feature=ai-diagnostics'
      },
      {
        name: 'Personalized Treatment Plans',
        description: 'Leverage patient data to create personalized treatment plans. Our system considers genetic information, lifestyle factors, and medical history to recommend the most effective therapies.',
        icon: '❤️',
        href: '/features?feature=personalized-treatment'
      },
      {
        name: 'Automated Clinical Documentation',
        description: 'Reduce administrative burden with our voice-to-text and NLP-powered documentation tools. Clinicians can focus on patient care while our system handles the note-taking.',
        icon: '📝',
        href: '/features?feature=automated-documentation'
      },
      {
        name: 'Remote Patient Monitoring',
        description: 'Monitor patients remotely using wearable devices and IoT sensors. Our platform provides real-time alerts and trend analysis to enable proactive care for chronic conditions.',
        icon: '📶',
        href: '/features?feature=remote-monitoring'
      },
      {
        name: 'Genomic Data Analysis',
        description: 'Unlock insights from genomic data to advance precision medicine. Our tools help researchers and clinicians understand the genetic basis of diseases and identify targeted therapies.',
        icon: '🧬',
        href: '/features?feature=genomic-analysis'
      }
  ];

  return (
    <section id="services" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">
            Our Services
          </h2>
          <h3 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Complete Clinical AI Experience
          </h3>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Building on our powerful hybrid AI core, MedAssist includes comprehensive features 
            to provide a seamless clinical decision support experience.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div key={index} className="bg-white p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
              <div className="text-4xl mb-4 text-blue-500">{service.icon}</div>
              <h3 className="text-xl font-bold text-gray-800 mb-2">{service.name}</h3>
              <p className="text-gray-600 mb-4">{service.description}</p>
              <a href={service.href} className="text-blue-500 hover:underline">Learn More &rarr;</a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
