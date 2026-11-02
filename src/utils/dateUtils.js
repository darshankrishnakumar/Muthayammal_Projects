/**
 * Date utility helpers to prevent timezone shifting and formatting discrepancies.
 */

/**
 * Formats a date string (ISO, LocalDateTime, or YYYY-MM-DD) into a localized, human-friendly date.
 * Safely parses the year, month, and day to prevent negative timezone offset shifts (e.g. 1-day backward shift).
 */
export const formatDate = (dateInput, fallback = 'Never (Permanent)') => {
  if (!dateInput) return fallback;

  if (typeof dateInput === 'string') {
    const match = dateInput.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (match) {
      const year = Number(match[1]);
      const monthIndex = Number(match[2]) - 1;
      const day = Number(match[3]);
      const d = new Date(year, monthIndex, day);
      return d.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  }

  const d = new Date(dateInput);
  if (isNaN(d.getTime())) return String(dateInput);
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Formats a date string or timestamp into 'YYYY-MM-DD' suitable for HTML <input type="date">.
 */
export const toDateInputValue = (dateInput) => {
  if (!dateInput) return '';

  if (typeof dateInput === 'string') {
    const match = dateInput.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (match) {
      return `${match[1]}-${match[2]}-${match[3]}`;
    }
  }

  const d = new Date(dateInput);
  if (isNaN(d.getTime())) return '';
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * Normalizes deadline date input (YYYY-MM-DD or date string) to end-of-day ISO string (YYYY-MM-DDT23:59:59).
 * Ensures the assignment is valid through the entire deadline date chosen by the user.
 */
export const normalizeDeadline = (dateInput) => {
  if (!dateInput) return null;
  const str = String(dateInput).trim();
  if (!str) return null;

  const match = str.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (match) {
    return `${match[1]}-${match[2]}-${match[3]}T23:59:59`;
  }
  return str;
};

/**
 * Checks whether an assignment deadline has expired, considering the full end of the deadline day.
 */
export const isDeadlineExpired = (expiredAt) => {
  if (!expiredAt) return false;

  if (typeof expiredAt === 'string') {
    const match = expiredAt.match(/^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}):(\d{2}))?/);
    if (match) {
      const year = Number(match[1]);
      const monthIndex = Number(match[2]) - 1;
      const day = Number(match[3]);
      const hour = match[4] !== undefined ? Number(match[4]) : 23;
      const min = match[5] !== undefined ? Number(match[5]) : 59;
      const sec = match[6] !== undefined ? Number(match[6]) : 59;
      const expiry = new Date(year, monthIndex, day, hour, min, sec);
      return expiry.getTime() < Date.now();
    }
  }

  const d = new Date(expiredAt);
  return !isNaN(d.getTime()) && d.getTime() < Date.now();
};
