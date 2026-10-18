import { useEffect, useState } from 'react';
import { X, Database, ArrowRight, RefreshCw, Car } from 'lucide-react';
import { CarSampleRow, CarPredictionInput } from '../types';

interface DatasetExplorerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectCar: (car: CarPredictionInput) => void;
}

export function DatasetExplorer({ isOpen, onClose, onSelectCar }: DatasetExplorerProps) {
  const [samples, setSamples] = useState<CarSampleRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSamples();
    }
  }, [isOpen]);

  const fetchSamples = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/dataset/sample');
      if (res.ok) {
        const data = await res.json();
        setSamples(data);
      }
    } catch (err) {
      console.error('Failed to fetch dataset samples:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div
        id="dataset-modal"
        className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-slate-200 shadow-xl flex flex-col"
      >
        <div className="p-5 sm:p-6 border-b border-slate-200 flex items-center justify-between bg-white">
          <div>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-emerald-600" />
              <h3 className="text-lg font-bold text-slate-900">Market Benchmark Database Explorer</h3>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Verified market transactions from <code className="text-slate-700 bg-slate-100 px-1 py-0.5 rounded">data/car_data.csv</code>. Click &quot;Test Car&quot; to test valuation against true sold prices.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 sm:p-6">
          {loading ? (
            <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-xs">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
              Loading dataset sample rows...
            </div>
          ) : (
            <div className="border border-slate-200 rounded-xl overflow-x-auto shadow-xs">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                    <th className="py-3 px-3.5">Car Model</th>
                    <th className="py-3 px-2">Year</th>
                    <th className="py-3 px-2.5">Sold Price</th>
                    <th className="py-3 px-2.5">Showroom</th>
                    <th className="py-3 px-3">Odometer</th>
                    <th className="py-3 px-2.5">Fuel</th>
                    <th className="py-3 px-2.5">Trans.</th>
                    <th className="py-3 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {samples.map((row, idx) => {
                    const carName = String(row.Car_Name || 'Car');
                    const brandName = carName.split(' ')[0] || 'Maruti';
                    return (
                      <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3.5 font-medium text-slate-900 flex items-center gap-1.5">
                          <Car className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                          {carName}
                        </td>
                        <td className="py-2.5 px-2 text-slate-600">{row.Year}</td>
                        <td className="py-2.5 px-2.5 font-bold text-emerald-700">
                          ₹{Number(row.Selling_Price).toFixed(2)}L
                        </td>
                        <td className="py-2.5 px-2.5 text-slate-500">
                          ₹{Number(row.Present_Price).toFixed(2)}L
                        </td>
                        <td className="py-2.5 px-3 text-slate-600">
                          {Number(row.Kms_Driven).toLocaleString()} km
                        </td>
                        <td className="py-2.5 px-2.5 text-slate-600">{row.Fuel_Type}</td>
                        <td className="py-2.5 px-2.5 text-slate-600">{row.Transmission}</td>
                        <td className="py-2.5 px-3 text-right">
                          <button
                            type="button"
                            onClick={() => {
                              const parts = carName.split(' ');
                              const brandName = parts[0] || 'Maruti';
                              const modelName = parts.slice(1).join(' ');
                              onSelectCar({
                                brand: brandName,
                                car_model: modelName,
                                year: Number(row.Year),
                                present_price: Number(row.Present_Price),
                                kms_driven: Number(row.Kms_Driven),
                                fuel_type: String(row.Fuel_Type),
                                seller_type: String(row.Seller_Type || 'Dealer'),
                                transmission: String(row.Transmission || 'Manual'),
                                owner: Number(row.Owner || 0),
                              });
                              onClose();
                            }}
                            className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors cursor-pointer"
                          >
                            <span>Test Car</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="p-4 sm:p-5 border-t border-slate-200 bg-slate-50 flex justify-between items-center">
          <span className="text-xs text-slate-500">Showing top 15 sampled records from training set</span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold transition-colors cursor-pointer"
          >
            Close Explorer
          </button>
        </div>
      </div>
    </div>
  );
}
