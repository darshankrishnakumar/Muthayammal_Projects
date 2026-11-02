import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../utils/api';
import { 
  ArrowLeft, 
  Save, 
  Send, 
  FileText, 
  IndianRupee, 
  Code, 
  Image as ImageIcon, 
  Mic, 
  AlertCircle,
  Upload,
  X,
  Music
} from 'lucide-react';

const RequirementForm = () => {
  const { id } = useParams();
  const isEditMode = Boolean(id);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    problemStatement: '',
    description: '',
    budget: '',
    technologyStack: '',
    imageUrl: '',
    audioUrl: ''
  });

  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isEditMode) {
      const fetchRequirement = async () => {
        try {
          const req = await api.getRequirementById(id);
          if (req.status !== 'DRAFT') {
            setError('Only requirements in DRAFT status can be edited.');
            return;
          }
          setFormData({
            title: req.title || '',
            problemStatement: req.problemStatement || '',
            description: req.description || '',
            budget: req.budget !== null && req.budget !== undefined ? req.budget : '',
            technologyStack: req.technologyStack || '',
            imageUrl: req.imageUrl || '',
            audioUrl: req.audioUrl || ''
          });
        } catch (err) {
          console.error('Error fetching requirement for edit:', err);
          setError(err.message || 'Failed to load requirement details.');
        } finally {
          setLoading(false);
        }
      };
      fetchRequirement();
    }
  }, [id, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileUpload = (e, fileType) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check size limit (max 5MB for smooth Data URL storage)
    if (file.size > 5 * 1024 * 1024) {
      setError(`File ${file.name} exceeds the 5MB size limit.`);
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target.result;
      if (fileType === 'image') {
        setFormData(prev => ({ ...prev, imageUrl: dataUrl }));
      } else if (fileType === 'audio') {
        setFormData(prev => ({ ...prev, audioUrl: dataUrl }));
      }
    };
    reader.readAsDataURL(file);
  };

  const clearFile = (fileType) => {
    if (fileType === 'image') {
      setFormData(prev => ({ ...prev, imageUrl: '' }));
    } else if (fileType === 'audio') {
      setFormData(prev => ({ ...prev, audioUrl: '' }));
    }
  };

  const handleSubmit = async (e, shouldSubmit = false) => {
    e.preventDefault();
    setError(null);

    if (!formData.title.trim()) {
      setError('Title is required.');
      return;
    }
    if (!formData.problemStatement.trim()) {
      setError('Problem statement is required.');
      return;
    }
    if (formData.budget && Number(formData.budget) < 0) {
      setError('Budget cannot be negative.');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        title: formData.title.trim(),
        problemStatement: formData.problemStatement.trim(),
        description: formData.description.trim(),
        budget: formData.budget !== '' ? Number(formData.budget) : null,
        technologyStack: formData.technologyStack.trim(),
        imageUrl: formData.imageUrl,
        audioUrl: formData.audioUrl
      };

      let result;
      if (isEditMode) {
        result = await api.updateRequirement(id, payload);
      } else {
        result = await api.createRequirement(payload);
      }

      if (shouldSubmit && result.id) {
        await api.submitRequirement(result.id);
      }

      navigate(`/requirements/${result.id}`);
    } catch (err) {
      console.error('Error saving requirement:', err);
      setError(err.message || 'Failed to save requirement.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '60px', textAlign: 'center' }}>
        <div style={{ border: '4px solid var(--border-color)', borderTop: '4px solid var(--primary)', borderRadius: '50%', width: '36px', height: '36px', animation: 'spin 1s linear infinite', margin: '0 auto 12px' }}></div>
        <p className="text-muted">Loading form details...</p>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div className="requirement-form-page text-left flex flex-col gap-4">
      {/* Back button & Title */}
      <div className="flex items-center justify-between card">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="btn btn-secondary" style={{ padding: '8px' }}>
            <ArrowLeft size={18} />
          </button>
          <div>
            <h2 className="font-display text-xl font-semibold">
              {isEditMode ? 'Edit Requirement' : 'Submit New Student Requirement'}
            </h2>
            <p className="text-muted text-sm">
              Fill in your problem statement, budget, tech stack, and upload media attachments.
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="card" style={{ borderLeft: '4px solid var(--error)', backgroundColor: 'var(--error-light)' }}>
          <div className="flex items-center gap-2 text-error">
            <AlertCircle size={18} />
            <span style={{ fontWeight: 600 }}>{error}</span>
          </div>
        </div>
      )}

      {/* Main Form */}
      <form onSubmit={(e) => handleSubmit(e, false)} className="card flex flex-col gap-4">
        {/* Requirement Title */}
        <div className="form-group">
          <label className="form-label" style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <FileText size={16} className="text-primary" />
            <span>Requirement Title *</span>
          </label>
          <input 
            type="text" 
            name="title"
            className="input-field" 
            style={{ width: '100%', marginTop: '6px' }}
            placeholder="e.g. AI-Powered Student Academic Performance Analytics Platform"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>

        {/* Problem Statement */}
        <div className="form-group">
          <label className="form-label" style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <FileText size={16} className="text-primary" />
            <span>Problem Statement *</span>
          </label>
          <textarea 
            name="problemStatement"
            className="input-field" 
            rows={4}
            style={{ width: '100%', marginTop: '6px', fontFamily: 'inherit' }}
            placeholder="Describe the problem, current gap, and target outcomes..."
            value={formData.problemStatement}
            onChange={handleChange}
            required
          />
        </div>

        {/* Detailed Requirement Description */}
        <div className="form-group">
          <label className="form-label" style={{ fontWeight: 600 }}>Detailed Description (Optional)</label>
          <textarea 
            name="description"
            className="input-field" 
            rows={4}
            style={{ width: '100%', marginTop: '6px', fontFamily: 'inherit' }}
            placeholder="Provide any additional functional/non-functional requirements or specifications..."
            value={formData.description}
            onChange={handleChange}
          />
        </div>

        {/* Budget & Tech Stack */}
        <div className="grid grid-cols-2 gap-4">
          <div className="form-group">
            <label className="form-label" style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <IndianRupee size={16} className="text-success" />
              <span>Project Budget (Rs.)</span>
            </label>
            <input 
              type="number" 
              name="budget"
              step="0.01"
              min="0"
              className="input-field" 
              style={{ width: '100%', marginTop: '6px' }}
              placeholder="e.g. 5000.00"
              value={formData.budget}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label" style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Code size={16} className="text-primary" />
              <span>Technology Stack</span>
            </label>
            <input 
              type="text" 
              name="technologyStack"
              className="input-field" 
              style={{ width: '100%', marginTop: '6px' }}
              placeholder="e.g. React, Spring Boot, MySQL, Python"
              value={formData.technologyStack}
              onChange={handleChange}
            />
          </div>
        </div>

        {/* File Upload Section (Image and Audio stored as URL in database table requirements) */}
        <div className="card" style={{ backgroundColor: 'var(--bg-main)', border: '1px dashed var(--border-color)', marginTop: '8px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '4px', color: 'var(--text-main)' }}>
            Requirement Media Attachments (Uploaded & Stored as URL)
          </h4>
          <p className="text-muted text-xs" style={{ marginBottom: '16px' }}>
            Upload an image diagram or audio voice note. Files will be saved as accessible URLs in the requirements table.
          </p>

          <div className="grid grid-cols-2 gap-6">
            {/* Image Upload Box */}
            <div className="form-group">
              <label className="form-label" style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <ImageIcon size={16} className="text-primary" />
                <span>Upload Image Attachment</span>
              </label>

              {formData.imageUrl ? (
                <div style={{ position: 'relative', border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#000' }}>
                  <img 
                    src={formData.imageUrl} 
                    alt="Requirement Diagram" 
                    style={{ width: '100%', maxHeight: '180px', objectFit: 'contain', display: 'block' }} 
                  />
                  <button 
                    type="button" 
                    onClick={() => clearFile('image')}
                    style={{ position: 'absolute', top: '8px', right: '8px', backgroundColor: 'rgba(0,0,0,0.7)', color: 'white', border: 'none', borderRadius: '50%', padding: '4px', cursor: 'pointer' }}
                    title="Remove Image"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center cursor-pointer" style={{ border: '2px dashed var(--border-color)', borderRadius: '8px', padding: '24px', textAlign: 'center', backgroundColor: 'var(--bg-card)', transition: 'border-color 0.2s' }}>
                  <Upload size={24} className="text-muted" style={{ marginBottom: '8px' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>Click to Upload Image</span>
                  <span className="text-muted" style={{ fontSize: '0.75rem', marginTop: '2px' }}>PNG, JPG, SVG up to 5MB</span>
                  <input 
                    type="file" 
                    accept="image/*" 
                    style={{ display: 'none' }}
                    onChange={(e) => handleFileUpload(e, 'image')}
                  />
                </label>
              )}
            </div>

            {/* Audio Upload Box */}
            <div className="form-group">
              <label className="form-label" style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                <Mic size={16} className="text-primary" />
                <span>Upload Audio Voice Note</span>
              </label>

              {formData.audioUrl ? (
                <div style={{ padding: '16px', border: '1px solid var(--border-color)', borderRadius: '8px', backgroundColor: 'var(--bg-card)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div className="flex items-center justify-between">
                    <span style={{ fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }} className="text-primary">
                      <Music size={14} /> Voice Recording Attached
                    </span>
                    <button 
                      type="button" 
                      onClick={() => clearFile('audio')}
                      style={{ backgroundColor: 'transparent', color: 'var(--error)', border: 'none', cursor: 'pointer', padding: '2px' }}
                      title="Remove Audio"
                    >
                      <X size={16} />
                    </button>
                  </div>
                  <audio controls src={formData.audioUrl} style={{ width: '100%', height: '36px' }} />
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center cursor-pointer" style={{ border: '2px dashed var(--border-color)', borderRadius: '8px', padding: '24px', textAlign: 'center', backgroundColor: 'var(--bg-card)', transition: 'border-color 0.2s' }}>
                  <Mic size={24} className="text-muted" style={{ marginBottom: '8px' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>Click to Upload Audio</span>
                  <span className="text-muted" style={{ fontSize: '0.75rem', marginTop: '2px' }}>MP3, WAV, M4A, OGG up to 5MB</span>
                  <input 
                    type="file" 
                    accept="audio/*" 
                    style={{ display: 'none' }}
                    onChange={(e) => handleFileUpload(e, 'audio')}
                  />
                </label>
              )}
            </div>
          </div>
        </div>

        {/* Form Action Buttons */}
        <div className="flex justify-end gap-3" style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
          <button 
            type="button" 
            onClick={() => navigate('/requirements')} 
            className="btn btn-secondary"
            disabled={submitting}
          >
            Cancel
          </button>

          <button 
            type="submit" 
            className="btn btn-secondary"
            disabled={submitting}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Save size={16} />
            <span>Save as Draft</span>
          </button>

          <button 
            type="button" 
            onClick={(e) => handleSubmit(e, true)}
            className="btn btn-primary"
            disabled={submitting}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Send size={16} />
            <span>Save & Submit</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default RequirementForm;
