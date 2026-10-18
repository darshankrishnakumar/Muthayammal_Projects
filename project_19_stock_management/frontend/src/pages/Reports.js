import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableHead, TableRow,
  TableCell, TableBody, Chip, TextField, Dialog, DialogTitle, DialogContent,
  DialogActions, Alert, CircularProgress
} from '@mui/material';
import {
  Download as ExportIcon,
  Rule as AuditIcon
} from '@mui/icons-material';
import { getReportsSummary, getExportUrl, getProducts, reconcileAudit } from '../api/stockApi';

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Physical Audit Dialog
  const [auditOpen, setAuditOpen] = useState(false);
  const [auditProductId, setAuditProductId] = useState('');
  const [countedQty, setCountedQty] = useState('');
  const [auditorName, setAuditorName] = useState('Staff Inventory Auditor');
  const [auditSuccess, setAuditSuccess] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sumRes, prodRes] = await Promise.all([getReportsSummary(), getProducts()]);
      setSummary(sumRes.data);
      setProducts(prodRes.data);
      if (prodRes.data.length > 0 && !auditProductId) {
        setAuditProductId(prodRes.data[0].id);
        setCountedQty(prodRes.data[0].quantity);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleDownloadCsv = (type) => {
    const url = getExportUrl(type);
    window.open(url, '_blank');
  };

  const handleReconcile = async () => {
    try {
      const res = await reconcileAudit({
        product_id: auditProductId,
        counted_quantity: parseInt(countedQty),
        auditor: auditorName
      });
      setAuditOpen(false);
      setAuditSuccess(`Audit logged for ${res.data.product_name}. Variance: ${res.data.variance} units (Shrinkage: ₹${res.data.financial_shrinkage})`);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress sx={{ color: '#6C63FF' }} /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>Reports & Inventory Auditing</Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
            Daily/Weekly Sales Ledgers, Stock Shrinkage Audits & Instant CSV Data Exports
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AuditIcon />}
          onClick={() => setAuditOpen(true)}
          sx={{ background: 'linear-gradient(135deg, #10B981, #059669)', fontWeight: 700 }}
        >
          Perform Stock Audit Count
        </Button>
      </Box>

      {auditSuccess && (
        <Alert severity="info" sx={{ mb: 3, background: 'rgba(59,130,246,0.15)', border: '1px solid #3B82F6', color: '#93C5FD' }} onClose={() => setAuditSuccess(null)}>
          {auditSuccess}
        </Alert>
      )}

      {/* Financial Snapshot */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(16,185,129,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Total Sales Revenue</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#10B981', mt: 0.5 }}>
                ₹{summary?.total_revenue?.toLocaleString('en-IN')}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>From {summary?.total_transactions} orders</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(108,99,255,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Warehouse Asset Worth</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#818CF8', mt: 0.5 }}>
                ₹{summary?.total_inventory_valuation?.toLocaleString('en-IN')}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>Real-time inventory value</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(245,158,11,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Total Units Dispatched</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#FBBF24', mt: 0.5 }}>
                {summary?.total_units_sold} units
              </Typography>
              <Typography variant="caption" sx={{ color: '#10B981' }}>Cumulative volume</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ border: '1px solid rgba(236,72,153,0.3)' }}>
            <CardContent>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>Product Lines Count</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#F472B6', mt: 0.5 }}>
                {products.length} SKUs
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>Across 4 major categories</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* One-Click CSV Export Hub */}
      <Card sx={{ mb: 4, p: 1, border: '1px solid rgba(108,99,255,0.4)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <ExportIcon sx={{ color: '#6C63FF' }} /> Data Export & Compliance Reports (Daily / Weekly)
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 3 }}>
            Download complete timestamped CSV reports formatted for management reviews, audits, and accounting spreadsheets.
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, background: 'rgba(255,255,255,0.02)', borderRadius: 2, border: '1px solid rgba(255,255,255,0.08)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'white' }}>📦 Complete Product Catalog</Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 2 }}>
                  SKU, Unit Cost, ROP, Stock Valuation & Barcodes
                </Typography>
                <Button variant="outlined" fullWidth startIcon={<ExportIcon />} onClick={() => handleDownloadCsv('products')} sx={{ borderColor: '#6C63FF', color: '#A5B4FC' }}>
                  Export Products CSV
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, background: 'rgba(255,255,255,0.02)', borderRadius: 2, border: '1px solid rgba(255,255,255,0.08)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'white' }}>💰 Sales & POS Revenue Log</Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 2 }}>
                  Timestamped transaction orders, prices and customer data
                </Typography>
                <Button variant="outlined" fullWidth startIcon={<ExportIcon />} onClick={() => handleDownloadCsv('sales')} sx={{ borderColor: '#10B981', color: '#6EE7B7' }}>
                  Export Sales CSV
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, background: 'rgba(255,255,255,0.02)', borderRadius: 2, border: '1px solid rgba(255,255,255,0.08)' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'white' }}>📋 Warehouse Audit & Movement Trail</Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 2 }}>
                  Full Inward/Outward logs, variance counts & device sources
                </Typography>
                <Button variant="outlined" fullWidth startIcon={<ExportIcon />} onClick={() => handleDownloadCsv('movements')} sx={{ borderColor: '#F59E0B', color: '#FCD34D' }}>
                  Export Movements CSV
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Category Revenue Breakdown Table */}
      <Card sx={{ border: '1px solid rgba(255,255,255,0.08)' }}>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 700, color: 'white', mb: 2 }}>
            Revenue Breakdown by Product Category
          </Typography>
          <Table>
            <TableHead sx={{ background: 'rgba(255,255,255,0.03)' }}>
              <TableRow>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Category Name</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Generated Revenue (₹)</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Contribution Share</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {summary?.sales_by_category && Object.entries(summary.sales_by_category).map(([cat, rev]) => {
                const share = summary.total_revenue > 0 ? ((rev / summary.total_revenue) * 100).toFixed(1) : 0;
                return (
                  <TableRow key={cat}>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>{cat}</TableCell>
                    <TableCell sx={{ color: '#10B981', fontWeight: 700, fontFamily: 'monospace' }}>
                      ₹{rev?.toLocaleString('en-IN')}
                    </TableCell>
                    <TableCell>
                      <Chip label={`${share}%`} size="small" sx={{ background: 'rgba(108,99,255,0.2)', color: '#A5B4FC', fontWeight: 700 }} />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Stock Audit Dialog */}
      <Dialog open={auditOpen} onClose={() => setAuditOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { background: '#12122A', border: '1px solid #10B981' } }}>
        <DialogTitle sx={{ color: 'white', fontWeight: 700 }}>Record Physical Inventory Stock Count</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField select label="Select Item Audited" value={auditProductId} onChange={e => {
            setAuditProductId(e.target.value);
            const p = products.find(x => x.id === e.target.value);
            if (p) setCountedQty(p.quantity);
          }} fullWidth>
            {products.map(p => (
              <option key={p.id} value={p.id}>{p.sku}: {p.name} (System Qty: {p.quantity})</option>
            ))}
          </TextField>
          <TextField label="Physical Counted Quantity" type="number" value={countedQty} onChange={e => setCountedQty(e.target.value)} fullWidth />
          <TextField label="Auditor Staff Name" value={auditorName} onChange={e => setAuditorName(e.target.value)} fullWidth />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setAuditOpen(false)} sx={{ color: 'rgba(255,255,255,0.6)' }}>Cancel</Button>
          <Button onClick={handleReconcile} variant="contained" sx={{ background: '#10B981' }}>Reconcile & Update Ledger</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
