import { useCallback, useEffect, useRef, useState } from 'react';

/**
 * Runs an async loader and tracks loading/error state. Re-runs when deps change.
 * Ignores results from superseded runs so fast navigation never shows stale data.
 */
export function useAsync(loader, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const runId = useRef(0);

  const run = useCallback(async () => {
    const id = ++runId.current;
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const data = await loader();
      if (id === runId.current) setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      if (id === runId.current) setState((s) => ({ ...s, loading: false, error }));
      return undefined;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    run();
  }, [run]);

  return { ...state, reload: run, setData: (data) => setState((s) => ({ ...s, data })) };
}

/** Debounces a fast-changing value (e.g. a search box). */
export function useDebounced(value, delay = 250) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}
