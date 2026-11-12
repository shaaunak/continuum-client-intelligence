import { Link } from 'react-router-dom';
import { ArrowRight, Compass, Shield, Activity, BarChart3, Database } from 'lucide-react';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#fdf9f5] text-[#1c1b1a] flex flex-col justify-between selection:bg-[#a9efec] selection:text-[#00201f]">
      {/* Top Header */}
      <header className="border-b border-[#bec9c7]/30 bg-[#fdf9f5]">
        <div className="w-full max-w-[1440px] mx-auto px-6 sm:px-10 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-[#11615f] text-white flex items-center justify-center rounded text-[11px] font-bold tracking-widest">
              C
            </div>
            <span className="font-headline text-[22px] tracking-tight uppercase font-medium">
              CONTINUUM
            </span>
          </div>
          <div className="flex items-center gap-4 text-xs font-semibold uppercase tracking-wider">
            <span className="text-[#6f7978] hidden sm:inline">Meridian Private Wealth</span>
            <Link
              to="/overview"
              className="rounded bg-[#11615f] text-white px-4 py-2 hover:bg-[#337a78] transition-colors"
            >
              Enter Studio
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Narrative */}
      <main className="w-full max-w-[1440px] mx-auto px-6 sm:px-10 py-16 flex-1 flex flex-col justify-center">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded bg-[#ffd9de]/50 border border-[#864e59]/30 text-[#864e59] text-[10px] font-bold uppercase tracking-widest mb-6">
            <span>Synthetic Demonstration Environment</span>
          </div>
          <h1 className="font-headline text-5xl sm:text-6xl text-[#1c1b1a] tracking-tight leading-[1.1] mb-6 font-normal">
            From client journeys to better decisions.
          </h1>
          <p className="font-headline text-2xl text-[#3f4948] font-normal leading-relaxed mb-8">
            An end-to-end wealth management intelligence studio connecting observation, root-cause investigation, and measurable retention outcomes.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <Link
              to="/overview"
              className="inline-flex items-center gap-2 rounded bg-[#11615f] text-white px-6 py-3 text-xs font-bold uppercase tracking-wider hover:bg-[#337a78] transition-colors shadow-sm"
            >
              <span>Explore Executive Overview</span>
              <ArrowRight className="h-4 w-4 text-[#a9efec]" />
            </Link>
            <Link
              to="/journeys"
              className="inline-flex items-center gap-2 rounded border border-[#bec9c7]/60 bg-white text-[#1c1b1a] px-6 py-3 text-xs font-bold uppercase tracking-wider hover:bg-[#f7f3ef] transition-colors"
            >
              <span>Inspect Journey Topology</span>
            </Link>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 pt-12 border-t border-[#bec9c7]/30">
          <div className="p-6 rounded border border-[#bec9c7]/30 bg-white architectural-shadow">
            <div className="w-8 h-8 rounded bg-[#11615f]/10 text-[#11615f] flex items-center justify-center mb-3">
              <Activity className="h-4 w-4" />
            </div>
            <h3 className="font-headline text-lg font-semibold text-[#1c1b1a] mb-1">
              Multi-Track Journey Fabric
            </h3>
            <p className="text-xs text-[#3f4948] leading-relaxed">
              Seven-stage episode topology isolating KYC rework loops, funding delays, and portfolio activation velocity.
            </p>
          </div>

          <div className="p-6 rounded border border-[#bec9c7]/30 bg-white architectural-shadow">
            <div className="w-8 h-8 rounded bg-[#864e59]/10 text-[#864e59] flex items-center justify-center mb-3">
              <Shield className="h-4 w-4" />
            </div>
            <h3 className="font-headline text-lg font-semibold text-[#1c1b1a] mb-1">
              Actuarial Retention Studio
            </h3>
            <p className="text-xs text-[#3f4948] leading-relaxed">
              Maturity-aware cohort heatmaps, Day-90 landmark survival curves, and confounding-adjusted Cox models.
            </p>
          </div>

          <div className="p-6 rounded border border-[#bec9c7]/30 bg-white architectural-shadow">
            <div className="w-8 h-8 rounded bg-[#876b38]/10 text-[#876b38] flex items-center justify-center mb-3">
              <Compass className="h-4 w-4" />
            </div>
            <h3 className="font-headline text-lg font-semibold text-[#1c1b1a] mb-1">
              Scenario &amp; Impact Parity
            </h3>
            <p className="text-xs text-[#3f4948] leading-relaxed">
              Interactive financial simulation with exact formula parity against synchronized Excel workbook exports.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#bec9c7]/30 bg-[#f7f3ef] py-6 text-xs text-[#6f7978]">
        <div className="w-full max-w-[1440px] mx-auto px-6 sm:px-10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-headline text-base text-[#1c1b1a] uppercase font-semibold">CONTINUUM</span>
            <span>•</span>
            <span>Client Experience Intelligence Studio</span>
          </div>
          <div>All client, advisor, and financial data are 100% synthetic (seed=20270101).</div>
        </div>
      </footer>
    </div>
  );
}
