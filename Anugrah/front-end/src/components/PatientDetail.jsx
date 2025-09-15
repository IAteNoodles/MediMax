import React from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import appointmentsData from '../data/appointments.json';
import patientsData from '../data/patients.json';
import Chatbot from './Chatbot';
import Sidebar from './Sidebar';

const PatientDetail = ({ handleLogout }) => {
  const { patientId } = useParams();
  
  const patient = patientsData.patients.find(
    (p) => p.id === parseInt(patientId)
  );

  const patientAppointments = appointmentsData.appointments.filter(
    (appointment) => appointment.patient_id === parseInt(patientId)
  );

  if (!patient) {
    return (
      <div className="flex">
        <Sidebar handleLogout={handleLogout} />
        <div className="flex-1 p-8 bg-gray-100">
          <div className="p-8 text-center text-gray-500">Patient not found</div>
        </div>
      </div>
    );
  }

  const mainVariants = {
    hidden: { opacity: 0, y: 50, scale: 0.95 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { 
        duration: 0.8, 
        ease: "easeOut" 
      } 
    },
  };

  const appointmentVariants = {
    hidden: { opacity: 0, x: -50, rotateY: -15 },
    visible: { 
      opacity: 1, 
      x: 0, 
      rotateY: 0,
      transition: { 
        duration: 0.7,
        ease: "easeOut" 
      } 
    },
  };

  const headerVariants = {
    hidden: { opacity: 0, y: -30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  const sectionVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut"
      }
    }
  };

  return (
    <div className="flex">
      <Sidebar handleLogout={handleLogout} />
      <motion.main 
        className="flex-1 min-h-screen bg-gray-100 p-8"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.1 }}
        variants={{ visible: { transition: { staggerChildren: 0.2 } } }}
      >
        <motion.div 
          className="bg-white rounded-2xl shadow-xl p-8" 
          variants={mainVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
        >
          <motion.h1 
            className="text-3xl font-bold text-gray-800 mb-2" 
            variants={headerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.8 }}
          >
            {patient.patient_name}
          </motion.h1>
          <motion.p 
            className="text-gray-500 mb-6" 
            variants={headerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.8 }}
          >
            Patient ID: {patient.id}
          </motion.p>

          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.5 }}
          >
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-600 mb-2">Age</h3>
              <p className="text-gray-800">{patient.age}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-600 mb-2">Sex</h3>
              <p className="text-gray-800">{patient.sex}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-600 mb-2">Contact</h3>
              <p className="text-gray-800">{patient.contact}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold text-gray-600 mb-2">Address</h3>
              <p className="text-gray-800">{patient.address}</p>
            </div>
          </motion.div>

          <motion.div 
            className="mt-8"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.5 }}
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Medical History</h2>
            <div className="space-y-3">
              {patient.medical_history.map((item, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                  <p className="font-semibold text-gray-700">{item.condition}</p>
                  <p className="text-sm text-gray-500">Diagnosed: {item.diagnosed_date}</p>
                </div>
              ))}
            </div>
          </motion.div>
          
          <motion.div 
            className="mt-8"
            variants={sectionVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.5 }}
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Appointments</h2>
            <div className="space-y-6">
              {patientAppointments.length > 0 ? (
                patientAppointments.map((appointment, index) => (
                  <motion.div 
                    key={appointment.appointment_id} 
                    className="p-6 border border-gray-200 rounded-xl bg-gray-50"
                    custom={index}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, amount: 0.3 }}
                    variants={appointmentVariants}
                    transition={{ delay: index * 0.15 }}
                  >
                    <div className="flex justify-between items-center mb-4">
                      <p className="font-semibold text-gray-700">
                        {appointment.appointment_date} at {appointment.appointment_time}
                      </p>
                      <span
                        className={`px-3 py-1 text-xs font-semibold rounded-full ${
                          appointment.status === 'Completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {appointment.status}
                      </span>
                    </div>
                    
                    <div>
                      <h3 className="text-xl font-semibold text-gray-700 mb-3">Symptoms</h3>
                      {appointment.symptoms.length > 0 ? (
                        <ul className="list-disc list-inside space-y-2 text-gray-600">
                          {appointment.symptoms.map((symptom) => (
                            <li key={symptom.symptom_id}>
                              <span className="font-semibold text-gray-700">{symptom.symptom_name}</span> ({symptom.severity}) - {symptom.symptom_description} <span className="text-sm text-gray-500">(Duration: {symptom.duration})</span>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-gray-500">No symptoms recorded for this appointment.</p>
                      )}
                    </div>
                  </motion.div>
                ))
              ) : (
                <p className="text-gray-500">No appointments found for this patient.</p>
              )}
            </div>
          </motion.div>
        </motion.div>
        <motion.div 
          variants={mainVariants} 
          initial="hidden" 
          whileInView="visible" 
          viewport={{ once: true, amount: 0.8 }}
        >
          <Chatbot patientId={patientId} />
        </motion.div>
      </motion.main>
    </div>
  );
};

export default PatientDetail;
