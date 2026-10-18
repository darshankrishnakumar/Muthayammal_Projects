import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MetricsOverview } from './components/MetricsOverview';
import { PredictionForm } from './components/PredictionForm';
import { ValuationResult } from './components/ValuationResult';
import { ModelBenchmarks } from './components/ModelBenchmarks';
import { DatasetExplorer } from './components/DatasetExplorer';
import { PredictionHistory } from './components/PredictionHistory';
import { Visualizations } from './components/Visualizations';
import { CarPredictionInput, PredictionResponse, ModelMetadata } from './types';

export default function App() {
  const [metadata, setMetadata] = useState<ModelMetadata | null>(null);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('Random Forest Regression');
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isBenchmarksOpen, setIsBenchmarksOpen] = useState<boolean>(false);
  const [isDatasetOpen, setIsDatasetOpen] = useState<boolean>(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState<boolean>(false);
  const [historyCount, setHistoryCount] = useState<number>(0);

  // Fetch model metadata and history on mount
  useEffect(() => {
    fetchMetadata();
    fetchHistoryCount();
    // Run an initial quick evaluation with a realistic car so the user sees results immediately
    runInitialPrediction();
  }, []);

  const fetchHistoryCount = async () => {
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const data = await res.json();
        setHistoryCount(Array.isArray(data) ? data.length : 0);
      }
    } catch (err) {
      // Silently fail if history not yet initialized
    }
  };

  const fetchMetadata = async () => {
    try {
      const res = await fetch('/api/info');
      if (res.ok) {
        const data = await res.json();
        setMetadata(data);
        if (data.best_model) {
          setSelectedAlgorithm(data.best_model);
        }
      }
    } catch (err) {
      console.warn('Could not fetch model metadata:', err);
    }
  };

  const runInitialPrediction = async () => {
    const initialCar: CarPredictionInput = {
      brand: 'Honda',
      car_model: 'City',
      year: 2018,
      present_price: 13.2,
      kms_driven: 45000,
      fuel_type: 'Petrol',
      seller_type: 'Dealer',
      transmission: 'Manual',
      owner: 0,
      algorithm: 'Random Forest Regression',
    };
    handlePredict(initialCar);
  };

  const handlePredict = async (input: CarPredictionInput) => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...input,
        algorithm: selectedAlgorithm,
      };

      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || errData.detail || 'Prediction failed. Check vehicle inputs.');
      }

      const data = await res.json();
      setResult(data);
      fetchHistoryCount();
    } catch (err: any) {
      console.error('Prediction error:', err);
      setError(err.message || 'Failed to calculate car valuation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans antialiased">
      <Header
        activeModelName={selectedAlgorithm}
        onOpenBenchmarks={() => setIsBenchmarksOpen(true)}
        onOpenDataset={() => setIsDatasetOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        historyCount={historyCount}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">

        {/* Model Evaluation Metrics Overview */}
        <MetricsOverview metadata={metadata} selectedAlgorithm={selectedAlgorithm} />

        {/* Form and Valuation Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7">
            <PredictionForm
              metadata={metadata}
              selectedAlgorithm={selectedAlgorithm}
              onAlgorithmChange={(algo) => setSelectedAlgorithm(algo)}
              onSubmit={handlePredict}
              loading={loading}
              error={error}
            />
          </div>

          <div className="lg:col-span-5">
            <ValuationResult result={result} loading={loading} />
          </div>
        </div>

        {/* Interactive Visualizations: Depreciation Curve & Feature Importance */}
        {result && (
          <Visualizations
            presentPrice={result.original_price_lakhs}
            predictedPrice={result.predicted_price_lakhs}
            currentAge={result.vehicle_summary.age_years}
            featureImportances={metadata?.feature_importances}
          />
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span>Automotive Valuation &amp; Market Pricing System</span>
            <span>&bull;</span>
            <span className="text-emerald-600 font-medium">Smart Pricing Engine &bull; Market Analytics</span>
          </div>
          <div>
            <span>Benchmark Database: 450 Verified Market Transactions</span>
          </div>
        </div>
      </footer>

      {/* Benchmarks Modal */}
      <ModelBenchmarks
        isOpen={isBenchmarksOpen}
        onClose={() => setIsBenchmarksOpen(false)}
        metadata={metadata}
        selectedAlgorithm={selectedAlgorithm}
        onSelectAlgorithm={(algo) => setSelectedAlgorithm(algo)}
      />

      {/* Dataset Explorer Modal */}
      <DatasetExplorer
        isOpen={isDatasetOpen}
        onClose={() => setIsDatasetOpen(false)}
        onSelectCar={(car) => {
          handlePredict(car);
        }}
      />

      {/* Prediction History Modal */}
      <PredictionHistory
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectRecord={(car) => {
          handlePredict(car);
        }}
        onRecordCountChange={setHistoryCount}
      />
    </div>
  );
}
