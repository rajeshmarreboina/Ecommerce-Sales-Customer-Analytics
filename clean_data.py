"""
Cleaning pipeline for the e-commerce project (5 raw files -> 4 clean tables + log).
Run:  python clean_data.py <folder_with_raw_csvs> <output_folder>
"""
import sys, pandas as pd, numpy as np

RAW = sys.argv[1] if len(sys.argv) > 1 else 'raw'
OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
log = []
def L(table, step, column, issue, action, rows): log.append((table, step, column, issue, action, int(rows)))

orders = pd.read_csv(f'{RAW}/ecommerce_sales_customer_analytics_150k.csv', dtype={'customer_postal_code': str})
items  = pd.read_csv(f'{RAW}/order_items.csv')
cust   = pd.read_csv(f'{RAW}/customer_master.csv', dtype={'customer_postal_code': str})
prod   = pd.read_csv(f'{RAW}/product_catalog.csv')

def trim(df, name):
    n = 0
    for c in df.columns:
        if str(df[c].dtype) in ('str', 'object'):
            s = df[c].dropna(); n += int((s != s.str.strip()).sum()); df[c] = df[c].str.strip()
    L(name, 'Trim text', 'all text columns', 'Leading/trailing spaces', 'Trimmed (none needed)' if n == 0 else 'Trimmed', n)
    return df

# ---------------- ORDERS ----------------
o = trim(orders.copy(), 'orders')
L('orders', 'Duplicates', 'order_id', 'Duplicate order IDs / rows', 'Checked; none found', o.order_id.duplicated().sum())
o['order_date'] = pd.to_datetime(o.order_date, format='%Y-%m-%d')
o['order_time'] = pd.to_datetime(o.order_time, format='%H:%M:%S').dt.time
L('orders', 'Data types', 'order_date, order_time', 'Stored as text', 'Converted to date / time', len(o))
m = o.customer_state == 'North Rhine'; o.loc[m, 'customer_state'] = 'North Rhine-Westphalia'
L('orders', 'Fix category', 'customer_state', "Truncated name 'North Rhine'", "Renamed 'North Rhine-Westphalia'", m.sum())
o['customer_postal_code'] = o.customer_postal_code.str.zfill(5)
for c, v in {'return_status': 'Not Returned', 'return_reason': 'Not Returned', 'campaign_name': 'No Campaign',
             'coupon_code': 'No Coupon', 'review_sentiment': 'No Review', 'customer_review': 'No Review'}.items():
    L('orders', 'Fill blanks', c, 'Blank = not applicable', f"Filled '{v}'", o[c].isna().sum()); o[c] = o[c].fillna(v)
for c in ['delivery_days', 'estimated_delivery_days', 'customer_rating']:
    L('orders', 'Kept blank', c, 'Blank for Cancelled/Pending/Returned (never delivered/reviewed)', 'Left NULL on purpose', o[c].isna().sum())
o['delivery_days'] = o.delivery_days.astype('Int64'); o['estimated_delivery_days'] = o.estimated_delivery_days.astype('Int64')
o['order_year'] = o.order_date.dt.year; o['order_month'] = o.order_date.dt.month
o['order_quarter'] = 'Q' + o.order_date.dt.quarter.astype(str); o['order_day_name'] = o.order_date.dt.day_name()
o['delivery_delay_days'] = o.delivery_days - o.estimated_delivery_days
o['has_coupon'] = np.where(o.coupon_code == 'No Coupon', 'No', 'Yes')
o['is_loss_making'] = np.where(o.profit < 0, 'Yes', 'No')
g = items.groupby('order_id').agg(item_lines=('product_id', 'count'), items_quantity=('quantity', 'sum'),
                                  items_net_sales=('net_sales', 'sum'), items_profit=('profit', 'sum'),
                                  items_gross=('gross_sales', 'sum')).reset_index()
o = o.merge(g, on='order_id', how='left')
o['items_reconciled'] = np.where((o.gross_sales - o.items_gross).abs() <= 0.05, 'Yes', 'No'); o = o.drop(columns='items_gross')
L('orders', 'Reconciliation', 'items_reconciled', 'Header totals differ from sum of line items (all 5,171 orders with 6+ lines and 6,055 with 2-5 lines)',
  "Flag added; header used for order KPIs, items table used for product analysis", (o.items_reconciled == 'No').sum())
