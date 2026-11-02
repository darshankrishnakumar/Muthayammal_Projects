import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ImagePlus, Mic, Trash2, Send, Save } from 'lucide-react';
import { api } from '../utils/api';
import { PageHeader, Field, Spinner, useToast, LoadingBlock, ErrorState, Alert } from '../components/ui';

const MAX_ATTACHMENT = 5 * 1024 * 1024;
const EMPTY = { title: '', problemStatement: '', description: '', technologyStack: '', budget: '', imageUrl: '', audioUrl: '' };

export default function RequirementForm() {
  const { id } = useParams();
  const editing = Boolean(id);
  const navigate = useNavigate();
  const { notify } = useToast();
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(editing);
  const [loadError, setLoadError] = useState(null);
  const [saving, setSaving] = useState(null);
  const [status, setStatus] = useState(null);
  const [notes, setNotes] = useState(null);
  const imageRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    if (!editing) return;
    api.getRequirementById(id)
      .then((r) => {
        setForm({
          title: r.title || '', problemStatement: r.problemStatement || '', description: r.description || '',
          technologyStack: r.technologyStack || '', budget: r.budget ?? '', imageUrl: r.imageUrl || '', audioUrl: r.audioUrl || '',
        });
        setStatus(r.status);
        setNotes(r.collegeAdminNotes || r.superAdminNotes);
      })
      .catch(setLoadError)
      .finally(() => setLoading(false));
  }, [id, editing]);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const attach = (kind) => (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_ATTACHMENT) {
      notify(`${file.name} is larger than 5 MB.`, { tone: 'error' });
      e.target.value = '';
      return;
    }
    const reader = new FileReader();
    reader.onload = () => setForm((f) => ({ ...f, [kind]: reader.result }));
    reader.readAsDataURL(file);
  };

  const validate = () => {
    const e = {};
    if (!form.title.trim()) e.title = 'Give your project a title.';
    if (!form.problemStatement.trim()) e.problemStatement = 'Describe the problem the project should solve.';
    if (form.budget !== '' && (Number.isNaN(Number(form.budget)) || Number(form.budget) < 0)) e.budget = 'Enter a budget of 0 or more.';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const save = async (submit) => {
    if (!validate()) return;
    setSaving(submit ? 'submit' : 'draft');
    const payload = { ...form, budget: form.budget === '' ? null : Number(form.budget) };
    try {
      const saved = editing ? await api.updateRequirement(id, payload) : await api.createRequirement(payload);
      if (submit) await api.submitRequirement(saved.id);
      notify(submit ? 'Requirement submitted to your college.' : 'Draft saved.');
      navigate(`/requirements/${saved.id}`);
    } catch (err) {
      notify(err.message, { tone: 'error' });
    } finally {
      setSaving(null);
    }
  };

  if (loading) return <LoadingBlock />;
  if (loadError) return <ErrorState error={loadError} />;

  const canSubmit = !editing || status === 'DRAFT' || status === 'CHANGES_REQUESTED';

  return (
    <div className="page-narrow" style={{ margin: '0 auto' }}>
      <PageHeader
        breadcrumbs={[{ label: 'Requirements', to: '/requirements' }, { label: editing ? 'Edit' : 'New' }]}
        title={editing ? 'Edit requirement' : 'New project requirement'}
        description="Be specific: the clearer the problem and expected features, the faster your college can forward it and the more accurate the quote."
      />

      {status === 'CHANGES_REQUESTED' && notes && <Alert tone="warning" title="Changes requested">{notes}</Alert>}

      <div className="card">
        <Field label="Project title" error={errors.title} htmlFor="title">
          <input id="title" className="input" value={form.title} onChange={set('title')} placeholder="e.g. Smart attendance using face recognition" />
        </Field>
        <Field label="Problem statement" error={errors.problemStatement} hint="What should the project solve, and for whom?" htmlFor="ps">
          <textarea id="ps" className="textarea" rows={4} value={form.problemStatement} onChange={set('problemStatement')} />
        </Field>
        <Field label="Features and details" hint="Modules, screens, datasets, reports — anything you already know" htmlFor="desc">
          <textarea id="desc" className="textarea" rows={6} value={form.description} onChange={set('description')} />
        </Field>
        <div className="form-grid">
          <Field label="Preferred technologies" hint="Optional" htmlFor="tech">
            <input id="tech" className="input" value={form.technologyStack} onChange={set('technologyStack')} placeholder="Python, Flask, MySQL" />
          </Field>
          <Field label="Your budget (INR)" error={errors.budget} hint="Optional. The final quote comes from the platform." htmlFor="budget">
            <input id="budget" className="input" inputMode="decimal" value={form.budget} onChange={set('budget')} />
          </Field>
        </div>

        <div className="section-title mt-2 mb-3">Attachments <span className="text-sm text-subtle font-medium">· optional, up to 5 MB each</span></div>
        <div className="grid grid-cols-2 gap-3">
          <div className="surface-muted p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium flex items-center gap-2"><ImagePlus size={15} /> Reference image</span>
              {form.imageUrl && <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setForm((f) => ({ ...f, imageUrl: '' }))} aria-label="Remove image"><Trash2 /></button>}
            </div>
            {form.imageUrl ? <img src={form.imageUrl} alt="Reference" style={{ maxHeight: 160, borderRadius: 8, margin: '0 auto' }} />
              : <button className="dropzone w-full" onClick={() => imageRef.current?.click()}>Choose an image (PNG, JPG)</button>}
            <input ref={imageRef} type="file" accept="image/*" hidden onChange={attach('imageUrl')} />
          </div>
          <div className="surface-muted p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium flex items-center gap-2"><Mic size={15} /> Voice note</span>
              {form.audioUrl && <button className="btn btn-ghost btn-icon btn-sm" onClick={() => setForm((f) => ({ ...f, audioUrl: '' }))} aria-label="Remove voice note"><Trash2 /></button>}
            </div>
            {form.audioUrl ? <audio controls src={form.audioUrl} style={{ width: '100%' }} />
              : <button className="dropzone w-full" onClick={() => audioRef.current?.click()}>Choose audio (MP3, WAV, M4A)</button>}
            <input ref={audioRef} type="file" accept="audio/*" hidden onChange={attach('audioUrl')} />
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-2 mt-4">
        <button className="btn btn-ghost" onClick={() => navigate(-1)}>Cancel</button>
        <button className="btn btn-secondary" onClick={() => save(false)} disabled={!!saving}>{saving === 'draft' ? <Spinner /> : <Save />} Save draft</button>
        {canSubmit && <button className="btn btn-primary" onClick={() => save(true)} disabled={!!saving}>{saving === 'submit' ? <Spinner /> : <Send />} Submit to college</button>}
      </div>
    </div>
  );
}
