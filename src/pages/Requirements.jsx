import { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../utils/api';
import { 
  FileText, 
  Plus, 
  Search, 
  Filter, 
  Eye, 
  Edit, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Send,
  AlertCircle
} from 'lucide-react';

const Requirements = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [rawRequirements, setRawRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Debounce search input by 250ms to prevent request thrashing
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 250);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const fetchRequirements = async () => {
    try {
      if (rawRequirements.length === 0) setLoading(true);
      setError(null);
      const data = await api.getRequirements(debouncedSearch, statusFilter);
      setRawRequirements(data || []);
    } catch (err) {
      console.error('Error fetching requirements:', err);
      setError(err.message || 'Failed to load requirements.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequirements();
  }, [debouncedSearch, statusFilter]);

  // Instant client-side filtering for immediate 0ms response on user input
  const filteredRequirements = useMemo(() => {
    if (!debouncedSearch && !statusFilter) return rawRequirements;
    const q = debouncedSearch.toLowerCase().trim();
    return rawRequirements.filter(req => {
      const matchesSearch = !q || 
        (req.title && req.title.toLowerCase().includes(q)) ||
        (req.problemStatement && req.problemStatement.toLowerCase().includes(q)) ||
        (req.technologyStack && req.technologyStack.toLowerCase().includes(q));
      const matchesStatus = !statusFilter || req.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [rawRequirements, debouncedSearch, statusFilter]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'DRAFT':
        return <span className="badge badge-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Clock size={12}/> DRAFT</span>;
      case 'SUBMITTED':
        return <span className="badge badge-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Send size={12}/> SUBMITTED</span>;
      case 'APPROVED':
        return <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={12}/> APPROVED</span>;
      case 'REJECTED':
        return <span className="badge badge-danger" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><XCircle size={12}/> REJECTED</span>;
      case 'IN_PROGRESS':
        return <span className="badge badge-warning" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Clock size={12}/> IN PROGRESS</span>;
      case 'COMPLETED':
        return <span className="badge badge-success" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={12}/> COMPLETED</span>;
      default:
        return <span className="badge badge-secondary">{status}</span>;
    }
  };

  return (
    <div className="requirements-page flex flex-col gap-4 text-left perf-contain">
      {/* Action Header */}
      <div className="flex justify-between items-center flex-wrap gap-4 card">
        <div>
          <h2 className="font-display text-xl font-semibold">
            {user.role === 'USER' ? 'My Requirements' : 'Requirement Management & Review'}
          </h2>
          <p className="text-muted text-sm">
            {user.role === 'USER' 
              ? 'Track, edit, and submit your research and project requirements.' 
              : 'Review submitted student requirements, approve or reject applications.'}
          </p>
        </div>

        {user.role === 'USER' && (
          <Link to="/requirements/new" className="btn btn-primary flex items-center gap-2">
            <Plus size={18} />
            <span>Submit New Requirement</span>
          </Link>
        )}
      </div>

      {/* Search Toolbar */}
      <div className="filter-toolbar card" style={{ padding: '12px 16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <div className="search-input-wrapper flex-1" style={{ position: 'relative' }}>
          <Search size={16} className="search-icon" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            className="form-control" 
            placeholder="Search by requirement title or problem statement..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: '36px', width: '100%' }}
          />
        </div>

        <div className="status-filter-wrapper" style={{ minWidth: '180px' }}>
          <select 
            className="form-control"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">Draft</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="card" style={{ borderLeft: '4px solid var(--error)', backgroundColor: 'var(--error-light)' }}>
          <div className="flex items-center gap-2 text-error">
            <AlertCircle size={18} />
            <span style={{ fontWeight: 600 }}>{error}</span>
          </div>
        </div>
      )}

      {/* Data Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {loading && rawRequirements.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center' }}>
            <div style={{ border: '3px solid var(--border-color)', borderTop: '3px solid var(--primary)', borderRadius: '50%', width: '32px', height: '32px', animation: 'spin 0.6s linear infinite', margin: '0 auto 12px' }}></div>
            <p className="text-muted" style={{ fontSize: '0.85rem' }}>Loading requirements...</p>
            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
          </div>
        ) : filteredRequirements.length === 0 ? (
          <div style={{ padding: '60px 20px', textAlign: 'center' }}>
            <FileText size={48} className="text-muted" style={{ margin: '0 auto 12px', opacity: 0.4 }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '4px' }}>No requirements found.</h3>
            <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '20px' }}>
              {searchTerm || statusFilter 
                ? 'No matching records found for the applied search filters.' 
                : user.role === 'USER' 
                  ? 'You have not submitted any requirements yet.' 
                  : 'There are no requirement records in the system.'}
            </p>
            {user.role === 'USER' && (
              <Link to="/requirements/new" className="btn btn-primary">
                Create First Requirement
              </Link>
            )}
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: 'var(--bg-main)', borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '14px 16px', fontSize: '0.8rem', fontWeight: 600 }}>TITLE & DETAILS</th>
                  {user.role !== 'USER' && <th style={{ padding: '14px 16px', fontSize: '0.8rem', fontWeight: 600 }}>SUBMITTED BY</th>}
                  <th style={{ padding: '14px 16px', fontSize: '0.8rem', fontWeight: 600 }}>BUDGET</th>
                  <th style={{ padding: '14px 16px', fontSize: '0.8rem', fontWeight: 600 }}>TECH STACK</th>
                  <th style={{ padding: '14px 16px', fontSize: '0.8rem', fontWeight: 600 }}>STATUS</th>
                  <th style={{ padding: '14px 16px', fontSize: '0.8rem', fontWeight: 600, textAlign: 'right' }}>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {filteredRequirements.map((req) => (
                  <tr key={req.id} style={{ borderBottom: '1px solid var(--border-color)', transition: 'background-color 0.15s ease' }}>
                    <td style={{ padding: '16px' }}>
                      <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>{req.title}</div>
                      <div className="text-muted" style={{ fontSize: '0.8rem', marginTop: '2px', maxWidth: '340px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {req.problemStatement}
                      </div>
                    </td>

                    {user.role !== 'USER' && (
                      <td style={{ padding: '16px' }}>
                        <div style={{ fontSize: '0.85rem', fontWeight: 500 }}>{req.user?.fullName || 'N/A'}</div>
                        <div className="text-muted" style={{ fontSize: '0.75rem' }}>{req.user?.email}</div>
                      </td>
                    )}

                    <td style={{ padding: '16px', fontSize: '0.9rem', fontWeight: 600 }}>
                      {req.budget ? `Rs. ${Number(req.budget).toLocaleString()}` : 'N/A'}
                    </td>

                    <td style={{ padding: '16px' }}>
                      <span style={{ fontSize: '0.8rem', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', padding: '4px 8px', borderRadius: '4px' }}>
                        {req.technologyStack || 'Unspecified'}
                      </span>
                    </td>

                    <td style={{ padding: '16px' }}>
                      {getStatusBadge(req.status)}
                    </td>

                    <td style={{ padding: '16px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                        <button 
                          onClick={() => navigate(`/requirements/${req.id}`)} 
                          className="btn btn-secondary" 
                          style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                          title="View Requirement Details"
                        >
                          <Eye size={14} />
                          <span>View</span>
                        </button>

                        {user.role === 'USER' && req.status === 'DRAFT' && (
                          <button 
                            onClick={() => navigate(`/requirements/${req.id}/edit`)} 
                            className="btn btn-primary" 
                            style={{ padding: '6px 12px', fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            title="Edit Requirement"
                          >
                            <Edit size={14} />
                            <span>Edit</span>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Requirements;
