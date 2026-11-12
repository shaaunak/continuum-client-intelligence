export interface FilterState {
  start_date: string;
  end_date: string;
  segment: string;
  team_id: string;
  region: string;
  asset_tier: string;
}

export interface KpiCardData {
  key: string;
  label: string;
  value: number;
  previous_value: number | null;
  change: number | null;
  change_unit: string;
  unit: string;
  direction: 'up' | 'down' | 'flat';
  favorable_direction: 'up' | 'down';
  tooltip: string;
  drilldown_route: string;
  numerator: number | null;
  denominator: number | null;
}

export interface FrictionSignal {
  id: string;
  title: string;
  metric_value: string;
  delta_label: string;
  severity: 'risk' | 'warning' | 'ok';
  evidence: string;
  route: string;
}

export interface ExecutiveInsight {
  category: string;
  headline: string;
  supporting_evidence: string;
  related_outcome: string;
  next_action: string;
  route: string;
}

export interface OverviewResponse {
  period: { start_date: string; end_date: string };
  comparison_period: { start_date: string; end_date: string };
  kpis: KpiCardData[];
  friction_signals: FrictionSignal[];
  insights: ExecutiveInsight[];
  narrative: {
    what_changed: string;
    who_was_affected: string;
    what_to_investigate_next: string;
  };
}

export interface MetricLineage {
  metric_key: string;
  kpi_name: string;
  business_meaning: string;
  formula: string;
  numerator: string;
  denominator: string;
  time_basis: string;
  inclusion_criteria: string;
  exclusions: string;
  data_source: string;
  sql_query: string;
  known_limitations: string;
  as_of_date: string;
}
