import csv
import sys
import re
from fpdf import FPDF
import datetime
import products as prod
#from products import ParseProductsFile
from avery import Avery5160
#import webbrowser


def PrintCells(title, prds, x, y):
  # Sort the dictionary of skus in order_qty
  sorted_skus = sorted(prds)

  # create header cell 
  pdf.set_xy(x, y)
  pdf.set_fill_color(200)
  pdf.cell(70, 5, title, 1, 1, 'C', True)
  pdf.set_fill_color(0)
  y += 5

  # for each sku in the sorted list of skus
  for sku in sorted_skus:
    rl = prds[sku]
    sub_products = rl.subProducts()
  
    # print the parent sku
    pdf.set_xy(x, y)
    pdf.cell(20, 5*len(sub_products), rl.parent_sku, 1, 1)

    xm = x + 20  
    pdf.set_xy(xm, y)
    for v in rl.subProducts():
      pdf.cell(35, 5, v, 1, 0)
      pdf.cell(10, 5, str(rl.product_qty[v]), 1, 0, 'R')

      # this empty box is reserved for check box
      pdf.cell(5, 5, "", 1, 0)

      y += 5
      pdf.set_xy(xm, y)

  return (x+70, y)


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

regular_products = {}
mini_products = {}
non_sausage = {}

non_link_qty = {}
labels = []
sku_product_not_found = []

# this line will parse the products csv file and return 
# a dictionary with sku -> description
products = prod.ParseProductsFile("products_export.csv")

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

  # correct instances of RLQF, they should be RLQFV
  if "RLQF" in sku:
    sku = sku.replace("RLQF", "RLQFV")

  # label link orders only
  if "Mini" in item_name or "Micro" in item_name or "links" in item_name:
    for i in range(qty):
      # product description associated with sku 
      key = sku.replace("+egg", "")
      if products.has_key(key):
        #desc = "order #: " + order_num + " " + products[key]
        desc = products[key]
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

  parent = prod.ExtractParentSku(sku)

  # mini orders have mini or micro in item name
  if "Mini" in item_name or "Micro" in item_name:
    if mini_products.has_key(parent):
      p = mini_products[parent]
      p.addProductQty(sku, qty)
      mini_products[parent] = p 
    else: 
      mini_products[parent] = prod.ReptilProductQty(sku, qty) 

  # non sausage orders 
  elif "links" not in item_name and "RLTEGU" not in sku:
    if non_sausage.has_key(parent):
      p = non_sausage[parent]
      p.addProductQty(sku, qty)
      non_sausage[parent] = p 
    else: 
      non_sausage[parent] = prod.ReptilProductQty(sku, qty) 

  # all link orders
  else:  
    if regular_products.has_key(parent):
      p = regular_products[parent]
      p.addProductQty(sku, qty)
      regular_products[parent] = p 
    else: 
      regular_products[parent] = prod.ReptilProductQty(sku, qty) 

f.close()


############################################
# Pick list to pdf file here 
############################################
now = datetime.datetime.now()
picks_file = "reptilinks-picks-" + now.strftime("%Y-%m-%d %H%M%S")
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
(xr, yr) = PrintCells("Regular", regular_products, x, y)

############################################
# Mini
############################################
(xm, ym) = PrintCells("Mini", mini_products, xr, y)

############################################
# Non link
############################################
(xn, yn) = PrintCells("Non-link", non_sausage, xr, ym)

############################################
# Summary
############################################
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
#pdf.output("../../../"+picks_file, 'F')
# if running file manually via command line
pdf.output(picks_file, 'F')

############################################
# Labels here 
############################################
label_file = "reptilinks-labels-" + now.strftime("%Y-%m-%d %H%M%S")
#pdf = FPDF(format = "Letter")
pdf = FPDF('P', 'in', (4, 0.5))
pdf.set_font('Helvetica', '', 8)
pdf.set_margins(0, 0)
pdf.set_auto_page_break(False)
x = y = 0

# sort labels alpha numeric
labels = sorted(labels)

for _, label in enumerate(labels):
  if label == "":
    continue

  #(x1, y1, w, h) = Avery5160(x, y)

  #pdf.set_xy(x1, y1)
  pdf.add_page()
  pdf.image('reptilinks.png', x = x, y = y+0.05, w = 1, h = 0.4, type = 'PNG')
  pdf.set_xy(x+1, y+0.1)
  pdf.multi_cell(2.8, 0.1, label, 0)

  #y += 0.1 # next row
  #if y == 10:  # end of page wrap to next column
  #  x += 1
  #  y = 0
  #  if x == 3:
  #    x = 0
  #    y = 0
  #    pdf.add_page()

# if running via app
#pdf.output("../../../"+label_file, 'F')
# if running via cli
pdf.output(label_file, 'F')
