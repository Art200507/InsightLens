import { AnalysisResult, ColumnInfo, DataOverview, Metric, ChartData } from '../types';

export class DataAnalyzer {
  private data: any[] = [];
  private columns: string[] = [];
  private rawData: string;

  constructor(csvData: string) {
    this.rawData = csvData;
    this.parseCSV();
  }

  private parseCSV(): void {
    const lines = this.rawData.trim().split('\n');
    if (lines.length < 2) throw new Error('CSV file must have at least header and one data row');

    // Parse header
    this.columns = lines[0].split(',').map(col => col.trim().replace(/"/g, ''));

    // Parse data rows
    this.data = lines.slice(1).map(line => {
      const values = this.parseCSVLine(line);
      const row: any = {};
      this.columns.forEach((col, index) => {
        row[col] = values[index] || '';
      });
      return row;
    });
  }

  private parseCSVLine(line: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];

      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim().replace(/"/g, ''));
        current = '';
      } else {
        current += char;
      }
    }

    result.push(current.trim().replace(/"/g, ''));
    return result;
  }

  private detectColumnType(columnName: string, values: any[]): ColumnInfo {
    const nonEmptyValues = values.filter(v => v !== '' && v != null);
    const uniqueValues = new Set(nonEmptyValues).size;
    const nullCount = values.length - nonEmptyValues.length;

    // Check if numeric
    const numericValues = nonEmptyValues.filter(v => !isNaN(parseFloat(v)) && isFinite(v));
    const isNumeric = numericValues.length > nonEmptyValues.length * 0.8;

    // Check if datetime
    const dateValues = nonEmptyValues.filter(v => !isNaN(Date.parse(v)));
    const isDateTime = dateValues.length > nonEmptyValues.length * 0.8;

    // Determine business relevance
    const lowerName = columnName.toLowerCase();
    const isBusinessRelevant = /^(amount|price|cost|revenue|sales|total|customer|client|user|id|date|time|created|updated)/.test(lowerName);

    let businessType: string | undefined;
    if (/^(amount|price|cost|revenue|sales|total|value)/.test(lowerName)) {
      businessType = 'revenue';
    } else if (/^(customer|client|user|id)/.test(lowerName)) {
      businessType = 'customer';
    } else if (/^(date|time|created|updated)/.test(lowerName)) {
      businessType = 'date';
    } else if (!isNumeric && uniqueValues < nonEmptyValues.length * 0.5) {
      businessType = 'category';
    } else if (isNumeric && !/^(amount|price|cost|revenue|sales|total|value)/.test(lowerName)) {
      businessType = 'quantity';
    }

    return {
      name: columnName,
      type: isNumeric ? 'numeric' : isDateTime ? 'datetime' : 'categorical',
      uniqueValues,
      nullCount,
      isBusinessRelevant,
      businessType
    };
  }

  private getDataOverview(): DataOverview {
    const columns = this.columns.map(col => {
      const values = this.data.map(row => row[col]);
      return this.detectColumnType(col, values);
    });

    const totalMissingValues = columns.reduce((sum, col) => sum + col.nullCount, 0);
    const duplicateRows = this.data.length - new Set(this.data.map(row => JSON.stringify(row))).size;

    return {
      totalRows: this.data.length,
      totalColumns: this.columns.length,
      columns,
      missingValues: totalMissingValues,
      duplicateRows,
      memoryUsage: `${Math.round(this.rawData.length / 1024)} KB`
    };
  }

  private generateMetrics(): Metric[] {
    const metrics: Metric[] = [];
    const overview = this.getDataOverview();

    // Basic metrics
    metrics.push({
      label: 'Total Records',
      value: this.data.length,
      format: 'number'
    });

    metrics.push({
      label: 'Data Columns',
      value: this.columns.length,
      format: 'number'
    });

    // Find revenue columns
    const revenueColumns = overview.columns.filter(col =>
      col.businessType === 'revenue' || col.type === 'numeric' &&
      /^(amount|price|cost|revenue|sales|total|value)/.test(col.name.toLowerCase())
    );

    if (revenueColumns.length > 0) {
      const revenueCol = revenueColumns[0];
      const values = this.data.map(row => parseFloat(row[revenueCol.name])).filter(v => !isNaN(v));
      const totalRevenue = values.reduce((sum, val) => sum + val, 0);
      const avgRevenue = values.length > 0 ? totalRevenue / values.length : 0;

      metrics.push({
        label: 'Total Revenue',
        value: totalRevenue,
        format: 'currency',
        trend: 'up'
      });

      metrics.push({
        label: 'Average Order Value',
        value: avgRevenue,
        format: 'currency'
      });
    }

    // Data quality metrics
    if (overview.missingValues > 0) {
      metrics.push({
        label: 'Data Completeness',
        value: Math.round(((this.data.length * this.columns.length - overview.missingValues) / (this.data.length * this.columns.length)) * 100),
        format: 'percentage',
        trend: overview.missingValues > this.data.length * 0.1 ? 'down' : 'neutral'
      });
    }

    return metrics;
  }

  private generateCharts(): ChartData[] {
    const charts: ChartData[] = [];
    const overview = this.getDataOverview();

    // Revenue chart if available
    const revenueColumns = overview.columns.filter(col =>
      col.businessType === 'revenue' || col.type === 'numeric' &&
      /^(amount|price|cost|revenue|sales|total|value)/.test(col.name.toLowerCase())
    );

    if (revenueColumns.length > 0) {
      const revenueCol = revenueColumns[0];
      const values = this.data.map(row => parseFloat(row[revenueCol.name])).filter(v => !isNaN(v));

      // Revenue distribution
      const bins = this.createHistogramBins(values, 10);
      charts.push({
        type: 'bar',
        title: `${revenueCol.name} Distribution`,
        data: {
          labels: bins.labels,
          datasets: [{
            label: revenueCol.name,
            data: bins.values,
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            borderColor: 'rgba(59, 130, 246, 1)',
            borderWidth: 1
          }]
        }
      });
    }

    // Category analysis
    const categoryColumns = overview.columns.filter(col =>
      col.type === 'categorical' && col.uniqueValues < 20
    );

    if (categoryColumns.length > 0) {
      const categoryCol = categoryColumns[0];
      const categoryCounts: { [key: string]: number } = {};

      this.data.forEach(row => {
        const value = row[categoryCol.name];
        categoryCounts[value] = (categoryCounts[value] || 0) + 1;
      });

      const sortedCategories = Object.entries(categoryCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);

      charts.push({
        type: 'doughnut',
        title: `${categoryCol.name} Distribution`,
        data: {
          labels: sortedCategories.map(([label]) => label),
          datasets: [{
            data: sortedCategories.map(([,count]) => count),
            backgroundColor: [
              '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
              '#8B5CF6', '#06B6D4', '#84CC16', '#F97316',
              '#EC4899', '#6366F1'
            ]
          }]
        }
      });
    }

    // Time series if date column exists
    const dateColumns = overview.columns.filter(col => col.businessType === 'date' || col.type === 'datetime');

    if (dateColumns.length > 0 && revenueColumns.length > 0) {
      const dateCol = dateColumns[0];
      const revenueCol = revenueColumns[0];

      const timeData: { [key: string]: number } = {};
      this.data.forEach(row => {
        const date = new Date(row[dateCol.name]).toISOString().split('T')[0];
        const revenue = parseFloat(row[revenueCol.name]);
        if (!isNaN(revenue)) {
          timeData[date] = (timeData[date] || 0) + revenue;
        }
      });

      const sortedDates = Object.keys(timeData).sort();
      charts.push({
        type: 'line',
        title: 'Revenue Trend Over Time',
        data: {
          labels: sortedDates,
          datasets: [{
            label: 'Daily Revenue',
            data: sortedDates.map(date => timeData[date]),
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4
          }]
        }
      });
    }

    return charts;
  }

  private createHistogramBins(values: number[], binCount: number): { labels: string[], values: number[] } {
    const min = Math.min(...values);
    const max = Math.max(...values);
    const binSize = (max - min) / binCount;

    const bins = Array(binCount).fill(0);
    const labels: string[] = [];

    for (let i = 0; i < binCount; i++) {
      const binStart = min + i * binSize;
      const binEnd = min + (i + 1) * binSize;
      labels.push(`${binStart.toFixed(0)}-${binEnd.toFixed(0)}`);
    }

    values.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
      bins[binIndex]++;
    });

    return { labels, values: bins };
  }

