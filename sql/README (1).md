# E-commerce Sales Analytics using SQL

An end-to-end SQL analysis of an e-commerce database covering data auditing, customer behaviour, sales and profitability, product performance and time-series trends. All queries are written for **SQLite** and executed in **DB Browser for SQLite**.

---

## Project Overview

| Item | Details |
|------|---------|
| **Objective** | Audit the data, then answer business questions on customers, sales, products and trends using SQL |
| **Database** | `Ecommerce_Analytics.db` (SQLite) |
| **Tools** | SQLite, DB Browser for SQLite, GitHub |
| **Skills shown** | Joins, aggregation, subqueries, CTEs, window functions (`RANK`, `ROW_NUMBER`, `LAG`), conditional aggregation, date functions |

## Database Schema

| Table | Description |
|-------|-------------|
| `ecommerce_sales_customer_analytics` | Order-level sales data (46 columns) |
| `customer_master` | Customer details |
| `order_items` | Products inside each order |
| `product_catalog` | Product details |
| `dataset_statistics` | Dataset summary |

**Relationships**

- `order_items.order_id` → `ecommerce_sales_customer_analytics.order_id`
- `order_items.product_id` → `product_catalog.product_id`
- `customer_master.customer_id` → `ecommerce_sales_customer_analytics.customer_id`

> **Important analyst note:** The dataset contains **7 currencies** (USD, EUR, GBP, INR and others). Amounts in different currencies are **never added together**. Every revenue and profit query is grouped by `currency`.

## Table of Contents

1. [Phase 1: Database and Data Quality Audit](#phase-1-database-and-data-quality-audit)
2. [Phase 2: Customer Analysis](#phase-2-customer-analysis)
3. [Phase 3: Sales and Profitability Analysis](#phase-3-sales-and-profitability-analysis)
4. [Phase 4: Product Analysis](#phase-4-product-analysis)
5. [Phase 5: Time Series Analysis](#phase-5-time-series-analysis)
6. [Key Findings](#key-findings)
7. [Limitations and Assumptions](#limitations-and-assumptions)
8. [Project Structure](#project-structure)
9. [Author](#author)

---

## Phase 1: Database and Data Quality Audit

**Objective:** Confirm the structure of all five tables, count records, and check for duplicates, missing values and order statuses before writing any analysis query.

### Query 1.1: List all tables

**Business question:** Which tables exist in the database?

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```

**Why this query:** `sqlite_master` is SQLite's system catalogue. It confirms that all five tables loaded correctly.

**SQL concepts:** `sqlite_master`, `WHERE`, `ORDER BY`

**Result:** `Screenshots/phase1_q1_tables.png`

---

### Query 1.2: Schema of every table

**Business question:** What columns and data types does each table have?

```sql
PRAGMA table_info(ecommerce_sales_customer_analytics);
PRAGMA table_info(customer_master);
PRAGMA table_info(order_items);
PRAGMA table_info(product_catalog);
PRAGMA table_info(dataset_statistics);
```

**Why this query:** Checking real column names and data types first prevents errors in JOINs and avoids wrong assumptions about the data.

**SQL concepts:** `PRAGMA table_info`

**Result:** The sales table has **46 columns**. Screenshots: `Screenshots/phase1_q2_schema.png`

---

### Query 1.3: Record count of every table

**Business question:** How many rows does each table hold?

```sql
SELECT COUNT(*) AS total_sales      FROM ecommerce_sales_customer_analytics;
SELECT COUNT(*) AS total_customers  FROM customer_master;
SELECT COUNT(*) AS total_order_items FROM order_items;
SELECT COUNT(*) AS total_products   FROM product_catalog;
SELECT COUNT(*) AS total_statistics FROM dataset_statistics;
```

**Why this query:** Row counts are the baseline. Any later result can be checked against them.

**SQL concepts:** `COUNT(*)`

**Result:** `Screenshots/phase1_q3_counts.png`

---

### Query 1.4: Duplicate ID check

**Business question:** Are there duplicate order IDs or customer IDs?

```sql
-- Duplicate Order IDs
SELECT order_id, COUNT(*) AS duplicate_count
FROM ecommerce_sales_customer_analytics
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Duplicate Customer IDs
SELECT customer_id, COUNT(*) AS duplicate_count
FROM customer_master
GROUP BY customer_id
HAVING COUNT(*) > 1;
```

**Why this query:** Duplicate IDs would inflate counts and revenue after JOINs. `HAVING` filters groups after aggregation, so only repeated IDs are shown.

**SQL concepts:** `GROUP BY`, `HAVING`

**Result:** No duplicate `order_id` values were found in the sales table.

---

### Query 1.5: Missing value check

**Business question:** Do key columns contain NULL or blank values?

```sql
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 ELSE 0 END)    AS missing_order_id,
    SUM(CASE WHEN customer_id IS NULL OR TRIM(customer_id) = '' THEN 1 ELSE 0 END) AS missing_customer_id,
    SUM(CASE WHEN order_date IS NULL OR TRIM(order_date) = '' THEN 1 ELSE 0 END)   AS missing_order_date,
    SUM(CASE WHEN net_sales IS NULL THEN 1 ELSE 0 END) AS missing_net_sales,
    SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END)    AS missing_profit
FROM ecommerce_sales_customer_analytics;
```

**Why this query:** Missing values silently distort `SUM` and `AVG`. `TRIM` also catches blank strings that `IS NULL` would miss.

**SQL concepts:** `CASE WHEN`, conditional aggregation, `TRIM`

**Result:** `Screenshots/phase1_q5_missing.png`

---

### Query 1.6: Order status distribution

**Business question:** How many orders are Completed, Pending, Returned or Cancelled?

```sql
SELECT
    order_status,
    COUNT(*) AS total_orders
FROM ecommerce_sales_customer_analytics
GROUP BY order_status
ORDER BY total_orders DESC;
```

**Why this query:** Returned and cancelled orders should not be counted as real revenue. This query shows the exact status labels to use in later filters.

**SQL concepts:** `GROUP BY`, `ORDER BY`

**Result:** `Screenshots/phase1_q6_status.png`

---

### Query 1.7: Currency distribution

**Business question:** Which currencies exist in the data?

```sql
SELECT
    currency,
    COUNT(*) AS total_records
FROM ecommerce_sales_customer_analytics
GROUP BY currency
ORDER BY total_records DESC;
```

**Why this query:** Adding values in different currencies gives meaningless totals. This confirms that currency-wise analysis is required.

**SQL concepts:** `GROUP BY`, `COUNT`

**Result:** **7 currencies** found.

---

## Phase 2: Customer Analysis

**Objective:** Understand who the customers are, where they are from, and how they buy.

### Query 2.1: Customer segments

**Business question:** Which customer segment is the largest?

```sql
SELECT
    customer_segment,
    COUNT(*) AS total_customers
FROM customer_master
GROUP BY customer_segment
ORDER BY total_customers DESC;
```

**Why this query:** Segment size guides marketing focus and campaign targeting.

**SQL concepts:** `GROUP BY`, `COUNT`, `ORDER BY`

**Result:** `Screenshots/phase2_q1_segments.png`

---

### Query 2.2: Top 10 countries by customers

**Business question:** Which countries have the most customers?

```sql
SELECT
    customer_country,
    COUNT(*) AS total_customers
FROM customer_master
GROUP BY customer_country
ORDER BY total_customers DESC
LIMIT 10;
```

**Why this query:** Shows the geographic concentration of the customer base.

**SQL concepts:** `GROUP BY`, `LIMIT`

**Result:** `Screenshots/phase2_q2_countries.png`

---

### Query 2.3: Customer age profile

**Business question:** What are the average, minimum and maximum customer ages?

```sql
SELECT
    COUNT(*)                     AS total_customers,
    ROUND(AVG(customer_age), 2)  AS average_age,
    MIN(customer_age)            AS minimum_age,
    MAX(customer_age)            AS maximum_age
FROM customer_master;
```

**Why this query:** Describes the age range and also exposes unrealistic ages that indicate data errors.

**SQL concepts:** `AVG`, `MIN`, `MAX`, `ROUND`

**Result:** `Screenshots/phase2_q3_age.png`

---

### Query 2.4: Repeat customers

**Business question:** How many customers buy repeatedly?

```sql
SELECT
    is_repeat_customer,
    COUNT(DISTINCT customer_id) AS total_customers
FROM ecommerce_sales_customer_analytics
GROUP BY is_repeat_customer;
```

**Why this query:** Repeat customers are cheaper to retain than new customers are to acquire. This measures loyalty.

**SQL concepts:** `COUNT(DISTINCT)`, `GROUP BY`

**Result:** `Screenshots/phase2_q4_repeat.png`

---

### Query 2.5: Top 10 customers by order count

**Business question:** Which customers place the most orders?

```sql
SELECT
    customer_id,
    COUNT(DISTINCT order_id) AS total_orders
FROM ecommerce_sales_customer_analytics
GROUP BY customer_id
ORDER BY total_orders DESC
LIMIT 10;
```

**Why this query:** Identifies the most active customers for loyalty programs.

**SQL concepts:** `COUNT(DISTINCT)`, `LIMIT`

**Result:** `Screenshots/phase2_q5_top_customers.png`

---

### Query 2.6: Customer-wise sales and profit

**Business question:** How much sales and profit does each customer generate?

```sql
SELECT
    customer_id,
    currency,
    COUNT(DISTINCT order_id)   AS total_orders,
    ROUND(SUM(net_sales), 2)   AS total_sales,
    ROUND(SUM(profit), 2)      AS total_profit
FROM ecommerce_sales_customer_analytics
GROUP BY customer_id, currency
ORDER BY total_sales DESC
LIMIT 20;
```

**Why this query:** Shows customer value. `currency` is part of `GROUP BY` so different currencies are not mixed.

**SQL concepts:** `SUM`, multi-column `GROUP BY`

**Result:** `Screenshots/phase2_q6_customer_sales.png`

---

### Query 2.7: Customer details with order activity (JOIN)

**Business question:** Can customer profile details be combined with purchase activity?

```sql
SELECT
    c.customer_id,
    c.customer_name,
    c.customer_country,
    c.customer_segment,
    COUNT(DISTINCT s.order_id) AS total_orders
FROM customer_master AS c
LEFT JOIN ecommerce_sales_customer_analytics AS s
    ON c.customer_id = s.customer_id
GROUP BY
    c.customer_id,
    c.customer_name,
    c.customer_country,
    c.customer_segment
ORDER BY total_orders DESC
LIMIT 20;
```

**Why this query:** `LEFT JOIN` keeps customers even if they have no orders, so inactive customers are not lost. `COUNT(DISTINCT)` avoids double counting.

**SQL concepts:** `LEFT JOIN`, table aliases, `GROUP BY`

**Result:** `Screenshots/phase2_q7_customer_join.png`

---

## Phase 3: Sales and Profitability Analysis

**Objective:** Measure revenue, profit and margin by currency, channel, region and customer, and find loss-making orders. Queries use **Completed orders only**, so returned and cancelled orders do not inflate revenue.

### Query 3.1: Overall sales performance

**Business question:** How many orders, how much revenue and profit, and what margin per currency?

```sql
SELECT
    currency,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2)    AS total_profit,
    ROUND(SUM(profit) * 100.0 / NULLIF(SUM(net_sales), 0), 2) AS profit_margin_percentage
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
GROUP BY currency
ORDER BY total_revenue DESC;
```

**Why this query:** These are the core business KPIs. `NULLIF` prevents division-by-zero errors.

**SQL concepts:** `SUM`, `COUNT(DISTINCT)`, `NULLIF`, `WHERE`

**Result:** `Screenshots/phase3_q1_kpis.png`

---

### Query 3.2: Monthly sales (Completed orders)

**Business question:** Which months generate the most sales?

```sql
SELECT
    strftime('%Y', order_date) AS sales_year,
    strftime('%m', order_date) AS sales_month,
    currency,
    COUNT(DISTINCT order_id)   AS total_orders,
    ROUND(SUM(net_sales), 2)   AS monthly_sales,
    ROUND(SUM(profit), 2)      AS monthly_profit
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
GROUP BY sales_year, sales_month, currency
ORDER BY sales_year, sales_month, currency;
```

**Why this query:** Reveals which months perform best, so stock and campaigns can be planned.

**SQL concepts:** `strftime`, date extraction, `GROUP BY`

**Result:** `Screenshots/phase3_q2_monthly.png`

---

### Query 3.3: Sales channel performance

**Business question:** Which channel generates the most sales?

```sql
SELECT
    sales_channel,
    currency,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_sales), 2) AS total_sales,
    ROUND(SUM(profit), 2)    AS total_profit
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
GROUP BY sales_channel, currency
ORDER BY total_sales DESC;
```

**Why this query:** Shows where to invest marketing budget.

**SQL concepts:** `GROUP BY` on multiple columns

**Result:** `Screenshots/phase3_q3_channel.png`

---

### Query 3.4: Region-wise sales

**Business question:** Which region earns the most revenue and profit?

```sql
SELECT
    region,
    currency,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_sales), 2) AS total_sales,
    ROUND(SUM(profit), 2)    AS total_profit
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
GROUP BY region, currency
ORDER BY total_sales DESC;
```

**Why this query:** Identifies strong and weak regions for expansion or correction.

**SQL concepts:** `GROUP BY`, `ORDER BY`

**Result:** `Screenshots/phase3_q4_region.png`

---

### Query 3.5: Top 10 most profitable customers

**Business question:** Which customers generate the most profit?

```sql
SELECT
    customer_id,
    currency,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_sales), 2) AS total_sales,
    ROUND(SUM(profit), 2)    AS total_profit
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
GROUP BY customer_id, currency
ORDER BY total_profit DESC
LIMIT 10;
```

**Why this query:** Profit matters more than sales volume. These are the customers worth retaining.

**SQL concepts:** `SUM`, `ORDER BY`, `LIMIT`

**Result:** `Screenshots/phase3_q5_profit_customers.png`

---

### Query 3.6: Loss-making orders

**Business question:** Which orders lost money?

```sql
SELECT
    order_id,
    order_date,
    customer_id,
    currency,
    net_sales,
    product_cost,
    profit
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
  AND profit < 0
ORDER BY profit ASC
LIMIT 20;
```

**Why this query:** Finds the worst losses so the cause (discount, shipping, cost) can be investigated.

**SQL concepts:** `WHERE` with multiple conditions, `ORDER BY ASC`

**Result:** `Screenshots/phase3_q6_loss_orders.png`

---

### Query 3.7: Discount impact on profit

**Business question:** Do higher discounts reduce profit?

```sql
SELECT
    CASE
        WHEN discount_amount = 0   THEN 'No Discount'
        WHEN discount_amount <= 100 THEN 'Low Discount'
        WHEN discount_amount <= 500 THEN 'Medium Discount'
        ELSE 'High Discount'
    END AS discount_category,
    currency,
    COUNT(*)                        AS total_orders,
    ROUND(AVG(discount_amount), 2)  AS average_discount,
    ROUND(AVG(profit), 2)           AS average_profit
FROM ecommerce_sales_customer_analytics
WHERE order_status = 'Completed'
GROUP BY discount_category, currency
ORDER BY currency, average_profit DESC;
```

**Why this query:** Groups orders into discount bands to test whether heavier discounting hurts profit. Results are split by currency because the same discount amount means different things in INR and USD.

**SQL concepts:** `CASE WHEN` for bucketing, `AVG`

**Result:** `Screenshots/phase3_q7_discount.png`

---

## Phase 4: Product Analysis

**Objective:** Combine `order_items`, `product_catalog` and the sales table to rank products, categories and brands.

**Join keys:** `order_items.product_id = product_catalog.product_id` and `order_items.order_id = ecommerce_sales_customer_analytics.order_id`

### Query 4.1: Order items with product details (INNER JOIN)

**Business question:** Which product was bought in each order, and with what quantity, price and profit?

```sql
SELECT
    oi.order_id,
    oi.product_id,
    pc.product_name,
    pc.product_category,
    pc.brand,
    oi.quantity,
    oi.unit_price,
    oi.discount_amount,
    oi.net_sales,
    oi.profit
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
LIMIT 20;
```

**Why this query:** Verifies the JOIN works before building analysis on top of it. `INNER JOIN` returns only rows with a match in both tables.

**SQL concepts:** `INNER JOIN`, aliases

**Result:** `Screenshots/phase4_q1_join.png`

---

### Query 4.2: Top 10 best-selling products

**Business question:** Which products sell the most units?

```sql
SELECT
    pc.product_id,
    pc.product_name,
    pc.product_category,
    pc.brand,
    SUM(oi.quantity)            AS total_quantity_sold,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
