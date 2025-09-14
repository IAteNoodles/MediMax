import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = 'http://10.26.5.65:8000';

const AgenticInterface = () => {
  const navigate = useNavigate();
  const [patientText, setPatientText] = useState("The patient is a 52-year-old male, height 175 cm, weight 95 kg. He presents for a routine check-up. He has a history of hypertension and his father had a heart attack at age 60. His systolic blood pressure is 145 (ap_hi: 145) and his diastolic blood pressure is 92 (ap_lo: 92). Recent lab work shows his cholesterol is above normal (cholesterol: 2) and his glucose is well above normal (gluc: 3). The patient reports that he smokes cigarettes daily (smoke: 1) and consumes alcohol a few times a week (alco: 1). He describes his lifestyle as mostly sedentary with little to no physical activity (active: 0).");
  const [query, setQuery] = useState("Cardiovascular risk assessment");
  const [additionalNotes, setAdditionalNotes] = useState("Patient has a family history of heart disease.");
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleApiCall = async (url, options = {}) => {
    setLoading(true);
    setResponse(null);
    setError(null);
    try {
      const res = await fetch(url, options);
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      setResponse(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAssessPatient = () => {
    const assessmentData = { patient_text: patientText, query, additional_notes: additionalNotes };
    handleApiCall(`${API_BASE_URL}/assess`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(assessmentData),
    });
  };

  const handleAssessMock = () => {
    handleApiCall(`${API_BASE_URL}/assess_mock?patient_index=0`, { method: 'POST' });
  };

  const handleHealthCheck = () => {
    handleApiCall(`${API_BASE_URL}/health`);
  };

  const handleGetModels = () => {
    handleApiCall(`${API_BASE_URL}/models`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-200 via-pink-100 to-indigo-200 p-4 text-gray-800 relative overflow-hidden">
      {/* Background gradient orbs for depth */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-purple-300/30 to-pink-300/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-to-r from-indigo-300/30 to-purple-300/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-3/4 left-3/4 w-64 h-64 bg-gradient-to-r from-pink-300/20 to-purple-300/20 rounded-full blur-2xl animate-pulse delay-2000"></div>
      </div>
      
      <div className="max-w-7xl mx-auto relative z-10 h-screen flex flex-col">
        {/* Header with Dashboard Button */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.5 }} 
          className="flex justify-between items-center mb-4"
        >
          <h1 className="text-3xl font-bold text-black">MedAssist AI</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-6 py-2 bg-white/40 backdrop-blur-md text-black font-semibold rounded-2xl hover:bg-white/50 transition-all duration-300 border border-white/30 transform hover:-translate-y-1"
          >
            Dashboard
          </button>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.5, delay: 0.2 }} 
          className="bg-white/20 backdrop-blur-xl p-6 rounded-3xl shadow-2xl mb-4 border border-white/30 hover:bg-white/25 transition-all duration-300"
        >
          <h2 className="text-2xl font-bold mb-4 text-black">
            Patient Assessment
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <textarea
              className="lg:col-span-2 p-4 border border-white/30 rounded-2xl bg-white/30 backdrop-blur-md focus:ring-2 focus:ring-purple-400/50 focus:outline-none focus:bg-white/40 transition-all duration-300 text-black placeholder-gray-700"
              rows="4"
              value={patientText}
              onChange={(e) => setPatientText(e.target.value)}
              placeholder="Enter patient text..."
            />
            <div className="space-y-4">
              <input
                type="text"
                className="w-full p-4 border border-white/30 rounded-2xl bg-white/30 backdrop-blur-md focus:ring-2 focus:ring-purple-400/50 focus:outline-none focus:bg-white/40 transition-all duration-300 text-black placeholder-gray-700"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter query..."
              />
              <textarea
                className="w-full p-4 border border-white/30 rounded-2xl bg-white/30 backdrop-blur-md focus:ring-2 focus:ring-purple-400/50 focus:outline-none focus:bg-white/40 transition-all duration-300 text-black placeholder-gray-700"
                rows="2"
                value={additionalNotes}
                onChange={(e) => setAdditionalNotes(e.target.value)}
                placeholder="Additional notes..."
              />
              <button
                className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-2xl hover:from-purple-600 hover:to-pink-600 transition-all duration-300 shadow-lg transform hover:-translate-y-1 backdrop-blur-sm"
                onClick={handleAssessPatient}
                disabled={loading}
              >
                {loading ? 'Assessing...' : 'Assess'}
              </button>
            </div>
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: 0.5, delay: 0.4 }} 
          className="bg-white/20 backdrop-blur-xl p-6 rounded-3xl shadow-2xl border border-white/30 hover:bg-white/25 transition-all duration-300 flex-1"
        >
          <div className="bg-white/30 backdrop-blur-md p-6 rounded-2xl h-full overflow-y-auto prose max-w-none border border-white/30 hover:bg-white/35 transition-all duration-300">
            {loading && <p className="text-center text-black">Loading...</p>}
            {error && <pre className="text-red-600 whitespace-pre-wrap">{error}</pre>}
            {response && response.report && <ReactMarkdown>{response.report}</ReactMarkdown>}
            {!response && !loading && !error && <p className="text-gray-600 text-center">Response will appear here</p>}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default AgenticInterface;