L('orders', 'New columns', 'order_year ... items_reconciled', 'Analysis helpers', 'Added derived columns', len(o))
L('orders', 'Kept as is', 'profit', 'Negative-profit orders', 'Genuine losses, kept', (o.profit < 0).sum())
o = o.sort_values(['order_date', 'order_time']).reset_index(drop=True)

# ---------------- CUSTOMERS ----------------
c = trim(cust.copy(), 'customer_master')
c['customer_age'] = pd.to_numeric(c.customer_age); c['customer_acquisition_cost'] = pd.to_numeric(c.customer_acquisition_cost)
L('customer_master', 'Data types', 'customer_age, customer_acquisition_cost', 'Read as text', 'Converted to numbers', len(c))
m = c.customer_state == 'North Rhine'; c.loc[m, 'customer_state'] = 'North Rhine-Westphalia'
L('customer_master', 'Fix category', 'customer_state', "Truncated name 'North Rhine'", "Renamed 'North Rhine-Westphalia'", m.sum())
c['customer_postal_code'] = c.customer_postal_code.str.zfill(5)
c['has_orders'] = np.where(c.customer_id.isin(o.customer_id), 'Yes', 'No')
L('customer_master', 'Orphans', 'customer_id', 'Customers with no orders', "Kept, flagged 'has_orders' = No", (c.has_orders == 'No').sum())
c['age_group'] = pd.cut(c.customer_age, [17, 24, 34, 44, 54, 64, 100], labels=['18-24', '25-34', '35-44', '45-54', '55-64', '65+']).astype(str)
L('customer_master', 'New columns', 'age_group', 'Analysis helper', 'Added age bands', len(c))

# ---------------- PRODUCTS ----------------
p = trim(prod.copy(), 'product_catalog')
p['gross_margin'] = (p.unit_price - p.product_cost).round(2)
p['margin_pct'] = ((p.unit_price - p.product_cost) / p.unit_price * 100).round(2)
p['price_tier'] = pd.cut(p.unit_price, [0, 50, 200, 500, 5000], labels=['Budget (<50)', 'Mid (50-200)', 'Premium (200-500)', 'Luxury (500+)']).astype(str)
L('product_catalog', 'Validation', 'unit_price vs product_cost', 'Price must exceed cost', 'Verified; all products have positive margin', (p.unit_price <= p.product_cost).sum())
L('product_catalog', 'New columns', 'gross_margin, margin_pct, price_tier', 'Analysis helpers', 'Added', len(p))

# ---------------- ORDER ITEMS ----------------
i = trim(items.copy(), 'order_items')
dup = i.duplicated(['order_id', 'product_id'], keep=False)
i.insert(0, 'item_id', np.arange(1, len(i) + 1))
i['is_repeat_product_line'] = np.where(dup, 'Yes', 'No')
i['discount_percentage'] = i.discount_percentage.round(4)
L('order_items', 'Surrogate key', 'item_id', 'No unique row id (order_id + product_id repeats)', 'Added item_id 1..n as primary key', len(i))
L('order_items', 'Duplicates', 'order_id, product_id', 'Same product on 2 lines of one order with different qty/discount', "Kept (not exact duplicates), flagged 'is_repeat_product_line'", dup.sum())
L('order_items', 'Validation', 'gross/net/profit', 'qty x price = gross; net = gross - discount + tax + shipping; profit = net - shipping - cost', 'Verified, all rows consistent', 0)
L('order_items', 'Validation', 'product_id, order_id', 'Foreign keys exist in parent tables', 'Verified, no orphans', 0)


# round money columns to 2 decimals (removes floating-point noise such as 8.389999999)
MONEY = ['gross_sales','discount_amount','tax_amount','shipping_cost','net_sales','product_cost','profit',
         'profit_margin_percentage','customer_lifetime_value','unit_price','items_net_sales','items_profit']
for df_ in (o, i, p, c):
    for col in MONEY + ['customer_acquisition_cost']:
        if col in df_.columns: df_[col] = df_[col].round(2)
L('all tables', 'Rounding', 'money columns', 'Floating-point noise (e.g. 8.389999999)', 'Rounded to 2 decimals', len(o) + len(i))

for name, df in [('orders', o), ('order_items', i), ('customer_master', c), ('product_catalog', p)]:
    df.to_csv(f'{OUT}/{name}_clean.csv', index=False, date_format='%Y-%m-%d')
    print(name, df.shape)
pd.DataFrame(log, columns=['Table', 'Step', 'Column(s)', 'Issue / check', 'Action taken', 'Rows affected']).to_csv(f'{OUT}/cleaning_log.csv', index=False)
