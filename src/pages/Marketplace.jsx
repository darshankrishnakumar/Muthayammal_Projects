import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  ShoppingBag, 
  Search, 
  Filter, 
  Sparkles, 
  CheckCircle2, 
  CreditCard, 
  QrCode, 
  Building2, 
  GraduationCap, 
  FileText, 
  Layers, 
  ShieldCheck, 
  Star, 
  ArrowRight, 
  X, 
  Check, 
  DownloadCloud, 
  Clock, 
  ExternalLink 
} from 'lucide-react';

const Marketplace = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [catalog, setCatalog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  // Modals state
  const [selectedItem, setSelectedItem] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [checkoutItem, setCheckoutItem] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('CARD');
  const [processingPayment, setProcessingPayment] = useState(false);
  const [completedOrder, setCompletedOrder] = useState(null);

  // Load catalog on mount
  useEffect(() => {
    const fetchCatalog = async () => {
      try {
        const items = await api.getCatalog();
        setCatalog(items || []);
      } catch (err) {
        console.error('Failed to fetch catalog:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCatalog();
  }, []);

  const categories = ['ALL', 'Academic Requirements', 'Datasets', 'Premium Modules', 'Research Services'];

  const filteredItems = catalog.filter(item => {
    const matchesCategory = selectedCategory === 'ALL' || item.category === selectedCategory;
    const matchesQuery = !searchQuery || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.technologyStack && item.technologyStack.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesQuery;
  });

  const handleOpenCheckout = (item) => {
    setSelectedItem(null);
    setCheckoutItem(item);
    setPaymentMethod('CARD');
    setCompletedOrder(null);
    setShowCheckout(true);
  };

  const handleConfirmPurchase = async () => {
    if (!checkoutItem) return;
    setProcessingPayment(true);

    try {
      const order = await api.checkoutOrder({
        itemName: checkoutItem.title,
        itemType: checkoutItem.itemType,
        itemDescription: checkoutItem.description,
        amount: checkoutItem.price,
        paymentMethod: paymentMethod,
        billingName: user?.fullName || 'Academic Researcher',
        billingEmail: user?.email || 'user@academic.com'
      });

      setCompletedOrder(order);
    } catch (err) {
      alert('Checkout error: ' + (err.message || 'Payment processing failed'));
    } finally {
      setProcessingPayment(false);
    }
  };

  return (
    <div className="container" style={{ padding: '32px 20px', maxWidth: '1200px' }}>
      
      {/* Header Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.08))',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-xl)',
        padding: '32px 28px',
        marginBottom: '32px',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px'
      }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600, marginBottom: '12px' }}>
            <Sparkles size={14} /> Academic Marketplace & Catalog
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, margin: '0 0 8px 0', color: 'var(--text-main)' }}>
            Browse Requirements, Datasets & Blueprints
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', margin: 0, maxWidth: '640px' }}>
            Purchase pre-approved IEEE software requirement specifications, peer-reviewed research datasets, and security modules with instant digital fulfillment.
          </p>
        </div>

        <button 
          onClick={() => navigate('/orders')} 
          className="btn btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px' }}
        >
          <ShoppingBag size={18} />
          <span>My Orders & Invoices</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        marginBottom: '28px'
      }}>
        {/* Category Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '0.84rem',
                fontWeight: 600,
                border: '1px solid',
                borderColor: selectedCategory === cat ? 'var(--primary)' : 'var(--border-color)',
                background: selectedCategory === cat ? 'var(--primary)' : 'var(--bg-card)',
                color: selectedCategory === cat ? '#fff' : 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search input */}
        <div style={{ position: 'relative', minWidth: '260px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search catalog, stack, keywords..."
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
      </div>

      {/* Catalog Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
          <p>Loading academic marketplace catalog...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="card text-center" style={{ padding: '60px 20px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-xl)' }}>
          <ShoppingBag size={48} style={{ color: 'var(--text-muted)', margin: '0 auto 16px' }} />
          <h3 style={{ margin: '0 0 8px 0', color: 'var(--text-main)' }}>No catalog items found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Try clearing your search query or selecting a different category filter.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '24px'
        }}>
          {filteredItems.map(item => (
            <div 
              key={item.id} 
              className="card"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-xl)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease'
              }}
            >
              <div>
                {/* Header Badge & Category */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                  <span style={{
                    fontSize: '0.74rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    color: 'var(--primary)',
                    background: 'rgba(99, 102, 241, 0.1)',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}>
                    {item.category}
                  </span>

                  {item.badge && (
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 600,
                      color: '#fbbf24',
                      background: 'rgba(245, 158, 11, 0.12)',
                      padding: '3px 8px',
                      borderRadius: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      <Star size={12} fill="#fbbf24" /> {item.badge}
                    </span>
                  )}
                </div>

                {/* Title */}
                <h3 style={{ fontSize: '1.15rem', fontWeight: 600, margin: '0 0 10px 0', color: 'var(--text-main)', lineHeight: 1.4 }}>
                  {item.title}
                </h3>

                {/* Description */}
                <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '16px' }}>
                  {item.description}
                </p>

                {/* Tech Stack */}
                {item.technologyStack && (
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                      Technology Stack:
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {item.technologyStack.split(',').map((tech, idx) => (
                        <span key={idx} style={{
                          fontSize: '0.75rem',
                          background: 'var(--bg-main)',
                          border: '1px solid var(--border-color)',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          color: 'var(--text-main)'
                        }}>
                          {tech.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Footer Price & Actions */}
              <div style={{
                marginTop: '20px',
                paddingTop: '16px',
                borderTop: '1px solid var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Digital Price</div>
                  <div style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    Rs. {Number(item.price).toFixed(2)}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={() => setSelectedItem(item)}
                    className="btn btn-secondary"
                    style={{ fontSize: '0.82rem', padding: '8px 12px' }}
                  >
                    Specs
                  </button>
                  <button
                    onClick={() => handleOpenCheckout(item)}
                    className="btn btn-primary"
                    style={{ fontSize: '0.82rem', padding: '8px 14px', display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <ShoppingBag size={14} />
                    <span>Purchase</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Specification Details Modal */}
      {selectedItem && (
        <div className="modal-backdrop" style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div className="card" style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-xl)',
            width: '100%',
            maxWidth: '560px',
            padding: '28px',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>
                  {selectedItem.category}
                </span>
                <h3 style={{ margin: '4px 0 0 0', fontSize: '1.25rem', color: 'var(--text-main)' }}>
                  {selectedItem.title}
                </h3>
              </div>
              <button 
                onClick={() => setSelectedItem(null)} 
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
              <div>
                <strong style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Specification Overview:</strong>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginTop: '4px', lineHeight: 1.5 }}>
                  {selectedItem.description}
                </p>
              </div>

              <div>
                <strong style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Deliverable Package:</strong>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginTop: '4px' }}>
                  {selectedItem.deliverable}
                </p>
              </div>

              <div>
                <strong style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Technology Architecture:</strong>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginTop: '4px' }}>
                  {selectedItem.technologyStack}
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button onClick={() => setSelectedItem(null)} className="btn btn-secondary">
                Close
              </button>
              <button onClick={() => handleOpenCheckout(selectedItem)} className="btn btn-primary">
                Proceed to Purchase (Rs. {Number(selectedItem.price).toFixed(2)})
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Checkout Modal */}
      {showCheckout && checkoutItem && (
        <div className="modal-backdrop" style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1100,
          padding: '20px'
        }}>
          <div className="card" style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-xl)',
            width: '100%',
            maxWidth: '540px',
            padding: '32px',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.6)'
          }}>

            {!completedOrder ? (
              <div>
                {/* Checkout Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CreditCard size={20} className="text-primary" />
                    <span>Checkout & Instant License</span>
                  </h3>
                  <button 
                    onClick={() => setShowCheckout(false)} 
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Item Summary Card */}
                <div style={{
                  background: 'var(--bg-main)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  marginBottom: '20px'
                }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase' }}>
                    {checkoutItem.category}
                  </div>
                  <div style={{ fontSize: '0.98rem', fontWeight: 600, color: 'var(--text-main)', margin: '4px 0' }}>
                    {checkoutItem.title}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', paddingTop: '12px', borderTop: '1px dashed var(--border-color)' }}>
                    <span style={{ fontSize: '0.86rem', color: 'var(--text-muted)' }}>Total Amount:</span>
                    <span style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text-main)' }}>
                      Rs. {Number(checkoutItem.price).toFixed(2)}
                    </span>
                  </div>
                </div>

                {/* Payment Method Selector */}
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '10px' }}>
                    Select Payment Method
                  </label>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    {[
                      { id: 'CARD', label: 'Credit / Debit Card', icon: CreditCard },
                      { id: 'UPI', label: 'UPI / QR Code', icon: QrCode },
                      { id: 'NET_BANKING', label: 'Net Banking', icon: Building2 },
                      { id: 'ACADEMIC_CREDIT', label: 'Academic Credits', icon: GraduationCap }
                    ].map(method => (
                      <button
                        key={method.id}
                        type="button"
                        onClick={() => setPaymentMethod(method.id)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          padding: '12px',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid',
                          borderColor: paymentMethod === method.id ? 'var(--primary)' : 'var(--border-color)',
                          background: paymentMethod === method.id ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-main)',
                          color: paymentMethod === method.id ? 'var(--primary)' : 'var(--text-main)',
                          cursor: 'pointer',
                          textAlign: 'left',
                          fontSize: '0.84rem',
                          fontWeight: 600
                        }}
                      >
                        <method.icon size={18} />
                        <span>{method.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Mock Gateway Notice */}
                <div style={{
                  background: 'rgba(16, 185, 129, 0.08)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  borderRadius: 'var(--radius-md)',
                  padding: '10px 14px',
                  fontSize: '0.8rem',
                  color: '#34d399',
                  marginBottom: '24px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <ShieldCheck size={16} />
                  <span>Mock payment gateway active: Instant clearance & invoice generation.</span>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                  <button 
                    onClick={() => setShowCheckout(false)} 
                    className="btn btn-secondary"
                    disabled={processingPayment}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleConfirmPurchase} 
                    className="btn btn-primary"
                    disabled={processingPayment}
                    style={{ padding: '10px 20px', fontWeight: 600 }}
                  >
                    {processingPayment ? 'Processing Transaction...' : `Pay Rs. ${Number(checkoutItem.price).toFixed(2)}`}
                  </button>
                </div>
              </div>
            ) : (
              /* Success Confirmation View */
              <div style={{ textAlign: 'center', padding: '10px 0' }}>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '64px',
                  height: '64px',
                  borderRadius: '50%',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#10b981',
                  marginBottom: '16px'
                }}>
                  <CheckCircle2 size={36} />
                </div>

                <h3 style={{ fontSize: '1.4rem', fontWeight: 700, margin: '0 0 8px 0', color: 'var(--text-main)' }}>
                  Purchase Completed!
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '0 0 20px 0' }}>
                  Your order has been cleared and the digital license has been issued.
                </p>

                <div style={{
                  background: 'var(--bg-main)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  textAlign: 'left',
                  marginBottom: '24px',
                  fontSize: '0.86rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Order Reference:</span>
                    <strong style={{ color: 'var(--text-main)' }}>{completedOrder.orderNumber}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Invoice Number:</span>
                    <strong style={{ color: 'var(--primary)' }}>{completedOrder.invoiceNumber}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Amount Cleared:</span>
                    <strong style={{ color: '#10b981' }}>Rs. {Number(completedOrder.amount).toFixed(2)}</strong>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                  <button 
                    onClick={() => setShowCheckout(false)} 
                    className="btn btn-secondary"
                  >
                    Continue Browsing
                  </button>
                  <button 
                    onClick={() => {
                      setShowCheckout(false);
                      navigate('/orders');
                    }} 
                    className="btn btn-primary"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <span>View Invoices & Orders</span>
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
};

export default Marketplace;
