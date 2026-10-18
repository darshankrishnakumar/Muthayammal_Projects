import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, CircularProgress
} from '@mui/material';
import { SwapVert as MvIcon } from '@mui/icons-material';
import { getMovements } from '../api/stockApi';

export default function StockMovements() {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMovements().then(res => setMovements(res.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <MvIcon sx={{ color: '#00BCD4' }} />
        <Typography variant="h4" fontWeight={700}>Stock Movements</Typography>
      </Box>
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow sx={{ '& th': { fontWeight: 700, color: 'rgba(255,255,255,0.7)' } }}>
                <TableCell>#</TableCell><TableCell>Product</TableCell>
                <TableCell>Type</TableCell><TableCell align="right">Quantity</TableCell>
                <TableCell>Reason</TableCell><TableCell>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow><TableCell colSpan={6} align="center"><CircularProgress sx={{ color: '#6C63FF', my: 2 }} /></TableCell></TableRow>
              ) : movements.map(m => (
                <TableRow key={m.id} sx={{ '&:hover': { background: 'rgba(0,188,212,0.05)' } }}>
                  <TableCell>#{m.id}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{m.product_name}</TableCell>
                  <TableCell>
                    <Chip label={m.movement_type} size="small"
                      color={m.movement_type === 'IN' ? 'success' : 'error'} />
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, color: m.movement_type === 'IN' ? '#4CAF50' : '#f44336' }}>
                    {m.movement_type === 'IN' ? '+' : '-'}{m.quantity}
                  </TableCell>
                  <TableCell sx={{ color: 'rgba(255,255,255,0.6)' }}>{m.reason}</TableCell>
                  <TableCell>{m.created_at ? new Date(m.created_at).toLocaleString() : '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
}
