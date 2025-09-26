import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, Target, ChevronRight } from 'lucide-react';

interface InsightsPanelProps {
  insights: string[];
  recommendations: string[];
}

const InsightsPanel: React.FC<InsightsPanelProps> = ({ insights, recommendations }) => {
  const [activeTab, setActiveTab] = useState<'insights' | 'recommendations'>('insights');

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
      <div className="flex items-center space-x-4 mb-4">
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'insights'
              ? 'bg-blue-100 text-blue-700'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Lightbulb className="w-4 h-4" />
          <span>Insights</span>
        </button>
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'recommendations'
              ? 'bg-green-100 text-green-700'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Target className="w-4 h-4" />
          <span>Actions</span>
        </button>
      </div>

      <div className="space-y-3">
        {activeTab === 'insights' ? (
          <>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Key Insights</h4>
            {insights.map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100"
              >
                <Lightbulb className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-blue-900 leading-relaxed">{insight}</p>
              </motion.div>
            ))}
          </>
        ) : (
          <>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Recommended Actions</h4>
            {recommendations.map((recommendation, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-100 hover:bg-green-100 transition-colors cursor-pointer"
              >
                <ChevronRight className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-green-900 leading-relaxed">{recommendation}</p>
              </motion.div>
            ))}
          </>
        )}

        {((activeTab === 'insights' && insights.length === 0) ||
          (activeTab === 'recommendations' && recommendations.length === 0)) && (
          <div className="text-center py-8 text-gray-500">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              {activeTab === 'insights' ? (
                <Lightbulb className="w-6 h-6 text-gray-400" />
              ) : (
                <Target className="w-6 h-6 text-gray-400" />
              )}
            </div>
            <p className="text-sm">
              {activeTab === 'insights'
                ? 'No insights available yet'
                : 'No recommendations available yet'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InsightsPanel;