export interface DataFile {
  name: string;
  size: number;
  type: string;
  data: string;
}

export interface ColumnInfo {
  name: string;
  type: 'numeric' | 'categorical' | 'datetime';
  uniqueValues: number;
  nullCount: number;
  isBusinessRelevant: boolean;
  businessType?: 'revenue' | 'customer' | 'date' | 'category' | 'quantity';
}

export interface DataOverview {
  totalRows: number;
  totalColumns: number;
  columns: ColumnInfo[];
  missingValues: number;
  duplicateRows: number;
  memoryUsage: string;
}

export interface Metric {
  label: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  format?: 'currency' | 'percentage' | 'number';
}

export interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'doughnut' | 'scatter';
  title: string;
  data: any;
  options?: any;
}

export interface AnalysisResult {
  overview: DataOverview;
  metrics: Metric[];
  charts: ChartData[];
  insights: string[];
  recommendations: string[];
  segmentation?: {
    clusters: number;
    clusterData: any[];
    description: string;
  };
}

export interface UploadProgress {
  percentage: number;
  stage: string;
}