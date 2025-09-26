import React from 'react';
import { motion } from 'framer-motion';
import { Database, Columns, AlertTriangle, CheckCircle } from 'lucide-react';
import { DataOverview as DataOverviewType } from '../types';

interface DataOverviewProps {
  overview: DataOverviewType;
}

const DataOverview: React.FC<DataOverviewProps> = ({ overview }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Database className="w-5 h-5 mr-2 text-blue-600" />
        Data Overview
      </h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Total Rows</span>
          <span className="font-medium text-gray-900">{overview.totalRows.toLocaleString()}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Columns</span>
          <span className="font-medium text-gray-900">{overview.totalColumns}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Memory Usage</span>
          <span className="font-medium text-gray-900">{overview.memoryUsage}</span>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Data Quality</span>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {overview.missingValues === 0 ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-yellow-500 mr-2" />
                )}
                <span className="text-xs text-gray-600">Missing Values</span>
              </div>
              <span className="text-xs font-medium text-gray-900">{overview.missingValues}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                {overview.duplicateRows === 0 ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                ) : (
                  <AlertTriangle className="w-4 h-4 text-yellow-500 mr-2" />
                )}
                <span className="text-xs text-gray-600">Duplicates</span>
              </div>
              <span className="text-xs font-medium text-gray-900">{overview.duplicateRows}</span>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3 flex items-center">
            <Columns className="w-4 h-4 mr-1" />
            Column Types
          </h4>
          <div className="space-y-2">
            {overview.columns.slice(0, 5).map((column, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center justify-between"
              >
                <div className="flex items-center flex-1 min-w-0">
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    column.type === 'numeric' ? 'bg-blue-500' :
                    column.type === 'datetime' ? 'bg-green-500' : 'bg-purple-500'
                  }`} />
                  <span className="text-xs text-gray-700 truncate" title={column.name}>
                    {column.name}
                  </span>
                </div>
                <div className="flex items-center space-x-1 ml-2">
                  {column.isBusinessRelevant && (
                    <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full" title="Business Relevant" />
                  )}
                  <span className="text-xs text-gray-500 capitalize">
                    {column.businessType || column.type}
                  </span>
                </div>
              </motion.div>
            ))}
            {overview.columns.length > 5 && (
              <div className="text-xs text-gray-500 text-center pt-2">
                +{overview.columns.length - 5} more columns
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataOverview;