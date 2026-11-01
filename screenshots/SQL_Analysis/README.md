# SQL Analysis Queries

This folder contains screenshots of SQL queries
and their corresponding results and  sql queries.


## SQL Analysis

### Overview

SQL analysis is a core component of this E-Commerce Sales & Customer Analytics project. SQLite and DB Browser for SQLite are used to explore the database, validate data quality, analyze customer behavior, evaluate sales and profitability, identify product performance, and uncover business trends.

The analysis follows a structured, business-oriented approach, starting with database schema verification and progressing toward advanced analytical queries and business recommendations.

### Database Tables

The project uses the following five tables:

| Table Name | Description |
|---|---|
| `ecommerce_sales_customer_analytics` | Main transactional table containing order, sales, customer, payment, delivery, and profitability information. |
| `customer_master` | Customer master data containing customer attributes and demographic information. |
| `dataset_statistics` | Dataset-level statistical summaries and descriptive information. |
| `order_items` | Individual product-level order details, including quantity, pricing, discounts, costs, and profit. |
| `product_catalog` | Product master data containing product names, categories, subcategories, brands, suppliers, and pricing information. |

### 1. Database & Schema Verification

**Objective:** Understand the database structure and verify table schemas before performing analytical queries.

**SQL Concepts Used:**
- SQLite system tables (`sqlite_master`)
- `PRAGMA TABLE_INFO`
- Database metadata inspection
- Table and column verification

**Activities Performed:**
- Identified all available database tables.
- Inspected column names and data types.
- Reviewed primary key information.
- Examined the structure of all five tables.
- Identified potential relationships between transactional, customer, order-item, and product tables.

### 2. Data Quality & Validation

**Objective:** Assess data completeness, consistency, uniqueness, and reliability before business analysis.

**SQL Concepts Used:**
- `COUNT()`
- `DISTINCT`
- `GROUP BY`
- `HAVING`
- `CASE WHEN`
- `IS NULL`

**Activities Performed:**
- Checked missing values in important columns.
- Identified duplicate customer records.
- Validated duplicate order identifiers.
- Examined currency distribution.
- Reviewed important data quality conditions.
- Performed financial calculation validation for net sales and profit.

### 3. Customer Analysis

**Objective:** Understand customer demographics, customer segments, purchasing behavior, and repeat purchase patterns.

**SQL Concepts Used:**
- `GROUP BY`
- `COUNT()`
- `COUNT(DISTINCT)`
- `AVG()`
- `MIN()`
- `MAX()`
- `ORDER BY`
- `LIMIT`
- Table joins

**Analysis Performed:**
- Customer distribution by segment.
- Customer distribution by country.
- Average, minimum, and maximum customer age.
- Repeat versus non-repeat customer analysis.
- Identification of customers with the highest order counts.
- Customer-level sales and profitability analysis.
- Customer master and transaction data integration.

### 4. Sales & Profitability Analysis

**Objective:** Evaluate revenue performance, order distribution, sales channels, regional performance, and profitability.

**SQL Concepts Used:**
- Aggregate functions
- `SUM()`
- `AVG()`
- `COUNT()`
- `GROUP BY`
- Conditional aggregation
- `CASE WHEN`

**Analysis Performed:**
- Order status distribution.
- Currency-wise revenue and profit analysis.
- Sales channel performance.
- Region-wise sales performance.
- Revenue and profit comparisons.
- Profit margin calculations.
- Discount impact analysis.

**Note:** Financial metrics are analyzed separately by currency to avoid incorrect comparisons between different currencies.

### 5. Product Performance Analysis

**Objective:** Identify high-performing products, profitable categories, brand performance, and loss-making products.

**SQL Concepts Used:**
- `INNER JOIN`
- Aggregate functions
- `GROUP BY`
- `HAVING`
- Common Table Expressions (CTEs)
- Window functions
- `RANK()`
- `ROW_NUMBER()`

**Analysis Performed:**
- Integrated order-item and product catalog data.
- Identified top-selling products by quantity.
- Analyzed category-wise product performance.
- Evaluated brand-wise sales and ratings.
- Identified top profitable products.
- Calculated product-level profit margins by currency.
- Identified loss-making product and currency combinations.
- Ranked top products within categories and currencies.
- Identified top five revenue-generating products for each currency.

### 6. Time Series Analysis

**Objective:** Analyze sales trends and revenue performance across different time periods.

**SQL Concepts Used:**
- `strftime()`
- Date and time functions
- `CASE WHEN`
- CTEs
- `LAG()`
- Window functions
- Percentage growth calculations

**Analysis Performed:**

| Analysis | Description |
|---|---|
| Monthly Sales Analysis | Evaluated monthly revenue, profit, and order counts by currency. |
| Yearly Sales Analysis | Compared annual revenue, profit, and order performance by currency. |
| Quarterly Sales Analysis | Analyzed business performance across Q1, Q2, Q3, and Q4. |
| Month-over-Month Growth | Compared current-month revenue against the previous available month. |
| Revenue Growth Status | Classified monthly revenue trends as Growth, Decline, No Change, or First Month. |

### 7. Marketing & Discount Analysis

**Objective:** Evaluate the relationship between promotional activities, discounts, and business performance.

**Planned Analytical Areas:**
- Marketing channel performance.
- Campaign-wise sales analysis.
- Coupon code utilization.
- Discount distribution.
- Revenue and profit comparison across discount levels.
- Customer acquisition and loyalty analysis.

### 8. Returns & Delivery Analysis

**Objective:** Understand product returns, delivery performance, customer satisfaction, and operational issues.

**Planned Analytical Areas:**
- Return status distribution.
- Return reason analysis.
- Delivery status analysis.
- Actual versus estimated delivery time.
- Customer rating and review sentiment.
- Relationship between delivery performance and customer satisfaction.

### 9. Advanced Business Analysis

**Objective:** Apply advanced SQL techniques to identify rankings, trends, and business opportunities.

**SQL Concepts Used:**
- Common Table Expressions (CTEs)
- Window functions
- `LAG()`
- `RANK()`
- `ROW_NUMBER()`
- `PARTITION BY`
- Conditional aggregation
- Subqueries

**Analysis Performed:**
- Top-performing products by currency.
- Product rankings within categories.
- Revenue growth comparisons.
- Customer purchasing behavior.
- Comparative product profitability.

### 10. Financial Calculation Validation

**Objective:** Verify the consistency of important financial metrics in the transactional dataset.

**Validation Rules Tested:**

**Net Sales Validation**
- Compared recorded net sales against the assumed calculation:
- Gross Sales − Discount Amount + Tax Amount + Shipping Cost.

**Profit Validation**
- Compared recorded profit against:
- Net Sales − Product Cost.

**SQL Concepts Used:**
- `ABS()`
- `NULLIF()`
- `CASE WHEN`
- Conditional aggregation

**Note:** These are validation assumptions. Any mismatches must be investigated against the dataset's actual financial calculation rules before classifying them as data errors.

### SQL Outcome

The SQL analysis establishes a foundation for further data analytics using Python, Microsoft Excel, and Power BI.

The outputs will support:
- Customer segmentation and purchasing behavior analysis.
- Sales and profitability evaluation.
- Product and category performance analysis.
- Revenue growth and seasonal trend identification.
- Data quality assessment.
- Business insights and actionable recommendations.

**Tools Used:** SQLite | DB Browser for SQLite | SQL

**Status:** Core database exploration, customer analysis, sales analysis, product analysis, and time series analysis have been executed. Remaining analytical areas and final business findings will be completed after result validation.
