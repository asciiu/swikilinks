import csv
import sys
from fpdf import FPDF
import datetime
from products import ParseProductsFile
from avery import Avery5160

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
order_num_index = 0
order_num_min = 0
order_num_max = 0
order_qty = {}
mini_qty = {}
non_link_qty = {}
labels = []
sku_product_not_found = []

# this line will parse the products csv file and return 
# a dictionary with sku -> description
products = ParseProductsFile("products_export.csv")

for i, val in enumerate(csv_file):

  # first row should be headers
  if i == 0:
    # assign indices of columns based upon headers
    for j, header in enumerate(val):
      if header == "Order - Number":
        order_number_index = j
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
  order_num = val[order_num_index]
  qty = int(val[qty_index])
  options = val[option_index]
  custom = val[custom_index]
  address = val[address_index]
  order_num = val[order_index]
  item_name = val[name_index]

  if order_num_min == 0 or order_num_min > order_num:
    order_num_min = order_num 
  
  if order_num_max == 0 or order_num_max < order_num:
    order_num_max = order_num

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

  # label link orders only
  if "Mini" in item_name or "Micro" in item_name or "links" in item_name:
    for i in range(qty):
      # product description associated with sku 
      key = sku.replace("+egg", "")
      if products.has_key(key):
        desc = "order #: " + order_num + " " + products[key]
        if "+egg" in sku:
          desc += " +egg"

        # 40 links = 2 labels with 20 links 
        if "(40 links)" in desc:
          desc = desc.replace("(40 links)", "(20/40 links)")
          labels.append(desc)
          labels.append(desc)

        # 24 links = 2 labels with 12 links
        elif "(24 links)" in desc:
          desc = desc.replace("(24 links)", "(12/24 links)")
          labels.append(desc)
          labels.append(desc)

        # 20 links = 2 labels with 10 links
        elif "(20 links)" in desc:
          desc = desc.replace("(20 links)", "(10/20 links)")
          labels.append(desc)
          labels.append(desc)

        # 10 links = 2 labels with 5 links
        elif "(10 links)" in desc:
          desc = desc.replace("(10 links)", "(5/10 links)")
          labels.append(desc)
          labels.append(desc)

        # 7 links = 2 labels with 3 links and 4 links 
        elif "(7 links)" in desc:
          d1 = desc.replace("(7 links)", "(3/7 links)")
          labels.append(d1)
          d2 = desc.replace("(7 links)", "(4/7 links)")
          labels.append(d2)

        # 6 links = 2 labels with 3 links
        elif "(6 links)" in desc:
          desc = desc.replace("(6 links)", "(3/6 links)")
          labels.append(desc)
          labels.append(desc)
        else:
          labels.append(desc)
      else: 
        sku_product_not_found.append(key)

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


# Summary Pick list to pdf file here 
####################################
now = datetime.datetime.now()
title = "pick-list date: " + now.strftime("%Y-%m-%d %H:%M:%S")
subtitle = "orders: " + str(order_num_min) + " - " + str(order_num_max)
file_name = "swicklist-" + now.strftime("%Y-%m-%d %H%M%S")

pdf = FPDF(format = "Letter")
pdf.add_page()
pdf.set_font('Times', '', 12)
pdf.cell(70, 5, title, 0, 0)
pdf.cell(60, 5, subtitle, 0, 1)

############################################
# regular 
############################################
x = pdf.get_x()
y = pdf.get_y()

# Sort the dictionary of skus in order_qty
sorted_skus = sorted(order_qty)
# create pdf cell
pdf.cell(50, 5, 'Regular', 1, 1)
regular_str = ""
# for each sku in the sorted list of skus
for sku in sorted_skus:
  qty = order_qty[sku]

  # append to string 
  regular_str += sku + ": " + str(qty) + "\n"

# print the cell for regular orders
pdf.multi_cell(50, 5, regular_str, 1)


############################################
# Mini
############################################
pdf.set_y(y)
pdf.set_x(x + 60)

sorted_mini_skus = sorted(mini_qty)

pdf.cell(50, 5, 'Mini', 1, 1)
mini_str = ""
for sku in sorted_mini_skus:
  qty = mini_qty[sku]

  mini_str += sku + ": " + str(qty) + "\n"

pdf.set_x(x + 60)
pdf.multi_cell(50, 5, mini_str, 1)


############################################
# Non link
############################################
pdf.set_y(y)
pdf.set_x(x + 120)

sorted_non_link = sorted(non_link_qty)

pdf.cell(50, 5, 'Non-link', 1, 1)
nonlink_str = ""
for sku in sorted_non_link:
  qty = non_link_qty[sku]
  
  nonlink_str += sku + ": " + str(qty) + "\n"

pdf.set_x(x + 120)
pdf.multi_cell(50, 5, nonlink_str, 1)


############################################
# Summary
############################################
pdf.set_x(x + 120)
pdf.cell(50, 5, "West cost orders: " +  str(len(west_coast_addresses)), 0, 1)

pdf.set_x(x + 120)
pdf.cell(50, 5, "2 day orders: " +  str(len(two_day_addresses)), 0, 1)

pdf.set_x(x + 120)
pdf.cell(50, 5, "Ice total: " + str(ice_total), 0, 1)

print sku_product_not_found

pdf.add_page(orientation= 'P')
pdf.set_font('Helvetica', '', 8)
pdf.set_margins(0, 0)
pdf.set_auto_page_break(False)
x = y = 0

for _, label in enumerate(labels):
  if label == "":
    continue

  (x1, y1, w, h) = Avery5160(x, y)

  pdf.set_xy(x1, y1)
  pdf.multi_cell(w, h, label, 0)

  y += 1 # next row
  if y == 10:  # end of page wrap to next column
    x += 1
    y = 0
    if x == 3:
      x = 0
      y = 0
      pdf.add_page()

pdf.output(file_name, 'F')
