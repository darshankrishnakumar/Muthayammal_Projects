import axios from 'axios';

export const BASE_URL = 'http://localhost:5019/api';
const api = axios.create({ baseURL: BASE_URL });

// Dashboard & Health
export const getHealth = () => api.get('/health');
export const getDashboard = () => api.get('/dashboard');

// Products CRUD
export const getProducts = (params) => api.get('/products', { params });
export const getProduct = (id) => api.get(`/products/${id}`);
export const addProduct = (data) => api.post('/products', data);
export const updateProduct = (id, data) => api.put(`/products/${id}`, data);
export const deleteProduct = (id) => api.delete(`/products/${id}`);

// Categories
export const getCategories = () => api.get('/categories');
export const addCategory = (data) => api.post('/categories', data);

// Sales & POS
export const getSales = (params) => api.get('/sales', { params });
export const recordSale = (data) => api.post('/sales', data);

// Stock Movements & Audit
export const getMovements = (params) => api.get('/movements', { params });
export const reconcileAudit = (data) => api.post('/audit/reconcile', data);

// Procurement & Suppliers
export const getSuppliers = () => api.get('/suppliers');
export const addSupplier = (data) => api.post('/suppliers', data);
export const getPurchases = () => api.get('/purchases');
export const createPurchaseOrder = (data) => api.post('/purchases', data);
export const receivePurchaseOrder = (id) => api.put(`/purchases/${id}/receive`);

// Large Shipments
export const getShipments = () => api.get('/shipments');
export const updateShipmentStatus = (id, data) => api.put(`/shipments/${id}/status`, data);

// Hardware & IoT Devices
export const getHardwareDevices = () => api.get('/hardware/devices');
export const processHardwareScan = (data) => api.post('/hardware/scan', data);
export const sendScaleTelemetry = (data) => api.post('/hardware/telemetry', data);

// Demand Forecasting
export const getForecast = () => api.get('/forecast');

// Reports & Export
export const getReportsSummary = () => api.get('/reports/summary');
export const getExportUrl = (type) => `${BASE_URL}/reports/export?type=${type}`;

// Database Seeding
export const seedData = () => api.post('/seed');

export default api;