  private generateInsights(): string[] {
    const insights: string[] = [];
    const overview = this.getDataOverview();

    // Dataset insights
    insights.push(`Dataset contains ${this.data.length.toLocaleString()} records across ${this.columns.length} columns`);

    // Data quality insights
    if (overview.missingValues > 0) {
      const completeness = Math.round(((this.data.length * this.columns.length - overview.missingValues) / (this.data.length * this.columns.length)) * 100);
      insights.push(`Data completeness is ${completeness}% with ${overview.missingValues} missing values`);
    }

    if (overview.duplicateRows > 0) {
      insights.push(`Found ${overview.duplicateRows} duplicate records that may need attention`);
    }

    // Business insights
    const revenueColumns = overview.columns.filter(col => col.businessType === 'revenue');
    if (revenueColumns.length > 0) {
      const revenueCol = revenueColumns[0];
      const values = this.data.map(row => parseFloat(row[revenueCol.name])).filter(v => !isNaN(v));
      const totalRevenue = values.reduce((sum, val) => sum + val, 0);
      insights.push(`Total revenue across all records is $${totalRevenue.toLocaleString()}`);
    }

    const customerColumns = overview.columns.filter(col => col.businessType === 'customer');
    if (customerColumns.length > 0) {
      const customerCol = customerColumns[0];
      const uniqueCustomers = new Set(this.data.map(row => row[customerCol.name])).size;
      insights.push(`Dataset includes ${uniqueCustomers.toLocaleString()} unique customers`);
    }

    return insights;
  }

  private generateRecommendations(): string[] {
    const recommendations: string[] = [];
    const overview = this.getDataOverview();

    // Data quality recommendations
    if (overview.missingValues > this.data.length * 0.05) {
      recommendations.push('Consider data cleaning to address missing values before analysis');
    }

    if (overview.duplicateRows > 0) {
      recommendations.push('Remove duplicate records to improve data quality');
    }

    // Business recommendations
    const revenueColumns = overview.columns.filter(col => col.businessType === 'revenue');
    const dateColumns = overview.columns.filter(col => col.businessType === 'date');

    if (revenueColumns.length > 0 && dateColumns.length > 0) {
      recommendations.push('Analyze revenue trends over time to identify seasonal patterns');
    }

    const categoryColumns = overview.columns.filter(col => col.type === 'categorical' && col.uniqueValues < 20);
    if (categoryColumns.length > 0) {
      recommendations.push('Segment analysis by categories could reveal growth opportunities');
    }

    if (revenueColumns.length > 0) {
      recommendations.push('Focus on high-value transactions to maximize revenue impact');
    }

    return recommendations;
  }

  public async performCompleteAnalysis(): Promise<AnalysisResult> {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));

    const overview = this.getDataOverview();
    const metrics = this.generateMetrics();
    const charts = this.generateCharts();
    const insights = this.generateInsights();
    const recommendations = this.generateRecommendations();

    return {
      overview,
      metrics,
      charts,
      insights,
      recommendations
    };
  }
}