"""Generate synthetic HR data for the Power BI HR Analytics project.
Run: python generate_data.py  -> writes CSVs into ../data/raw
All data is fictional. Seeded for reproducibility.
"""
import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUT, exist_ok=True)

# ---------- reference data ----------
DEPTS = {
    # dept: (headcount weight, base salary, attrition prob multiplier, perf mean)
    "Engineering": (0.28, 1_100_000, 1.0, 3.5),
    "Sales": (0.20, 800_000, 1.6, 3.2),
    "Customer Support": (0.15, 520_000, 1.8, 3.1),
    "Marketing": (0.08, 750_000, 1.1, 3.4),
    "Finance": (0.07, 900_000, 0.7, 3.6),
    "HR": (0.05, 700_000, 0.8, 3.5),
    "Operations": (0.12, 640_000, 1.2, 3.3),
    "Product": (0.05, 1_250_000, 0.9, 3.7),
}
ROLES = {
    "Engineering": ["Software Engineer", "Senior Engineer", "QA Engineer", "DevOps Engineer", "Data Analyst"],
    "Sales": ["Sales Executive", "Account Manager", "Sales Manager"],
    "Customer Support": ["Support Associate", "Support Lead"],
    "Marketing": ["Marketing Executive", "Content Specialist", "Brand Manager"],
    "Finance": ["Accountant", "Financial Analyst"],
    "HR": ["HR Executive", "Recruiter", "HR Manager"],
    "Operations": ["Operations Executive", "Operations Manager", "Logistics Coordinator"],
    "Product": ["Product Analyst", "Product Manager"],
}
ROLE_MULT = {r: m for d in ROLES for r, m in zip(ROLES[d], np.linspace(0.8, 1.6, len(ROLES[d])))}
EDU = ["High School", "Bachelor's", "Master's", "PhD"]
EDU_W = [0.08, 0.57, 0.31, 0.04]
EDU_MULT = {"High School": 0.85, "Bachelor's": 1.0, "Master's": 1.15, "PhD": 1.3}
REASONS = ["Better Compensation", "Career Growth", "Poor Management", "Work-Life Balance",
           "Relocation", "Higher Studies", "Retirement", "Personal Reasons"]
SOURCES = ["LinkedIn", "Referral", "Job Portal", "Company Website", "Campus", "Agency"]

TODAY = date(2026, 9, 30)
START = date(2022, 1, 1)


def rand_date(a, b):
    return a + timedelta(days=random.randint(0, (b - a).days))


# ---------- employees ----------
N = 620
dept_names = list(DEPTS)
dept_w = [DEPTS[d][0] for d in dept_names]
rows = []
for i in range(1, N + 1):
    d = random.choices(dept_names, dept_w)[0]
    role = random.choice(ROLES[d])
    edu = random.choices(EDU, EDU_W)[0]
    gender = random.choices(["Male", "Female", "Non-binary"], [0.54, 0.43, 0.03])[0]
    age = int(np.clip(np.random.normal(33, 7), 21, 60))
    # hires skewed toward recent years (company growing)
    if random.random() < 0.35:
        hire = rand_date(date(2015, 1, 1), date(2021, 12, 31))
    else:
        hire = rand_date(START, TODAY)
    exp = int(np.clip(age - 22 - random.randint(0, 4) + np.random.randint(-2, 3), 0, 35))
    salary = DEPTS[d][1] * ROLE_MULT[role] * EDU_MULT[edu] * (1 + exp * 0.018) * np.random.normal(1, 0.06)
    if gender == "Female" and random.random() < 0.4:
        salary *= 0.97  # mild pay-gap signal for analysis
    salary = round(salary, -3)

    # attrition: higher in first 2 yrs, low pay, high-attrition depts
    tenure_years = (TODAY - hire).days / 365
    p = 0.16 * DEPTS[d][2]
    if tenure_years < 2:
        p *= 1.4
    p *= 1.25 if salary < DEPTS[d][1] * 0.95 else 1.0
    left = random.random() < p and tenure_years > 0.25
    term = None
    reason = None
    if left:
        term = hire + timedelta(days=random.randint(90, max(91, int((TODAY - hire).days))))
        term = min(term, TODAY)
        reason = random.choices(REASONS, [0.24, 0.20, 0.14, 0.14, 0.08, 0.08, 0.04, 0.08])[0]
        if d in ("Sales", "Customer Support") and random.random() < 0.3:
            reason = "Poor Management"
    rows.append(dict(
        EmployeeID=f"E{i:04d}", Gender=gender, Age=age, Education=edu, Department=d, JobRole=role,
        HireDate=hire, TerminationDate=term, ReasonForLeaving=reason,
        EmploymentType=random.choices(["Full-Time", "Part-Time", "Contract"], [0.82, 0.06, 0.12])[0],
        ExperienceYears=exp, AnnualSalary=salary,
    ))
emp = pd.DataFrame(rows)
emp["EmploymentStatus"] = np.where(emp.TerminationDate.isna(), "Active", "Resigned")

