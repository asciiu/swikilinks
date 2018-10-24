import csv
import sys
from fpdf import FPDF
import datetime

file = sys.argv[1]
f = open(file)
csv_file = csv.reader(f)

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

order_qty = {}
mini_qty = {}
non_link_qty = {}

for i, val in enumerate(csv_file):

  # first row should be headers
  if i == 0:
    # assign indices of columns based upon headers
    for j, header in enumerate(val):
      if header == "Item - SKU":
        sku_index = j
      if header == "Item - Qty":
        qty_index = j
      if header == "Item - Options":
        option_index = j
      if header == "Custom - Field 1":
        custom_index = j
      if header == "Ship To - Address 1":
        address_index = j
      if header == "Order - Number":
        order_index = j
      if header == "Item - Name":
        name_index = j
    
    # skip outer loop once since the first row are headers
    continue

  sku = val[sku_index]
  qty = int(val[qty_index])
  options = val[option_index]
  custom = val[custom_index]
  address = val[address_index]
  order_num = val[order_index]
  item_name = val[name_index]

  # count unique addresses that are west coast orders
  if address not in west_coast_addresses and "West" in custom:
    west_coast_addresses.append(address)
  elif address not in two_day_addresses and "West" not in custom:
    two_day_addresses.append(address)

  # skip no sku rows
  if sku == "": 
    continue

  # dry ice total
  if order_num not in order_nums:
    if "West" in custom:
      ice_total += 40
    else:
      ice_total += 20

  if order_num not in order_nums:
    order_nums.append(order_num)

  # Find the orders that have egg added, and modify the SKU number so that
  # those items appear as a unique product.  
  if "1350249218131" in options:
    sku = sku+"+egg"

  # mini orders have mini or micro in item name
  if "Mini" in item_name or "Micro" in item_name:
    if mini_qty.has_key(sku):
      total = mini_qty[sku]
      mini_qty[sku] = total + qty
    else: 
      mini_qty[sku] = qty

  # non link orders 
  elif "links" not in item_name:
    if non_link_qty.has_key(sku):
      total = non_link_qty[sku]
      non_link_qty[sku] = total + qty
    else: 
      non_link_qty[sku] = qty

  # all link orders
  else:  
    if order_qty.has_key(sku):
      total = order_qty[sku]
      order_qty[sku] = total + qty
    else:
      order_qty[sku] = qty

f.close()

# Summary Pick list to pid file here 
####################################
now = datetime.datetime.now()
title = "pick-list date: " + now.strftime("%Y-%m-%d %H:%M:%S")
file_name = "swicklist-" + now.strftime("%Y-%m-%d %H%M%S")

pdf = FPDF()
pdf.add_page()
pdf.set_font('Times', '', 12)
pdf.cell(40, 10, title, 0, 1)

x = pdf.get_x()
y = pdf.get_y()

# Sort the dictionary of skus in order_qty
sorted_skus = sorted(order_qty)
# create pdf cell
pdf.cell(40, 5, 'Regular', 1, 1)
regular_str = ""
# for each sku in the sorted list of skus
for sku in sorted_skus:
  regular_str += sku + ": " + str(order_qty[sku]) + "\n"

# print the cell for regular orders
pdf.multi_cell(40, 5, regular_str, 1, 0)


############################################
# Mini
############################################
pdf.set_y(y)
pdf.set_x(x + 40)

sorted_mini_skus = sorted(mini_qty)

pdf.cell(40, 5, 'Mini', 1, 1)
mini_str = ""
for sku in sorted_mini_skus:
  mini_str += sku + ": " + str(mini_qty[sku]) + "\n"

pdf.set_x(x + 40)
pdf.multi_cell(40, 5, mini_str, 1, 0)


############################################
# Non link
############################################
pdf.set_y(y)
pdf.set_x(x + 80)

sorted_non_link = sorted(non_link_qty)

pdf.cell(40, 5, 'Non-link', 1, 1)
nonlink_str = ""
for sku in sorted_non_link:
  nonlink_str += sku + ": " + str(non_link_qty[sku]) + "\n"

pdf.set_x(x + 80)
pdf.multi_cell(40, 5, nonlink_str, 1, 0)


############################################
# Summary
############################################
pdf.set_x(x + 80)
pdf.cell(40, 5, "West cost orders: " +  str(len(west_coast_addresses)), 0, 1)

pdf.set_x(x + 80)
pdf.cell(40, 5, "2 day orders: " +  str(len(two_day_addresses)), 0, 1)

pdf.set_x(x + 80)
pdf.cell(40, 5, "Ice total: " + str(ice_total), 0, 1)

pdf.output(file_name, 'F')
