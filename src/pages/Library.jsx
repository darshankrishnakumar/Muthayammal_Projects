import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  Plus, Download, Search, Library as LibraryIcon, Video, FileCode2, Upload, FolderOpen, Pencil, Eye, EyeOff, Archive,
  CheckCircle2, AlertTriangle, RefreshCw,
} from 'lucide-react';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import {
  PageHeader, StatCard, EmptyState, ErrorState, SkeletonRows, StatusBadge, Badge, Drawer, Modal, Field,
  Segmented, AsyncButton, Spinner, Progress, useToast, Alert,
} from '../components/ui';
import { money, bytes } from '../utils/format';

const EMPTY_FORM = {
  title: '', code: '', domain: '', technologyStack: '', tags: '', price: '',
  abstractText: '', description: '', installationInstructions: '', catalogStatus: 'DRAFT',
};

const CATEGORIES = [
  ['SOURCE_CODE', 'Source code (ZIP)'], ['DOCUMENTATION', 'Documentation'], ['DATABASE', 'Database'],
  ['VIDEO', 'Demo video'], ['SCREENSHOT', 'Screenshot'], ['PRESENTATION', 'Presentation'], ['OTHER', 'Other resource'],
];

export default function Library() {
  const { notify } = useToast();
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get('search') || '');
  const [status, setStatus] = useState('ALL');
  const [domain, setDomain] = useState('');
  const [selected, setSelected] = useState(new Set());
  const [editing, setEditing] = useState(null); // null | 'new' | project row
  const [importOpen, setImportOpen] = useState(false);
  const q = useDebounced(search);

  useEffect(() => {
    const s = params.get('search') || '';
    setSearch(s);
  }, [params]);

  const stats = useAsync(() => api.getLibraryStats(), []);
  const list = useAsync(() => api.getLibrary({ search: q, status: status === 'ALL' ? '' : status, domain }), [q, status, domain]);
  const rows = list.data || [];

  const refresh = () => {
    list.reload();
    stats.reload();
  };

  const allSelected = rows.length > 0 && rows.every((r) => selected.has(r.id));
  const toggleAll = () => setSelected(allSelected ? new Set() : new Set(rows.map((r) => r.id)));
  const toggle = (id) => setSelected((s) => {
    const n = new Set(s);
    if (n.has(id)) n.delete(id);
    else n.add(id);
    return n;
  });

  const bulk = async (target) => {
    try {
      const res = await api.bulkCatalogStatus([...selected], target);
      notify(`${res.updated} project${res.updated === 1 ? '' : 's'} ${target === 'PUBLISHED' ? 'published' : target === 'ARCHIVED' ? 'archived' : 'moved to draft'}.`);
      setSelected(new Set());
      refresh();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  const setOne = async (row, target) => {
    try {
      await api.setCatalogStatus(row.id, target);
      notify(`${row.projectCode} ${target === 'PUBLISHED' ? 'published' : target === 'ARCHIVED' ? 'archived' : 'unpublished'}.`);
      refresh();
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  const s = stats.data || {};

  return (
    <>
      <PageHeader
        title="Project library"
        description="The central catalogue of completed projects. Each project is stored once and shared with colleges through allocations."
        actions={
          <>
            <button className="btn btn-secondary" onClick={() => setImportOpen(true)}><Download /> Import from repository</button>
            <button className="btn btn-primary" onClick={() => setEditing('new')}><Plus /> Add project</button>
          </>
        }
      />

      <div className="stat-grid mb-6">
        <StatCard label="Library projects" value={s.total} icon={LibraryIcon} loading={stats.loading} index={0} />
        <StatCard label="Published" value={s.published} icon={CheckCircle2} tone="success" loading={stats.loading} index={1} />
        <StatCard label="Drafts" value={s.draft} icon={EyeOff} loading={stats.loading} index={2} />
        <StatCard label="Allocated to colleges" value={s.allocatedProjects} hint={`${s.activeAllocations ?? 0} allocations`} icon={FolderOpen} loading={stats.loading} index={3} />
      </div>

      <div className="toolbar">
        <div className="input-with-icon grow">
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search by title, code, technology or tag" value={search}
            onChange={(e) => { setSearch(e.target.value); setParams(e.target.value ? { search: e.target.value } : {}, { replace: true }); }} />
        </div>
        <select className="select" style={{ width: 210 }} value={domain} onChange={(e) => setDomain(e.target.value)} aria-label="Domain">
          <option value="">All domains</option>
          {(s.domains || []).map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
        <Segmented
          value={status}
          onChange={setStatus}
          options={[{ value: 'ALL', label: 'All' }, { value: 'PUBLISHED', label: 'Published' }, { value: 'DRAFT', label: 'Draft' }, { value: 'ARCHIVED', label: 'Archived' }]}
        />
      </div>

      {selected.size > 0 && (
        <div className="surface-muted flex items-center gap-2 mb-4 p-3 flex-wrap">
          <span className="text-sm font-medium">{selected.size} selected</span>
          <span className="ml-auto" />
          <AsyncButton className="btn btn-secondary btn-sm" onClick={() => bulk('PUBLISHED')}><Eye /> Publish</AsyncButton>
          <AsyncButton className="btn btn-secondary btn-sm" onClick={() => bulk('DRAFT')}><EyeOff /> Unpublish</AsyncButton>
          <AsyncButton className="btn btn-danger-ghost btn-sm" onClick={() => bulk('ARCHIVED')}><Archive /> Archive</AsyncButton>
          <button className="btn btn-ghost btn-sm" onClick={() => setSelected(new Set())}>Clear</button>
        </div>
      )}

      {list.error ? <ErrorState error={list.error} onRetry={list.reload} /> : (
        <div className="card card-flush">
          {list.loading && !list.data ? <div className="p-4"><SkeletonRows rows={8} /></div> : rows.length === 0 ? (
            <EmptyState
              icon={LibraryIcon}
              title={q || status !== 'ALL' || domain ? 'No projects match these filters' : 'The library is empty'}
              text={q || status !== 'ALL' || domain ? 'Try a different search or clear the filters.' : 'Add projects one by one, or import the completed projects from the master repository.'}
              action={!q && status === 'ALL' && !domain && <button className="btn btn-primary" onClick={() => setImportOpen(true)}><Download /> Import projects</button>}
            />
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: 36 }}><input type="checkbox" checked={allSelected} onChange={toggleAll} aria-label="Select all" /></th>
                    <th>Project</th>
                    <th className="hide-lg">Domain</th>
                    <th className="hide-lg">Deliverables</th>
                    <th className="cell-num">Price</th>
                    <th className="cell-num">Colleges</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.id} className={selected.has(r.id) ? 'is-selected' : ''}>
                      <td><input type="checkbox" checked={selected.has(r.id)} onChange={() => toggle(r.id)} aria-label={`Select ${r.projectName}`} /></td>
                      <td style={{ maxWidth: 380 }}>
                        <div className="project-code">{r.projectCode}</div>
                        <div className="font-medium truncate">{r.projectName}</div>
                        <div className="text-xs text-subtle truncate">{r.technologyStack}</div>
                      </td>
                      <td className="cell-muted text-sm hide-lg">{r.domain || '—'}</td>
                      <td className="hide-lg">
                        <div className="flex items-center gap-2 text-sm text-muted">
                          <span title="Files">{r.fileCount} files</span>
                          {r.hasSourceCode && <FileCode2 size={14} aria-label="Source code" />}
                          {r.hasDemoVideo && <Video size={14} aria-label="Demo video" />}
                        </div>
                        <div className="text-xs text-subtle">{bytes(r.totalBytes)}</div>
                      </td>
                      <td className="cell-num">{r.price != null ? money(r.price) : <span className="text-subtle">Not set</span>}</td>
                      <td className="cell-num">{r.allocatedColleges}</td>
                      <td><StatusBadge status={r.catalogStatus} /></td>
                      <td>
                        <div className="flex items-center gap-1 justify-end">
                          <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setEditing(r)} aria-label={`Edit ${r.projectName}`} title="Edit"><Pencil /></button>
                          <Link className="btn btn-ghost btn-icon btn-sm" to={`/projects/${r.id}`} aria-label="Files" title="Files and preview"><FolderOpen /></Link>
                          {r.catalogStatus === 'PUBLISHED'
                            ? <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setOne(r, 'DRAFT')} title="Unpublish" aria-label="Unpublish"><EyeOff /></button>
                            : <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setOne(r, 'PUBLISHED')} title="Publish" aria-label="Publish"><Eye /></button>}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <ProjectEditor
        open={editing !== null}
        project={editing === 'new' ? null : editing}
        domains={s.domains || []}
        onClose={() => setEditing(null)}
        onSaved={() => { setEditing(null); refresh(); }}
      />
      <ImportDialog open={importOpen} onClose={() => setImportOpen(false)} onFinished={refresh} />
    </>
  );
}

/* ------------------------------------------------------------------ */

function ProjectEditor({ open, project, domains, onClose, onSaved }) {
  const { notify } = useToast();
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [upload, setUpload] = useState({ category: 'SOURCE_CODE', previewable: false, file: null });
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    setErrors({});
    setForm(project ? {
      title: project.projectName || '', code: project.projectCode || '', domain: project.domain || '',
      technologyStack: project.technologyStack || '', tags: project.tags || '', price: project.price ?? '',
      abstractText: project.abstractText || '', description: project.description || '',
      installationInstructions: project.installationInstructions || '', catalogStatus: project.catalogStatus || 'DRAFT',
    } : EMPTY_FORM);
    setUpload({ category: 'SOURCE_CODE', previewable: false, file: null });
  }, [open, project]);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const save = async () => {
    const e = {};
    if (!form.title.trim()) e.title = 'Title is required.';
    if (form.price !== '' && (Number.isNaN(Number(form.price)) || Number(form.price) < 0)) e.price = 'Enter a price of 0 or more.';
    setErrors(e);
    if (Object.keys(e).length) return;
    setSaving(true);
    const payload = { ...form, price: form.price === '' ? null : Number(form.price), code: form.code.trim() || null };
    try {
      if (project) await api.updateLibraryProject(project.id, payload);
      else await api.createLibraryProject(payload);
      notify(project ? 'Project updated.' : 'Project added to the library.');
      onSaved();
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const doUpload = async () => {
    if (!upload.file) return;
    setUploading(true);
    try {
      await api.uploadLibraryFile(project.id, upload.file, { category: upload.category, previewable: upload.previewable });
      notify(`${upload.file.name} uploaded.`);
      setUpload((u) => ({ ...u, file: null }));
      if (fileRef.current) fileRef.current.value = '';
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title={project ? `Edit ${project.projectCode}` : 'Add library project'}
      description={project ? project.projectName : 'Create the catalogue entry, then upload its deliverables.'}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>{saving && <Spinner />} {project ? 'Save changes' : 'Create project'}</button>
        </>
      }
    >
      <Field label="Title" error={errors.title}><input className="input" value={form.title} onChange={set('title')} /></Field>
      <div className="form-grid">
        <Field label="Project code" hint={project ? undefined : 'Leave empty to generate (LIB-###)'}><input className="input font-mono" value={form.code} onChange={set('code')} /></Field>
        <Field label="List price (INR)" error={errors.price} hint="Colleges can be given their own price"><input className="input" inputMode="decimal" value={form.price} onChange={set('price')} /></Field>
        <Field label="Domain">
          <input className="input" list="domains" value={form.domain} onChange={set('domain')} placeholder="e.g. Computer Vision" />
          <datalist id="domains">{domains.map((d) => <option key={d} value={d} />)}</datalist>
        </Field>
        <Field label="Catalogue status">
          <select className="select" value={form.catalogStatus} onChange={set('catalogStatus')}>
            <option value="DRAFT">Draft (hidden)</option>
            <option value="PUBLISHED">Published</option>
            <option value="ARCHIVED">Archived</option>
          </select>
        </Field>
      </div>
      <Field label="Technologies" hint="Comma separated"><input className="input" value={form.technologyStack} onChange={set('technologyStack')} placeholder="Python, FastAPI, PyTorch" /></Field>
      <Field label="Tags" hint="Comma separated"><input className="input" value={form.tags} onChange={set('tags')} /></Field>
      <Field label="Abstract" hint="Shown to students before purchase"><textarea className="textarea" rows={4} value={form.abstractText} onChange={set('abstractText')} /></Field>
      <Field label="Detailed description"><textarea className="textarea" rows={5} value={form.description} onChange={set('description')} /></Field>
      <Field label="Installation and execution" hint="Shown only after purchase"><textarea className="textarea font-mono" rows={5} value={form.installationInstructions} onChange={set('installationInstructions')} /></Field>

      {project && (
        <>
          <hr className="divider" />
          <div className="section-header">
            <div>
              <div className="section-title">Upload deliverable</div>
              <p className="text-sm">Files go into the matching category folder. Mark screenshots, abstracts and demo videos as preview to show them before purchase.</p>
            </div>
          </div>
          <div className="form-grid">
            <Field label="Category">
              <select className="select" value={upload.category} onChange={(e) => setUpload((u) => ({ ...u, category: e.target.value, previewable: ['SCREENSHOT', 'VIDEO'].includes(e.target.value) }))}>
                {CATEGORIES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </Field>
            <Field label="Visibility">
              <label className="checkbox" style={{ height: 36 }}>
                <input type="checkbox" checked={upload.previewable} onChange={(e) => setUpload((u) => ({ ...u, previewable: e.target.checked }))} />
                Preview before purchase
              </label>
            </Field>
          </div>
          <div className="flex gap-2 items-center">
            <input ref={fileRef} type="file" className="input" style={{ paddingTop: 6 }} onChange={(e) => setUpload((u) => ({ ...u, file: e.target.files?.[0] || null }))} />
            <button className="btn btn-secondary" onClick={doUpload} disabled={!upload.file || uploading}>{uploading ? <Spinner /> : <Upload />} Upload</button>
          </div>
          <Link to={`/projects/${project.id}`} className="btn btn-ghost btn-sm mt-3"><FolderOpen /> Manage all files</Link>
        </>
      )}
    </Drawer>
  );
}

/* ------------------------------------------------------------------ */

function ImportDialog({ open, onClose, onFinished }) {
  const { notify } = useToast();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chosen, setChosen] = useState(new Set());
  const [price, setPrice] = useState('');
  const [publish, setPublish] = useState(false);
  const [job, setJob] = useState(null);
  const timer = useRef(null);

  const loadScan = async () => {
    setLoading(true);
    try {
      const res = await api.scanLibraryImport();
      setScan(res);
      setChosen(new Set((res.projects || []).filter((p) => !p.imported).map((p) => p.directory)));
    } catch (e) {
      notify(e.message, { tone: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const poll = async () => {
    try {
      const status = await api.getLibraryImportStatus();
      setJob(status);
      if (!status.running) {
        clearInterval(timer.current);
        timer.current = null;
        onFinished();
        loadScan();
      }
    } catch { /* keep polling */ }
  };

  useEffect(() => {
    if (!open) return undefined;
    setJob(null);
    loadScan();
    api.getLibraryImportStatus().then((st) => {
      if (st.running) {
        setJob(st);
        timer.current = setInterval(poll, 2000);
      }
    }).catch(() => {});
    return () => { if (timer.current) clearInterval(timer.current); timer.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const start = async () => {
    try {
      const res = await api.startLibraryImport({ directories: [...chosen], defaultPrice: price === '' ? null : price, publish });
      setJob(res);
      timer.current = setInterval(poll, 2000);
    } catch (e) {
      notify(e.message, { tone: 'error' });
    }
  };

  const projects = scan?.projects || [];
  const pending = projects.filter((p) => !p.imported).length;
  const running = job?.running;
  const pct = job?.total ? Math.round((job.completed / job.total) * 100) : 0;

  const toggle = (dir) => setChosen((s) => {
    const n = new Set(s);
    if (n.has(dir)) n.delete(dir);
    else n.add(dir);
    return n;
  });

  const summary = useMemo(() => {
    if (!job || job.running || !job.log) return null;
    const ok = job.log.filter((l) => l.status === 'OK');
    return { ok: ok.length, failed: job.failed, files: ok.reduce((a, l) => a + (l.files || 0), 0) };
  }, [job]);

  return (
    <Modal
      open={open}
      onClose={onClose}
      size="lg"
      title="Import from project repository"
      description="Reads a local checkout of the master repository on the server. Re-running is safe: existing projects are updated, not duplicated."
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>{running ? 'Run in background' : 'Close'}</button>
          <button className="btn btn-primary" onClick={start} disabled={!scan?.configured || running || chosen.size === 0}>
            {running ? <><Spinner /> Importing…</> : <><Download /> Import {chosen.size} project{chosen.size === 1 ? '' : 's'}</>}
          </button>
        </>
      }
    >
      {loading && !scan ? <SkeletonRows rows={6} height={36} /> : !scan?.configured ? (
        <Alert tone="warning" title="Import source not configured">
          {scan?.message || 'Set LIBRARY_IMPORT_ROOT on the backend to a local checkout of the project repository, then restart the server.'}
        </Alert>
      ) : (
        <>
          {job && (
            <div className="surface-muted p-4 mb-4">
              <div className="flex items-center justify-between mb-2 text-sm">
                <span className="font-medium">{running ? `Importing ${job.current || '…'}` : 'Import finished'}</span>
                <span className="tabular text-muted">{job.completed}/{job.total}</span>
              </div>
              <Progress value={pct} tone={!running && !job.failed ? 'success' : undefined} />
              {summary && (
                <p className="text-sm mt-2">
                  {summary.ok} imported, {summary.files} new files{summary.failed ? `, ${summary.failed} failed` : ''}.
                </p>
              )}
              {job.log?.filter((l) => l.status === 'FAILED').map((l) => (
                <div key={l.directory} className="text-sm text-danger mt-1 flex gap-2"><AlertTriangle size={14} /> {l.directory}: {l.error}</div>
              ))}
            </div>
          )}

          <div className="form-grid">
            <Field label="Default price for new projects (INR)" hint="Leave empty to set prices later">
              <input className="input" inputMode="decimal" value={price} onChange={(e) => setPrice(e.target.value)} />
            </Field>
            <Field label="After import">
              <label className="checkbox" style={{ height: 36 }}>
                <input type="checkbox" checked={publish} onChange={(e) => setPublish(e.target.checked)} /> Publish new projects immediately
              </label>
            </Field>
          </div>

          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted">{projects.length} projects found · {pending} not yet imported</span>
            <div className="flex gap-1">
              <button className="btn btn-ghost btn-sm" onClick={() => setChosen(new Set(projects.map((p) => p.directory)))}>Select all</button>
              <button className="btn btn-ghost btn-sm" onClick={() => setChosen(new Set())}>None</button>
              <button className="btn btn-ghost btn-sm" onClick={loadScan} aria-label="Rescan"><RefreshCw /></button>
            </div>
          </div>
          <div className="border rounded" style={{ maxHeight: 340, overflowY: 'auto' }}>
            {projects.map((p) => (
              <label key={p.directory} className="list-item cursor-pointer" style={{ padding: '9px 12px' }}>
                <input type="checkbox" checked={chosen.has(p.directory)} onChange={() => toggle(p.directory)} />
                <span className="project-code" style={{ width: 28 }}>{String(p.number ?? '').padStart(2, '0')}</span>
                <span className="flex-1 min-w-0">
                  <span className="block text-sm font-medium truncate">{p.title}</span>
                  <span className="block text-xs text-subtle truncate">{p.domain} · {p.technologyStack}</span>
                </span>
                {p.hasVideo && <Video size={14} className="text-subtle" aria-label="Has demo video" />}
                {p.imported ? <Badge tone="success">Imported</Badge> : <Badge>New</Badge>}
              </label>
            ))}
          </div>
        </>
      )}
    </Modal>
  );
}
