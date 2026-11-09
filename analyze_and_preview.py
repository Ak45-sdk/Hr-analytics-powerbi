"""Compute headline HR metrics from the cleaned data (mirrors the DAX logic) and
render preview charts. Run after generate_data.py.
Preview PNGs are matplotlib mock-ups of the report pages, NOT Power BI screenshots.
"""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(__file__), "..")
RAW = f"{BASE}/data/raw"
OUT = f"{BASE}/screenshots"
os.makedirs(OUT, exist_ok=True)

emp = pd.read_csv(f"{RAW}/employees.csv", parse_dates=["HireDate", "TerminationDate"]).drop_duplicates("EmployeeID")
emp["Department"] = emp.Department.str.title().replace({"Hr": "HR"})
emp["JobRole"] = emp.JobRole.str.strip()
emp["Gender"] = emp.Gender.str.title()
emp["AnnualSalary"] = emp.groupby(["Department", "JobRole"]).AnnualSalary.transform(lambda s: s.fillna(s.median()))
rec = pd.read_csv(f"{RAW}/recruitment.csv", parse_dates=["ApplicationDate", "HireDate", "RequisitionDate"])
perf = pd.read_csv(f"{RAW}/performance.csv")
sat = pd.read_csv(f"{RAW}/satisfaction.csv", parse_dates=["SurveyDate"])

TODAY = pd.Timestamp("2026-09-30")
active = emp[emp.EmploymentStatus == "Active"]
left = emp[emp.EmploymentStatus == "Resigned"]

def stat(label, v):
    print(f"{label}: {v}")

stat("Total employees (ever)", len(emp))
stat("Active", len(active))
stat("Resigned", len(left))
stat("Attrition rate overall", round(len(left) / len(emp) * 100, 1))
stat("Avg salary (active)", round(active.AnnualSalary.mean()))
stat("Avg performance", round(perf.PerformanceRating.mean(), 2))
stat("Avg satisfaction", round(sat.OverallSatisfaction.mean(), 2))

# last 12 months
l12 = TODAY - pd.DateOffset(months=12)
hires12 = emp[emp.HireDate > l12]
left12 = left[left.TerminationDate > l12]
avg_hc = (len(active) + len(active) + len(left12) - len(hires12)) / 2
stat("Hires L12M", len(hires12))
stat("Exits L12M", len(left12))
stat("Attrition L12M %", round(len(left12) / avg_hc * 100, 1))

# recruitment
apps = len(rec)
funnel = {s: (rec.FinalStage.isin(order)).sum() for s, order in {
    "Applied": ["Applied", "Screened", "Interviewed", "Offered", "Hired"],
    "Screened": ["Screened", "Interviewed", "Offered", "Hired"],
    "Interviewed": ["Interviewed", "Offered", "Hired"],
    "Offered": ["Offered", "Hired"],
    "Hired": ["Hired"]}.items()}
print("Funnel", funnel)
rec["TimeToHire"] = (rec.HireDate - rec.RequisitionDate).dt.days
stat("Recruitment success rate % (hires/applicants)", round(funnel["Hired"] / apps * 100, 2))
stat("Avg time to hire (days)", round(rec.TimeToHire.mean(), 1))
stat("Offer accept rate %", round(funnel["Hired"] / funnel["Offered"] * 100, 1))

# department table
d = emp.groupby("Department").agg(
    Employees=("EmployeeID", "count"), Active=("EmploymentStatus", lambda s: (s == "Active").sum()),
    Left=("EmploymentStatus", lambda s: (s == "Resigned").sum()), AvgSalary=("AnnualSalary", "mean"))
d["AttritionPct"] = d.Left / d.Employees * 100
pf = perf.merge(emp[["EmployeeID", "Department"]], on="EmployeeID").groupby("Department").PerformanceRating.mean()
sf = sat.merge(emp[["EmployeeID", "Department"]], on="EmployeeID").groupby("Department").OverallSatisfaction.mean()
d["AvgPerf"] = pf
d["AvgSat"] = sf
d["PayrollCr"] = active.groupby("Department").AnnualSalary.sum() / 1e7
print(d.round(2).sort_values("AttritionPct", ascending=False))

print("\nReasons:\n", left.ReasonForLeaving.value_counts(normalize=True).round(3) * 100)
fac = sat.merge(emp[["EmployeeID", "EmploymentStatus"]], on="EmployeeID")
print("\nSatisfaction factors by status:\n", fac.groupby("EmploymentStatus")[["WorkLifeBalance", "Compensation", "Management", "CareerGrowth", "WorkEnvironment"]].mean().round(2))
left_ten = ((left.TerminationDate - left.HireDate).dt.days / 365)
stat("Share of exits within 2 yrs of hire %", round((left_ten < 2).mean() * 100, 1))
print("\nGender avg salary:\n", active.groupby("Gender").AnnualSalary.mean().round(0))
print("\nSource -> hire rate:\n", (rec.assign(h=rec.FinalStage.eq("Hired")).groupby("Source").h.mean() * 100).round(2))

# yearly hires for forecast
hy = emp.groupby(emp.HireDate.dt.year).size()
print("\nHires by year:\n", hy.loc[2022:])

