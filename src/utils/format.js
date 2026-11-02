const CURRENCY = 'INR';

const moneyFormatter = new Intl.NumberFormat('en-IN', { style: 'currency', currency: CURRENCY, maximumFractionDigits: 2, minimumFractionDigits: 0 });
const numberFormatter = new Intl.NumberFormat('en-IN');

export const money = (value, currency = CURRENCY) => {
  const n = Number(value ?? 0);
  if (currency !== CURRENCY) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency, maximumFractionDigits: 2 }).format(n);
  }
  return moneyFormatter.format(Number.isFinite(n) ? n : 0);
};

export const number = (value) => numberFormatter.format(Number(value ?? 0));

export const date = (value, opts = { day: 'numeric', month: 'short', year: 'numeric' }) => {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleDateString('en-IN', opts);
};

export const dateTime = (value) => {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '—' : d.toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
};

export const relativeTime = (value) => {
  if (!value) return '';
  const d = new Date(value);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}d ago`;
  return date(value);
};

export const bytes = (value) => {
  const n = Number(value ?? 0);
  if (n < 1024) return `${n} B`;
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
  if (n < 1024 ** 3) return `${(n / 1024 ** 2).toFixed(1)} MB`;
  return `${(n / 1024 ** 3).toFixed(2)} GB`;
};

export const initials = (name = '') =>
  name.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || '?';

export const titleCase = (value = '') =>
  String(value).toLowerCase().split('_').map((w) => (w ? w[0].toUpperCase() + w.slice(1) : w)).join(' ');

export const ROLE_LABELS = {
  SUPER_ADMIN: 'Super Admin',
  ADMIN: 'College Admin',
  PROJECT_DEVELOPER: 'Developer',
  USER: 'Student',
};

/** Human labels and tones for every lifecycle status used in the UI. */
const STATUS = {
  // Requirements
  DRAFT: ['Draft', 'neutral'],
  SUBMITTED: ['Awaiting college review', 'info'],
  SUPER_ADMIN_REVIEW: ['Awaiting approval', 'info'],
  CHANGES_REQUESTED: ['Changes requested', 'warning'],
  ADVANCE_PAYMENT_PENDING: ['Advance due', 'warning'],
  ADVANCE_PAYMENT_COMPLETED: ['Ready for assignment', 'accent'],
  APPROVED: ['Approved', 'success'],
  REJECTED: ['Rejected', 'danger'],
  IN_PROGRESS: ['In progress', 'accent'],
  COMPLETED: ['Completed', 'success'],
  INACTIVE: ['Inactive', 'neutral'],
  // Projects
  CREATED: ['Created', 'neutral'],
  DEVELOPER_ASSIGNED: ['Awaiting acceptance', 'info'],
  TESTING: ['Testing', 'accent'],
  READY_FOR_REVIEW: ['In review', 'info'],
  REVIEW_APPROVED: ['Review approved', 'success'],
  READY_FOR_FINAL_PAYMENT: ['Final payment due', 'warning'],
  FINAL_PAYMENT_COMPLETED: ['Paid', 'success'],
  ACCESS_GRANTED: ['Delivered', 'success'],
  MARKETPLACE_AVAILABLE: ['Available', 'success'],
  // Catalog
  PUBLISHED: ['Published', 'success'],
  ARCHIVED: ['Archived', 'neutral'],
  // Orders / payments
  PENDING: ['Pending', 'warning'],
  PROCESSING: ['Processing', 'info'],
  FAILED: ['Failed', 'danger'],
  CANCELLED: ['Cancelled', 'neutral'],
  REFUNDED: ['Refunded', 'neutral'],
  SUCCEEDED: ['Succeeded', 'success'],
  // Accounts
  ACTIVE: ['Active', 'success'],
  PENDING_VERIFICATION: ['Pending verification', 'warning'],
};

export const statusLabel = (status) => (STATUS[status] ? STATUS[status][0] : titleCase(status || 'Unknown'));
export const statusTone = (status) => (STATUS[status] ? STATUS[status][1] : 'neutral');
