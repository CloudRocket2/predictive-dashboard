import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Replace the whole MetricCards block
content = re.sub(
    r'<MetricCards.*?/>',
    r'<MetricCards totalRevenue={summary?.total_revenue || 0} revenueAtRisk={summary?.revenue_at_risk || 0} totalCustomers={summary?.total_customers || 0} avgChurnRisk={summary?.avg_churn_risk || 0} />',
    content,
    flags=re.DOTALL,
    count=1
)

# Replace RiskDonutChart block
content = re.sub(
    r'<RiskDonutChart.*?/>',
    r"""<RiskDonutChart 
              data={{
                highRisk: customersData?.customers.filter((c: any) => c.churn_probability > 0.75).length || 0,
                mediumRisk: customersData?.customers.filter((c: any) => c.churn_probability > 0.5 && c.churn_probability <= 0.75).length || 0,
                lowRisk: customersData?.customers.filter((c: any) => c.churn_probability <= 0.5).length || 0,
              }} 
            />""",
    content,
    flags=re.DOTALL,
    count=1
)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
