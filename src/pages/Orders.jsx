import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  FileText, 
  ShoppingBag, 
  Search, 
  Printer, 
  Download, 
  CheckCircle2, 
  Clock, 
  X, 
  ExternalLink, 
  ShieldCheck, 
  QrCode, 
  Building2, 
  Calendar, 
  Hash, 
  ArrowLeft,
  Sparkles,
  CreditCard
} from 'lucide-react';

const Orders = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [invoiceLoading, setInvoiceLoading] = useState(false);

  const invoicePrintRef = useRef(null);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await api.getMyOrders();
      setOrders(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleViewInvoice = async (orderId) => {
    setInvoiceLoading(true);
    try {
      const invoiceData = await api.getInvoice(orderId);
      setSelectedInvoice(invoiceData);
    } catch (err) {
      alert('Failed to load invoice: ' + (err.message || 'Error occurred'));
    } finally {
      setInvoiceLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const filteredOrders = orders.filter(o => {
    const q = searchQuery.toLowerCase();
    return (
      (o.orderNumber && o.orderNumber.toLowerCase().includes(q)) ||
      (o.invoiceNumber && o.invoiceNumber.toLowerCase().includes(q)) ||
      (o.itemName && o.itemName.toLowerCase().includes(q)) ||
      (o.paymentMethod && o.paymentMethod.toLowerCase().includes(q))
    );
  });

  return (
    <div className="container" style={{ padding: '32px 20px', maxWidth: '1200px' }}>
      
      {/* Header */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px',
        marginBottom: '32px'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <button 
              onClick={() => navigate('/marketplace')} 
              style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.86rem' }}
            >
              <ArrowLeft size={16} /> Back to Marketplace
            </button>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: '0 0 6px 0', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShoppingBag className="text-primary" />
            <span>My Orders & Invoices</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: 0 }}>
            Review purchase history, verify digital licenses, and download academic invoices.
          </p>
        </div>

        <button 
          onClick={() => navigate('/marketplace')} 
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px' }}
        >
          <Sparkles size={16} />
          <span>Browse Catalog</span>
        </button>
      </div>

      {/* Filter / Search Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '24px',
        gap: '16px'
      }}>
        <div style={{ position: 'relative', width: '100%', maxWidth: '360px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search orders, invoices, items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 12px 9px 36px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-main)',
              fontSize: '0.86rem'
            }}
          />
        </div>

        <div style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>
          Total Orders: <strong style={{ color: 'var(--text-main)' }}>{filteredOrders.length}</strong>
        </div>
      </div>

      {/* Orders List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
          <p>Loading purchase records...</p>
        </div>
      ) : filteredOrders.length === 0 ? (
        <div className="card text-center" style={{ padding: '60px 20px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-xl)' }}>
          <FileText size={48} style={{ color: 'var(--text-muted)', margin: '0 auto 16px' }} />
          <h3 style={{ margin: '0 0 8px 0', color: 'var(--text-main)' }}>No purchase orders found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '20px' }}>
            You have not placed any orders yet. Explore our academic store to purchase requirement packages.
          </p>
          <button onClick={() => navigate('/marketplace')} className="btn btn-primary">
            Explore Marketplace
          </button>
        </div>
      ) : (
        <div className="card" style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-xl)',
          overflow: 'hidden',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ background: 'var(--bg-main)', borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  <th style={{ padding: '14px 20px' }}>Order & Invoice</th>
                  <th style={{ padding: '14px 20px' }}>Item Details</th>
                  <th style={{ padding: '14px 20px' }}>Date</th>
                  <th style={{ padding: '14px 20px' }}>Amount</th>
                  <th style={{ padding: '14px 20px' }}>Payment</th>
                  <th style={{ padding: '14px 20px' }}>Status</th>
                  <th style={{ padding: '14px 20px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map(order => (
                  <tr key={order.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background 0.15s ease' }}>
                    
                    {/* Order & Invoice */}
                    <td style={{ padding: '16px 20px' }}>
                      <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{order.orderNumber}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--primary)', marginTop: '2px' }}>{order.invoiceNumber}</div>
                    </td>

                    {/* Item */}
                    <td style={{ padding: '16px 20px', maxWidth: '280px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{order.itemName}</div>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        Type: {order.itemType}
                      </div>
                    </td>

                    {/* Date */}
                    <td style={{ padding: '16px 20px', color: 'var(--text-muted)', fontSize: '0.84rem', whiteSpace: 'nowrap' }}>
                      {new Date(order.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                    </td>

                    {/* Amount */}
                    <td style={{ padding: '16px 20px', fontWeight: 700, color: 'var(--text-main)', whiteSpace: 'nowrap' }}>
                      Rs. {Number(order.amount).toFixed(2)}
                    </td>

                    {/* Payment Method */}
                    <td style={{ padding: '16px 20px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        fontSize: '0.78rem',
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: 'var(--bg-main)',
                        border: '1px solid var(--border-color)',
                        color: 'var(--text-muted)'
                      }}>
                        {order.paymentMethod}
                      </span>
                    </td>

                    {/* Status */}
                    <td style={{ padding: '16px 20px', whiteSpace: 'nowrap' }}>
                      <span style={{
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        padding: '4px 10px',
                        borderRadius: '12px',
                        background: 'rgba(16, 185, 129, 0.12)',
                        color: '#10b981',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <CheckCircle2 size={12} />
                        <span>{order.status}</span>
                      </span>
                    </td>

                    {/* Action */}
                    <td style={{ padding: '16px 20px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                      <button
                        onClick={() => handleViewInvoice(order.id)}
                        className="btn btn-secondary"
                        style={{ fontSize: '0.82rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                      >
                        <FileText size={14} className="text-primary" />
                        <span>Invoice</span>
                      </button>
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Invoice Modal */}
      {selectedInvoice && (
        <div className="modal-backdrop" style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.8)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1200,
          padding: '20px'
        }}>
          <div className="card" style={{
            background: '#ffffff',
            color: '#1e293b',
            borderRadius: 'var(--radius-xl)',
            width: '100%',
            maxWidth: '680px',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '36px',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
            position: 'relative'
          }} ref={invoicePrintRef}>

            {/* Action Bar (Close & Print) */}
            <div className="no-print" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button 
                  onClick={handlePrint}
                  style={{
                    background: '#4f46e5',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 14px',
                    fontSize: '0.84rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <Printer size={16} />
                  <span>Print Invoice</span>
                </button>
              </div>

              <button 
                onClick={() => setSelectedInvoice(null)} 
                style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Printable Invoice Document */}
            <div>
              
              {/* Invoice Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '28px' }}>
                <div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
                    ACADEMIC INTEGRATION PLATFORM
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>
                    Official Research Deliverables & Requirement License
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '2px' }}>
                    Tax ID: US-ACAD-889021 • ISO 27001 Certified
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#4f46e5' }}>
                    INVOICE
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>
                    {selectedInvoice.invoiceNumber}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '2px' }}>
                    Ref: {selectedInvoice.orderNumber}
                  </div>
                </div>
              </div>

              {/* Bill To & Date Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '20px',
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '16px 20px',
                marginBottom: '24px',
                fontSize: '0.86rem'
              }}>
                <div>
                  <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Billed To:
                  </div>
                  <div style={{ fontWeight: 700, color: '#0f172a' }}>{selectedInvoice.customerName}</div>
                  <div style={{ color: '#475569' }}>{selectedInvoice.customerEmail}</div>
                  <div style={{ color: '#475569' }}>{selectedInvoice.organization}</div>
                  {selectedInvoice.mobileNumber && selectedInvoice.mobileNumber !== 'N/A' && (
                    <div style={{ color: '#64748b', fontSize: '0.8rem' }}>Tel: {selectedInvoice.mobileNumber}</div>
                  )}
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
                    Invoice Details:
                  </div>
                  <div style={{ color: '#475569' }}>
                    Date: <strong>{new Date(selectedInvoice.createdAt).toLocaleDateString()}</strong>
                  </div>
                  <div style={{ color: '#475569' }}>
                    Payment: <strong>{selectedInvoice.paymentMethod}</strong>
                  </div>
                  <div style={{ color: '#16a34a', fontWeight: 700, marginTop: '4px' }}>
                    Status: PAID / COMPLETED
                  </div>
                </div>
              </div>

              {/* Line Items Table */}
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', marginBottom: '24px', fontSize: '0.88rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #cbd5e1', color: '#475569', fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    <th style={{ padding: '10px 0' }}>Description</th>
                    <th style={{ padding: '10px 0', textAlign: 'center' }}>Type</th>
                    <th style={{ padding: '10px 0', textAlign: 'right' }}>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '14px 0' }}>
                      <div style={{ fontWeight: 700, color: '#0f172a' }}>{selectedInvoice.itemName}</div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '2px' }}>
                        {selectedInvoice.itemDescription}
                      </div>
                    </td>
                    <td style={{ padding: '14px 0', textAlign: 'center', color: '#475569', fontSize: '0.82rem' }}>
                      {selectedInvoice.itemType}
                    </td>
                    <td style={{ padding: '14px 0', textAlign: 'right', fontWeight: 700, color: '#0f172a' }}>
                      Rs. {Number(selectedInvoice.subtotal).toFixed(2)}
                    </td>
                  </tr>
                </tbody>
              </table>

              {/* Financial Calculation */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '28px' }}>
                <div style={{ width: '240px', fontSize: '0.88rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', color: '#64748b' }}>
                    <span>Subtotal:</span>
                    <span>Rs. {Number(selectedInvoice.subtotal).toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', color: '#64748b' }}>
                    <span>Academic Tax (0%):</span>
                    <span>Rs. 0.00</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderTop: '2px solid #0f172a', fontWeight: 800, fontSize: '1.1rem', color: '#0f172a' }}>
                    <span>Total Paid:</span>
                    <span style={{ color: '#4f46e5' }}>Rs. {Number(selectedInvoice.total).toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Digital Verification & Stamp */}
              <div style={{
                borderTop: '1px dashed #cbd5e1',
                paddingTop: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.78rem',
                color: '#64748b'
              }}>
                <div>
                  <div style={{ fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ShieldCheck size={16} color="#16a34a" /> Cryptographically Verified Digital Receipt
                  </div>
                  <div style={{ marginTop: '3px', fontFamily: 'monospace', color: '#94a3b8' }}>
                    {selectedInvoice.qrVerificationPayload}
                  </div>
                </div>

                <div style={{ textAlign: 'right', fontStyle: 'italic', color: '#94a3b8' }}>
                  Thank you for supporting open academic research.
                </div>
              </div>

            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default Orders;
