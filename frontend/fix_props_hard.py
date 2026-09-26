import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# Fix MetricCards
content = re.sub(
    r'<MetricCards\s+data=\{summaryData\}\s+simulationSavings=\{simResult\?\.[^}]*\}\s*/>',
    r'<MetricCards totalRevenue={summaryData.total_revenue} revenueAtRisk={summaryData.revenue_at_risk} totalCustomers={summaryData.total_customers} avgChurnRisk={summaryData.avg_churn_risk} />',
    content,
    flags=re.DOTALL
)

# Fix RiskDonutChart
content = re.sub(
    r'<RiskDonutChart\s+customers=\{[^\}]*\}\s*/>',
    r"""<RiskDonutChart 
                data={{
                  highRisk: customersData.customers.filter((c: any) => c.churn_probability > 0.75).length,
                  mediumRisk: customersData.customers.filter((c: any) => c.churn_probability > 0.5 && c.churn_probability <= 0.75).length,
                  lowRisk: customersData.customers.filter((c: any) => c.churn_probability <= 0.5).length,
                }} 
              />""",
    content,
    flags=re.DOTALL
)

# Fix RevenueAreaChart
content = re.sub(
    r'<RevenueAreaChart\s+simulationData=\{.*?\}\s*/>',
    r"""<RevenueAreaChart 
                baselineRevenue={simResult ? simResult.projection_without_intervention : []} 
                retainedRevenue={simResult ? simResult.projection_with_intervention : []} 
              />""",
    content,
    flags=re.DOTALL
)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
