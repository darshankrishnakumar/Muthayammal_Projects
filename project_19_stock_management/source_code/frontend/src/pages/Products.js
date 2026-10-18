import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Button, Card, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Chip, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  MenuItem, InputAdornment, Alert, CircularProgress
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon,
  Search as SearchIcon, Inventory as InvIcon
} from '@mui/icons-material';
import { getProducts, addProduct, updateProduct, deleteProduct, getCategories } from '../api/stockApi';

const EMPTY_FORM = { name: '', sku: '', price: '', quantity: '', min_stock: '10', category_id: '', description: '' };

export default function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const fetchAll = async () => {
    try {
      const [pRes, cRes] = await Promise.all([getProducts({ search }), getCategories()]);
      setProducts(pRes.data);
      setCategories(cRes.data);
    } catch (e) { setError('Failed to load products'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchAll(); }, [search]);

  const openAdd = () => { setForm(EMPTY_FORM); setEditingId(null); setDialogOpen(true); };
  const openEdit = (p) => { setForm({...p, category_id: p.category_id || ''}); setEditingId(p.id); setDialogOpen(true); };

  const handleSave = async () => {
    try {
      const payload = { ...form, price: parseFloat(form.price), quantity: parseInt(form.quantity), min_stock: parseInt(form.min_stock) };
      if (editingId) await updateProduct(editingId, payload);
      else await addProduct(payload);
      setDialogOpen(false);
      fetchAll();
    } catch (e) { setError('Failed to save product. Check SKU uniqueness.'); }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this product?')) {
      await deleteProduct(id);
      fetchAll();
    }
  };

  const statusColor = (s) => s === 'In Stock' ? 'success' : 'warning';

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <InvIcon sx={{ color: '#6C63FF' }} />
          <Typography variant="h4" fontWeight={700}>Products</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openAdd}
          sx={{ background: 'linear-gradient(135deg, #6C63FF, #FF6584)', borderRadius: 2 }}>
          Add Product
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <TextField fullWidth placeholder="Search products..." value={search} onChange={e => setSearch(e.target.value)}
        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }}
        sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2, background: 'rgba(108,99,255,0.05)' } }} />

      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ '& th': { fontWeight: 700, color: 'rgba(255,255,255,0.7)', borderBottom: '1px solid rgba(108,99,255,0.2)' } }}>
                <TableCell>Product</TableCell><TableCell>SKU</TableCell>
                <TableCell>Category</TableCell><TableCell align="right">Price</TableCell>
                <TableCell align="right">Qty</TableCell><TableCell>Status</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={7} align="center"><CircularProgress sx={{ color: '#6C63FF', my: 3 }} /></TableCell></TableRow>
              ) : products.map((p) => (
                <TableRow key={p.id} sx={{ '&:hover': { background: 'rgba(108,99,255,0.05)' }, '& td': { borderBottom: '1px solid rgba(255,255,255,0.05)' } }}>
                  <TableCell><Typography fontWeight={600}>{p.name}</Typography></TableCell>
                  <TableCell><Typography variant="body2" sx={{ color: '#6C63FF', fontFamily: 'monospace' }}>{p.sku}</Typography></TableCell>
                  <TableCell>{p.category}</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>${p.price?.toFixed(2)}</TableCell>
                  <TableCell align="right">{p.quantity}</TableCell>
                  <TableCell><Chip label={p.status} color={statusColor(p.status)} size="small" /></TableCell>
                  <TableCell align="center">
                    <IconButton onClick={() => openEdit(p)} size="small" sx={{ color: '#6C63FF', mr: 1 }}><EditIcon /></IconButton>
                    <IconButton onClick={() => handleDelete(p.id)} size="small" sx={{ color: '#f44336' }}><DeleteIcon /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { background: '#12122A', border: '1px solid rgba(108,99,255,0.2)', borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>{editingId ? 'Edit Product' : 'Add New Product'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField label="Product Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} fullWidth />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField label="SKU" value={form.sku} onChange={e => setForm({...form, sku: e.target.value})} fullWidth />
              <TextField label="Price ($)" type="number" value={form.price} onChange={e => setForm({...form, price: e.target.value})} fullWidth />
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField label="Quantity" type="number" value={form.quantity} onChange={e => setForm({...form, quantity: e.target.value})} fullWidth />
              <TextField label="Min Stock" type="number" value={form.min_stock} onChange={e => setForm({...form, min_stock: e.target.value})} fullWidth />
            </Box>
            <TextField select label="Category" value={form.category_id} onChange={e => setForm({...form, category_id: e.target.value})} fullWidth>
              {categories.map(c => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
            </TextField>
            <TextField label="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} multiline rows={2} fullWidth />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" sx={{ background: 'linear-gradient(135deg, #6C63FF, #FF6584)' }}>
            {editingId ? 'Update' : 'Add Product'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