# introduce a few realistic data-quality issues so Power Query has real cleaning work
emp.loc[emp.sample(8, random_state=1).index, "Department"] = emp.Department.str.upper()
emp.loc[emp.sample(6, random_state=2).index, "Gender"] = emp.Gender.str.lower()
emp.loc[emp.sample(5, random_state=3).index, "JobRole"] = "  " + emp.JobRole + " "
emp.loc[emp.sample(7, random_state=4).index, "AnnualSalary"] = np.nan
emp = pd.concat([emp, emp.sample(3, random_state=5)])  # duplicate rows
emp.to_csv(f"{OUT}/employees.csv", index=False)

# clean copy used below
clean = emp.drop_duplicates("EmployeeID").copy()
clean["Department"] = clean.Department.str.title().replace({"Hr": "HR"})
clean["JobRole"] = clean.JobRole.str.strip()
clean["Gender"] = clean.Gender.str.title()

# ---------- recruitment ----------
rec = []
app_id = 1
for month_start in pd.date_range("2022-01-01", "2026-09-01", freq="MS"):
    growth = 1 + (month_start.year - 2022) * 0.12
    for d in dept_names:
        reqs = np.random.poisson(1.1 * DEPTS[d][0] * 10 * growth / 3)
        for _ in range(reqs):
            role = random.choice(ROLES[d])
            req_date = month_start + timedelta(days=random.randint(0, 27))
            n_app = np.random.randint(12, 45)
            hired = False
            for a in range(n_app):
                src = random.choices(SOURCES, [0.25, 0.15, 0.25, 0.12, 0.08, 0.15])[0]
                apply_date = req_date + timedelta(days=random.randint(1, 30))
                stage = "Applied"
                if random.random() < 0.45:
                    stage = "Screened"
                    if random.random() < 0.55:
                        stage = "Interviewed"
                        if random.random() < 0.28 and not hired:
                            stage = "Offered"
                            if random.random() < 0.8:
                                stage = "Hired"
                                hired = True
                hire_date = None
                if stage == "Hired":
                    hire_date = apply_date + timedelta(days=random.randint(18, 60))
                rec.append(dict(ApplicationID=f"A{app_id:06d}", RequisitionDate=req_date.date(),
                                Department=d, JobRole=role, ApplicationDate=apply_date.date(),
                                Source=src, FinalStage=stage,
                                HireDate=hire_date.date() if hire_date else None))
                app_id += 1
rec = pd.DataFrame(rec)
rec.to_csv(f"{OUT}/recruitment.csv", index=False)

# ---------- performance (annual) ----------
perf = []
for _, e in clean.iterrows():
    end_year = (e.TerminationDate.year if pd.notna(e.TerminationDate) else 2025)
    for y in range(max(e.HireDate.year + 1, 2022), min(end_year, 2025) + 1):
        base = DEPTS[e.Department][3] + 0.04 * min(e.ExperienceYears, 10) - 0.4
        r = int(np.clip(round(np.random.normal(base, 0.7)), 1, 5))
        perf.append(dict(EmployeeID=e.EmployeeID, ReviewYear=y, PerformanceRating=r))
pd.DataFrame(perf).to_csv(f"{OUT}/performance.csv", index=False)

# ---------- satisfaction survey (2 per year) ----------
sat = []
for _, e in clean.iterrows():
    for sd in [date(2024, 6, 30), date(2024, 12, 31), date(2025, 6, 30), date(2025, 12, 31), date(2026, 6, 30)]:
        if sd < e.HireDate + timedelta(days=60):
            continue
        if pd.notna(e.TerminationDate) and sd > e.TerminationDate:
            continue
        low_pay = e.AnnualSalary < DEPTS[e.Department][1] * 0.95 if pd.notna(e.AnnualSalary) else False
        base = 3.6 - (0.5 if e.Department in ("Sales", "Customer Support") else 0) - (0.3 if low_pay else 0)
        f = {k: int(np.clip(round(np.random.normal(base + o, 0.9)), 1, 5)) for k, o in
             {"WorkLifeBalance": -0.15, "Compensation": -0.3 if low_pay else 0.0, "Management": 0.0,
              "CareerGrowth": -0.2, "WorkEnvironment": 0.3}.items()}
        f["OverallSatisfaction"] = int(round(np.mean(list(f.values()))))
        sat.append(dict(EmployeeID=e.EmployeeID, SurveyDate=sd, **f))
pd.DataFrame(sat).to_csv(f"{OUT}/satisfaction.csv", index=False)

# ---------- departments dimension ----------
pd.DataFrame({
    "Department": dept_names,
    "DepartmentHead": ["A. Rao", "S. Mehta", "P. Nair", "K. Iyer", "R. Gupta", "M. Das", "V. Shah", "T. Khan"],
    "BudgetedHeadcount": [190, 130, 100, 55, 45, 32, 80, 35],
}).to_csv(f"{OUT}/departments.csv", index=False)

# ---------- dim date ----------
dd = pd.DataFrame({"Date": pd.date_range("2015-01-01", "2027-12-31")})
dd.to_csv(f"{OUT}/calendar.csv", index=False)

print("employees", len(clean), "applications", len(rec), "performance", len(perf), "survey", len(sat))