GROUP BY pc.product_id, pc.product_name, pc.product_category, pc.brand
ORDER BY total_quantity_sold DESC
LIMIT 10;
```

**Why this query:** Shows demand leaders, useful for inventory planning.

**SQL concepts:** `JOIN`, `SUM`, `GROUP BY`, `LIMIT`

**Result:** `Screenshots/phase4_q2_top_products.png`

---

### Query 4.3: Category-wise analysis

**Business question:** Which product categories sell the most?

```sql
SELECT
    pc.product_category,
    COUNT(DISTINCT pc.product_id) AS total_products,
    SUM(oi.quantity)              AS total_quantity_sold,
    COUNT(DISTINCT oi.order_id)   AS total_orders
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
GROUP BY pc.product_category
ORDER BY total_quantity_sold DESC;
```

**Why this query:** Shows category demand and how many products each category carries.

**SQL concepts:** `COUNT(DISTINCT)`, `GROUP BY`

**Result:** `Screenshots/phase4_q3_category.png`

---

### Query 4.4: Brand-wise performance

**Business question:** Which brands sell the most, and how are they rated?

```sql
SELECT
    pc.brand,
    COUNT(DISTINCT pc.product_id) AS total_products,
    SUM(oi.quantity)              AS total_quantity_sold,
    COUNT(DISTINCT oi.order_id)   AS total_orders,
    ROUND(AVG(pc.product_rating), 2) AS average_product_rating
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
GROUP BY pc.brand
ORDER BY total_quantity_sold DESC;
```

**Why this query:** Compares brand popularity against customer rating.

**SQL concepts:** `AVG`, `GROUP BY`

**Result:** `Screenshots/phase4_q4_brand.png`

---

### Query 4.5: Top 20 most profitable products

**Business question:** Which products generate the highest profit?

```sql
SELECT
    pc.product_id,
    pc.product_name,
    pc.product_category,
    pc.brand,
    SUM(oi.quantity)           AS total_quantity_sold,
    ROUND(SUM(oi.net_sales), 2)    AS total_revenue,
    ROUND(SUM(oi.product_cost), 2) AS total_product_cost,
    ROUND(SUM(oi.profit), 2)       AS total_profit
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
GROUP BY pc.product_id, pc.product_name, pc.product_category, pc.brand
ORDER BY total_profit DESC
LIMIT 20;
```

**Why this query:** Best sellers are not always the most profitable. This ranks by profit. Note that this query does not split by currency, so use Query 4.6 for currency-safe comparisons.

**SQL concepts:** multiple aggregates, `ORDER BY`

**Result:** `Screenshots/phase4_q5_profitable.png`

---

### Query 4.6: Currency-wise product profit margin (3-table JOIN)

**Business question:** What is each product's revenue, profit and margin in each currency?

`order_items` has no `currency` column, so it is taken from the sales table through `order_id`. Because `order_id` is unique in the sales table (verified in Query 1.4), this JOIN does not duplicate rows.

```sql
SELECT
    pc.product_id,
    pc.product_name,
    pc.product_category,
    pc.brand,
    s.currency,
    ROUND(SUM(oi.net_sales), 2) AS total_revenue,
    ROUND(SUM(oi.profit), 2)    AS total_profit,
    ROUND(SUM(oi.profit) * 100.0 / NULLIF(SUM(oi.net_sales), 0), 2) AS profit_margin_percentage
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
INNER JOIN ecommerce_sales_customer_analytics AS s
    ON oi.order_id = s.order_id
