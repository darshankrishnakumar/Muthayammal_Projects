export function formatMethodName(method?: string): string {
  if (!method) return 'Multi-Factor Ensemble';
  if (method.includes('Random Forest')) return 'Multi-Factor Ensemble';
  if (method.includes('Decision Tree')) return 'Decision Tree';
  if (method.includes('Linear Regression')) return 'Market Trend Baseline';
  return method.replace(/ Regression/i, '');
}

export interface CarPredictionInput {
  brand: string;
  car_model?: string;
  year: number;
  present_price: number;
  kms_driven: number;
  fuel_type: string;
  seller_type: string;
  transmission: string;
  owner: number;
  algorithm?: string;
}

export interface ConfidenceRange {
  lower_lakhs: number;
  upper_lakhs: number;
  lower_usd: number;
  upper_usd: number;
}

export interface ModelDetails {
  algorithm: string;
  r2_score: number;
  rmse: number;
  mae: number;
}

export interface VehicleSummary {
  brand: string;
  car_model?: string;
  year: number;
  age_years: number;
  mileage_kms: number;
  fuel_type: string;
  transmission: string;
  seller_type: string;
  previous_owners: number;
}

export interface PredictionResponse {
  success: boolean;
  history_id?: number;
  predicted_price_lakhs: number;
  predicted_price_usd: number;
  original_price_lakhs: number;
  original_price_usd: number;
  depreciation_percentage: number;
  depreciation_amount_lakhs: number;
  retention_rating: string;
  confidence_range: ConfidenceRange;
  model_details: ModelDetails;
  vehicle_summary: VehicleSummary;
}

export interface ModelMetric {
  train_r2: number;
  test_r2: number;
  test_rmse: number;
  test_mae: number;
  params: string;
}

export interface FeatureImportanceItem {
  feature: string;
  key: string;
  importance_pct: number;
}

export interface ModelMetadata {
  best_model: string;
  metrics: Record<string, ModelMetric>;
  training_samples: number;
  test_samples: number;
  feature_importances?: FeatureImportanceItem[];
  models_by_brand?: Record<string, string[]>;
  model_price_lookup?: Record<string, number>;
  numerical_features: string[];
  categorical_features: string[];
  categorical_options: {
    Brand: string[];
    Fuel_Type: string[];
    Seller_Type: string[];
    Transmission: string[];
    Owner: number[];
  };
  stats: {
    min_year: number;
    max_year: number;
    min_present_price: number;
    max_present_price: number;
    avg_present_price: number;
    min_selling_price: number;
    max_selling_price: number;
    avg_selling_price: number;
  };
}

export interface CarSampleRow {
  Car_Name: string;
  Year: string | number;
  Selling_Price: string | number;
  Present_Price: string | number;
  Kms_Driven: string | number;
  Fuel_Type: string;
  Seller_Type: string;
  Transmission: string;
  Owner: string | number;
}

export interface PredictionHistoryRecord {
  id: number;
  created_at: string;
  brand: string;
  car_model?: string;
  year: number;
  age_years: number;
  present_price: number;
  kms_driven: number;
  fuel_type: string;
  transmission: string;
  seller_type: string;
  owner: number;
  algorithm: string;
  predicted_price_lakhs: number;
  predicted_price_usd: number;
  depreciation_percentage: number;
  retention_rating: string;
  lower_bound_lakhs?: number;
  upper_bound_lakhs?: number;
}
