const KEY = 'ui.theme';

export const getTheme = () => {
  try {
    return localStorage.getItem(KEY) || 'system';
  } catch {
    return 'system';
  }
};

/** 'light' | 'dark' | 'system'. System follows prefers-color-scheme via CSS. */
export const setTheme = (theme) => {
  try {
    localStorage.setItem(KEY, theme);
  } catch {
    /* storage unavailable */
  }
  applyTheme(theme);
};

export const applyTheme = (theme = getTheme()) => {
  const root = document.documentElement;
  if (theme === 'light' || theme === 'dark') root.setAttribute('data-theme', theme);
  else root.removeAttribute('data-theme');
};
