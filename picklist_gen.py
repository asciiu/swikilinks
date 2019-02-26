import csv
import sys
import re
from fpdf import FPDF
import datetime
import reptile 
import layout

def addProdQty(category, parent, sku, qty): 
  if category.has_key(parent):
    p = category[parent]
    p.addProductQty(sku, qty)
    category[parent] = p 
  else: 
    category[parent] = reptile.ReptilProductQty(sku, qty)

two_day_addresses = []
west_coast_addresses = []
order_nums = []

ice_total = 0
sku_index = 0
qty_index = 0
option_index = 0
custom_index = 0
addres_index = 0
order_index = 0
name_index = 0
order_num_index = 0
order_num_min = 0
order_num_max = 0
order_qty = {}

regular_products = {}
mini_products = {}
non_sausage = {}

non_link_qty = {}
labels = []
sku_product_not_found = []

# this line will parse the products csv file and return 
# a dictionary with sku: label_description 
products = reptile.ParseProductsFile("products_export.csv")

# ship station csv file required as command line argument
sscsv = sys.argv[1]
f = open(sscsv)
for row_number, row in enumerate(csv.reader(f)):
  # first row should be headers
  if row_number == 0:
    # assign indices of columns based upon headers
    for col, header in enumerate(row):
      if header == "Order - Number":
        order_number_index = col 
      if header == "Item - SKU":
        sku_index = col
      if header == "Item - Qty":
        qty_index = col
      if header == "Item - Options":
        option_index = col
      if header == "Custom - Field 1":
        custom_index = col
      if header == "Ship To - Address 1":
        address_index = col
      if header == "Order - Number":
        order_index = col
      if header == "Item - Name":
        name_index = col
    
    # skip outer loop once since the first row are headers
    continue

  sku = row[sku_index]
  order_num = row[order_num_index]
  qty = int(row[qty_index])
  options = row[option_index]
  custom = row[custom_index]
  address = row[address_index]
  order_num = row[order_index]
  item_name = row[name_index]
  desc = products[sku] if products.has_key(sku) else ""
  parent = reptile.ExtractParentSku(sku)

  # keep track of the min/max order numbers so we can report
  # the order numbers at the top page of the pick list
  # i.e: "Orders: RL2586 - RL2617"
  if order_num_min == 0 or order_num_min > order_num:
    order_num_min = order_num 
  if order_num_max == 0 or order_num_max < order_num:
    order_num_max = order_num

  if address not in west_coast_addresses and "West" in custom:
    # count unique addresses that are west coast orders
    west_coast_addresses.append(address)
  elif address not in two_day_addresses and "West" not in custom:
    # count unique 2 day addresses that don't have "West" in the custom field
    two_day_addresses.append(address)

  # skip no sku rows
  if sku == "": 
    continue

  # this a new order number?
  if order_num not in order_nums:
    order_nums.append(order_num)
    # increment dry ice total 
    if "West" in custom:
      ice_total += 40
    else:
      ice_total += 20

  # Find the orders that have egg added, and modify the SKU number so that
  # those items appear as a unique product.  
  plus_egg = False
  if "1350249218131" in options:
    sku = sku+"+egg"
    desc = desc +" +egg"
    plus_egg = True

  # Picklist Data:
  # mini orders have mini or micro in item name
  if "Mini" in item_name or "Micro" in item_name:
    addProdQty(mini_products, parent, sku, qty)
  # non sausage orders 
  elif "links" not in item_name and "RLTEGU" not in sku and "RLMULTR-01" not in sku:
    addProdQty(non_sausage, parent, sku, qty)
  # all link orders
  else:  
    addProdQty(regular_products, parent, sku, qty)

  # Labels Data:
  if "RLTEGU" in sku:
    # if RLTEGU bundle is found 
    reptile.TeguBundle(qty, plus_egg, regular_products, labels)

  elif "RLMULTR-01" in sku:
    reptile.RabbitBundle(qty, plus_egg, labels)

  elif "Mini" in item_name or "Micro" in item_name or "links" in item_name:
    if not products.has_key(sku.replace("+egg", "")):
      sku_product_not_found.append(sku)
    else:
      reptile.MiniMicro(qty, desc, labels)
  
f.close()



############################################
# Pick list to pdf file here 
############################################
now = datetime.datetime.now()
picks_file = "reptilinks-picks-" + now.strftime("%Y-%m-%d %H%M%S") + ".pdf"
title = "Orders: " + str(order_num_min) + " - " + str(order_num_max)

pdf = FPDF(format = "Letter")
pdf.add_page()
pdf.set_font('Times', '', 8)
pdf.cell(70, 5, title, 0, 1)

############################################
# regular 
############################################
x = pdf.get_x()
y = pdf.get_y()
(xr, yr) = layout.PrintCells(pdf, "Regular", regular_products, x, y)

############################################
# Mini
############################################
(xm, ym) = layout.PrintCells(pdf, "Mini", mini_products, xr, yr)

############################################
# Non link
############################################
(xn, yn) = layout.PrintCells(pdf, "Non-link", non_sausage, xr, ym)

############################################
# Summary
############################################
# if not 3rd column set summary to 3rd column
if xn < 150:
  xn += 70

pdf.set_xy(xn, y-5)
timestamp = "Date: " + now.strftime("%Y-%m-%d %H:%M:%S")
pdf.cell(70, 5, timestamp, 0, 1) 

pdf.set_xy(xn, y)
pdf.cell(50, 5, "West coast orders", 1, 0)
pdf.cell(10, 5, str(len(west_coast_addresses)), 1, 0, 'R')

pdf.set_xy(xn, y+5)
pdf.cell(50, 5, "2 day orders", 1, 0)
pdf.cell(10, 5, str(len(two_day_addresses)), 1, 0, 'R')

pdf.set_xy(xn, y+10)
pdf.cell(50, 5, "Ice total", 1, 0)
pdf.cell(10, 5, str(ice_total), 1, 0, 'R')

ye = y+15
pdf.set_xy(xn, y+15)
pdf.cell(50, 5, "Skus not found:", 0, 1)
ye += 5
for sku in sku_product_not_found:
  pdf.set_xy(xn+5, ye)
  pdf.cell(10, 5, sku, 0, 0)
  ye += 5

# if running via app
pdf.output("../../../"+picks_file, 'F')
# if running file manually via command line
#pdf.output(picks_file, 'F')

############################################
# Labels here 
############################################
label_file = "reptilinks-labels-" + now.strftime("%Y-%m-%d %H%M%S") + ".pdf"
#pdf = FPDF(format = "Letter")
pdf = FPDF('P', 'in', (4, 0.5))
pdf.set_font('Helvetica', '', 12)
pdf.set_margins(0, 0)
pdf.set_auto_page_break(False)
x = y = 0

# sort labels alpha numeric
labels = sorted(labels)

for _, label in enumerate(labels):
  if label == "":
    continue

  pdf.add_page()
  pdf.set_xy(x, y+0.03)

  # 2019/01/23 avoid text rollover for label
  label = label.replace("+ Fruits and Veggies", "+ F & V")
  pdf.multi_cell(4, 0.15, label, 0)

# if running via app
pdf.output("../../../"+label_file, 'F')
# if running via cli
#pdf.output(label_file, 'F')