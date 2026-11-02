import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, Store, CheckCircle2, SlidersHorizontal, X } from 'lucide-react';
import { api } from '../utils/api';
import { useAsync, useDebounced } from '../hooks/useAsync';
import { useAuth } from '../context/AuthContext';
import { PageHeader, EmptyState, ErrorState, SpotlightCard, Badge } from '../components/ui';
import { money } from '../utils/format';

export default function Marketplace() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get('search') || '');
  const [domain, setDomain] = useState(params.get('domain') || '');
  const [technology, setTechnology] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sort, setSort] = useState('relevance');
  const [showFilters, setShowFilters] = useState(false);
  const q = useDebounced(search);
  const min = useDebounced(minPrice, 400);
  const max = useDebounced(maxPrice, 400);

  useEffect(() => { setSearch(params.get('search') || ''); }, [params]);

  const filters = useAsync(() => api.getMarketplaceFilters(), []);
  const results = useAsync(
    () => api.browseMarketplace({ search: q, domain, technology, minPrice: min, maxPrice: max, sort }),
    [q, domain, technology, min, max, sort],
  );

  const f = filters.data || {};
  const rows = results.data || [];
  const activeFilters = [domain, technology, minPrice, maxPrice].filter(Boolean).length;
  const clear = () => { setDomain(''); setTechnology(''); setMinPrice(''); setMaxPrice(''); };

  const description = user?.role === 'USER'
    ? `Completed projects offered by ${user?.college?.name || 'your college'}. Preview each one, then buy to unlock the code, documentation and demo.`
    : user?.role === 'ADMIN'
      ? `Projects the platform has allocated to ${user?.college?.name || 'your college'}, at your college's price.`
      : 'Every published library project, as students see it.';

  const FilterPanel = (
    <aside className="space-y-6">
      <div>
        <div className="text-xs font-medium text-subtle uppercase mb-2">Domain</div>
        <div className="flex flex-col gap-1">
          <button className={`nav-item ${!domain ? 'active' : ''}`} onClick={() => setDomain('')}>All domains <span className="ml-auto text-xs text-subtle">{f.total ?? ''}</span></button>
          {(f.domains || []).map((d) => (
            <button key={d} className={`nav-item ${domain === d ? 'active' : ''}`} onClick={() => setDomain(d)}>{d}</button>
          ))}
        </div>
      </div>
      <div>
        <div className="text-xs font-medium text-subtle uppercase mb-2">Technology</div>
        <div className="flex flex-wrap gap-2">
          {(f.technologies || []).slice(0, 14).map((t) => (
            <button key={t} className={`chip ${technology === t ? 'active' : ''}`} onClick={() => setTechnology(technology === t ? '' : t)}>{t}</button>
          ))}
        </div>
      </div>
      <div>
        <div className="text-xs font-medium text-subtle uppercase mb-2">Price (INR)</div>
        <div className="flex items-center gap-2">
          <input className="input input-sm" inputMode="numeric" placeholder={f.minPrice != null ? String(Math.floor(f.minPrice)) : 'Min'} value={minPrice} onChange={(e) => setMinPrice(e.target.value)} aria-label="Minimum price" />
          <span className="text-subtle">–</span>
          <input className="input input-sm" inputMode="numeric" placeholder={f.maxPrice != null ? String(Math.ceil(f.maxPrice)) : 'Max'} value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} aria-label="Maximum price" />
        </div>
      </div>
      {activeFilters > 0 && <button className="btn btn-ghost btn-sm" onClick={clear}><X /> Clear filters</button>}
    </aside>
  );

  return (
    <>
      <PageHeader title={user?.role === 'USER' ? 'Browse projects' : 'Project catalogue'} description={description} />

      <div className="toolbar">
        <div className="input-with-icon grow">
          <Search aria-hidden="true" />
          <input className="input" placeholder="Search by title, technology or keyword" value={search}
            onChange={(e) => { setSearch(e.target.value); setParams(e.target.value ? { search: e.target.value } : {}, { replace: true }); }} />
        </div>
        <button className="btn btn-secondary mobile-only" onClick={() => setShowFilters((s) => !s)}>
          <SlidersHorizontal /> Filters{activeFilters ? ` (${activeFilters})` : ''}
        </button>
        <select className="select" style={{ width: 190 }} value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort">
          <option value="relevance">Most relevant</option>
          <option value="price_asc">Price: low to high</option>
          <option value="price_desc">Price: high to low</option>
          <option value="title">Title A–Z</option>
          <option value="newest">Newest</option>
        </select>
      </div>

      {showFilters && <div className="card mb-4 mobile-only" style={{ display: 'block' }}>{FilterPanel}</div>}

      <div className="layout-sidebar-filters">
        <div className="desktop-only">{FilterPanel}</div>
        <div>
          {results.error ? <ErrorState error={results.error} onRetry={results.reload} /> : results.loading && !results.data ? (
            <div className="card-grid">{Array.from({ length: 6 }).map((_, i) => <div key={i} className="skeleton" style={{ height: 232, borderRadius: 12 }} />)}</div>
          ) : rows.length === 0 ? (
            <div className="card">
              <EmptyState
                icon={Store}
                title={q || activeFilters ? 'No projects match your search' : 'No projects available yet'}
                text={q || activeFilters ? 'Try other keywords or clear the filters.' : user?.role === 'USER' ? 'Your college has not been allocated any projects yet. You can still request a custom project.' : 'Allocate library projects to this college to fill the catalogue.'}
                action={user?.role === 'USER' && !(q || activeFilters) && <button className="btn btn-primary" onClick={() => navigate('/requirements/new')}>Request a custom project</button>}
              />
            </div>
          ) : (
            <>
              <p className="text-sm text-muted mb-3">{rows.length} project{rows.length === 1 ? '' : 's'}</p>
              <div className="card-grid">
                {rows.map((p, i) => (
                  <SpotlightCard
                    key={p.id}
                    className="card-interactive project-card reveal"
                    style={{ '--i': Math.min(i, 12) }}
                    role="link"
                    tabIndex={0}
                    onClick={() => navigate(`/marketplace/${p.id}`)}
                    onKeyDown={(e) => e.key === 'Enter' && navigate(`/marketplace/${p.id}`)}
                  >
                    <div className="project-card-head">
                      <span className="project-code">{p.projectCode}</span>
                      {p.domain && <Badge>{p.domain}</Badge>}
                    </div>
                    <div className="project-title">{p.projectName}</div>
                    {p.abstractText && <p className="project-abstract">{p.abstractText}</p>}
                    <div className="project-meta">
                      {(p.technologyStack || '').split(',').map((t) => t.trim()).filter(Boolean).slice(0, 4).map((t) => <span key={t} className="tag">{t}</span>)}
                    </div>
                    <div className="project-card-foot">
                      <span className="price">{money(p.price)}</span>
                      {p.owned ? <Badge tone="success"><CheckCircle2 /> Owned</Badge> : <span className="text-sm text-accent font-medium">View details</span>}
                    </div>
                  </SpotlightCard>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
