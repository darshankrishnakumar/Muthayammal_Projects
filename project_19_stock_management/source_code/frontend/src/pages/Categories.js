import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Button, Card, Grid, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, Alert, CircularProgress, Chip
} from '@mui/material';
import { Add as AddIcon, Category as CatIcon } from '@mui/icons-material';
import { getCategories, addCategory } from '../api/stockApi';

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({ name: '', description: '' });
  const [error, setError] = useState('');

  const fetchCats = async () => {
    try { const res = await getCategories(); setCategories(res.data); }
    catch(e) { setError('Failed to load'); } finally { setLoading(false); }
  };

  useEffect(() => { fetchCats(); }, []);

  const handleAdd = async () => {
    try { await addCategory(form); setDialogOpen(false); setForm({name:'',description:''}); fetchCats(); }
    catch(e) { setError('Failed to add category'); }
  };

  const COLORS = ['#6C63FF','#FF6584','#4CAF50','#FF9800','#00BCD4','#9C27B0'];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CatIcon sx={{ color: '#FF6584' }} />
          <Typography variant="h4" fontWeight={700}>Categories</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}
          sx={{ background: 'linear-gradient(135deg, #FF6584, #FF8E53)', borderRadius: 2 }}>
          Add Category
        </Button>
      </Box>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading ? <CircularProgress sx={{ color: '#6C63FF' }} /> : (
        <Grid container spacing={3}>
          {categories.map((cat, i) => (
            <Grid item xs={12} sm={6} md={4} key={cat.id}>
              <Card sx={{ borderTop: `3px solid ${COLORS[i % COLORS.length]}`, p: 0.5 }}>
                <Box sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="h6" fontWeight={700}>{cat.name}</Typography>
                    <Chip label={`ID: ${cat.id}`} size="small" sx={{ background: `${COLORS[i % COLORS.length]}22`, color: COLORS[i % COLORS.length] }} />
                  </Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)' }}>{cat.description || 'No description'}</Typography>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { background: '#12122A', border: '1px solid rgba(255,101,132,0.3)', borderRadius: 3 } }}>
        <DialogTitle fontWeight={700}>Add Category</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField label="Category Name" value={form.name} onChange={e => setForm({...form, name: e.target.value})} fullWidth />
            <TextField label="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} fullWidth multiline rows={2} />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAdd} variant="contained" sx={{ background: 'linear-gradient(135deg, #FF6584, #FF8E53)' }}>Add</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
