import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Share2, Search, Building2, Check, X, Pencil, Undo2 } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import {
  PageHeader, EmptyState, ErrorState, SkeletonRows, StatusBadge, Badge, Modal, Field, Spinner, Segmented,
  useToast, ConfirmDialog, AsyncButton,
} from '../components/ui';
import { money, date } from '../utils/format';

export default function Allocations() {
  const { notify } = useToast();
  const [params, setParams] = useSearchParams();
  const collegeId = params.get('college') || '';
  const colleges = useAsync(() => api.getColleges(), []);
  const [search, setSearch] = useState('');
  const [view, setView] = useState('ALL');
  const [selected, setSelected] = useState(new Set());
  const [allocateOpen, setAllocateOpen] = useState(false);
  const [revokeOpen, setRevokeOpen] = useState(false);
  const q = useDebounced(search);

  useEffect(() => {
    if (!collegeId && colleges.data?.length) {
      setParams({ college: String(colleges.data.find((c) => c.active)?.id ?? colleges.data[0].id) }, { replace: true });
    }
  }, [collegeId, colleges.data, setParams]);

  const board = useAsync(() => (collegeId ? api.getAllocationBoard(collegeId, q) : Promise.resolve([])), [collegeId, q]);
  useEffect(() => setSelected(new Set()), [collegeId]);

  const rows = useMemo(() => (board.data || []).filter((r) =>
    view === 'ALL' || (view === 'ALLOCATED' ? r.allocated : !r.allocated)), [board.data, view]);
  const college = (colleges.data || []).find((c) => String(c.id) === String(collegeId));
  const allocatedCount = (board.data || []).filter((r) => r.allocated).length;

  const selectedRows = rows.filter((r) => selected.has(r.projectId));
  const toAllocate = selectedRows.filter((r) => !r.allocated && r.catalogStatus !== 'ARCHIVED');
  const toRevoke = selectedRows.filter((r) => r.allocated);

  const toggle = (id) => setSelected((s) => {
    const n = new Set(s);
    if (n.has(id)) n.delete(id);
    else n.add(id);
    return n;
  });
  const allChecked = rows.length > 0 && rows.every((r) => selected.has(r.projectId));

  const revoke = async () => {
    try {
      const res = await api.revokeAllocations(toRevoke.map((r) => r.allocationId));
      notify(`${res.revoked} allocation${res.revoked === 1 ? '' : 's'} revoked. Students who already purchased keep their access.`);
      setRevokeOpen(false);
      setSelected(new Set());
      board.reload();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  if (colleges.error) return <><PageHeader title="Allocations" /><ErrorState error={colleges.error} onRetry={colleges.reload} /></>;

  if (!colleges.loading && (colleges.data || []).length === 0) {
    return (
      <>
        <PageHeader title="Allocations" description="Decide which library projects each college can offer to its students." />
        <div className="card"><EmptyState icon={Building2} title="Register a college first" text="Allocations connect library projects to colleges." action={<Link to="/colleges" className="btn btn-primary">Go to colleges</Link>} /></div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title="Allocations"
        description="Decide which library projects each college can offer to its students. Projects are shared, never copied."
      />

      <div className="card mb-4" style={{ padding: 16 }}>
        <div className="flex items-center gap-4 flex-wrap">
          <Field label="College" className="mb-0" htmlFor="college" >
            <select id="college" className="select" style={{ minWidth: 300 }} value={collegeId} onChange={(e) => setParams({ college: e.target.value })}>
              {(colleges.data || []).map((c) => <option key={c.id} value={c.id}>{c.name}{c.active ? '' : ' (inactive)'}</option>)}
            </select>
          </Field>
          {college && (
            <div className="flex gap-6 text-sm ml-auto flex-wrap">
              <div><div className="text-muted text-xs">Allocated</div><div className="font-semibold tabular text-lg">{allocatedCount}</div></div>
              <div><div className="text-muted text-xs">Students</div><div className="font-semibold tabular text-lg">{college.studentCount}</div></div>
              <div><div className="text-muted text-xs">Orders</div><div className="font-semibold tabular text-lg">{college.orderCount}</div></div>
            </div>
          )}
        </div>
        {college && !college.active && <p className="text-sm text-warning mt-3">This college is inactive. Its students cannot browse or buy until it is reactivated.</p>}
      </div>

      <div className="toolbar">
        <div className="input-with-icon grow">
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search library projects" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <Segmented value={view} onChange={setView} options={[
          { value: 'ALL', label: 'All' }, { value: 'ALLOCATED', label: 'Allocated' }, { value: 'AVAILABLE', label: 'Not allocated' },
        ]} />
      </div>

      {selected.size > 0 && (
        <div className="surface-muted flex items-center gap-2 mb-4 p-3 flex-wrap">
          <span className="text-sm font-medium">{selected.size} selected</span>
          <span className="ml-auto" />
          <button className="btn btn-primary btn-sm" disabled={!toAllocate.length} onClick={() => setAllocateOpen(true)}><Share2 /> Allocate {toAllocate.length || ''}</button>
          <button className="btn btn-danger-ghost btn-sm" disabled={!toRevoke.length} onClick={() => setRevokeOpen(true)}><Undo2 /> Revoke {toRevoke.length || ''}</button>
          <button className="btn btn-ghost btn-sm" onClick={() => setSelected(new Set())}>Clear</button>
        </div>
      )}

      {board.error ? <ErrorState error={board.error} onRetry={board.reload} /> : (
        <div className="card card-flush">
          {board.loading && !board.data ? <div className="p-4"><SkeletonRows rows={8} /></div> : rows.length === 0 ? (
            <EmptyState icon={Share2} title={view === 'ALLOCATED' ? 'Nothing allocated yet' : 'No projects found'} text={view === 'ALLOCATED' ? 'Select projects from the library and allocate them to this college.' : 'Add projects to the library first.'} />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: 36 }}><input type="checkbox" checked={allChecked} onChange={() => setSelected(allChecked ? new Set() : new Set(rows.map((r) => r.projectId)))} aria-label="Select all" /></th>
                    <th>Project</th><th className="hide-lg">Catalogue</th><th>Allocation</th><th className="cell-num hide-lg">List price</th><th className="cell-num">College price</th><th className="hide-lg">Since</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.projectId} className={selected.has(r.projectId) ? 'is-selected' : ''}>
                      <td><input type="checkbox" checked={selected.has(r.projectId)} onChange={() => toggle(r.projectId)} aria-label={`Select ${r.projectName}`} /></td>
                      <td style={{ maxWidth: 360 }}>
                        <div className="project-code">{r.projectCode}</div>
                        <div className="font-medium truncate">{r.projectName}</div>
                        <div className="text-xs text-subtle truncate">{r.domain}</div>
                      </td>
                      <td className="hide-lg"><StatusBadge status={r.catalogStatus} /></td>
                      <td>{r.allocated ? <Badge tone="accent" dot>Allocated</Badge> : r.revoked ? <Badge dot>Revoked</Badge> : <span className="text-subtle text-sm">—</span>}</td>
                      <td className="cell-num cell-muted hide-lg">{r.listPrice != null ? money(r.listPrice) : '—'}</td>
                      <td className="cell-num">{r.allocated ? <PriceCell row={r} onSaved={board.reload} /> : <span className="text-subtle">—</span>}</td>
                      <td className="cell-muted text-sm hide-lg">{r.allocated ? date(r.allocatedAt) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <AllocateDialog
        open={allocateOpen}
        college={college}
        projects={toAllocate}
        onClose={() => setAllocateOpen(false)}
        onDone={() => { setAllocateOpen(false); setSelected(new Set()); board.reload(); colleges.reload(); }}
      />
      <ConfirmDialog
        open={revokeOpen}
        title={`Revoke ${toRevoke.length} allocation${toRevoke.length === 1 ? '' : 's'}?`}
        text={`These projects will disappear from ${college?.name}'s catalogue. Students who already purchased them keep full access.`}
        confirmLabel="Revoke"
        tone="danger"
        onConfirm={revoke}
        onClose={() => setRevokeOpen(false)}
      />
    </>
  );
}

function PriceCell({ row, onSaved }) {
  const { notify } = useToast();
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(row.priceOverride ?? '');

  const save = async () => {
    if (value !== '' && (Number.isNaN(Number(value)) || Number(value) < 0)) {
      notify('Enter a price of 0 or more, or leave empty to use the list price.', { tone: 'error' });
      return;
    }
    try {
      await api.updateAllocation(row.allocationId, { priceOverride: value === '' ? null : Number(value) });
      setEditing(false);
      onSaved();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  if (!editing) {
    return (
      <span className="inline-flex items-center gap-1">
        <span className={row.priceOverride != null ? 'font-medium' : 'cell-muted'}>{row.effectivePrice != null ? money(row.effectivePrice) : '—'}</span>
        <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setEditing(true)} aria-label="Edit college price"><Pencil /></button>
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1">
      <input className="input input-sm" style={{ width: 100 }} value={value} onChange={(e) => setValue(e.target.value)} placeholder="List price" autoFocus
        onKeyDown={(e) => { if (e.key === 'Enter') save(); if (e.key === 'Escape') setEditing(false); }} />
      <AsyncButton className="btn btn-ghost btn-icon btn-sm" onClick={save} aria-label="Save"><Check /></AsyncButton>
      <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setEditing(false)} aria-label="Cancel"><X /></button>
    </span>
  );
}

function AllocateDialog({ open, college, projects, onClose, onDone }) {
  const { notify } = useToast();
  const [price, setPrice] = useState('');
  const [notes, setNotes] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) { setPrice(''); setNotes(''); }
  }, [open]);

  const submit = async () => {
    if (price !== '' && (Number.isNaN(Number(price)) || Number(price) < 0)) {
      notify('Enter a price of 0 or more.', { tone: 'error' });
      return;
    }
    setBusy(true);
    try {
      const res = await api.allocateProjects(college.id, projects.map((p) => p.projectId), price === '' ? null : Number(price), notes || null);
      notify(`${res.created + res.reactivated} project${res.created + res.reactivated === 1 ? '' : 's'} allocated to ${college.name}.`);
      onDone();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    } finally {
      setBusy(false);
    }
  };

  const drafts = projects.filter((p) => p.catalogStatus === 'DRAFT').length;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Allocate to ${college?.name}`}
      description={`${projects.length} project${projects.length === 1 ? '' : 's'} selected`}
      footer={<><button className="btn btn-secondary" onClick={onClose}>Cancel</button><button className="btn btn-primary" onClick={submit} disabled={busy}>{busy && <Spinner />} Allocate</button></>}
    >
      {drafts > 0 && (
        <div className="alert alert-warning"><span className="text-sm">{drafts} of these are drafts. They will be allocated but stay hidden from students until you publish them.</span></div>
      )}
      <div className="border rounded mb-4" style={{ maxHeight: 180, overflowY: 'auto' }}>
        {projects.map((p) => (
          <div key={p.projectId} className="list-item" style={{ padding: '8px 12px' }}>
            <span className="project-code">{p.projectCode}</span>
            <span className="flex-1 text-sm truncate">{p.projectName}</span>
            <span className="text-sm text-muted tabular">{p.listPrice != null ? money(p.listPrice) : 'No price'}</span>
          </div>
        ))}
      </div>
      <Field label="College price (INR)" hint="Optional. Applies to every selected project; leave empty to use each project's list price.">
        <input className="input" inputMode="decimal" value={price} onChange={(e) => setPrice(e.target.value)} />
      </Field>
      <Field label="Notes" hint="Internal; visible to the platform owner only">
        <textarea className="textarea" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </Field>
    </Modal>
  );
}
