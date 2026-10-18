import React from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Sales from './pages/Sales';
import Purchases from './pages/Purchases';
import HardwareHub from './pages/HardwareHub';
import Forecast from './pages/Forecast';
import Categories from './pages/Categories';
import StockMovements from './pages/StockMovements';
import Reports from './pages/Reports';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6C63FF' },
    secondary: { main: '#FF6584' },
    background: { default: '#0A0A1A', paper: '#12122A' },
    success: { main: '#10B981' },
    warning: { main: '#F59E0B' },
    error: { main: '#EF4444' },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", sans-serif',
    h4: { fontWeight: 800 },
    h6: { fontWeight: 700 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          background: 'linear-gradient(135deg, rgba(18,18,42,0.95), rgba(30,30,60,0.85))',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(108,99,255,0.22)',
          boxShadow: '0 8px 32px rgba(0,0,0,0.37)'
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 10, textTransform: 'none', fontWeight: 600 }
      }
    }
  }
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/sales" element={<Sales />} />
            <Route path="/purchases" element={<Purchases />} />
            <Route path="/hardware" element={<HardwareHub />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/movements" element={<StockMovements />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
