import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, CircularProgress,
  Avatar, Chip, Button, Alert
} from '@mui/material';
import {
  Inventory as InvIcon,
  Warning as WarningIcon,
  AttachMoney as MoneyIcon,
  LocalShipping as TruckIcon,
  QrCodeScanner as ScanIcon,
  TrendingUp as TrendIcon,
  ShoppingCart as PoIcon
} from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';
import { getDashboard, getProducts } from '../api/stockApi';

const StatCard = ({ title, value, icon, color, subtitle, onClick }) => (
  <Card
    onClick={onClick}
    sx={{
      position: 'relative',
      overflow: 'hidden',
      cursor: onClick ? 'pointer' : 'default',
      transition: 'transform 0.2s',
      '&:hover': onClick ? { transform: 'translateY(-3px)' } : {}
    }}
  >
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)', mb: 1 }}>{title}</Typography>
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>{value}</Typography>
          {subtitle && <Typography variant="caption" sx={{ color }}>{subtitle}</Typography>}
        </Box>
        <Avatar sx={{ background: `${color}22`, color, width: 52, height: 52 }}>{icon}</Avatar>
      </Box>
    </CardContent>
    <Box sx={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 3, background: `linear-gradient(90deg, ${color}66, ${color})` }} />
  </Card>
);

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [lowStock, setLowStock] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [dashRes, productsRes] = await Promise.all([getDashboard(), getProducts()]);
      setStats(dashRes.data);
      setLowStock(productsRes.data.filter(p => p.quantity <= p.reorder_point).slice(0, 5));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
      <CircularProgress sx={{ color: '#6C63FF' }} />
    </Box>
  );

  return (
    <Box>
      {/* Header Banner */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>Enterprise Inventory Command Center</Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
            Real-Time Valuation, IoT Scanners, Automated Reorders & Wholesaler Logistics
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button
            variant="contained"
            startIcon={<ScanIcon />}
            onClick={() => navigate('/hardware')}
            sx={{ background: 'linear-gradient(135deg, #6C63FF, #FF6584)', fontWeight: 700 }}
          >
            Terminal Scan
          </Button>
          <Button
            variant="outlined"
            startIcon={<PoIcon />}
            onClick={() => navigate('/purchases')}
            sx={{ borderColor: 'rgba(108,99,255,0.5)', color: '#A5B4FC', fontWeight: 600 }}
          >
            Wholesaler Orders
          </Button>
        </Box>
      </Box>

      {/* Low Stock Reorder Point Alert Banner */}
      {stats?.low_stock_count > 0 && (
        <Alert
          severity="warning"
          action={
            <Button color="inherit" size="small" onClick={() => navigate('/forecast')} sx={{ fontWeight: 700 }}>
              Optimize Replenishment →
            </Button>
          }
          sx={{ mb: 3, background: 'rgba(245,158,11,0.15)', border: '1px solid #F59E0B', color: '#FCD34D' }}
        >
          <strong>Notice:</strong> {stats.low_stock_count} item(s) have reached or dipped below their automated Reorder Point (ROP).
        </Alert>
      )}

      {/* KPI Cards Grid */}
      <Grid container spacing={2.5} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Catalog SKUs"
            value={stats.total_products}
            icon={<InvIcon />}
            color="#6C63FF"
            subtitle={`${stats.total_categories} Category Ledgers`}
            onClick={() => navigate('/products')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Asset Valuation"
            value={`₹${stats.total_valuation?.toLocaleString('en-IN')}`}
            icon={<MoneyIcon />}
            color="#10B981"
            subtitle={`Potential Margin: ₹${stats.gross_margin_potential?.toLocaleString('en-IN')}`}
            onClick={() => navigate('/reports')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Sales Revenue"
            value={`₹${stats.total_sales?.toLocaleString('en-IN')}`}
            icon={<TrendIcon />}
            color="#00BCD4"
            subtitle="Real-time POS revenue"
            onClick={() => navigate('/sales')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Cargo Shipments"
            value={stats.active_shipments || 1}
            icon={<TruckIcon />}
            color="#FF9800"
            subtitle={`${stats.pending_pos || 1} POs In Transit`}
            onClick={() => navigate('/purchases')}
          />
        </Grid>
      </Grid>

      {/* Middle Row: Sales Trend + Low Stock Watchlist */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%', p: 1 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>Weekly Sales & Outflow Velocity</Typography>
                <Chip label="7-Day Moving Ledger" size="small" sx={{ background: 'rgba(108,99,255,0.2)', color: '#A5B4FC', fontWeight: 600 }} />
              </Box>
              <Box sx={{ height: 280 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stats.weekly_sales}>
                    <defs>
                      <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" />
                    <YAxis stroke="rgba(255,255,255,0.4)" />
                    <Tooltip contentStyle={{ background: '#12122A', border: '1px solid #10B981', borderRadius: 8 }} />
                    <Area type="monotone" dataKey="amount" stroke="#10B981" strokeWidth={3} fillOpacity={1} fill="url(#salesGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                  <WarningIcon sx={{ color: '#FF9800' }} /> ROP Watchlist
                </Typography>
                <Button size="small" onClick={() => navigate('/forecast')} sx={{ color: '#6C63FF', fontWeight: 600 }}>All</Button>
              </Box>
              {lowStock.length === 0 ? (
                <Typography sx={{ color: '#10B981', textAlign: 'center', mt: 4 }}>✅ All SKUs safely above ROP!</Typography>
              ) : (
                lowStock.map(p => (
                  <Box
                    key={p.id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 1.5,
                      mb: 1.5,
                      borderRadius: 2,
                      background: 'rgba(255,152,0,0.08)',
                      border: '1px solid rgba(255,152,0,0.2)'
                    }}
                  >
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: 'white' }}>{p.name}</Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', fontFamily: 'monospace' }}>{p.sku}</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Chip
                        label={`${p.quantity} / ${p.reorder_point} ROP`}
                        size="small"
                        sx={{ background: 'rgba(239,68,68,0.2)', color: '#EF4444', fontWeight: 700 }}
                      />
                    </Box>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
