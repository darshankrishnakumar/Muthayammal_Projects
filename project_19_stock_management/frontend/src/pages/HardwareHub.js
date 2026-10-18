import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, TextField, Chip,
  Alert, CircularProgress, Divider, Avatar
} from '@mui/material';
import {
  QrCodeScanner as ScanIcon,
  Sensors as SensorIcon,
  Scale as ScaleIcon,
  BatteryFull as BatteryIcon,
  CheckCircle as SuccessIcon,
  PlayArrow as ActionIcon,
  FlashOn as TriggerIcon
} from '@mui/icons-material';
import { getHardwareDevices, processHardwareScan, sendScaleTelemetry, getProducts } from '../api/stockApi';

export default function HardwareHub() {
  const [devices, setDevices] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Scanner Simulator
  const [scanCode, setScanCode] = useState('8901001001');
  const [scanAction, setScanAction] = useState('LOOKUP');
  const [scanResult, setScanResult] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);

  // Smart Scale Telemetry
  const [scaleSku, setScaleSku] = useState('SKU-001');
  const [scaleWeight, setScaleWeight] = useState(11.25); // 45 items * 0.25kg = 11.25kg
  const [scaleResult, setScaleResult] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [devRes, prodRes] = await Promise.all([getHardwareDevices(), getProducts()]);
      setDevices(devRes.data);
      setProducts(prodRes.data);
      if (prodRes.data.length > 0) {
        setScanCode(prodRes.data[0].barcode || '8901001001');
        setScaleSku(prodRes.data[0].sku);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const playBeep = () => {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.12);
    } catch (e) {
      // AudioContext fallback
    }
  };

  const handleScan = async (codeToScan = scanCode, actionToPerform = scanAction) => {
    try {
      setScanLoading(true);
      playBeep();
      const res = await processHardwareScan({
        code: codeToScan,
        action: actionToPerform,
        device_id: 'SCANNER-W01',
        quantity: 10
      });
      setScanResult(res.data);
      // Reload products to refresh inventory
      const pRes = await getProducts();
      setProducts(pRes.data);
    } catch (err) {
      setScanResult({
        found: false,
        message: err.response?.data?.message || 'Barcode / RFID scan failed or unregistered'
      });
    } finally {
      setScanLoading(false);
    }
  };

  const handleScaleTest = async () => {
    try {
      const res = await sendScaleTelemetry({
        sku: scaleSku,
        weight_kg: parseFloat(scaleWeight),
        unit_weight_kg: 0.25
      });
      setScaleResult(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}><CircularProgress sx={{ color: '#6C63FF' }} /></Box>;

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 800, color: 'white' }}>IoT & Hardware System Integration</Typography>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)' }}>
          Barcode / RFID Scanners, Smart Scale Weighing Telemetry & Warehouse Sensor Hubs
        </Typography>
      </Box>

      {/* IoT Devices Status Grid */}
      <Typography variant="h6" sx={{ color: '#A5B4FC', fontWeight: 700, mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
        <SensorIcon /> Connected Hardware Devices ({devices.length})
      </Typography>
      <Grid container spacing={2.5} sx={{ mb: 4 }}>
        {devices.map(d => (
          <Grid item xs={12} sm={6} md={3} key={d.id}>
            <Card sx={{ border: '1px solid rgba(108,99,255,0.3)', background: 'linear-gradient(135deg, rgba(18,18,42,0.95), rgba(30,30,60,0.8))' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1.5 }}>
                  <Avatar sx={{ background: 'rgba(108,99,255,0.2)', color: '#6C63FF', width: 44, height: 44 }}>
                    {d.device_type === 'BARCODE_SCANNER' ? <ScanIcon /> : (d.device_type === 'WEIGHT_SCALE' ? <ScaleIcon /> : <SensorIcon />)}
                  </Avatar>
                  <Chip label={d.status} color="success" size="small" sx={{ fontWeight: 700 }} />
                </Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'white', lineHeight: 1.2 }}>{d.device_name}</Typography>
                <Typography variant="caption" sx={{ color: '#818CF8', fontFamily: 'monospace' }}>ID: {d.device_id}</Typography>
                <Divider sx={{ my: 1.5, borderColor: 'rgba(255,255,255,0.08)' }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>📍 {d.location_area}</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#10B981', fontSize: 12 }}>
                    <BatteryIcon sx={{ fontSize: 16 }} /> {d.battery_level}%
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Hardware Interactivity Row */}
      <Grid container spacing={3}>
        {/* Left: Barcode / RFID Hardware Simulator */}
        <Grid item xs={12} md={7}>
          <Card sx={{ border: '1px solid rgba(108,99,255,0.4)', height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                <Avatar sx={{ background: 'linear-gradient(135deg, #6C63FF, #FF6584)', color: 'white' }}><ScanIcon /></Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>Handheld Barcode / RFID Terminal</Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>Simulates physical laser scans and UHF RFID archway tag reads</Typography>
                </Box>
              </Box>

              <Box sx={{ p: 2, background: 'rgba(0,0,0,0.3)', borderRadius: 2, border: '1px dashed rgba(108,99,255,0.4)', mb: 3 }}>
                <Typography variant="caption" sx={{ color: '#A5B4FC', display: 'block', mb: 1, fontWeight: 700 }}>
                  QUICK PRESETS FROM CATALOG (Click to simulate instant scan):
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {products.slice(0, 6).map(p => (
                    <Chip
                      key={p.id}
                      label={`${p.name.slice(0, 18)} (${p.barcode})`}
                      onClick={() => { setScanCode(p.barcode); handleScan(p.barcode, scanAction); }}
                      sx={{ background: 'rgba(108,99,255,0.2)', color: 'white', '&:hover': { background: '#6C63FF' }, cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>

              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Scanned Barcode / RFID Tag"
                    value={scanCode}
                    onChange={e => setScanCode(e.target.value)}
                    fullWidth
                    sx={{ input: { fontFamily: 'monospace', fontWeight: 700 } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    select
                    label="Terminal Action Mode"
                    value={scanAction}
                    onChange={e => setScanAction(e.target.value)}
                    fullWidth
                    SelectProps={{ native: true }}
                  >
                    <option value="LOOKUP">🔍 Product Lookup & Inventory Check</option>
                    <option value="SALE">⚡ Smart POS Checkout (-1 Unit)</option>
                    <option value="INWARD">📥 Inbound Intake (+10 Units)</option>
                  </TextField>
                </Grid>
              </Grid>

              <Button
                variant="contained"
                fullWidth
                size="large"
                startIcon={<TriggerIcon />}
                onClick={() => handleScan()}
                disabled={scanLoading}
                sx={{ background: 'linear-gradient(135deg, #6C63FF, #FF6584)', py: 1.5, fontWeight: 700, fontSize: 16 }}
              >
                {scanLoading ? 'Processing Hardware Intercept...' : 'Trigger Hardware Scan Event'}
              </Button>

              {/* Scan Result Visualizer */}
              {scanResult && (
                <Box sx={{ mt: 3, p: 2.5, borderRadius: 2, border: '1px solid', borderColor: scanResult.found ? '#10B981' : '#EF4444', background: scanResult.found ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <SuccessIcon sx={{ color: scanResult.found ? '#10B981' : '#EF4444' }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'white' }}>{scanResult.message}</Typography>
                  </Box>
                  {scanResult.found && scanResult.product && (
                    <Grid container spacing={1} sx={{ mt: 1, color: 'rgba(255,255,255,0.8)', fontSize: 13 }}>
                      <Grid item xs={4}>SKU: <strong>{scanResult.product.sku}</strong></Grid>
                      <Grid item xs={4}>Live Stock: <strong style={{ color: '#10B981' }}>{scanResult.product.quantity} units</strong></Grid>
                      <Grid item xs={4}>Price: <strong>₹{scanResult.product.price}</strong></Grid>
                      <Grid item xs={6}>Aisle Location: <strong>{scanResult.product.location_aisle}</strong></Grid>
                      <Grid item xs={6}>Status: <strong>{scanResult.product.status}</strong></Grid>
                    </Grid>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right: Smart Scale Telemetry Test */}
        <Grid item xs={12} md={5}>
          <Card sx={{ border: '1px solid rgba(255,255,255,0.1)', height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                <Avatar sx={{ background: 'rgba(16,185,129,0.2)', color: '#10B981' }}><ScaleIcon /></Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'white' }}>IoT Smart Scale Telemetry</Typography>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>Calculates unit count from weight sensors & flags variance</Typography>
                </Box>
              </Box>

              <TextField
                select
                label="Target Shelf SKU"
                value={scaleSku}
                onChange={e => setScaleSku(e.target.value)}
                fullWidth
                SelectProps={{ native: true }}
                sx={{ mb: 2 }}
              >
                {products.map(p => (
                  <option key={p.id} value={p.sku}>{p.sku}: {p.name} (DB Qty: {p.quantity})</option>
                ))}
              </TextField>

              <TextField
                label="Sensor Measured Weight (kg)"
                type="number"
                value={scaleWeight}
                onChange={e => setScaleWeight(e.target.value)}
                fullWidth
                sx={{ mb: 2.5 }}
                helperText="Assuming standard unit weight: 0.25 kg / unit"
              />

              <Button variant="outlined" fullWidth onClick={handleScaleTest} startIcon={<ActionIcon />} sx={{ borderColor: '#10B981', color: '#10B981', py: 1.2, fontWeight: 700 }}>
                Query Smart Scale Telemetry
              </Button>

              {scaleResult && (
                <Box sx={{ mt: 3, p: 2, background: 'rgba(255,255,255,0.03)', borderRadius: 2, border: '1px solid rgba(255,255,255,0.1)' }}>
                  <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>Telemetry Diagnostic:</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.8 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>Database Stored Qty:</Typography>
                    <Typography variant="caption" sx={{ color: 'white', fontWeight: 700 }}>{scaleResult.system_qty} units</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.8 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>Weight Calculated Qty:</Typography>
                    <Typography variant="caption" sx={{ color: 'white', fontWeight: 700 }}>{scaleResult.calculated_qty_from_weight} units</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>Count Discrepancy:</Typography>
                    <Chip
                      label={scaleResult.discrepancy === 0 ? "0 (Perfect Match)" : `${scaleResult.discrepancy > 0 ? '+' : ''}${scaleResult.discrepancy} Variance`}
                      size="small"
                      color={scaleResult.discrepancy === 0 ? "success" : "error"}
                      sx={{ fontWeight: 700 }}
                    />
                  </Box>
                  <Alert severity={scaleResult.status === 'MATCH' ? "success" : "warning"} sx={{ mt: 1 }}>
                    Status: {scaleResult.status} {scaleResult.status !== 'MATCH' && "- Physical stock discrepancy detected on shelf!"}
                  </Alert>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