GROUP BY pc.product_id, pc.product_name, pc.product_category, pc.brand, s.currency
ORDER BY s.currency, total_profit DESC
LIMIT 50;
```

**Why this query:** Gives accurate margins by keeping currencies separate.

**SQL concepts:** multi-table `JOIN`, `NULLIF`, margin calculation

**Result:** 50 rows returned. `Screenshots/phase4_q6_margin.png`

---

### Query 4.7: Loss-making products

**Business question:** Which products lose money overall?

```sql
SELECT
    pc.product_id,
    pc.product_name,
    pc.product_category,
    pc.brand,
    s.currency,
    SUM(oi.quantity)               AS total_quantity_sold,
    ROUND(SUM(oi.net_sales), 2)    AS total_revenue,
    ROUND(SUM(oi.product_cost), 2) AS total_product_cost,
    ROUND(SUM(oi.profit), 2)       AS total_profit
FROM order_items AS oi
INNER JOIN product_catalog AS pc
    ON oi.product_id = pc.product_id
INNER JOIN ecommerce_sales_customer_analytics AS s
    ON oi.order_id = s.order_id
GROUP BY pc.product_id, pc.product_name, pc.product_category, pc.brand, s.currency
HAVING SUM(oi.profit) < 0
ORDER BY total_profit ASC
LIMIT 20;
```

**Why this query:** Finds products to reprice, renegotiate or drop. `HAVING` filters after aggregation, which `WHERE` cannot do.

**SQL concepts:** `HAVING`, aggregate filtering

**Result:** Only **1 product-currency combination** had a net loss.

---

### Query 4.8: Top 5 products per category and currency (CTE + RANK)

**Business question:** Which are the best 5 products by revenue within each category?

```sql
WITH ProductSales AS (
    SELECT
        pc.product_id,
        pc.product_name,
        pc.product_category,
        s.currency,
        SUM(oi.net_sales) AS total_revenue
    FROM order_items AS oi
    INNER JOIN product_catalog AS pc
        ON oi.product_id = pc.product_id
    INNER JOIN ecommerce_sales_customer_analytics AS s
        ON oi.order_id = s.order_id
    GROUP BY pc.product_id, pc.product_name, pc.product_category, s.currency
),
RankedProducts AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY product_category, currency
            ORDER BY total_revenue DESC
        ) AS product_rank
    FROM ProductSales
)
SELECT *
FROM RankedProducts
WHERE product_rank <= 5
ORDER BY product_category, currency, product_rank;
```

**Why this query:** A CTE keeps the logic readable, and `RANK()` with `PARTITION BY` ranks products inside each category and currency separately.

**SQL concepts:** `WITH` (CTE), `RANK()`, `PARTITION BY`, window functions

**Result:** 525 rows (Top 5 across all category-currency groups).

---

### Query 4.9: Top 5 products per currency (ROW_NUMBER)

**Business question:** Which 5 products earn the most revenue in each currency?

```sql
WITH ProductSales AS (
    SELECT
        pc.product_id,
        pc.product_name,
        pc.product_category,
        s.currency,
        SUM(oi.net_sales) AS total_revenue
    FROM order_items AS oi
    INNER JOIN product_catalog AS pc
        ON oi.product_id = pc.product_id
    INNER JOIN ecommerce_sales_customer_analytics AS s
        ON oi.order_id = s.order_id
    GROUP BY pc.product_id, pc.product_name, pc.product_category, s.currency
),
RankedProducts AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY currency
            ORDER BY total_revenue DESC
        ) AS revenue_rank
    FROM ProductSales
)
SELECT *
FROM RankedProducts
WHERE revenue_rank <= 5
ORDER BY currency, revenue_rank;
```

**Why this query:** `ROW_NUMBER()` gives every row a unique position, which is ideal for a strict Top-N list. `RANK()` can return more than N rows when there are ties.

| Function | Ties | Skips numbers |
|----------|------|---------------|
| `RANK()` | Same rank | Yes |
| `ROW_NUMBER()` | Unique number | No |

**SQL concepts:** `ROW_NUMBER()`, window functions

**Result:** `Screenshots/phase4_q9_top5_currency.png`

---

## Phase 5: Time Series Analysis

**Objective:** Study revenue, profit and growth over months, quarters and years, separately for each currency.

### Query 5.1: Monthly sales trend

**Business question:** How do revenue and profit change month by month?

```sql
SELECT
    strftime('%Y', order_date) AS sales_year,
    strftime('%m', order_date) AS sales_month,
    currency,
    COUNT(DISTINCT order_id)   AS total_orders,
    ROUND(SUM(net_sales), 2)   AS monthly_revenue,
    ROUND(SUM(profit), 2)      AS monthly_profit
