import React, { useState } from 'react';
import { Car, Calendar, Gauge, Fuel, Cog, UserCheck, Tag, Sparkles, AlertCircle, ArrowRight } from 'lucide-react';
import { CarPredictionInput, ModelMetadata } from '../types';

interface PredictionFormProps {
  metadata: ModelMetadata | null;
  selectedAlgorithm: string;
  onAlgorithmChange: (algo: string) => void;
  onSubmit: (input: CarPredictionInput) => void;
  loading: boolean;
  error: string | null;
}

const PRESET_VEHICLES: Array<{ label: string; data: CarPredictionInput }> = [
  {
    label: '2018 Honda City',
    data: {
      brand: 'Honda',
      car_model: 'City',
      year: 2018,
      present_price: 13.2,
      kms_driven: 45000,
      fuel_type: 'Petrol',
      seller_type: 'Dealer',
      transmission: 'Manual',
      owner: 0,
    },
  },
  {
    label: '2019 Toyota Fortuner',
    data: {
      brand: 'Toyota',
      car_model: 'Fortuner',
      year: 2019,
      present_price: 35.5,
      kms_driven: 62000,
      fuel_type: 'Diesel',
      seller_type: 'Dealer',
      transmission: 'Automatic',
      owner: 0,
    },
  },
  {
    label: '2016 Maruti Swift',
    data: {
      brand: 'Maruti',
      car_model: 'Swift',
      year: 2016,
      present_price: 6.8,
      kms_driven: 58000,
      fuel_type: 'Petrol',
      seller_type: 'Individual',
      transmission: 'Manual',
      owner: 1,
    },
  },
  {
    label: '2021 Hyundai Creta',
    data: {
      brand: 'Hyundai',
      car_model: 'Creta',
      year: 2021,
      present_price: 14.5,
      kms_driven: 28000,
      fuel_type: 'Diesel',
      seller_type: 'Dealer',
      transmission: 'Automatic',
      owner: 0,
    },
  },
];

