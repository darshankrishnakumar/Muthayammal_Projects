import React, { useState } from 'react';
import {
  Drawer, List, ListItem, ListItemIcon, ListItemText, ListItemButton,
  AppBar, Toolbar, Typography, Box, IconButton, Avatar, Chip, Divider
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  ShoppingCart as SalesIcon,
  LocalShipping as PurchasesIcon,
  QrCodeScanner as HardwareIcon,
  TrendingUp as ForecastIcon,
  Assessment as ReportsIcon,
  Category as CategoryIcon,
  SwapVert as MovementIcon,
  Menu as MenuIcon,
  Notifications as NotifIcon,
  Storefront as StoreIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const DRAWER_WIDTH = 250;

const NAV_ITEMS = [
  { label: 'Executive Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
  { label: 'Products & Inventory', path: '/products', icon: <InventoryIcon /> },
  { label: 'Sales & POS', path: '/sales', icon: <SalesIcon /> },
  { label: 'Purchases & Wholesalers', path: '/purchases', icon: <PurchasesIcon /> },
  { label: 'Hardware & IoT Hub', path: '/hardware', icon: <HardwareIcon /> },
  { label: 'Demand Forecast & ROP', path: '/forecast', icon: <ForecastIcon /> },
  { label: 'Category Ledgers', path: '/categories', icon: <CategoryIcon /> },
  { label: 'Stock Movements Audit', path: '/movements', icon: <MovementIcon /> },
  { label: 'Reports & CSV Export', path: '/reports', icon: <ReportsIcon /> },
];

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const drawer = (
    <Box sx={{ height: '100%', background: 'linear-gradient(180deg, #0D0D2B 0%, #1A1A40 100%)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box sx={{
          width: 44, height: 44, borderRadius: 2,
          background: 'linear-gradient(135deg, #6C63FF, #FF6584)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(108,99,255,0.4)'
        }}>
          <StoreIcon sx={{ color: 'white', fontSize: 24 }} />
        </Box>
        <Box>
          <Typography variant="h6" sx={{ color: 'white', fontWeight: 800, lineHeight: 1.1, fontSize: 17 }}>
            StockMS Pro
          </Typography>
          <Typography variant="caption" sx={{ color: '#818CF8', fontWeight: 600 }}>
            IoT & Fintech ERP · P19
          </Typography>
        </Box>
      </Box>
      <Divider sx={{ borderColor: 'rgba(108,99,255,0.2)' }} />
      <List sx={{ p: 1.5, flexGrow: 1, overflowY: 'auto' }}>
        {NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.6 }}>
              <ListItemButton
                onClick={() => {
                  navigate(item.path);
                  setMobileOpen(false);
                }}
                sx={{
                  borderRadius: 2,
                  py: 1,
                  background: isActive ? 'linear-gradient(135deg, rgba(108,99,255,0.35), rgba(255,101,132,0.15))' : 'transparent',
                  border: isActive ? '1px solid rgba(108,99,255,0.45)' : '1px solid transparent',
                  '&:hover': { background: 'rgba(108,99,255,0.15)', border: '1px solid rgba(108,99,255,0.3)' },
                  transition: 'all 0.2s ease',
                }}
              >
                <ListItemIcon sx={{ color: isActive ? '#6C63FF' : 'rgba(255,255,255,0.6)', minWidth: 38 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  sx={{ '& .MuiListItemText-primary': { color: isActive ? 'white' : 'rgba(255,255,255,0.7)', fontWeight: isActive ? 700 : 500, fontSize: 13.5 } }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Box sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(0,0,0,0.2)' }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>
          Backend Port: <strong>:5019</strong>
        </Typography>
        <Typography variant="caption" sx={{ color: '#10B981', display: 'flex', alignItems: 'center', gap: 0.5 }}>
          ● REST API Synchronized
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{
        width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
        ml: { sm: `${DRAWER_WIDTH}px` },
        background: 'rgba(10,10,26,0.85)',
        backdropFilter: 'blur(20px)',
        boxShadow: 'none',
        borderBottom: '1px solid rgba(108,99,255,0.15)'
      }}>
        <Toolbar>
          <IconButton color="inherit" edge="start" onClick={() => setMobileOpen(!mobileOpen)} sx={{ mr: 2, display: { sm: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1, fontWeight: 700 }}>
            {NAV_ITEMS.find(n => n.path === location.pathname)?.label || 'Executive Dashboard'}
          </Typography>
          <Chip label="API :5019" color="success" size="small" sx={{ mr: 1.5, fontWeight: 700 }} />
          <IconButton color="inherit"><NotifIcon /></IconButton>
          <Avatar sx={{ ml: 1, background: 'linear-gradient(135deg, #6C63FF, #FF6584)', width: 36, height: 36, fontSize: 13, fontWeight: 700 }}>SMS</Avatar>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}>
        <Drawer variant="temporary" open={mobileOpen} onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ display: { xs: 'block', sm: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH, border: 'none' } }}>
          {drawer}
        </Drawer>
        <Drawer variant="permanent" sx={{ display: { xs: 'none', sm: 'block' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH, border: 'none', boxSizing: 'border-box' } }} open>
          {drawer}
        </Drawer>
      </Box>
      <Box component="main" sx={{
        flexGrow: 1,
        p: 3,
        width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
        mt: 8,
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0A0A1A 0%, #0D0D2B 100%)'
      }}>
        {children}
      </Box>
    </Box>
  );
}