FROM ecommerce_sales_customer_analytics
GROUP BY sales_year, sales_month, currency
ORDER BY sales_year, sales_month, currency;
```

**Why this query:** Builds the monthly time series used for growth analysis.

**SQL concepts:** `strftime`, `GROUP BY` on derived columns

**Result:** 420 rows.

---

### Query 5.2: Yearly sales analysis

**Business question:** How do yearly revenue, profit and margin compare?

```sql
SELECT
    strftime('%Y', order_date) AS sales_year,
    currency,
    COUNT(DISTINCT order_id)   AS total_orders,
    ROUND(SUM(net_sales), 2)   AS yearly_revenue,
    ROUND(SUM(profit), 2)      AS yearly_profit,
    ROUND(SUM(profit) * 100.0 / NULLIF(SUM(net_sales), 0), 2) AS profit_margin_percentage
FROM ecommerce_sales_customer_analytics
GROUP BY sales_year, currency
ORDER BY sales_year, currency;
```

**Why this query:** Shows long-term direction and whether margin is improving.

**SQL concepts:** `strftime`, margin calculation

**Result:** 35 rows.

---

### Query 5.3: Quarterly sales analysis

**Business question:** Which quarters perform best, and is there seasonality?

```sql
SELECT
    strftime('%Y', order_date) AS sales_year,
    CASE
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END AS sales_quarter,
    currency,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(net_sales), 2) AS quarterly_revenue,
    ROUND(SUM(profit), 2)    AS quarterly_profit
