import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Table, TableHead, TableRow, TableCell,
  TableBody, Chip, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, Alert, CircularProgress, LinearProgress, Tab, Tabs
} from '@mui/material';
import {
  LocalShipping as TruckIcon,
  ShoppingBag as PoIcon,
  CheckCircle as CheckIcon,
  Add as AddIcon,
  Business as SupplierIcon
} from '@mui/icons-material';
import {
  getPurchases, getSuppliers, getShipments, createPurchaseOrder,
  receivePurchaseOrder, getProducts, addSupplier
} from '../api/stockApi';

export default function Purchases() {
  const [tab, setTab] = useState(0);
  const [pos, setPos] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [shipments, setShipments] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openPoDialog, setOpenPoDialog] = useState(false);
  const [openSupDialog, setOpenSupDialog] = useState(false);
  const [alertMsg, setAlertMsg] = useState(null);

  // Form states
  const [selectedSupplier, setSelectedSupplier] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [orderQty, setOrderQty] = useState(25);
  const [orderCost, setOrderCost] = useState('');
  const [poNotes, setPoNotes] = useState('Standard stock replenishment');

  const [newSup, setNewSup] = useState({
    name: '', contact_person: '', email: '', phone: '', address: '', lead_time_days: 3, rating: 4.8
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [poRes, supRes, shipRes, prodRes] = await Promise.all([
        getPurchases(), getSuppliers(), getShipments(), getProducts()
      ]);
      setPos(poRes.data);
      setSuppliers(supRes.data);
      setShipments(shipRes.data);
      setProducts(prodRes.data);
      if (supRes.data.length > 0 && !selectedSupplier) setSelectedSupplier(supRes.data[0].id);
      if (prodRes.data.length > 0 && !selectedProduct) {
        setSelectedProduct(prodRes.data[0].id);
        setOrderCost(prodRes.data[0].cost_price || 1500);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleProductChange = (pid) => {
    setSelectedProduct(pid);
    const p = products.find(x => x.id === pid);
    if (p) setOrderCost(p.cost_price || Math.round(p.price * 0.65));
  };

  const handleCreatePo = async () => {
    try {
      await createPurchaseOrder({
        supplier_id: selectedSupplier,
        items: [{
          product_id: selectedProduct,
          quantity_ordered: parseInt(orderQty),
          unit_cost: parseFloat(orderCost)
        }],
        notes: poNotes
      });
      setOpenPoDialog(false);
      setAlertMsg('Purchase Order & Cargo Shipment registered successfully!');
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleReceive = async (poId) => {
    try {
      await receivePurchaseOrder(poId);
      setAlertMsg(`PO #${poId} received: Inventory updated & intake audit logged!`);
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddSupplier = async () => {
    try {
      await addSupplier(newSup);
      setOpenSupDialog(false);
      setAlertMsg(`Supplier "${newSup.name}" enrolled successfully!`);
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
          <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>Procurement & Wholesaler Management</Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
            Automated Reorders, Wholesaler Purchase Orders & Large Shipment Tracking
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1.5 }}>
          <Button variant="outlined" startIcon={<SupplierIcon />} onClick={() => setOpenSupDialog(true)} sx={{ borderColor: 'rgba(108,99,255,0.5)', color: '#A5B4FC' }}>
            + Add Wholesaler
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenPoDialog(true)} sx={{ background: 'linear-gradient(135deg, #6C63FF, #FF6584)' }}>
            New Purchase Order
          </Button>
        </Box>
      </Box>

      {alertMsg && <Alert severity="success" sx={{ mb: 3, background: 'rgba(16,185,129,0.15)', border: '1px solid #10B981', color: '#6EE7B7' }} onClose={() => setAlertMsg(null)}>{alertMsg}</Alert>}

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3, '& .MuiTab-root': { color: 'rgba(255,255,255,0.6)', fontWeight: 600 }, '& .Mui-selected': { color: '#6C63FF' } }}>
        <Tab icon={<PoIcon />} iconPosition="start" label={`Purchase Orders (${pos.length})`} />
        <Tab icon={<TruckIcon />} iconPosition="start" label={`Cargo Shipments (${shipments.length})`} />
        <Tab icon={<SupplierIcon />} iconPosition="start" label={`Wholesaler Network (${suppliers.length})`} />
      </Tabs>

      {/* Tab 0: Purchase Orders */}
      {tab === 0 && (
        <Card>
          <Table>
            <TableHead sx={{ background: 'rgba(255,255,255,0.03)' }}>
              <TableRow>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>PO Number</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Wholesaler / Supplier</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Items & Qty</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Total Value</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Order Date</TableCell>
                <TableCell sx={{ color: '#A5B4FC', fontWeight: 700 }}>Status</TableCell>
                <TableCell align="right" sx={{ color: '#A5B4FC', fontWeight: 700 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {pos.map(po => (
                <TableRow key={po.id} sx={{ '&:hover': { background: 'rgba(255,255,255,0.02)' } }}>
                  <TableCell sx={{ fontWeight: 700, color: 'white', fontFamily: 'monospace' }}>{po.po_number}</TableCell>
                  <TableCell sx={{ color: 'white' }}>{po.supplier_name}</TableCell>
                  <TableCell sx={{ color: 'rgba(255,255,255,0.8)' }}>
                    {po.items.map(i => `${i.product_name} (${i.quantity_ordered}x)`).join(', ')}
                  </TableCell>
                  <TableCell sx={{ color: '#10B981', fontWeight: 700, fontFamily: 'monospace' }}>
                    ₹{po.total_amount?.toLocaleString('en-IN')}
                  </TableCell>
                  <TableCell sx={{ color: 'rgba(255,255,255,0.6)', fontSize: 13 }}>
                    {po.ordered_date ? new Date(po.ordered_date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={po.status}
                      size="small"
                      sx={{
                        fontWeight: 700,
                        background: po.status === 'RECEIVED' ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)',
                        color: po.status === 'RECEIVED' ? '#10B981' : '#F59E0B',
                        border: `1px solid ${po.status === 'RECEIVED' ? '#10B981' : '#F59E0B'}`
                      }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    {po.status !== 'RECEIVED' ? (
                      <Button
                        size="small"
                        variant="contained"
                        startIcon={<CheckIcon />}
                        onClick={() => handleReceive(po.id)}
                        sx={{ background: '#10B981', color: 'white', fontSize: 12, '&:hover': { background: '#059669' } }}
                      >
                        Receive Cargo
                      </Button>
                    ) : (
                      <Typography variant="caption" sx={{ color: '#10B981', fontWeight: 600 }}>✅ Stock Inwarded</Typography>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {/* Tab 1: Shipments */}
      {tab === 1 && (
        <Grid container spacing={2.5}>
          {shipments.map(s => {
            const isDelivered = s.status === 'DELIVERED';
            return (
              <Grid item xs={12} md={6} key={s.id}>
                <Card sx={{ border: '1px solid rgba(108,99,255,0.3)', p: 1 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TruckIcon sx={{ color: '#6C63FF' }} />
                        <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>{s.tracking_number}</Typography>
                      </Box>
                      <Chip label={s.status} color={isDelivered ? "success" : "warning"} size="small" sx={{ fontWeight: 700 }} />
                    </Box>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 2 }}>Carrier: <strong>{s.carrier}</strong> | Linked to {s.po_number}</Typography>

                    <LinearProgress
                      variant="determinate"
                      value={isDelivered ? 100 : 65}
                      sx={{ height: 8, borderRadius: 4, mb: 2, background: 'rgba(255,255,255,0.1)', '& .MuiLinearProgress-bar': { background: isDelivered ? '#10B981' : 'linear-gradient(90deg, #6C63FF, #FF6584)' } }}
                    />

                    <Grid container spacing={1} sx={{ background: 'rgba(255,255,255,0.02)', p: 1.5, borderRadius: 2 }}>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>Origin</Typography>
                        <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>{s.origin}</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>Destination</Typography>
                        <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>{s.destination}</Typography>
                      </Grid>
                      <Grid item xs={12} sx={{ mt: 1 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>Current Location</Typography>
                        <Typography variant="body2" sx={{ color: '#818CF8', fontWeight: 600 }}>📍 {s.current_location}</Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Tab 2: Suppliers */}
      {tab === 2 && (
        <Grid container spacing={2.5}>
          {suppliers.map(sup => (
            <Grid item xs={12} md={4} key={sup.id}>
              <Card sx={{ height: '100%', border: '1px solid rgba(255,255,255,0.08)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>{sup.name}</Typography>
                    <Chip label={`⭐ ${sup.rating}`} size="small" sx={{ background: 'rgba(245,158,11,0.2)', color: '#F59E0B', fontWeight: 700 }} />
                  </Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1 }}>Contact: {sup.contact_person}</Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1 }}>📧 {sup.email}</Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1 }}>📞 {sup.phone}</Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>📍 {sup.address}</Typography>
                  <Box sx={{ mt: 2, pt: 1.5, borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" sx={{ color: '#A5B4FC' }}>Avg Lead Time: <strong>{sup.lead_time_days} days</strong></Typography>
                    <Typography variant="caption" sx={{ color: '#A5B4FC' }}>Terms: <strong>{sup.payment_terms}</strong></Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dialog: Create PO */}
      <Dialog open={openPoDialog} onClose={() => setOpenPoDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { background: '#12122A', border: '1px solid #6C63FF' } }}>
        <DialogTitle sx={{ color: 'white', fontWeight: 700 }}>Create Wholesaler Purchase Order</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField select label="Select Wholesaler / Supplier" value={selectedSupplier} onChange={(e) => setSelectedSupplier(e.target.value)} fullWidth>
            {suppliers.map(s => <MenuItem key={s.id} value={s.id}>{s.name} (Lead time: {s.lead_time_days}d)</MenuItem>)}
          </TextField>
          <TextField select label="Product to Replenish" value={selectedProduct} onChange={(e) => handleProductChange(e.target.value)} fullWidth>
            {products.map(p => <MenuItem key={p.id} value={p.id}>{p.sku}: {p.name} (Stock: {p.quantity}, ROP: {p.reorder_point})</MenuItem>)}
          </TextField>
          <TextField label="Order Quantity" type="number" value={orderQty} onChange={(e) => setOrderQty(e.target.value)} fullWidth />
          <TextField label="Negotiated Unit Cost (₹)" type="number" value={orderCost} onChange={(e) => setOrderCost(e.target.value)} fullWidth />
          <TextField label="Purchase Notes / Instructions" multiline rows={2} value={poNotes} onChange={(e) => setPoNotes(e.target.value)} fullWidth />
          <Box sx={{ p: 2, background: 'rgba(108,99,255,0.1)', borderRadius: 2 }}>
            <Typography variant="body2" sx={{ color: 'white', fontWeight: 700 }}>
              Estimated PO Total: ₹{((parseInt(orderQty) || 0) * (parseFloat(orderCost) || 0)).toLocaleString('en-IN')}
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
              * Automatically provisions an active cargo shipment with tracking.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenPoDialog(false)} sx={{ color: 'rgba(255,255,255,0.6)' }}>Cancel</Button>
          <Button onClick={handleCreatePo} variant="contained" sx={{ background: '#6C63FF' }}>Submit Purchase Order</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog: Add Supplier */}
      <Dialog open={openSupDialog} onClose={() => setOpenSupDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { background: '#12122A', border: '1px solid #6C63FF' } }}>
        <DialogTitle sx={{ color: 'white', fontWeight: 700 }}>Enroll New Wholesaler</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
          <TextField label="Company Name" value={newSup.name} onChange={e => setNewSup({...newSup, name: e.target.value})} fullWidth />
          <TextField label="Contact Person" value={newSup.contact_person} onChange={e => setNewSup({...newSup, contact_person: e.target.value})} fullWidth />
          <TextField label="Email" value={newSup.email} onChange={e => setNewSup({...newSup, email: e.target.value})} fullWidth />
          <TextField label="Phone" value={newSup.phone} onChange={e => setNewSup({...newSup, phone: e.target.value})} fullWidth />
          <TextField label="Physical Yard / Hub Address" value={newSup.address} onChange={e => setNewSup({...newSup, address: e.target.value})} fullWidth />
          <TextField label="Lead Time (Days)" type="number" value={newSup.lead_time_days} onChange={e => setNewSup({...newSup, lead_time_days: parseInt(e.target.value)})} fullWidth />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenSupDialog(false)} sx={{ color: 'rgba(255,255,255,0.6)' }}>Cancel</Button>
          <Button onClick={handleAddSupplier} variant="contained" sx={{ background: '#6C63FF' }}>Save Wholesaler</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
