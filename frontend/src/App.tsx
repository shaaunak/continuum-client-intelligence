import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { FilterProvider } from '@/hooks/useFilters';
import { LandingPage } from '@/features/overview/LandingPage';
import { ExecutiveOverviewPage } from '@/features/overview/ExecutiveOverviewPage';
import { JourneyAnalyticsPage } from '@/features/journeys/JourneyAnalyticsPage';
import { RetentionStudioPage } from '@/features/retention/RetentionStudioPage';
import { ClientExplorerPage } from '@/features/clients/ClientExplorerPage';
import { ClientDetailPage } from '@/features/clients/ClientDetailPage';
import { InvestigationLabPage } from '@/features/investigations/InvestigationLabPage';
import { ServiceOperationsPage } from '@/features/operations/ServiceOperationsPage';
import { AdvisorIntelligencePage } from '@/features/advisors/AdvisorIntelligencePage';
import { ImprovementRoadmapPage } from '@/features/roadmap/ImprovementRoadmapPage';
import { ImpactSimulatorPage } from '@/features/simulator/ImpactSimulatorPage';
import { KpiDictionaryPage } from '@/features/requirements/KpiDictionaryPage';
import { RequirementsHubPage } from '@/features/requirements/RequirementsHubPage';
import { DataQualityPage } from '@/features/requirements/DataQualityPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 2,
      retry: 1,
    },
  },
});

function ShellRoute({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <FilterProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/overview" element={<ShellRoute><ExecutiveOverviewPage /></ShellRoute>} />
            <Route path="/journeys" element={<ShellRoute><JourneyAnalyticsPage /></ShellRoute>} />
            <Route path="/retention" element={<ShellRoute><RetentionStudioPage /></ShellRoute>} />
            <Route path="/clients" element={<ShellRoute><ClientExplorerPage /></ShellRoute>} />
            <Route path="/clients/:clientId" element={<ShellRoute><ClientDetailPage /></ShellRoute>} />
            <Route path="/investigations" element={<ShellRoute><InvestigationLabPage /></ShellRoute>} />
            <Route path="/operations" element={<ShellRoute><ServiceOperationsPage /></ShellRoute>} />
            <Route path="/advisors" element={<ShellRoute><AdvisorIntelligencePage /></ShellRoute>} />
            <Route path="/roadmap" element={<ShellRoute><ImprovementRoadmapPage /></ShellRoute>} />
            <Route path="/simulator" element={<ShellRoute><ImpactSimulatorPage /></ShellRoute>} />
            <Route path="/kpi-dictionary" element={<ShellRoute><KpiDictionaryPage /></ShellRoute>} />
            <Route path="/requirements" element={<ShellRoute><RequirementsHubPage /></ShellRoute>} />
            <Route path="/data-quality" element={<ShellRoute><DataQualityPage /></ShellRoute>} />
            <Route path="*" element={<Navigate to="/overview" replace />} />
          </Routes>
        </BrowserRouter>
      </FilterProvider>
    </QueryClientProvider>
  );
}

export default App;
