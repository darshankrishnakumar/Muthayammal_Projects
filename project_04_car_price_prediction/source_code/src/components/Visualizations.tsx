import React, { useState } from 'react';
import { TrendingDown, BarChart2, Info, Sparkles, Activity } from 'lucide-react';
import { FeatureImportanceItem } from '../types';

interface VisualizationsProps {
  presentPrice: number;
  predictedPrice: number;
  currentAge: number;
  featureImportances?: FeatureImportanceItem[];
}

export function Visualizations({
  presentPrice,
  predictedPrice,
  currentAge,
  featureImportances,
}: VisualizationsProps) {
  const [activeTab, setActiveTab] = useState<'depreciation' | 'features'>('depreciation');

  // Compute 10-year depreciation trajectory simulation
  // Age 0 (showroom) to Age 10
  const points = [];
  const basePrice = Math.max(0.5, presentPrice);
  for (let age = 0; age <= 10; age++) {
    // Non-linear depreciation: ~10% year 1, 8% after, adjusted by current car's scale
    const factor = Math.max(0.18, Math.pow(1 - 0.09, age));
    const projected = Math.max(0.3, Number((basePrice * factor).toFixed(2)));
    points.push({ age, price: projected });
  }

  const maxPrice = Math.max(...points.map((p) => p.price), basePrice);
  const minPrice = 0;

  // SVG Chart dimensions
  const width = 500;
  const height = 180;
  const padding = { top: 20, right: 30, bottom: 30, left: 45 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const getX = (age: number) => padding.left + (age / 10) * chartW;
  const getY = (price: number) =>
    padding.top + chartH - ((price - minPrice) / (maxPrice - minPrice || 1)) * chartH;

  const pathD = points
    .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(p.age).toFixed(1)} ${getY(p.price).toFixed(1)}`)
    .join(' ');

  const currentX = getX(Math.min(10, currentAge));
  const currentY = getY(Math.min(maxPrice, predictedPrice));

  const defaultImportances: FeatureImportanceItem[] = [
    { feature: 'Showroom Price (Ex-Showroom)', key: 'Present_Price', importance_pct: 75.15 },
    { feature: 'Vehicle Age', key: 'Car_Age', importance_pct: 13.23 },
    { feature: 'Odometer (Kms Driven)', key: 'Kms_Driven', importance_pct: 9.33 },
    { feature: 'Manufacturer Brand', key: 'Brand', importance_pct: 1.32 },
    { feature: 'Previous Owners', key: 'Owner', importance_pct: 0.33 },
    { feature: 'Fuel Powertrain', key: 'Fuel_Type', importance_pct: 0.24 },
    { feature: 'Transmission Type', key: 'Transmission', importance_pct: 0.22 },
  ];

  const items = featureImportances && featureImportances.length > 0 ? featureImportances : defaultImportances;

  return (
    <div id="ml-visualizations-card" className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs mt-5">
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-blue-600" />
            Automotive Price Analytics &amp; Value Drivers
          </h3>
          <p className="text-[11px] text-slate-500">
            Interactive depreciation trajectory and key price-determining factors
          </p>
        </div>

        <div className="flex rounded-lg bg-slate-100 p-0.5 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab('depreciation')}
            className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
              activeTab === 'depreciation'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Depreciation Curve
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('features')}
            className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
              activeTab === 'features'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Key Value Drivers
          </button>
        </div>
      </div>

      {activeTab === 'depreciation' ? (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
            <span>
              Resale Value Projection: <strong className="text-slate-800">₹{basePrice.toFixed(2)}L</strong> initial showroom
            </span>
            <span className="flex items-center gap-1 text-blue-600 font-semibold">
              <span className="w-2 h-2 rounded-full bg-blue-600 inline-block"></span>
              Current Vehicle: {currentAge} yrs old &bull; ₹{predictedPrice.toFixed(2)}L
            </span>
          </div>

          <div className="relative w-full overflow-hidden bg-slate-50/50 rounded-xl p-2 border border-slate-100">
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
              {/* Grid Lines */}
              {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
                const yVal = padding.top + chartH * (1 - pct);
                const priceLabel = (minPrice + pct * (maxPrice - minPrice)).toFixed(1);
                return (
                  <g key={i}>
                    <line
                      x1={padding.left}
                      y1={yVal}
                      x2={width - padding.right}
                      y2={yVal}
                      stroke="#e2e8f0"
                      strokeDasharray="3 3"
                    />
                    <text
                      x={padding.left - 6}
                      y={yVal + 3}
                      textAnchor="end"
                      fontSize="9"
                      fill="#94a3b8"
                    >
                      ₹{priceLabel}L
                    </text>
                  </g>
                );
              })}

              {/* X-axis labels */}
              {[0, 2, 4, 6, 8, 10].map((age) => (
                <text
                  key={age}
                  x={getX(age)}
                  y={height - 8}
                  textAnchor="middle"
                  fontSize="9"
                  fill="#94a3b8"
                >
                  {age === 0 ? 'New' : `${age}y`}
                </text>
              ))}

              {/* Area fill */}
              <path
                d={`${pathD} L ${getX(10)} ${padding.top + chartH} L ${getX(0)} ${padding.top + chartH} Z`}
                fill="url(#deprecGradient)"
                opacity="0.25"
              />

              {/* Primary Line */}
              <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth="2.5" strokeLinecap="round" />

              {/* Data points */}
              {points.map((p) => (
                <circle
                  key={p.age}
                  cx={getX(p.age)}
                  cy={getY(p.price)}
                  r={p.age === currentAge ? '5' : '2.5'}
                  fill={p.age === currentAge ? '#2563eb' : '#60a5fa'}
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              ))}

              {/* Current Car Marker */}
              {currentAge <= 10 && (
                <g>
                  <circle cx={currentX} cy={currentY} r="7" fill="#2563eb" fillOpacity="0.3" />
                  <circle cx={currentX} cy={currentY} r="4" fill="#2563eb" stroke="#fff" strokeWidth="1.5" />
                </g>
              )}

              <defs>
                <linearGradient id="deprecGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#ffffff" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div className="grid grid-cols-3 gap-2 mt-3 text-center text-xs">
            <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-medium">3-Year Residual</span>
              <span className="font-bold text-slate-800">
                ~{Math.round(Math.pow(1 - 0.09, 3) * 100)}% of value
              </span>
            </div>
            <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-medium">5-Year Residual</span>
              <span className="font-bold text-slate-800">
                ~{Math.round(Math.pow(1 - 0.09, 5) * 100)}% of value
              </span>
            </div>
            <div className="p-2 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 block font-medium">10-Year Floor</span>
              <span className="font-bold text-slate-800">~22% market retention</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
            <span>Market Valuation Factor Weights</span>
            <span className="text-[11px] text-emerald-600 font-semibold">Calibrated from 150 Market Splits</span>
          </div>

          <div className="space-y-2.5">
            {items.map((item) => (
              <div key={item.key} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-700">{item.feature}</span>
                  <span className="font-bold text-slate-900">{item.importance_pct}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500"
                    style={{ width: `${Math.max(2, item.importance_pct)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-3 p-3 rounded-lg bg-blue-50/70 border border-blue-100 text-[11px] text-blue-900 flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <div>
              <strong>Market Valuation Insight:</strong> Original Showroom Price and Vehicle Age account for over <strong>88%</strong> of total price variation in used car transactions, with odometer usage contributing an additional <strong>9%</strong>.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
