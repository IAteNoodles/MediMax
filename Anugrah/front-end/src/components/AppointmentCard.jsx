import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

const AppointmentCard = ({ appointment, index }) => {
  const colors = [
    'bg-yellow-200',
    'bg-pink-200',
    'bg-blue-200',
    'bg-green-200',
    'bg-purple-200',
  ];
  const color = colors[index % colors.length];

  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"]
  });

  // Move odd cards one way, even cards the other
  const x = useTransform(scrollYProgress, [0, 1], index % 2 === 0 ? ['-10%', '10%'] : ['10%', '-10%']);

  return (
    <motion.div ref={ref} style={{ x }} className="h-full">
      <div className="relative p-2 h-full">
        <div className={`absolute bottom-0 left-0 right-4 top-4 ${color} rounded-2xl transform -rotate-3 transition-transform duration-300 group-hover:rotate-0`}></div>
        <div className="relative bg-white rounded-2xl shadow-lg p-6 space-y-4 group h-full flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-start">
              <h2 className="text-xl font-bold text-gray-800">{appointment.patient_name}</h2>
              <span className="text-xs font-semibold text-gray-500">
                {new Date(appointment.appointment_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </span>
            </div>
            <p className="text-gray-600 text-sm mt-2">{appointment.appointment_type}</p>
          </div>
          <div className="flex items-center justify-between text-sm mt-4">
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
              appointment.status === 'Completed' ? 'bg-green-100 text-green-700' :
              appointment.status === 'Confirmed' ? 'bg-blue-100 text-blue-700' :
              'bg-yellow-100 text-yellow-700'
            }`}>
              {appointment.status}
            </span>
            <span className="text-gray-500">{appointment.appointment_time}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default AppointmentCard;
