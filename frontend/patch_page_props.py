import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Fix Moon/Sun imports
if "Moon, Sun" not in content:
    content = content.replace("import { PieChart,", "import { Moon, Sun } from 'lucide-react';\nimport { PieChart,")

# Fix MetricCards props
content = content.replace(
    "<MetricCards data={summaryData} simulationSavings={simResult?.net_savings || null} />",
    "<MetricCards totalRevenue={summaryData.total_revenue} revenueAtRisk={summaryData.revenue_at_risk} totalCustomers={summaryData.total_customers} avgChurnRisk={summaryData.avg_churn_risk} />"
)

# Fix RiskDonutChart props
old_donut = "<RiskDonutChart customers={customersData.customers.map(c => ({ churn_probability: c.churn_probability, monthly_charges: c.monthly_charges }))} />"
new_donut = """<RiskDonutChart 
                data={{
                  highRisk: customersData.customers.filter((c: any) => c.churn_probability > 0.75).length,
                  mediumRisk: customersData.customers.filter((c: any) => c.churn_probability > 0.5 && c.churn_probability <= 0.75).length,
                  lowRisk: customersData.customers.filter((c: any) => c.churn_probability <= 0.5).length,
                }} 
              />"""
content = content.replace(old_donut, new_donut)

# Fix RevenueAreaChart props
old_area = """<RevenueAreaChart simulationData={{
                  withoutIntervention: simResult ? simResult.projection_without_intervention : [],
                  withIntervention: simResult ? simResult.projection_with_intervention : []
                }} />"""
new_area = """<RevenueAreaChart 
                baselineRevenue={simResult ? simResult.projection_without_intervention : []} 
                retainedRevenue={simResult ? simResult.projection_with_intervention : []} 
              />"""
content = content.replace(old_area, new_area)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