export function PredictionForm({
  metadata,
  selectedAlgorithm,
  onAlgorithmChange,
  onSubmit,
  loading,
  error,
}: PredictionFormProps) {
  const [brand, setBrand] = useState('Maruti');
  const [carModel, setCarModel] = useState('Swift');
  const [year, setYear] = useState(2018);
  const [presentPrice, setPresentPrice] = useState(6.8);
  const [kmsDriven, setKmsDriven] = useState(42000);
  const [fuelType, setFuelType] = useState('Petrol');
  const [sellerType, setSellerType] = useState('Dealer');
  const [transmission, setTransmission] = useState('Manual');
  const [owner, setOwner] = useState(0);

  const availableBrands = metadata?.categorical_options?.Brand || [
    'Toyota', 'Honda', 'Hyundai', 'Maruti', 'Ford', 'Volkswagen', 'Mahindra', 'Tata', 'BMW', 'Audi', 'Mercedes'
  ];

  const modelsForBrand = metadata?.models_by_brand?.[brand] || [
    'Swift', 'Dzire', 'Baleno', 'Ertiga', 'Ciaz', 'Wagon R', 'Brezza'
  ];

  const handleBrandChange = (newBrand: string) => {
    setBrand(newBrand);
    const newModels = metadata?.models_by_brand?.[newBrand] || [];
    const firstModel = newModels.length > 0 ? newModels[0] : '';
    setCarModel(firstModel);

    // Auto-suggest showroom price for the selected model
    const fullName = `${newBrand} ${firstModel}`.trim();
    if (metadata?.model_price_lookup?.[fullName]) {
      setPresentPrice(metadata.model_price_lookup[fullName]);
    }
  };

  const handleModelChange = (newModel: string) => {
    setCarModel(newModel);
    const fullName = `${brand} ${newModel}`.trim();
    if (metadata?.model_price_lookup?.[fullName]) {
      setPresentPrice(metadata.model_price_lookup[fullName]);
    }
  };

  const handleApplyPreset = (preset: CarPredictionInput) => {
    setBrand(preset.brand);
    if (preset.car_model) {
      setCarModel(preset.car_model);
    }
    setYear(preset.year);
    setPresentPrice(preset.present_price);
    setKmsDriven(preset.kms_driven);
    setFuelType(preset.fuel_type);
    setSellerType(preset.seller_type);
    setTransmission(preset.transmission);
    setOwner(preset.owner);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      brand,
      car_model: carModel,
      year: Number(year),
      present_price: Number(presentPrice),
      kms_driven: Number(kmsDriven),
      fuel_type: fuelType,
      seller_type: sellerType,
      transmission: transmission,
      owner: Number(owner),
      algorithm: selectedAlgorithm,
    });
  };

  return (
    <div id="prediction-input-card" className="bg-white border border-slate-200 rounded-xl p-5 sm:p-6 shadow-xs">
      <div className="flex flex-wrap items-center justify-between gap-2 pb-4 mb-5 border-b border-slate-100">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900">Vehicle Specification Input</h2>
          <p className="text-xs text-slate-500">Provide parameters to evaluate predicted resale value</p>
        </div>

        {/* Quick Sample Presets */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-xs text-slate-400 font-medium">Quick Presets:</span>
          {PRESET_VEHICLES.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => handleApplyPreset(preset.data)}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors font-medium cursor-pointer"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div id="form-error-alert" className="mb-5 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form id="car-valuation-form" onSubmit={handleSubmit} className="space-y-4">
        {/* Make, Model & Manufacturing Year */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          <div>
            <label htmlFor="car-brand" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <Car className="w-3.5 h-3.5 text-blue-600" />
              Manufacturer / Brand
            </label>
            <select
              id="car-brand"
              value={brand}
              onChange={(e) => handleBrandChange(e.target.value)}
              className="w-full text-sm rounded-lg border border-slate-300 px-3 py-2 text-slate-800 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {availableBrands.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="car-model" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <Car className="w-3.5 h-3.5 text-blue-600" />
              Car Model
            </label>
            <select
              id="car-model"
              value={carModel}
              onChange={(e) => handleModelChange(e.target.value)}
              className="w-full text-sm rounded-lg border border-slate-300 px-3 py-2 text-slate-800 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {modelsForBrand.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
              <option value="Custom Model">Other / Custom</option>
            </select>
          </div>

          <div>
            <label htmlFor="car-year" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-blue-600" />
                Year
              </span>
              <span className="text-xs font-bold text-blue-600">{year} ({2024 - year}y old)</span>
            </label>
            <input
              type="range"
              id="car-year"
              min={2008}
              max={2024}
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer h-2 bg-slate-200 rounded-lg appearance-none mt-2"
            />
            <div className="flex justify-between text-[11px] text-slate-400 mt-1">
              <span>2008</span>
              <span>2016</span>
              <span>2024</span>
            </div>
          </div>
        </div>

        {/* Present Price & Odometer Mileage */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="car-present-price" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5 text-blue-600" />
                Original Showroom Price
              </span>
              <span className="text-xs text-slate-500 font-medium">~${Math.round(presentPrice * 1200).toLocaleString()} USD</span>
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-sm text-slate-400 font-semibold">₹</span>
              <input
                type="number"
                id="car-present-price"
                step="0.1"
                min="0.5"
                max="90.0"
                value={presentPrice}
                onChange={(e) => setPresentPrice(Number(e.target.value))}
                className="w-full text-sm rounded-lg border border-slate-300 pl-7 pr-16 py-2 text-slate-800 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g. 8.5"
                required
              />
              <span className="absolute right-3 top-2.5 text-xs font-semibold text-slate-400">Lakhs</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">1 Lakh INR ≈ $1,200 USD (e.g., 10 Lakhs = $12,000)</p>
          </div>

          <div>
            <label htmlFor="car-kms-driven" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Gauge className="w-3.5 h-3.5 text-blue-600" />
                Kilometers Driven
              </span>
              <span className="text-xs text-slate-500 font-medium">~{Math.round(kmsDriven * 0.621371).toLocaleString()} miles</span>
            </label>
            <div className="relative">
              <input
                type="number"
                id="car-kms-driven"
                step="500"
                min="500"
                max="350000"
                value={kmsDriven}
                onChange={(e) => setKmsDriven(Number(e.target.value))}
                className="w-full text-sm rounded-lg border border-slate-300 px-3 pr-12 py-2 text-slate-800 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
              <span className="absolute right-3 top-2.5 text-xs font-semibold text-slate-400">km</span>
            </div>
            <div className="flex gap-1.5 mt-1.5">
              {[20000, 45000, 80000, 120000].map((presetKm) => (
                <button
                  key={presetKm}
                  type="button"
                  onClick={() => setKmsDriven(presetKm)}
                  className={`text-[10px] px-2 py-0.5 rounded-sm font-medium border transition-colors ${
                    kmsDriven === presetKm ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {(presetKm / 1000).toFixed(0)}k km
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Fuel Type & Transmission */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <Fuel className="w-3.5 h-3.5 text-blue-600" />
              Fuel Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['Petrol', 'Diesel', 'CNG'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFuelType(type)}
                  className={`text-xs py-2 px-3 rounded-lg font-medium border text-center transition-all cursor-pointer ${
                    fuelType === type
                      ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                      : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <Cog className="w-3.5 h-3.5 text-blue-600" />
              Transmission
            </label>
            <div className="grid grid-cols-2 gap-2">
              {['Manual', 'Automatic'].map((trans) => (
                <button
                  key={trans}
                  type="button"
                  onClick={() => setTransmission(trans)}
                  className={`text-xs py-2 px-3 rounded-lg font-medium border text-center transition-all cursor-pointer ${
                    transmission === trans
                      ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                      : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {trans}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Seller Type & Owners */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <UserCheck className="w-3.5 h-3.5 text-blue-600" />
              Seller Type
            </label>
            <div className="grid grid-cols-2 gap-2">
              {['Dealer', 'Individual'].map((seller) => (
                <button
                  key={seller}
                  type="button"
                  onClick={() => setSellerType(seller)}
                  className={`text-xs py-2 px-3 rounded-lg font-medium border text-center transition-all cursor-pointer ${
                    sellerType === seller
                      ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                      : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {seller}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label htmlFor="car-owner" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
              <UserCheck className="w-3.5 h-3.5 text-blue-600" />
              Previous Owners
            </label>
            <select
              id="car-owner"
              value={owner}
              onChange={(e) => setOwner(Number(e.target.value))}
              className="w-full text-sm rounded-lg border border-slate-300 px-3 py-2 text-slate-800 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={0}>0 (First Owner / Single Handed)</option>
              <option value={1}>1 Prior Owner</option>
              <option value={2}>2 Prior Owners</option>
              <option value={3}>3+ Prior Owners</option>
            </select>
          </div>
        </div>

        {/* Algorithm Switcher */}
        <div className="pt-2 border-t border-slate-100">
          <label htmlFor="algorithm-selector" className="block text-xs font-semibold text-slate-700 mb-1.5 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              Valuation Method
            </span>
            <span className="text-[11px] text-slate-400">Multi-method pricing comparison</span>
          </label>
          <select
            id="algorithm-selector"
            value={selectedAlgorithm}
            onChange={(e) => onAlgorithmChange(e.target.value)}
            className="w-full text-xs font-medium rounded-lg border border-slate-300 px-3 py-2 text-slate-800 bg-slate-50 focus:bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="Random Forest Regression">Multi-Factor Ensemble (Optimal: 97.2% Accuracy)</option>
            <option value="Decision Tree Regression">Decision Tree Breakdown (95.3% Accuracy)</option>
            <option value="Linear Regression">Market Trend Baseline (89.7% Accuracy)</option>
          </select>
        </div>

        <button
          type="submit"
          id="predict-submit-button"
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl text-sm transition-all shadow-sm hover:shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span>Calculating Market Valuation...</span>
            </>
          ) : (
            <>
              <span>Calculate Valuation &amp; Market Insights</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
