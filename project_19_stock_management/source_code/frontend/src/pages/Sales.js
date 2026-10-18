import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Button, Card, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, Alert, CircularProgress
} from '@mui/material';
import { Add as AddIcon, ShoppingCart as SaleIcon } from '@mui/icons-material';
import { getSales, recordSale, getProducts } from '../api/stockApi';

export default function Sales() {
  const [sales, setSales] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({ product_id: '', quantity_sold: '1', customer_name: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchAll = async () => {
    try {
      const [sRes, pRes] = await Promise.all([getSales(), getProducts()]);
      setSales(sRes.data);
      setProducts(pRes.data);
    } catch(e) {} finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleSale = async () => {
    setError('');
    try {
      await recordSale({ ...form, quantity_sold: parseInt(form.quantity_sold) });
      setSuccess('Sale recorded successfully!');
      setDialogOpen(false);
      setForm({ product_id: '', quantity_sold: '1', customer_name: '' });
      fetchAll();
    } catch(e) { setError(e.response?.data?.error || 'Failed to record sale'); }
  };

  const totalRevenue = sales.reduce((sum, s) => sum + (s.total_amount || 0), 0);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SaleIcon sx={{ color: '#4CAF50' }} />
          <Typography variant="h4" fontWeight={700}>Sales</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}
          sx={{ background: 'linear-gradient(135deg, #4CAF50, #66BB6A)', borderRadius: 2 }}>
          New Sale
        </Button>
      </Box>

      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        {[{ label: 'Total Sales', value: sales.length, color: '#6C63FF' },
          { label: 'Total Revenue', value: `$${totalRevenue.toFixed(2)}`, color: '#4CAF50' }].map(stat => (
          <Card key={stat.label} sx={{ flex: 1, p: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)' }}>{stat.label}</Typography>
            <Typography variant="h5" sx={{ color: stat.color, fontWeight: 700 }}>{stat.value}</Typography>
          </Card>
        ))}
      </Box>

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ '& th': { fontWeight: 700, color: 'rgba(255,255,255,0.7)' } }}>
                <TableCell>#</TableCell><TableCell>Product</TableCell>
                <TableCell>Customer</TableCell><TableCell align="right">Qty</TableCell>
                <TableCell align="right">Unit Price</TableCell><TableCell align="right">Total</TableCell>
                <TableCell>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={7} align="center"><CircularProgress sx={{ color: '#6C63FF', my: 2 }} /></TableCell></TableRow>
              ) : sales.map(s => (
                <TableRow key={s.id} sx={{ '&:hover': { background: 'rgba(76,175,80,0.05)' } }}>
                  <TableCell>#{s.id}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{s.product_name}</TableCell>
                  <TableCell>{s.customer_name}</TableCell>
                  <TableCell align="right">{s.quantity_sold}</TableCell>
                  <TableCell align="right">${s.unit_price?.toFixed(2)}</TableCell>
                  <TableCell align="right" sx={{ color: '#4CAF50', fontWeight: 700 }}>${s.total_amount?.toFixed(2)}</TableCell>
                  <TableCell>{s.sale_date ? new Date(s.sale_date).toLocaleDateString() : '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { background: '#12122A', border: '1px solid rgba(76,175,80,0.3)', borderRadius: 3 } }}>
        <DialogTitle fontWeight={700}>Record New Sale</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField select label="Product" value={form.product_id} onChange={e => setForm({...form, product_id: e.target.value})} fullWidth>
              {products.map(p => <MenuItem key={p.id} value={p.id}>{p.name} (Stock: {p.quantity})</MenuItem>)}
            </TextField>
            <TextField label="Quantity" type="number" value={form.quantity_sold} onChange={e => setForm({...form, quantity_sold: e.target.value})} fullWidth />
            <TextField label="Customer Name" value={form.customer_name} onChange={e => setForm({...form, customer_name: e.target.value})} fullWidth />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSale} variant="contained" sx={{ background: 'linear-gradient(135deg, #4CAF50, #66BB6A)' }}>
            Record Sale
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