FROM ecommerce_sales_customer_analytics
GROUP BY sales_year, sales_quarter, currency
ORDER BY sales_year, sales_quarter, currency;
```

**Why this query:** SQLite has no built-in quarter function, so `CASE WHEN` on the month number is used. Quarterly data smooths monthly noise and shows seasonal patterns.

**SQL concepts:** `CASE WHEN`, `CAST`, `BETWEEN`

**Result:** 140 rows.

---

### Query 5.4: Month-over-Month (MoM) growth

**Business question:** By what percentage does revenue change from one month to the next?

```sql
WITH MonthlySales AS (
    SELECT
        strftime('%Y-%m', order_date) AS sales_month,
        currency,
        SUM(net_sales) AS monthly_revenue
    FROM ecommerce_sales_customer_analytics
    GROUP BY sales_month, currency
),
PreviousMonthSales AS (
    SELECT
        sales_month,
        currency,
        monthly_revenue,
        LAG(monthly_revenue) OVER (
            PARTITION BY currency
            ORDER BY sales_month
        ) AS previous_month_revenue
    FROM MonthlySales
)
SELECT
    sales_month,
    currency,
    ROUND(monthly_revenue, 2)       AS monthly_revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(
        (monthly_revenue - previous_month_revenue) * 100.0
        / NULLIF(previous_month_revenue, 0), 2
    ) AS mom_growth_percentage