# ---------------- preview charts ----------------
NAVY, TEAL, AMBER, RED, GREY = "#1F3A5F", "#2A9D8F", "#E9A23B", "#D1495B", "#8A94A6"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

# Page 1 executive overview
fig = plt.figure(figsize=(14, 8), facecolor="white")
fig.suptitle("HR Analytics – Executive Overview (preview mock-up)", fontsize=15, color=NAVY, x=0.02, ha="left")
kpis = [("Active Employees", f"{len(active)}"), ("New Hires (L12M)", f"{len(hires12)}"),
        ("Attrition Rate (L12M)", f"{len(left12)/avg_hc*100:.1f}%"), ("Avg Salary", f"₹{active.AnnualSalary.mean()/1e5:.1f}L"),
        ("Avg Performance", f"{perf.PerformanceRating.mean():.2f}/5")]
for i, (k, v) in enumerate(kpis):
    ax = fig.add_axes([0.02 + i * 0.196, 0.80, 0.18, 0.11]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#F2F5F9", transform=ax.transAxes))
    ax.text(0.5, 0.62, v, ha="center", fontsize=19, color=NAVY, weight="bold")
    ax.text(0.5, 0.18, k, ha="center", fontsize=9, color=GREY)
ax = fig.add_axes([0.11, 0.42, 0.23, 0.3]); s = active.Department.value_counts().sort_values()
ax.barh(s.index, s.values, color=NAVY); ax.set_title("Employees by Department", loc="left", color=NAVY)
ax = fig.add_axes([0.38, 0.42, 0.34, 0.3])
m_h = emp[emp.HireDate >= "2024-01-01"].groupby(emp.HireDate.dt.to_period("M")).size()
m_l = left[left.TerminationDate >= "2024-01-01"].groupby(left.TerminationDate.dt.to_period("M")).size()
idx = pd.period_range("2024-01", "2026-09", freq="M")
ax.plot(range(len(idx)), m_h.reindex(idx, fill_value=0).values, color=TEAL, label="Hires")
ax.plot(range(len(idx)), m_l.reindex(idx, fill_value=0).values, color=RED, label="Exits")
ax.set_xticks(range(0, len(idx), 6)); ax.set_xticklabels([str(p) for p in idx[::6]]); ax.legend(frameon=False)
ax.set_title("Monthly Hiring vs Attrition", loc="left", color=NAVY)
ax = fig.add_axes([0.78, 0.40, 0.2, 0.34]); g = active.Gender.value_counts()
ax.pie(g.values, labels=g.index, colors=[NAVY, TEAL, AMBER], wedgeprops=dict(width=0.45), autopct="%1.0f%%")
ax.set_title("Gender Mix", loc="left", color=NAVY)
ax = fig.add_axes([0.11, 0.06, 0.33, 0.25]); dd = d.sort_values("AvgPerf")
ax.barh(dd.index, dd.AvgPerf, color=TEAL); ax.set_xlim(2.5, 4); ax.set_title("Avg Performance by Department", loc="left", color=NAVY)
ax = fig.add_axes([0.55, 0.06, 0.4, 0.25]); dd = d.sort_values("AttritionPct")
ax.barh(dd.index, dd.AttritionPct, color=[RED if v > 25 else GREY for v in dd.AttritionPct])
ax.set_title("Attrition % by Department (cumulative)", loc="left", color=NAVY)
fig.savefig(f"{OUT}/01_executive_overview_preview.png", dpi=110); plt.close(fig)

# Page 2 recruitment funnel + forecast
fig, axs = plt.subplots(1, 2, figsize=(14, 5))
st = list(funnel); vals = list(funnel.values())
axs[0].barh(st[::-1], vals[::-1], color=[TEAL, AMBER, NAVY, GREY, NAVY][::-1][:5])
for i, v in enumerate(vals[::-1]): axs[0].text(v, i, f" {v:,}", va="center")
axs[0].set_title("Recruitment Funnel", loc="left", color=NAVY)
hm = emp[emp.HireDate >= "2022-01-01"].groupby(emp.HireDate.dt.to_period("Q")).size()
x = np.arange(len(hm)); co = np.polyfit(x, hm.values, 1)
fx = np.arange(len(hm), len(hm) + 4)
axs[1].plot(x, hm.values, color=NAVY, marker="o", label="Actual hires")
axs[1].plot(fx, np.polyval(co, fx), color=AMBER, ls="--", marker="o", label="Forecast (linear trend)")
axs[1].set_xticks(list(x[::3]) + list(fx[::3])); axs[1].set_xticklabels([str(p) for p in hm.index[::3]] + ["+1Q", "+4Q"][: len(fx[::3])])
axs[1].legend(frameon=False); axs[1].set_title("Quarterly Hires & Forecast", loc="left", color=NAVY)
fig.suptitle("Recruitment & Predictive Hiring (preview mock-up)", color=NAVY, x=0.02, ha="left")
fig.savefig(f"{OUT}/02_recruitment_forecast_preview.png", dpi=110); plt.close(fig)
print("\nQuarterly forecast next 4Q:", np.round(np.polyval(co, fx)).astype(int))
