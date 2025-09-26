import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Database } from 'lucide-react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'validating' | 'valid' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setUploadStatus('validating');

    // Validate file
    if (file.size > 50 * 1024 * 1024) { // 50MB limit
      setUploadStatus('error');
      setErrorMessage('File size must be less than 50MB');
      return;
    }

    if (!file.name.toLowerCase().endsWith('.csv')) {
      setUploadStatus('error');
      setErrorMessage('Please upload a CSV file');
      return;
    }

    setUploadStatus('valid');
    setTimeout(() => {
      onFileUpload(file);
    }, 500);
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/csv': ['.csv']
    },
    multiple: false,
    maxSize: 50 * 1024 * 1024
  });

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'validating':
        return <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />;
      case 'valid':
        return <CheckCircle className="w-8 h-8 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-8 h-8 text-red-500" />;
      default:
        return <Upload className="w-8 h-8 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    if (isDragReject || uploadStatus === 'error') return 'border-red-300 bg-red-50';
    if (isDragActive) return 'border-blue-500 bg-blue-50';
    if (uploadStatus === 'valid') return 'border-green-500 bg-green-50';
    return 'border-gray-300 hover:border-blue-400 bg-gray-50 hover:bg-blue-50';
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Transform Your Data Into
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600"> Insights</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Upload your CSV file and get instant analytics, visualizations, and business intelligence
          </p>
        </motion.div>
      </div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-8"
      >
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${getStatusColor()}`}
        >
          <input {...getInputProps()} />

          <div className="space-y-4">
            {getStatusIcon()}

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {uploadStatus === 'validating' && 'Validating file...'}
                {uploadStatus === 'valid' && 'File ready for analysis!'}
                {uploadStatus === 'error' && 'Upload failed'}
                {uploadStatus === 'idle' && (
                  isDragActive ? 'Drop your CSV file here' : 'Upload your CSV file'
                )}
              </h3>

              <p className="text-gray-600">
                {uploadStatus === 'error' ? (
                  errorMessage
                ) : uploadStatus === 'valid' ? (
                  'Processing your data...'
                ) : (
                  <>
                    Drag and drop your file here, or{' '}
                    <span className="text-blue-600 font-medium">click to browse</span>
                  </>
                )}
              </p>
            </div>

            {uploadStatus === 'idle' && (
              <div className="flex justify-center space-x-6 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4" />
                  <span>CSV files only</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4" />
                  <span>Up to 50MB</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Features Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="grid md:grid-cols-3 gap-6"
      >
        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <BarChart3 className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Analysis</h3>
          <p className="text-gray-600 text-sm">
            Automatic detection of revenue, customer, and date columns with intelligent insights
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <TrendingUp className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-time Visualization</h3>
          <p className="text-gray-600 text-sm">
            Interactive charts and dashboards that update instantly as you explore your data
          </p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <Target className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Actionable Insights</h3>
          <p className="text-gray-600 text-sm">
            Get specific recommendations and business intelligence tailored to your data
          </p>
        </div>
      </motion.div>

      {/* Sample Data Format */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="mt-12 bg-white rounded-xl p-6 border border-gray-200"
      >
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Supported Data Format Example</h4>
        <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-600">
                <th className="text-left py-2">customer_id</th>
                <th className="text-left py-2">product</th>
                <th className="text-left py-2">amount</th>
                <th className="text-left py-2">date</th>
                <th className="text-left py-2">region</th>
              </tr>
            </thead>
            <tbody className="text-gray-800">
              <tr>
                <td className="py-1">CUST-001</td>
                <td className="py-1">Laptop</td>
                <td className="py-1">999.99</td>
                <td className="py-1">2024-01-15</td>
                <td className="py-1">North</td>
              </tr>
              <tr>
                <td className="py-1">CUST-002</td>
                <td className="py-1">Mouse</td>
                <td className="py-1">29.99</td>
                <td className="py-1">2024-01-16</td>
                <td className="py-1">South</td>
              </tr>
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
};

export default FileUpload;