FROM PreviousMonthSales
ORDER BY currency, sales_month;
```

**Why this query:** `LAG()` reads the previous row's value inside each currency, which makes growth calculation possible without a self-join. The first month of every currency shows `NULL` because no earlier month exists.

**SQL concepts:** CTE, `LAG()`, `PARTITION BY`, `NULLIF`

**Result:** 420 rows.

---

### Query 5.5: Revenue growth status

**Business question:** Did revenue grow, decline or stay flat each month?

```sql
WITH MonthlySales AS (
    SELECT
        strftime('%Y-%m', order_date) AS sales_month,
        currency,
        SUM(net_sales) AS monthly_revenue
    FROM ecommerce_sales_customer_analytics
    GROUP BY sales_month, currency
),
GrowthAnalysis AS (
    SELECT
        sales_month,
        currency,
        monthly_revenue,
        LAG(monthly_revenue) OVER (
            PARTITION BY currency
            ORDER BY sales_month
        ) AS previous_month_revenue
    FROM MonthlySales
)
SELECT
    sales_month,
    currency,
    ROUND(monthly_revenue, 2)        AS monthly_revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    CASE
        WHEN previous_month_revenue IS NULL THEN 'First Month'
        WHEN monthly_revenue > previous_month_revenue THEN 'Growth'
        WHEN monthly_revenue < previous_month_revenue THEN 'Decline'
        ELSE 'No Change'
    END AS revenue_status
FROM GrowthAnalysis
ORDER BY currency, sales_month;
```

**Why this query:** Turns numbers into labels so growth and decline months can be counted and filtered easily.

**SQL concepts:** `LAG()`, `CASE WHEN`, CTE

**Result:** `Screenshots/phase5_q5_growth_status.png`

---

## Key Findings

> Add this section after all result values are final. Only write findings that are visible in the actual query output. Suggested format:

| # | Finding | Evidence (query) |
|---|---------|------------------|
| 1 | _Largest customer segment and country_ | Query 2.1, 2.2 |
| 2 | _Repeat customer share_ | Query 2.4 |
| 3 | _Best and worst performing currency by margin_ | Query 3.1 |
| 4 | _Best channel and region_ | Query 3.3, 3.4 |
| 5 | _Effect of discounts on profit_ | Query 3.7 |
| 6 | _Top categories, brands and the loss-making product_ | Query 4.3, 4.4, 4.7 |
| 7 | _Yearly and quarterly trend, growth and decline months_ | Query 5.2, 5.3, 5.5 |

## Recommendations

> Write 3 to 5 recommendations after the findings, each linked to one finding above.

## Limitations and Assumptions

- Currencies are analysed separately. No exchange-rate conversion is applied, so totals across currencies are not comparable.
- Phase 3 uses `order_status = 'Completed'`, while Phase 5 time-series queries include all statuses. Phase 5 therefore represents all booked orders, not only completed ones.
- Discount bands in Query 3.7 use fixed amounts (100 and 500) that are not currency-adjusted, so band meaning differs between currencies such as INR and USD.
- `order_items.net_sales` and `order_items.profit` are line-level values, while the sales table holds order-level values. Totals from the two tables are not expected to match exactly.

## SQL Structure

```
Ecommerce_Analytics_Project/
├── Database/
│   └── Ecommerce_Analytics.db
├── SQL/
│   ├── 01_database_audit.sql
│   ├── 02_customer_analysis.sql
│   ├── 03_sales_profitability.sql
│   ├── 04_product_analysis.sql
│   └── 05_time_series_analysis.sql
├── Screenshots/
└── README.md
```

## Author

**Marreboina Rajesh**
M.Sc Data Science | Hyderabad, India
LinkedIn: www.linkedin.com/in/rajesh-marreboina-948a18324

 | Email:marreboinarajesh@gmail.com
