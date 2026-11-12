import React, { createContext, useContext, useState } from 'react';
import type { FilterState } from '@/types/api';

const DEFAULT_FILTERS: FilterState = {
  start_date: '2026-04-01',
  end_date: '2026-10-31',
  segment: 'All',
  team_id: 'All',
  region: 'All',
  asset_tier: 'All',
};

interface FilterContextValue {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  resetFilters: () => void;
  activeMetricKey: string | null;
  openMetricDrawer: (metricKey: string) => void;
  closeMetricDrawer: () => void;
}

const FilterContext = createContext<FilterContextValue | null>(null);

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [activeMetricKey, setActiveMetricKey] = useState<string | null>(null);

  const resetFilters = () => setFilters(DEFAULT_FILTERS);

  return (
    <FilterContext.Provider
      value={{
        filters,
        setFilters,
        resetFilters,
        activeMetricKey,
        openMetricDrawer: (k) => setActiveMetricKey(k),
        closeMetricDrawer: () => setActiveMetricKey(null),
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const ctx = useContext(FilterContext);
  if (!ctx) throw new Error('useFilters must be used inside FilterProvider');
  return ctx;
}
