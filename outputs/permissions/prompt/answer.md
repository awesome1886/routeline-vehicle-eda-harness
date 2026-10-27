I have determined the data structure and sample for both datasets. Inventory has 240 vehicles with 26 columns including year, brand, model, segment, condition, price_usd, mileage, horsepower, and powertrain. History has 48 records for unique model-year combinations with reliability, repair costs, resale values, and ownership satisfaction metrics.

A few sample inventory records showed new models priced from about $25K to $50K, horsepower ranging broadly from ~200 to 310, and powertrains including gasoline, electric, and hybrid. Sample history records for a compact SUV hybrid showed reliability scores around 8.2-8.7/10 and average annual repair cost from $263 to $726.

In the inventory:
- Most vehicles are used (210) versus new (30).
- Top segments include midsize SUVs, adventure SUVs, compact sedans, electric hatchbacks, and sport sedans.
- Gasoline vehicles dominate the powertrain count at 102, followed by electric (57), hybrid (56), and plug-in hybrid (25).

Unfortunately, I cannot run the planned Welch two-sample t-test to compare prices for New vs. Used vehicles due to tool restrictions.

Next, with your permission, I will create:
- A scatter plot of horsepower versus price_usd for the full inventory.
- A bar chart of average annual repair cost by segment using the history data.

Please confirm if I should proceed with these plots.
