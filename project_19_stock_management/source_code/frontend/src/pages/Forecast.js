import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Table, TableHead, TableRow, TableCell,
  TableBody, Chip, Button, Alert, CircularProgress
} from '@mui/material';
import {
  TrendingUp as TrendIcon,
  Warning as AlertIcon,
  ShoppingCartCheckout as OrderIcon
} from '@mui/icons-material';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { getForecast, getSuppliers, createPurchaseOrder } from '../api/stockApi';

export default function Forecast() {
  const [forecastData, setForecastData] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [poSuccess, setPoSuccess] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [fRes, supRes] = await Promise.all([getForecast(), getSuppliers()]);
      setForecastData(fRes.data);
      setSuppliers(supRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleInstantPO = async (item) => {
    try {
      const supplierId = suppliers[0]?.id || 1;
      await createPurchaseOrder({
        supplier_id: supplierId,
        items: [{
          product_id: item.id,
          quantity_ordered: item.suggested_reorder,
          unit_cost: 1200
        }],
        notes: `Automated ROP replenishment trigger for ${item.name} (Current Stock: ${item.current_stock})`
      });
      setPoSuccess(`Purchase Order automatically generated and dispatched for ${item.name} (${item.suggested_reorder} units)!`);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress sx={{ color: '#6C63FF' }} /></Box>;

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>Demand Forecasting & ROP Optimization</Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
          Predictive Inventory Planning, Lead Time Demand & Wholesaler Auto-Replenishment
        </Typography>
      </Box>

      {poSuccess && (
        <Alert severity="success" sx={{ mb: 3, background: 'rgba(16,185,129,0.15)', border: '1px solid #10B981', color: '#6EE7B7' }} onClose={() => setPoSuccess(null)}>
          {poSuccess}
        </Alert>
      )}

      {/* KPI Cards */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(108,99,255,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Forecast Model</Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#818CF8', mt: 0.5 }}>ARIMA + EMA</Typography>
              <Typography variant="caption" sx={{ color: '#10B981' }}>Confidence: {forecastData?.confidence_score}%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(16,185,129,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Turnover Ratio</Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#34D399', mt: 0.5 }}>{forecastData?.inventory_turnover_ratio}x</Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>Annual Velocity</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(245,158,11,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Items At / Below ROP</Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#FBBF24', mt: 0.5 }}>{forecastData?.reorder_alerts?.length || 0}</Typography>
              <Typography variant="caption" sx={{ color: '#F59E0B' }}>Action Required</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(244,63,94,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Service Level Target</Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, color: '#FB7185', mt: 0.5 }}>{forecastData?.service_level_target}</Typography>
              <Typography variant="caption" sx={{ color: '#10B981' }}>Stockout Risk: Minimal (&lt;1.5%)</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Demand Curve Chart */}
      <Card sx={{ mb: 4, p: 1, border: '1px solid rgba(108,99,255,0.2)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendIcon sx={{ color: '#6C63FF' }} /> 7-Day Demand Projection (Actual vs AI Predicted)
            </Typography>
            <Chip label="High Fidelity Forecast" color="primary" size="small" />
          </Box>

          <Box sx={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecastData?.forecast_series || []} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="actualColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6C63FF" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6C63FF" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="predColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#A855F7" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#A855F7" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="day" stroke="rgba(255,255,255,0.4)" />
                <YAxis stroke="rgba(255,255,255,0.4)" />
                <Tooltip contentStyle={{ background: '#12122A', border: '1px solid #6C63FF', borderRadius: 8 }} />
                <Legend />
                <Area type="monotone" dataKey="actual" name="Actual Sales Demand" stroke="#6C63FF" strokeWidth={3} fillOpacity={1} fill="url(#actualColor)" />
                <Area type="monotone" dataKey="predicted" name="Predicted Demand" stroke="#A855F7" strokeWidth={3} strokeDasharray="5 5" fillOpacity={1} fill="url(#predColor)" />
              </AreaChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>

      {/* Automated ROP Reorder Alerts Table */}
      <Card sx={{ border: '1px solid rgba(245,158,11,0.3)' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', display: 'flex', alignItems: 'center', gap: 1 }}>
                <AlertIcon sx={{ color: '#F59E0B' }} /> Reorder Point (ROP) Alerts & Wholesaler Restock Suggestions
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                Triggered when Current Stock ≤ Lead Time Demand + Safety Stock
              </Typography>
            </Box>
          </Box>

          <Table>
            <TableHead sx={{ background: 'rgba(255,255,255,0.03)' }}>
              <TableRow>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>SKU</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Product Name</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Current Stock</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Reorder Point (ROP)</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Lead Time</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Suggested PO Size</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Urgency</TableCell>
                <TableCell align="right" sx={{ color: '#A5B4FC', fontWeight: 700 }}>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {forecastData?.reorder_alerts?.map(alert => (
                <TableRow key={alert.id} sx={{ '&:hover': { background: 'rgba(255,255,255,0.02)' } }}>
                  <TableCell sx={{ fontWeight: 700, color: 'white', fontFamily: 'monospace' }}>{alert.sku}</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 600 }}>{alert.name}</TableCell>
                  <TableCell sx={{ color: '#EF4444', fontWeight: 700, fontFamily: 'monospace' }}>{alert.current_stock} units</TableCell>
                  <TableCell sx={{ color: '#F59E0B', fontWeight: 700, fontFamily: 'monospace' }}>{alert.reorder_point} units</TableCell>
                  <TableCell sx={{ color: 'rgba(255,255,255,0.7)' }}>{alert.lead_time_days} days</TableCell>
                  <TableCell sx={{ color: '#10B981', fontWeight: 700, fontFamily: 'monospace' }}>+{alert.suggested_reorder} units</TableCell>
                  <TableCell>
                    <Chip
                      label={alert.urgency}
                      size="small"
                      color={alert.urgency === 'CRITICAL' ? 'error' : 'warning'}
                      sx={{ fontWeight: 700 }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<OrderIcon />}
                      onClick={() => handleInstantPO(alert)}
                      sx={{ background: 'linear-gradient(135deg, #6C63FF, #A855F7)', fontSize: 12, fontWeight: 700 }}
                    >
                      Instant Wholesaler PO
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
}
