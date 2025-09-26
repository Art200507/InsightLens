import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Target, TrendingUp } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white shadow-lg border-b border-gray-100"
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-xl">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">InsightLens</h1>
              <p className="text-sm text-gray-600">Advanced Data Analytics Platform</p>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            <div className="flex items-center space-x-2 text-gray-700">
              <Target className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium">Smart Analysis</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <TrendingUp className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium">Real-time Insights</span>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;