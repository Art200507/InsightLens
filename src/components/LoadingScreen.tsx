import React from 'react';
import { motion } from 'framer-motion';
import { BarChart3 } from 'lucide-react';

const LoadingScreen: React.FC = () => {
  const loadingSteps = [
    'Parsing CSV data...',
    'Detecting column types...',
    'Analyzing patterns...',
    'Generating insights...',
    'Creating visualizations...'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center max-w-md mx-auto px-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="bg-white rounded-2xl p-8 shadow-xl border border-gray-100">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-16 h-16 mx-auto mb-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center"
            >
              <BarChart3 className="w-8 h-8 text-white" />
            </motion.div>

            <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Your Data</h2>
            <p className="text-gray-600 mb-6">
              Please wait while we process your file and generate insights
            </p>

            <div className="space-y-3">
              {loadingSteps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.2 }}
                  className="flex items-center space-x-3"
                >
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: index * 0.2 }}
                    className="w-2 h-2 bg-blue-600 rounded-full"
                  />
                  <span className="text-sm text-gray-700">{step}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-gray-500 text-sm"
        >
          This usually takes 10-30 seconds depending on your file size
        </motion.div>
      </div>
    </div>
  );
};

export default LoadingScreen;