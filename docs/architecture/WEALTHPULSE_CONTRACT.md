# WealthPulse Integration Contract

CONTINUUM is designed as the complementary operational & client-lifecycle intelligence platform alongside **WealthPulse** (asset flows & portfolio performance).

## Canonical Shared Identifier Conventions
| Identifier | Format | Description |
| --- | --- | --- |
| `client_id` | `C-000001` .. `C-012000` | Synthetic household/client primary key |
| `advisor_id` | `ADV-001` .. `ADV-048` | Synthetic advisor primary key |
| `team_id` | `T-01` .. `T-08` | Regional advisory team key |
| `observation_date` | `YYYY-MM-DD` (ISO 8601) | Reporting as-of date (`2026-10-31`) |
| `asset_tier` | `Tier 1 (<$250K)` .. `Tier 4 ($5M+)` | Standardized AUM tier |

## Future Integration Design
Joining WealthPulse net-flow tables with CONTINUUM `journey_stage_episodes` and `service_cases` on `(client_id, observation_date)` enables tracking whether onboarding delays or early SLA breaches precede net asset outflows prior to formal account closure.
