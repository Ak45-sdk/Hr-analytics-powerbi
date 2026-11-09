# Insights & Recommendations

> Figures below come from the **synthetic** dataset in `data/raw` (seed 42) and will match the report when it is built from these files. Re-validate if you regenerate or replace the data.

## Headline metrics
| Metric | Value |
|---|---|
| Active employees (30 Sep 2026) | 488 (620 ever employed) |
| Hires, last 12 months | 95 |
| Exits, last 12 months | 67 |
| Attrition rate (L12M, annualised) | 14.1 % (cumulative across all years: 21.3 %) |
| Average salary (active) | ₹12.7 L |
| Average performance rating | 3.25 / 5 |
| Average satisfaction | 3.38 / 5 |
| Applicants → hires | 7,717 → 201 (2.6 % success rate) |
| Offer acceptance rate | 78.5 % |
| Average time to hire | ≈ 52 days |
| Exits within 2 years of joining | 66.7 % of all exits |

## Key insights
1. **Attrition is concentrated in front-line departments.** Customer Support (32 % cumulative) and Sales (27 %) lose the most people; Marketing (15 %), HR (15 %) and Engineering (16 %) are the most stable.
2. **Early-tenure churn is the biggest leak.** Two-thirds of leavers exit within two years of joining, which points to onboarding and role-fit problems rather than long-term burnout.
3. **Top reasons for leaving:** career growth (≈ 24 %), better compensation (≈ 19 %), poor management (≈ 19 %) and work-life balance (≈ 17 %) – together ~78 % of exits, and all are addressable by HR policy.
4. **Satisfaction is lowest where attrition is highest.** Customer Support (3.03) and Sales (3.01) score well below the company average; *career growth* (3.18) is the weakest factor company-wide and *work environment* (3.65) the strongest.
5. **Recruitment is efficient at the bottom of the funnel but slow overall.** Offers are accepted 78 % of the time, but only 2.6 % of applicants convert and requisition-to-hire takes ~52 days. Campus (3.4 %) and agency (3.3 %) sources convert best; the company website converts worst (1.7 %).
6. **Hiring volume is flat (~75–95 hires/year)**, so headcount growth depends on how quickly attrition is brought down; a linear trend forecast projects ~24 hires per quarter.
7. **Performance is highest in Product (3.76) and HR (3.50), lowest in Customer Support (3.03) and Sales (3.06)** – the same departments with low satisfaction and high attrition, which suggests a management/engagement issue rather than a talent issue.
8. **Pay equity check:** average female salary is ~1 % below male in this dataset – small, but worth testing after controlling for role and experience.

## Recommendations
**Retention**
- Launch a 90-day onboarding and buddy programme for Support and Sales; track 6-month retention as a KPI.
- Introduce career-ladder frameworks and internal mobility postings (career growth is the #1 exit reason).
- Run a compensation benchmark for Support/Sales roles paid below department median (low pay raises both attrition and low satisfaction scores).
- Manager-effectiveness training and quarterly pulse surveys for teams with satisfaction < 3.2.

**Recruitment**
- Shift budget toward campus and referral channels (higher conversion); review the careers-page experience.
- Target ≤ 40 days time-to-hire: parallelise screening/interviews, set stage SLAs, pre-build talent pools for Support/Sales.
- Track cost per hire and source quality (retention of hires by source) – replace the placeholder assumption in the model.

**Workforce planning**
- Plan for ~65–70 replacement hires + gap-to-budget hires over the next 12 months; use the what-if attrition parameter to quantify savings if attrition falls by 10–20 %.
- Estimated attrition cost (50 % of salary assumption) ≈ ₹4.2 Cr over the last 12 months – use it to build the business case for retention spend.

**Performance**
- Share Product/HR practices (goal-setting, feedback cadence) with Support and Sales; introduce performance-improvement plans with coaching, not only exits.

## Limitations
- Synthetic data; patterns were designed to be plausible, not empirical.
- Forecast is a trend extrapolation (Power BI exponential smoothing / linear trend) – a starting point, not a hiring plan.
- Cost-of-attrition and cost-per-hire use stated assumptions.
