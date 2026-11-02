import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  ShoppingCart, CheckCircle2, Lock, FileText, Video, Image as ImageIcon, FileCode2, Database, Presentation, Package,
  ArrowRight, AlertTriangle, ShieldCheck,
} from 'lucide-react';
import { api } from '../utils/api';
import { useAsync } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import { PageHeader, ErrorState, LoadingBlock, Badge, Card, Modal, Spinner, useToast, Alert } from '../components/ui';
import { money, bytes } from '../utils/format';

const CATEGORY = {
  SOURCE_CODE: { label: 'Source code', icon: FileCode2 },
  DOCUMENTATION: { label: 'Documentation', icon: FileText },
  PRESENTATION: { label: 'Presentation', icon: Presentation },
  DATABASE: { label: 'Database files', icon: Database },
  VIDEO: { label: 'Demo video', icon: Video },
  SCREENSHOT: { label: 'Screenshots', icon: ImageIcon },
  OTHER: { label: 'Other resources', icon: Package },
};

export default function MarketplaceProject() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const { notify } = useToast();
  const project = useAsync(() => api.getMarketplaceProject(id), [id]);
  const payment = useAsync(() => api.getPaymentConfig(), []);
  const [confirm, setConfirm] = useState(false);
  const [buying, setBuying] = useState(false);

  const buy = async () => {
    setBuying(true);
    try {
      const res = await api.purchaseProject(id);
      notify(res.message, { title: 'Purchase complete' });
      setConfirm(false);
      navigate(`/projects/${id}`);
    } catch (e) {
      notify(e.message, { tone: 'error' });
    } finally {
      setBuying(false);
    }
  };

  if (project.error) return <><PageHeader title="Project" breadcrumbs={[{ label: 'Projects', to: '/marketplace' }]} /><ErrorState error={project.error} onRetry={project.reload} /></>;
  if (project.loading || !project.data) return <LoadingBlock />;

  const p = project.data;
  const pay = payment.data || {};
  const videos = (p.previewAssets || []).filter((a) => a.category === 'VIDEO' || (a.mimeType || '').startsWith('video/'));
  const images = (p.previewAssets || []).filter((a) => a.category === 'SCREENSHOT' || (a.mimeType || '').startsWith('image/'));
  const docs = (p.previewAssets || []).filter((a) => !videos.includes(a) && !images.includes(a));
  const techs = (p.technologyStack || '').split(',').map((t) => t.trim()).filter(Boolean);

  return (
    <>
      <PageHeader
        breadcrumbs={[{ label: user?.role === 'USER' ? 'Browse projects' : 'Catalogue', to: '/marketplace' }, { label: p.projectCode }]}
        title={p.projectName}
        description={[p.projectCode, p.domain].filter(Boolean).join(' · ')}
      />

      <div className="layout-split">
        <div className="space-y-6">
          {videos[0] && <PreviewVideo asset={videos[0]} />}

          <Card title="Abstract">
            <p className="text-md" style={{ color: 'var(--text)', whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{p.abstractText || 'No abstract has been added yet.'}</p>
          </Card>

          {p.description && p.description !== p.abstractText && (
            <Card title="Overview">
              <div className="text-base" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, color: 'var(--text-2)' }}>{p.description}</div>
            </Card>
          )}

          {images.length > 0 && (
            <Card title="Screenshots">
              <div className="grid grid-cols-2 gap-3">
                {images.slice(0, 6).map((a) => <PreviewImage key={a.id} asset={a} />)}
              </div>
            </Card>
          )}

          {docs.length > 0 && (
            <Card title="Preview documents" flush>
              <div className="list">
                {docs.map((a) => (
                  <div key={a.id} className="list-item">
                    <FileText size={16} className="text-subtle" />
                    <span className="flex-1 text-sm truncate">{a.name}</span>
                    <span className="text-xs text-subtle">{bytes(a.fileSize)}</span>
                    <OpenPreviewButton asset={a} />
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        <div className="space-y-4 aside-priority" style={{ position: 'sticky', top: 'calc(var(--topbar-height) + 20px)' }}>
          <div className="card">
            {p.owned ? (
              <>
                <Badge tone="success" className="badge-lg"><CheckCircle2 /> You own this project</Badge>
                <p className="text-sm mt-3">Full access to the source code, documentation, database files and demo video.</p>
                <Link to={`/projects/${p.id}`} className="btn btn-primary btn-block btn-lg mt-4">Open deliverables <ArrowRight /></Link>
              </>
            ) : (
              <>
                <div className="text-xs text-muted">{user?.role === 'USER' ? 'Price for your college' : 'College price'}</div>
                <div className="price price-lg mt-1">{money(p.price)}</div>
                {p.canPurchase ? (
                  <>
                    {pay.simulation && <div className="mt-3"><span className="notice-simulated"><AlertTriangle size={12} /> Development payment mode</span></div>}
                    {pay.available === false && <Alert tone="warning">Online payments are not configured yet. Contact your college administrator.</Alert>}
                    <button className="btn btn-primary btn-block btn-lg mt-4" onClick={() => setConfirm(true)} disabled={pay.available === false}>
                      <ShoppingCart /> Buy project
                    </button>
                    <p className="text-xs text-subtle mt-3 flex items-center gap-1"><ShieldCheck size={13} /> Access is granted only after the payment is verified.</p>
                  </>
                ) : (
                  <p className="text-sm mt-3">Students of the college purchase this project from their account.</p>
                )}
              </>
            )}
          </div>

          <div className="card">
            <div className="section-title mb-3">What's included</div>
            <ul className="space-y-2">
              {Object.entries(p.filesByCategory || {}).map(([cat, count]) => {
                const meta = CATEGORY[cat] || CATEGORY.OTHER;
                return (
                  <li key={cat} className="flex items-center gap-3 text-sm">
                    <meta.icon size={15} className="text-subtle" />
                    <span className="flex-1">{meta.label}</span>
                    <span className="text-subtle tabular">{count}</span>
                    {!p.owned && <Lock size={13} className="text-subtle" aria-label="Locked" />}
                  </li>
                );
              })}
              {Object.keys(p.filesByCategory || {}).length === 0 && <li className="text-sm text-subtle">Files are being prepared.</li>}
            </ul>
          </div>

          {techs.length > 0 && (
            <div className="card">
              <div className="section-title mb-3">Technologies</div>
              <div className="flex flex-wrap gap-2">{techs.map((t) => <span key={t} className="tag">{t}</span>)}</div>
            </div>
          )}
        </div>
      </div>

      <Modal
        open={confirm}
        onClose={() => !buying && setConfirm(false)}
        title="Confirm purchase"
        footer={<><button className="btn btn-secondary" onClick={() => setConfirm(false)} disabled={buying}>Cancel</button><button className="btn btn-primary" onClick={buy} disabled={buying}>{buying && <Spinner />} Pay {money(p.price)}</button></>}
      >
        <dl className="kv">
          <dt>Project</dt><dd className="font-medium">{p.projectName}</dd>
          <dt>Code</dt><dd className="font-mono">{p.projectCode}</dd>
          <dt>Amount</dt><dd className="font-medium">{money(p.price)}</dd>
          <dt>Account</dt><dd>{user?.email}</dd>
        </dl>
        {pay.simulation && (
          <Alert tone="warning" title="Simulated payment">
            This server is in development payment mode. No money is charged, and the order is recorded as simulated.
          </Alert>
        )}
      </Modal>
    </>
  );
}

function useObjectUrl(assetId) {
  const [state, setState] = useState({ url: null, error: null });
  useEffect(() => {
    let url;
    let cancelled = false;
    api.viewAsset(assetId)
      .then((res) => { url = res.url; if (!cancelled) setState({ url: res.url, error: null }); })
      .catch((e) => !cancelled && setState({ url: null, error: e }));
    return () => { cancelled = true; if (url) URL.revokeObjectURL(url); };
  }, [assetId]);
  return state;
}

function PreviewVideo({ asset }) {
  const { url, error } = useObjectUrl(asset.id);
  return (
    <div className="media-frame">
      {error ? <span className="text-sm" style={{ color: '#aaa' }}>Preview unavailable</span>
        : url ? <video src={url} controls preload="metadata" controlsList="nodownload" onContextMenu={(e) => e.preventDefault()} />
          : <Spinner large />}
    </div>
  );
}

function PreviewImage({ asset }) {
  const { url } = useObjectUrl(asset.id);
  return (
    <div className="border rounded overflow-hidden" style={{ aspectRatio: '16/10', background: 'var(--surface-2)' }}>
      {url ? <img src={url} alt={asset.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <div className="skeleton h-full" />}
    </div>
  );
}

function OpenPreviewButton({ asset }) {
  const { notify } = useToast();
  const open = async () => {
    try {
      const res = await api.viewAsset(asset.id);
      window.open(res.url, '_blank', 'noopener');
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };
  return <button className="btn btn-ghost btn-sm" onClick={open}>Open</button>;
}
