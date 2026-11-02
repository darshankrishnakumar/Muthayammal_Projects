import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Receipt, Search, Printer, AlertTriangle, IndianRupee, CheckCircle2, Clock } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import { PageHeader, EmptyState, ErrorState, SkeletonRows, StatusBadge, Modal, LoadingBlock, StatCard, Segmented } from '../components/ui';
import { money, dateTime, titleCase } from '../utils/format';

export default function Orders() {
  const { user } = useAuth();
  const { data, loading, error, reload } = useAsync(() => api.getOrders(), []);
  const payment = useAsync(() => api.getPaymentConfig(), []);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('ALL');
  const [invoiceId, setInvoiceId] = useState(null);
  const isStudent = user?.role === 'USER';

  const all = data || [];
  const rows = all
    .filter((o) => filter === 'ALL' || o.paymentStatus === filter)
    .filter((o) => {
      const q = search.trim().toLowerCase();
      return !q || o.orderNumber.toLowerCase().includes(q) || o.itemName.toLowerCase().includes(q) || (o.user?.fullName || '').toLowerCase().includes(q);
    });
  const completed = all.filter((o) => o.paymentStatus === 'COMPLETED');
  const verified = completed.filter((o) => !o.simulatedPayment).reduce((a, o) => a + Number(o.amount || 0), 0);

  return (
    <>
      <PageHeader
        title={isStudent ? 'Orders' : 'Orders & payments'}
        description={isStudent ? 'Purchases, advances and final payments, with invoices.' : user?.role === 'ADMIN' ? `Payments made by students of ${user?.college?.name || 'your college'}.` : 'Every order across colleges. Only gateway-verified payments count as revenue.'}
      />

      {payment.data?.simulation && (
        <div className="alert alert-warning"><AlertTriangle aria-hidden="true" /><div>Payment simulation is enabled on this server. Simulated orders are labelled and grant access, but no money is collected.</div></div>
      )}

      {!isStudent && (
        <div className="stat-grid mb-6">
          <StatCard label="Orders" value={all.length} icon={Receipt} loading={loading} index={0} />
          <StatCard label="Completed" value={completed.length} icon={CheckCircle2} tone="success" loading={loading} index={1} />
          <StatCard label="Pending or failed" value={all.length - completed.length} icon={Clock} loading={loading} index={2} />
          <StatCard label="Verified revenue" value={verified} format={money} icon={IndianRupee} loading={loading} index={3} hint="Excludes simulated payments" />
        </div>
      )}

      <div className="toolbar">
        <div className="input-with-icon grow" style={{ maxWidth: 420 }}>
          <Search aria-hidden="true" />
          <input className="input" placeholder={isStudent ? 'Search orders' : 'Search by order, item or student'} value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <Segmented value={filter} onChange={setFilter} options={[
          { value: 'ALL', label: 'All' }, { value: 'COMPLETED', label: 'Paid' }, { value: 'PENDING', label: 'Pending' }, { value: 'FAILED', label: 'Failed' },
        ]} />
      </div>

      {error ? <ErrorState error={error} onRetry={reload} /> : (
        <div className="card card-flush">
          {loading && !data ? <div className="p-4"><SkeletonRows rows={6} /></div> : rows.length === 0 ? (
            <EmptyState icon={Receipt} title={all.length ? 'No orders match' : 'No orders yet'}
              text={all.length ? 'Try another filter.' : isStudent ? 'Your purchases and payments will appear here.' : 'Orders appear as students buy projects and pay for custom development.'}
              action={!all.length && isStudent && <Link to="/marketplace" className="btn btn-primary">Browse projects</Link>} />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Order</th><th>Item</th>{!isStudent && <th>Student</th>}<th>Type</th><th className="cell-num">Amount</th><th>Payment</th><th>Date</th><th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((o) => (
                    <tr key={o.id}>
                      <td className="font-mono text-sm">{o.orderNumber}</td>
                      <td style={{ maxWidth: 320 }}><div className="truncate font-medium">{o.itemName}</div></td>
                      {!isStudent && <td className="cell-muted">{o.user?.fullName}<div className="text-xs text-subtle">{o.user?.college?.name}</div></td>}
                      <td className="cell-muted text-sm">{titleCase(o.paymentType || 'FULL')}</td>
                      <td className="cell-num font-medium">{money(o.amount, o.currency || 'INR')}</td>
                      <td>
                        <div className="flex items-center gap-2">
                          <StatusBadge status={o.paymentStatus} label={o.paymentStatus === 'COMPLETED' ? 'Paid' : undefined} />
                          {o.simulatedPayment && <span className="notice-simulated">Simulated</span>}
                        </div>
                      </td>
                      <td className="cell-muted text-sm">{dateTime(o.createdAt)}</td>
                      <td><button className="btn btn-ghost btn-sm" onClick={() => setInvoiceId(o.id)}>Invoice</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <InvoiceModal orderId={invoiceId} onClose={() => setInvoiceId(null)} />
    </>
  );
}

function InvoiceModal({ orderId, onClose }) {
  const inv = useAsync(() => (orderId ? api.getInvoice(orderId) : Promise.resolve(null)), [orderId]);
  const i = inv.data;
  return (
    <Modal
      open={!!orderId}
      onClose={onClose}
      size="lg"
      title={i ? `Invoice ${i.invoiceNumber}` : 'Invoice'}
      description={i ? `Order ${i.orderNumber} · ${dateTime(i.createdAt)}` : undefined}
      footer={<><button className="btn btn-secondary" onClick={onClose}>Close</button><button className="btn btn-primary" onClick={() => window.print()} disabled={!i}><Printer /> Print</button></>}
    >
      {inv.loading || !i ? (inv.error ? <p className="text-danger text-sm">{inv.error.message}</p> : <LoadingBlock />) : (
        <div className="space-y-6">
          {i.simulatedPayment && (
            <div className="alert alert-warning"><AlertTriangle aria-hidden="true" /><div><span className="font-medium">Simulated payment.</span> Recorded by the development payment simulator; no money was collected.</div></div>
          )}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="text-xs text-subtle uppercase mb-1">Billed to</div>
              <div className="font-medium">{i.customerName}</div>
              <div className="text-sm text-muted">{i.customerEmail}</div>
              <div className="text-sm text-muted">{i.organization}</div>
            </div>
            <div>
              <div className="text-xs text-subtle uppercase mb-1">Payment</div>
              <dl className="kv" style={{ gridTemplateColumns: '110px 1fr', gap: '4px 12px' }}>
                <dt>Status</dt><dd><StatusBadge status={i.paymentStatus} label={i.paymentStatus === 'COMPLETED' ? 'Paid' : undefined} /></dd>
                <dt>Provider</dt><dd>{i.paymentProvider || '—'}</dd>
                <dt>Reference</dt><dd className="font-mono text-sm">{i.transactionReference || '—'}</dd>
                <dt>Verified</dt><dd>{i.verifiedAt ? dateTime(i.verifiedAt) : '—'}</dd>
              </dl>
            </div>
          </div>
          <div className="border rounded overflow-hidden">
            <table className="table">
              <thead><tr><th>Item</th><th>Type</th><th className="cell-num">Amount</th></tr></thead>
              <tbody>
                <tr>
                  <td><div className="font-medium">{i.itemName}</div><div className="text-xs text-subtle">{i.itemDescription}</div></td>
                  <td className="cell-muted">{titleCase(i.paymentType || i.itemType)}</td>
                  <td className="cell-num">{money(i.subtotal, i.currency)}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="flex justify-end">
            <dl className="kv" style={{ gridTemplateColumns: '120px 120px' }}>
              <dt>Subtotal</dt><dd className="text-right tabular">{money(i.subtotal, i.currency)}</dd>
              <dt>Tax</dt><dd className="text-right tabular">{money(i.tax, i.currency)}</dd>
              <dt className="font-medium" style={{ color: 'var(--text)' }}>Total</dt><dd className="text-right tabular font-semibold">{money(i.total, i.currency)}</dd>
            </dl>
          </div>
        </div>
      )}
    </Modal>
  );
}
