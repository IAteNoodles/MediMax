import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiGrid, FiLogOut } from 'react-icons/fi';

const Sidebar = ({ handleLogout }) => {
  const navigate = useNavigate();

  const onLogout = () => {
    handleLogout();
    navigate('/login');
  };

  return (
    <div className="w-64 bg-blue-900 text-white h-screen flex flex-col shadow-lg">
      <div className="p-6 text-2xl font-bold border-b border-blue-800">
        MedAssist
      </div>
      <nav className="flex-1 p-4">
        <ul>
          <li className="mb-4">
            <Link to="/dashboard" className="flex items-center p-3 rounded-lg bg-blue-700 hover:bg-blue-600 transition-colors">
              <FiGrid className="mr-3" />
              Dashboard
            </Link>
          </li>
        </ul>
      </nav>
      <div className="p-4 border-t border-blue-800">
        <button
          onClick={onLogout}
          className="w-full flex items-center p-3 rounded-lg hover:bg-red-600 transition-colors"
        >
          <FiLogOut className="mr-3" />
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
