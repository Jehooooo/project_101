/**
 * Choose Login Page for DMMMSU-SLUC Disaster Monitoring System
 * Users select either Admin or Staff login
 */

import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';

export default function ChooseLogin() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Left Side - Image & Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: 'url(/images/dmmmsu-campus1.jpg)' }}
        />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-800/60 via-blue-800/80 to-blue-900/85" />

        <div className="relative z-10 flex flex-col justify-start items-center pt-60 p-7 text-white text-center space-y-0">
          <img
             //src="/images/dmmmsu-logo1.png"
            // alt="DMMMSU Logo"
          // className="w-40 h-40 object-contain drop-shadow-lg"
          />
          <h1 className="text-base font-body font-bold">Don Mariano Marcos Memorial State University - South La Union Campus</h1>
          <h1 className="text-8xl font-heading font-bold">DMMMSU SLUC</h1>
          <h1 className="text-5xl font-body font-bold">Disaster/Emergency Incident Reports Management System</h1>
        </div>
      </div>

      {/* Right Side - Login Selection */}
      <div className="flex-1 flex flex-col justify-center items-center bg-slate-900 relative">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-40 -right-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl"
          />
          <motion.div
            animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.4, 0.2] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
            className="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl"
          />
        </div>

        {/* Selection Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="relative z-10 w-full max-w-md mx-4 p-8 bg-slate-800/80 backdrop-blur-xl border border-slate-700 rounded-2xl shadow-2xl space-y-6 text-center"
        >
          <img
            src="/images/dmmmsu-logo1.png"
            alt="DMMMSU Logo"
            className="w-24 h-24 mx-auto object-contain"
          />
          <h1 className="text-2xl font-bold text-white">Choose Login Type</h1>
          <p className="text-sm text-slate-400">
            Please select whether you want to log in as Admin or Staff
          </p>

          <div className="flex flex-col gap-4 mt-6">
            <Button
              onClick={() => navigate('/admin-login')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium h-12 rounded-lg shadow-lg hover:from-blue-700 hover:to-indigo-700"
            >
              Admin Login
            </Button>
            <Button
              onClick={() => navigate('/staff-login')}
              className="bg-gradient-to-r from-green-600 to-emerald-600 text-white font-medium h-12 rounded-lg shadow-lg hover:from-green-700 hover:to-emerald-700"
            >
              Staff Login
            </Button>
          </div>

          <p className="text-xs text-slate-500 mt-4">© 2026 DMMMSU - South La Union Campus</p>
        </motion.div>
      </div>
    </div>
  );
}