import { useEffect, useState } from 'react';
import { X, History, Trash2, ArrowRight, RefreshCw, Download, Calendar, DollarSign, Car } from 'lucide-react';
import { PredictionHistoryRecord, CarPredictionInput } from '../types';

interface PredictionHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectRecord: (input: CarPredictionInput) => void;
  onRecordCountChange?: (count: number) => void;
}

export function PredictionHistory({
  isOpen,
  onClose,
  onSelectRecord,
  onRecordCountChange,
}: PredictionHistoryProps) {
  const [history, setHistory] = useState<PredictionHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
        if (onRecordCountChange) {
          onRecordCountChange(data.length);
        }
      } else {
        throw new Error('Failed to load history');
      }
    } catch (err: any) {
      setError(err.message || 'Could not fetch history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
      if (res.ok) {
        const updated = history.filter((item) => item.id !== id);
        setHistory(updated);
        if (onRecordCountChange) {
          onRecordCountChange(updated.length);
        }
      }
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear all prediction history?')) {
      return;
    }
    try {
      const res = await fetch('/api/history', { method: 'DELETE' });
      if (res.ok) {
        setHistory([]);
        if (onRecordCountChange) {
          onRecordCountChange(0);
        }
      }
    } catch (err) {
      console.error('Clear error:', err);
    }
  };

  const exportCSV = () => {
    if (history.length === 0) return;
    const headers = [
      'ID',
      'Date',
      'Brand',
      'Model',
      'Year',
      'Present_Price_Lakhs',
      'Kms_Driven',
      'Fuel',
      'Transmission',
      'Predicted_Price_Lakhs',
      'Predicted_USD',
      'Depreciation_Pct',
      'Algorithm',
    ];
    const rows = history.map((h) => [
      h.id,
      h.created_at,
      h.brand,
      h.car_model || '',
      h.year,
      h.present_price,
      h.kms_driven,
      h.fuel_type,
      h.transmission,
      h.predicted_price_lakhs,
      h.predicted_price_usd,
      h.depreciation_percentage,
      h.algorithm,
    ]);
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `car_prediction_history_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div
        id="history-modal"
        className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-slate-200 shadow-xl flex flex-col"
      >
        <div className="p-5 sm:p-6 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-white">
          <div>
            <div className="flex items-center gap-2">
              <History className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-bold text-slate-900">Valuation Prediction History</h3>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                {history.length} Saved {history.length === 1 ? 'Record' : 'Records'}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Persistent SQLite storage of past car valuation assessments and market estimates
            </p>
          </div>

          <div className="flex items-center gap-2">
            {history.length > 0 && (
              <>
                <button
                  type="button"
                  onClick={exportCSV}
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export CSV</span>
                </button>
                <button
                  type="button"
                  onClick={handleClearAll}
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-rose-200 text-rose-700 hover:bg-rose-50 transition-colors cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                  <span>Clear All</span>
                </button>
              </>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5 sm:p-6">
          {loading ? (
            <div className="flex items-center justify-center py-16 text-slate-500 gap-2 text-xs">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
              Loading persistent history records...
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              {error}
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-16 flex flex-col items-center">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mb-3">
                <History className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-bold text-slate-800">No Predictions Recorded Yet</h4>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Calculate vehicle valuations using the main form to automatically log records into your SQLite database.
              </p>
            </div>
          ) : (
            <div className="border border-slate-200 rounded-xl overflow-x-auto shadow-xs">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                    <th className="py-3 px-3">Date</th>
                    <th className="py-3 px-3.5">Vehicle</th>
                    <th className="py-3 px-2">Year</th>
                    <th className="py-3 px-2.5">Odometer</th>
                    <th className="py-3 px-2.5">Showroom</th>
                    <th className="py-3 px-3">Predicted Value</th>
                    <th className="py-3 px-2">Deprec.</th>
                    <th className="py-3 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {history.map((item) => {
                    const formattedDate = new Date(item.created_at).toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    });

                    return (
                      <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-2.5 px-3 text-slate-500 whitespace-nowrap">
                          {formattedDate}
                        </td>
                        <td className="py-2.5 px-3.5 font-semibold text-slate-900">
                          <div className="flex items-center gap-1.5">
                            <Car className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                            <span>
                              {item.brand} {item.car_model || ''}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400 font-normal">
                            {item.fuel_type} &bull; {item.transmission}
                          </div>
                        </td>
                        <td className="py-2.5 px-2 text-slate-600">{item.year}</td>
                        <td className="py-2.5 px-2.5 text-slate-600">
                          {item.kms_driven.toLocaleString()} km
                        </td>
                        <td className="py-2.5 px-2.5 text-slate-500">
                          ₹{item.present_price.toFixed(2)}L
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="font-bold text-emerald-700 text-sm">
                            ₹{item.predicted_price_lakhs.toFixed(2)}L
                          </span>
                          <span className="block text-[10px] text-slate-400">
                            ${item.predicted_price_usd.toLocaleString()} USD
                          </span>
                        </td>
                        <td className="py-2.5 px-2">
                          <span className="inline-flex items-center text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                            -{item.depreciation_percentage}%
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-right whitespace-nowrap">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              type="button"
                              onClick={() => {
                                onSelectRecord({
                                  brand: item.brand,
                                  car_model: item.car_model,
                                  year: item.year,
                                  present_price: item.present_price,
                                  kms_driven: item.kms_driven,
                                  fuel_type: item.fuel_type,
                                  seller_type: item.seller_type,
                                  transmission: item.transmission,
                                  owner: item.owner,
                                  algorithm: item.algorithm,
                                });
                                onClose();
                              }}
                              className="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-1 rounded-md transition-colors cursor-pointer"
                              title="Load this car's specs into the valuation form"
                            >
                              <span>Replay</span>
                              <ArrowRight className="w-3 h-3" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDelete(item.id)}
                              className="text-slate-400 hover:text-rose-600 p-1 rounded-md hover:bg-rose-50 transition-colors cursor-pointer"
                              title="Delete record"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
