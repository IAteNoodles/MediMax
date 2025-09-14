import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import appointmentsData from '../data/appointments.json';
import AppointmentCard from './AppointmentCard';
import Sidebar from './Sidebar';

const Dashboard = ({ handleLogout }) => {
  const appointments = appointmentsData.appointments;

  const containerVariants = {
    hidden: { opacity: 1 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 60, opacity: 0, scale: 0.8 },
    visible: {
      y: 0,
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  const titleVariants = {
    hidden: { x: -100, opacity: 0 },
    visible: {
      x: 0,
      opacity: 1,
      transition: {
        duration: 0.8,
        ease: "easeOut",
      },
    },
  };

  return (
    <div className="flex">
      <Sidebar handleLogout={handleLogout} />
      <div className="flex-1 p-8 bg-gray-100">
        <motion.h1 
          className="text-4xl font-bold text-gray-800 mb-10"
          variants={titleVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.8 }}
        >
          Appointments
        </motion.h1>
        <motion.div 
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          {appointments.map((appointment, index) => (
            <motion.div key={appointment.appointment_id} variants={itemVariants} className="h-full">
              <Link to={`/patient/${appointment.patient_id}`} className="group h-full">
                <AppointmentCard appointment={appointment} index={index} />
              </Link>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
