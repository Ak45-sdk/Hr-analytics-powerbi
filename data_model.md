# Data Model

Star schema with `Employees` as the central dimension-like table and `Calendar` as the shared date dimension.

```
                         Departments (dim)
                               │ 1
                               │ Department
                               ▼ *
 Calendar (dim) ──1:*── Employees ──1:*── Performance
   │  Date ─ HireDate (active)   │ EmployeeID
   │  Date ─ TerminationDate     └──1:*── Satisfaction ──1:*── Satisfaction_Factors (via EmployeeID+SurveyDate, or use the unpivoted query directly with EmployeeID)
   │  (inactive)
   ├──1:*── Recruitment (Date ─ RequisitionDate, active)
   │
 FunnelStages (disconnected helper)      _Measures (disconnected, holds all DAX)
```

| Relationship | Cardinality | Filter direction | Active |
|---|---|---|---|
| Calendar[Date] → Employees[HireDate] | 1:* | Single | Yes |
| Calendar[Date] → Employees[TerminationDate] | 1:* | Single | **No** (used via `USERELATIONSHIP`) |
| Calendar[Date] → Recruitment[RequisitionDate] | 1:* | Single | Yes |
| Calendar[Date] → Performance[ReviewDate] | 1:* | Single | Yes |
| Calendar[Date] → Satisfaction[SurveyDate] | 1:* | Single | Yes |
| Departments[Department] → Employees[Department] | 1:* | Single | Yes |
| Departments[Department] → Recruitment[Department] | 1:* | Single | Yes |
| Employees[EmployeeID] → Performance[EmployeeID] | 1:* | Single | Yes |
| Employees[EmployeeID] → Satisfaction[EmployeeID] | 1:* | Single | Yes |
| Employees[EmployeeID] → Satisfaction_Factors[EmployeeID] | 1:* | Single | Yes |

Notes
- `Employees` contains both active and resigned people, so one table answers headcount, hiring and attrition questions.
- `Performance`/`Satisfaction` are filtered by employee attributes (department, gender, education) through `Employees`; no bi-directional filters are needed.
- Mark `Calendar` as the Date table (Table tools → Mark as date table → `Date`). Hide `Date`-key columns in fact tables.
- Hide helper columns; put all measures in `_Measures` with display folders.

## Data dictionary

| Table | Grain | Key columns |
|---|---|---|
| Employees | 1 row / employee | EmployeeID, Gender, Age, Education, Department, JobRole, HireDate, TerminationDate, ReasonForLeaving, EmploymentType, ExperienceYears, Salary, EmploymentStatus + derived TenureYears, AgeBand, ExperienceBand, TenureBand, SalaryBand |
| Recruitment | 1 row / application | ApplicationID, RequisitionDate, Department, JobRole, ApplicationDate, Source, FinalStage, StageNumber, HireDate, TimeToHireDays |
| Performance | 1 row / employee / year | EmployeeID, ReviewYear, PerformanceRating (1–5) |
| Satisfaction | 1 row / employee / survey | EmployeeID, SurveyDate, WorkLifeBalance, Compensation, Management, CareerGrowth, WorkEnvironment, OverallSatisfaction (1–5) |
| Departments | 1 row / department | Department, DepartmentHead, BudgetedHeadcount |

## Data-cleaning steps (Power Query)
1. Remove 3 duplicated employee rows (`Table.Distinct` on EmployeeID).
2. Standardise casing/whitespace in Department, Gender and JobRole (e.g. `ENGINEERING`, `male`, `"  Sales Executive "`).
3. Impute 7 missing salaries with the Department + JobRole median.
4. Set data types, validate ratings are within 1–5.
5. Add derived columns: TenureYears, AgeBand, ExperienceBand, TenureBand, SalaryBand, StageNumber, TimeToHireDays.
6. Unpivot satisfaction factors for the factor-analysis visual.
