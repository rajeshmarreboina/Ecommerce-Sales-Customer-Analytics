
========================================================
PROJECT NAME : E-Commerce Sales Analysis
MODULE       : Dataset Record Count Verification
FILE NAME   : 01_data_exploration.sql

DESCRIPTION:
This SQL script verifies the total number of records
available in all five project datasets.

OBJECTIVES:
1. Count total sales records.
2. Count total customer records.
3. Count total order item records.
4. Count total product records.
5. Count total dataset statistics records.

PURPOSE:
To understand dataset size and validate the number
of records available before performing further analysis.

DATABASE:
SQLite
=========================================================
*/

-- 1. Total Sales Records
SELECT COUNT(*) AS total_sales
FROM ecommerce_sales_customer_analytics;

-- 2. Total Customer Records
SELECT COUNT(*) AS total_customers
FROM customer_master;

-- 3. Total Order Item Records
SELECT COUNT(*) AS total_order_items
FROM order_items;

-- 4. Total Product Records
SELECT COUNT(*) AS total_products
FROM product_catalog;

-- 5. Total Statistics Records
SELECT COUNT(*) AS total_statistics
FROM dataset_statistics;


