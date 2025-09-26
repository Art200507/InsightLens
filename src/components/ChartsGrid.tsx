import React from 'react';
import { motion } from 'framer-motion';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';
import { ChartData } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface ChartsGridProps {
  charts: ChartData[];
}

const ChartsGrid: React.FC<ChartsGridProps> = ({ charts }) => {
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            family: 'Inter, sans-serif',
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#f9fafb',
        bodyColor: '#f9fafb',
        borderColor: '#374151',
        borderWidth: 1,
        cornerRadius: 8,
        titleFont: {
          family: 'Inter, sans-serif',
          size: 13,
          weight: '600'
        },
        bodyFont: {
          family: 'Inter, sans-serif',
          size: 12
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: '#f3f4f6',
          drawBorder: false
        },
        ticks: {
          font: {
            family: 'Inter, sans-serif',
            size: 11
          },
          color: '#6b7280'
        }
      },
      y: {
        grid: {
          color: '#f3f4f6',
          drawBorder: false
        },
        ticks: {
          font: {
            family: 'Inter, sans-serif',
            size: 11
          },
          color: '#6b7280'
        }
      }
    }
  };

  const renderChart = (chart: ChartData, index: number) => {
    const mergedOptions = { ...defaultOptions, ...chart.options };

    switch (chart.type) {
      case 'bar':
        return <Bar data={chart.data} options={mergedOptions} />;
      case 'line':
        return <Line data={chart.data} options={mergedOptions} />;
      case 'pie':
        return <Pie data={chart.data} options={mergedOptions} />;
      case 'doughnut':
        return <Doughnut data={chart.data} options={mergedOptions} />;
      default:
        return <Bar data={chart.data} options={mergedOptions} />;
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Visualizations</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {charts.map((chart, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="chart-container"
          >
            <h3 className="text-lg font-medium text-gray-900 mb-4">{chart.title}</h3>
            <div className="h-64 w-full">
              {renderChart(chart, index)}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default ChartsGrid;