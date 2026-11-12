import React, { useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Calendar,
  Download,
  Filter,
  RotateCcw,
  Search,
  SlidersHorizontal,
  ChevronDown,
  Layers,
  Sparkles,
} from 'lucide-react';
import { useFilters } from '@/hooks/useFilters';
import { apiGet, downloadBlob } from '@/services/api';
import { SqlEvidenceDrawer } from '@/components/shared/SqlEvidenceDrawer';

interface FilterOptions {
  segments: string[];
  asset_tiers: string[];
  regions: string[];
  teams: { team_id: string; team_name: string; region: string }[];
}

const PRIMARY_NAV = [
  { to: '/overview', label: 'Overview' },
  { to: '/journeys', label: 'Journeys' },
  { to: '/investigations', label: 'Investigations' },
  { to: '/retention', label: 'Retention' },
  { to: '/operations', label: 'Operations' },
  { to: '/decisions', label: 'Decisions' }, // routes to roadmap / simulator hub
];

const MORE_NAV = [
  { to: '/clients', label: 'Client Explorer', meta: 'Searchable Directory' },
  { to: '/advisors', label: 'Advisor Intelligence', meta: 'O/E Workload' },
  { to: '/simulator', label: 'Impact Simulator', meta: 'Scenario Modeling' },
  { to: '/kpi-dictionary', label: 'KPI Dictionary', meta: 'Metrics Specification' },
  { to: '/requirements', label: 'Requirements Hub', meta: 'BRD & Traceability' },
  { to: '/data-quality', label: 'Data Quality', meta: 'Synthetic Integrity' },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { filters, setFilters, resetFilters } = useFilters();
  const location = useLocation();
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);

  const { data: options } = useQuery<FilterOptions>({
    queryKey: ['filter-options'],
    queryFn: () => apiGet<FilterOptions>('/filters/options'),
    staleTime: 1000 * 60 * 10,
  });

  const handleExport = async (reportType: string) => {
    setExportOpen(false);
    await downloadBlob(`/exports/${reportType}`, 'GET', `${reportType}.csv`);
  };

  const isDecisionsActive = location.pathname === '/roadmap' || location.pathname === '/simulator';

  return (
    <div className="min-h-screen flex flex-col bg-[#fdf9f5] text-[#1c1b1a]">
      {/* Stitch Design Top Navigation Bar (Docked, 64px, Stationary Top Bar) */}
      <header className="bg-[#fdf9f5] border-b border-[#bec9c7]/30 sticky top-0 z-50 h-16 transition-all duration-150 ease-out">
        <div className="w-full max-w-[1440px] mx-auto px-6 sm:px-10 flex items-center justify-between h-full">
          {/* Brand Logo / Monogram & Links */}
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2.5 cursor-pointer group">
              <div className="w-7 h-7 bg-[#11615f] text-white flex items-center justify-center rounded text-[11px] font-bold tracking-widest group-hover:bg-[#337a78] transition-colors">
                C
              </div>
              <span className="font-headline text-[22px] tracking-tight text-[#1c1b1a] uppercase font-medium">
                CONTINUUM
              </span>
            </Link>

            {/* Navigation Cluster */}
            <nav className="hidden md:flex items-center gap-6 lg:gap-8">
              {PRIMARY_NAV.map((item) => {
                if (item.label === 'Decisions') {
                  return (
                    <NavLink
                      key={item.to}
                      to="/roadmap"
                      className={() =>
                        `text-[11px] uppercase tracking-[0.08em] font-semibold pb-5 pt-5 transition-all ${
                          isDecisionsActive
                            ? 'text-[#864e59] border-b-2 border-[#864e59]'
                            : 'text-[#3f4948] hover:text-[#1c1b1a]'
                        }`
                      }
                    >
                      {item.label}
                    </NavLink>
                  );
                }
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `text-[11px] uppercase tracking-[0.08em] font-semibold pb-5 pt-5 transition-all ${
                        isActive
                          ? item.label === 'Journeys'
                            ? 'text-[#864e59] border-b-2 border-[#864e59]'
                            : 'text-[#11615f] border-b-2 border-[#11615f]'
                          : 'text-[#3f4948] hover:text-[#1c1b1a]'
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                );
              })}

              {/* More / Governance dropdown */}
              <div className="relative">
                <button
                  onClick={() => setMoreMenuOpen((o) => !o)}
                  className="flex items-center gap-1 text-[11px] uppercase tracking-[0.08em] font-semibold pb-5 pt-5 text-[#3f4948] hover:text-[#1c1b1a] transition-colors"
                >
                  <span>More</span>
                  <ChevronDown className="h-3 w-3 text-[#6f7978]" />
                </button>
                {moreMenuOpen && (
                  <div
                    className="absolute left-0 top-full mt-1 w-64 rounded bg-white border border-[#bec9c7]/40 shadow-lg p-1.5 z-50 architectural-shadow"
                    onMouseLeave={() => setMoreMenuOpen(false)}
                  >
                    <div className="px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-[#6f7978]">
                      Extended Studio Tools
                    </div>
                    {MORE_NAV.map((m) => (
                      <Link
                        key={m.to}
                        to={m.to}
                        onClick={() => setMoreMenuOpen(false)}
                        className="block rounded px-2.5 py-1.5 hover:bg-[#f7f3ef] transition-colors"
                      >
                        <div className="text-xs font-medium text-[#1c1b1a]">{m.label}</div>
                        <div className="text-[10px] text-[#6f7978]">{m.meta}</div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </nav>
          </div>

          {/* Trailing Controls: Search, Date Range, Filter Drawer, Profile */}
          <div className="flex items-center gap-3">
            {/* Filter Toggle Button */}
            <button
              onClick={() => setFilterDrawerOpen((o) => !o)}
              className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded border text-[11px] font-semibold tracking-wider uppercase transition-colors ${
                filters.segment !== 'All' || filters.region !== 'All' || filters.team_id !== 'All'
                  ? 'bg-[#ffd9de]/50 border-[#864e59] text-[#864e59]'
                  : 'bg-white border-[#bec9c7]/50 text-[#1c1b1a] hover:border-[#11615f]'
              }`}
            >
              <SlidersHorizontal className="h-3.5 w-3.5 text-[#6f7978]" />
              <span>
                {filters.segment !== 'All' || filters.region !== 'All' || filters.team_id !== 'All'
                  ? 'Filters Active'
                  : 'Filter Studio'}
              </span>
              <ChevronDown className="h-3.5 w-3.5 text-[#6f7978]" />
            </button>

            {/* Quick Cohort / Segment Badge */}
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 bg-[#f1edea] rounded border border-[#bec9c7]/40 text-[11px] font-medium text-[#3f4948]">
              <span className="w-2 h-2 rounded-full bg-[#11615f]"></span>
              <span>{filters.segment === 'All' ? 'All Segments' : filters.segment}</span>
            </div>

            {/* Export Dropdown */}
            <div className="relative">
              <button
                onClick={() => setExportOpen((o) => !o)}
                className="p-1.5 text-[#3f4948] hover:text-[#1c1b1a] hover:bg-[#f1edea] transition-colors rounded border border-[#bec9c7]/40 bg-white"
                title="Tableau CSV Extracts"
              >
                <Download className="h-4 w-4" />
              </button>
              {exportOpen && (
                <div
                  className="absolute right-0 mt-2 w-64 rounded bg-white border border-[#bec9c7]/50 p-2 shadow-lg z-50 architectural-shadow"
                  onMouseLeave={() => setExportOpen(false)}
                >
                  <div className="px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-[#6f7978]">
                    Tableau-Ready CSV Extracts
                  </div>
                  {[
                    ['executive_monthly_metrics', 'Executive Monthly Metrics'],
                    ['journey_stage_metrics', 'Journey Stage Metrics'],
                    ['service_sla_metrics', 'Service SLA Metrics'],
                    ['advisor_workload_metrics', 'Advisor Workload Metrics'],
                    ['complaint_category_metrics', 'Complaint Category Metrics'],
                  ].map(([key, label]) => (
                    <button
                      key={key}
                      onClick={() => handleExport(key)}
                      className="block w-full text-left rounded px-2.5 py-1.5 text-xs text-[#1c1b1a] hover:bg-[#f7f3ef] transition-colors"
                    >
                      {label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Hairline Divider */}
            <div className="h-5 w-px bg-[#bec9c7]/40 mx-1"></div>

            {/* Workspace & Senior Partner Avatar */}
            <div className="flex items-center gap-2.5 pl-1 cursor-pointer group">
              <div className="text-right hidden xl:block">
                <p className="text-[11px] font-semibold text-[#1c1b1a] tracking-wider uppercase group-hover:text-[#11615f] transition-colors">
                  Private Wealth
                </p>
                <p className="text-[10px] text-[#6f7978]">Meridian Advisory</p>
              </div>
              <div className="w-8 h-8 rounded-full overflow-hidden border border-[#bec9c7]/60 shrink-0 bg-[#ece7e4]">
                <img
                  alt="Senior Partner Avatar"
                  className="w-full h-full object-cover"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuALfNv4Zd2vMXK8JKFz6H9ixq2B0x5dlXTGEPlwSDHFhFduPFjKQFGTMRHHxbgbak8Ls6EM1SNsSwicVqh3NDGlDxZeW-I4dzQ2Z0G7ld7bYH-ruGwEl3cSYChtdMIA9Y5dpSg7AYs_SExouRC0bYJgoNmu3FarMsHPwZMklfjZJoZTmNIR42iTXGkSfFkEfqTSkQFzjCY7QqtsVjRF1bC-Ya81EvGWJTUUmgM0Wp4"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Global Expandable Filter Tray */}
        {filterDrawerOpen && (
          <div className="bg-[#f7f3ef] border-b border-[#bec9c7]/40 px-6 sm:px-10 py-3 transition-all architectural-shadow">
            <div className="w-full max-w-[1440px] mx-auto flex flex-wrap items-center justify-between gap-4 text-xs">
              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-1.5 rounded border border-[#bec9c7]/60 bg-white px-2.5 py-1">
                  <Calendar className="h-3.5 w-3.5 text-[#6f7978]" />
                  <span className="text-[#6f7978]">From</span>
                  <input
                    type="date"
                    value={filters.start_date}
                    onChange={(e) => setFilters((f) => ({ ...f, start_date: e.target.value }))}
                    className="bg-transparent font-medium text-[#1c1b1a] outline-none"
                  />
                  <span className="text-[#6f7978]">to</span>
                  <input
                    type="date"
                    value={filters.end_date}
                    onChange={(e) => setFilters((f) => ({ ...f, end_date: e.target.value }))}
                    className="bg-transparent font-medium text-[#1c1b1a] outline-none"
                  />
                </div>

                <select
                  aria-label="Filter by segment"
                  value={filters.segment}
                  onChange={(e) => setFilters((f) => ({ ...f, segment: e.target.value }))}
                  className="rounded border border-[#bec9c7]/60 bg-white px-2.5 py-1 text-[#1c1b1a] outline-none font-medium"
                >
                  <option value="All">All Client Segments</option>
                  {options?.segments.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>

                <select
                  aria-label="Filter by asset tier"
                  value={filters.asset_tier}
                  onChange={(e) => setFilters((f) => ({ ...f, asset_tier: e.target.value }))}
                  className="rounded border border-[#bec9c7]/60 bg-white px-2.5 py-1 text-[#1c1b1a] outline-none font-medium"
                >
                  <option value="All">All Asset Tiers</option>
                  {options?.asset_tiers.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>

                <select
                  aria-label="Filter by region"
                  value={filters.region}
                  onChange={(e) => setFilters((f) => ({ ...f, region: e.target.value }))}
                  className="rounded border border-[#bec9c7]/60 bg-white px-2.5 py-1 text-[#1c1b1a] outline-none font-medium"
                >
                  <option value="All">All Regions</option>
                  {options?.regions.map((r) => (
                    <option key={r} value={r}>
                      {r} Region
                    </option>
                  ))}
                </select>

                <select
                  aria-label="Filter by team"
                  value={filters.team_id}
                  onChange={(e) => setFilters((f) => ({ ...f, team_id: e.target.value }))}
                  className="rounded border border-[#bec9c7]/60 bg-white px-2.5 py-1 text-[#1c1b1a] outline-none font-medium"
                >
                  <option value="All">All Advisor Teams</option>
                  {options?.teams.map((t) => (
                    <option key={t.team_id} value={t.team_id}>
                      {t.team_id} — {t.team_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={resetFilters}
                  className="inline-flex items-center gap-1 rounded border border-[#bec9c7]/60 bg-white px-2.5 py-1 text-[#6f7978] hover:text-[#1c1b1a] transition-colors"
                >
                  <RotateCcw className="h-3 w-3" />
                  <span>Reset</span>
                </button>
                <button
                  onClick={() => setFilterDrawerOpen(false)}
                  className="rounded bg-[#11615f] text-white px-3 py-1 font-semibold text-[11px] tracking-wider uppercase hover:bg-[#337a78] transition-colors"
                >
                  Apply & Close
                </button>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Main Content Area */}
      <main className="w-full max-w-[1440px] mx-auto px-6 sm:px-10 py-8 flex-1 flex flex-col gap-8">
        {children}
      </main>

      {/* Shared Footer / Colophon */}
      <footer className="border-t border-[#bec9c7]/30 bg-[#f7f3ef] py-6 text-[#3f4948] text-[11px]">
        <div className="w-full max-w-[1440px] mx-auto px-6 sm:px-10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-headline text-[16px] text-[#1c1b1a] uppercase tracking-tight font-medium">
              CONTINUUM
            </span>
            <span>•</span>
            <span>Client Experience Intelligence Studio</span>
            <span>•</span>
            <span className="text-[#6f7978]">Production Build v4.12.8</span>
          </div>
          <div className="flex items-center gap-6 text-[#6f7978]">
            <span>Meridian Private Wealth (Fictional Demo Environment)</span>
            <span>•</span>
            <span className="text-[#1c1b1a] font-medium">FINRA / SEC Supervisory Standards</span>
          </div>
        </div>
      </footer>

      {/* Global SQL Evidence Drawer for Transparent Calculations */}
      <SqlEvidenceDrawer />
    </div>
  );
}
