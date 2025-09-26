import React from 'react';
import { motion } from 'framer-motion';
import { AnalysisResult } from '../types';
import MetricsGrid from './MetricsGrid';
import ChartsGrid from './ChartsGrid';
import InsightsPanel from './InsightsPanel';
import DataOverview from './DataOverview';
import { ArrowLeft, Download, Share } from 'lucide-react';

interface DashboardProps {
  analysisResult: AnalysisResult;
  fileName: string;
  onReset: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ analysisResult, fileName, onReset }) => {
  const handleExport = () => {
    const reportData = {
      fileName,
      timestamp: new Date().toISOString(),
      metrics: analysisResult.metrics,
      insights: analysisResult.insights,
      recommendations: analysisResult.recommendations
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `insightlens-analysis-${fileName.replace('.csv', '')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-8 bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <div className="flex items-center space-x-4">
          <button
            onClick={onReset}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Upload New File</span>
          </button>

          <div className="h-6 border-l border-gray-300" />

          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analysis Dashboard</h1>
            <p className="text-gray-600">File: {fileName}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleExport}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>

          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg transition-colors">
            <Share className="w-4 h-4" />
            <span>Share</span>
          </button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="xl:col-span-3 space-y-6">
          {/* Metrics Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <MetricsGrid metrics={analysisResult.metrics} />
          </motion.div>

          {/* Charts Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <ChartsGrid charts={analysisResult.charts} />
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="xl:col-span-1 space-y-6">
          {/* Data Overview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <DataOverview overview={analysisResult.overview} />
          </motion.div>

          {/* Insights Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <InsightsPanel
              insights={analysisResult.insights}
              recommendations={analysisResult.recommendations}
            />
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;