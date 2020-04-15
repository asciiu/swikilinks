import csv
import sys
import re
from fpdf import FPDF
import datetime
import reptile 
import layout
import itertools
import codecs

################################################################################################
# Main script stuff follows here. You may execute this script from the command line (terminal app of OSX).
# terminal command: "python /path/to/picklist_gen.py /path/to/csv true"
#
# This stuff is within scope of this script
#import sys
#def __main__():
    #with open("parameters.log", "ab") as f:
        #f.write(str(sys.argv))

# an array of address strings
one_day_addresses = []
two_day_addresses = []
three_day_addresses = []
four_day_addresses = []

# keeps all order numbers e.g. RL2019
# this array is used to report the order number range in the top left of the pick list pdf
order_nums = []
order_num_min = 0
order_num_max = 0

# ice total
ice_total = 0

# you can think of these as hashmaps where the key to each of these collections
# is a parent sku: e.g. RLQR and the value is an ReptilProductQty object (reptile.py file)
# Refer to the addProdQty function above in that these variables will be the first 
# parameter to that function. Each of these collections will correlate to the mini, regular, etc
# sections in the generated pick list pdf output.
regular_products = {}
mini_products = {}
non_sausage = {}

# a array of label strings. This data is used to generate the labels.
labels = []

# used to report that a sku from the csv was not recognized
sku_product_not_found = []

# this line will parse the products master csv file and return 
# a dictionary with sku string -> product description 
# refer to the products_export.csv that you exported from ship station
products = reptile.ParseProductsFile("assets/products_export.csv")
#products = reptile.ParseProductsFile("assets/products_export.csv")

# ship station csv file required as command line argument
sscsv = sys.argv[1]
#f = open(sscsv)
f = codecs.open(sscsv, encoding="utf-8")

# This chunk of code here assigns the column indices
# for each header. 
ship_station_iter = iter(csv.reader(f))
headers = next(ship_station_iter)
# these variables are used to reference the column numbers with the csv file
sku_index = 0      # this is the column number in the csv for sku
qty_index = 0
option_index = 0
custom_index = 0
addres_index = 0
name_index = 0
order_num_index = 0
# assign indices of columns based upon headers
for col, header in enumerate(headers):
  if header == "Order - Number":
    order_num_index = col 
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
  if header == "Item - Name":
    name_index = col

# this is the start of the loop that will go over
# each row in the ship station csv file
while True: 
  try:
    # assign row as the next row in the csv file
    row = next(ship_station_iter)
    # grab the sku at row[sku_index]
    sku = row[sku_index]
    # grab the order number at row[order_num_index]
    order_num = row[order_num_index]
    qty = int(row[qty_index])
    # options column
    options = row[option_index]
    # custom column
    custom = row[custom_index]
    # customer address
    address = row[address_index]
    # the item name
    item_name = row[name_index]
    # the description
    desc = products[sku] if sku in products else ""

    # extract the parent sku from the sku: e.g parent is RLQR from sku RLQR25
    parent = reptile.ExtractParentSku(sku)

    # keep track of the min/max order numbers so we can report
    # the order numbers at the top page of the pick list
    # i.e: "Orders: RL2586 - RL2617"
    if order_num_min == 0 or order_num_min > order_num:
      order_num_min = order_num 
    if order_num_max == 0 or order_num_max < order_num:
      order_num_max = order_num

    #if address not in west_coast_addresses and "West" in custom:
    #  # count unique addresses that are west coast orders
    #  west_coast_addresses.append(address)
    #elif address not in two_day_addresses and "West" not in custom:
    #  # count unique 2 day addresses that don't have "West" in the custom field
    #  two_day_addresses.append(address)

    # skip no sku rows
    if sku == "": 
      continue

    # this a new order number?
    if order_num not in order_nums:
      order_nums.append(order_num)
      # increment dry ice total 
      if "ONE DAY" in custom:
        ice_total += 10
        one_day_addresses.append(address)
      elif "TWO DAY" in custom:
        ice_total += 20
        two_day_addresses.append(address)
      elif "THREE DAY" in custom:
        ice_total += 30
        three_day_addresses.append(address)
      elif "FOUR DAY" in custom:
        ice_total += 40
        four_day_addresses.append(address)

    # Find the orders that have egg added, and modify the SKU number so that
    # those items appear as a unique product.  
    plus_egg = False
    mix_eggs = "Mix in 1-dozen quail eggs" 

    # if the special code is in the options column or the mix_eggs string is in the item name
    # column add +egg to the sku
    if mix_eggs in options:
      sku = sku+"+egg"
      desc = desc +" +egg"
      plus_egg = True

    # Picklist Data:
    # mini orders have mini or micro in item name
    if "Mini" in item_name or "Micro" in item_name:
      mini_products = reptile.AddProdQty(mini_products, parent, sku, qty)
    # non sausage orders 
    elif "links" not in item_name and "RLTEGU" not in sku and "RLMULTIR-01" not in sku:
      non_sausage = reptile.AddProdQty(non_sausage, parent, sku, qty)
    # all link orders
    else:  
      regular_products = reptile.AddProdQty(regular_products, parent, sku, qty)

    # Labels Data:
    if "RLTEGU" in sku:
      # if RLTEGU bundle is found 
      # refer to TeguBundle function in the reptile.py file 
      reptile.TeguBundle(qty, plus_egg, regular_products, labels)

    elif "RLMULTIR-01" in sku:
      # RabbitBundle is defined in the reptile.py file 
      reptile.RabbitBundle(qty, plus_egg, labels)

    elif "Mini" in item_name or "Micro" in item_name or "links" in item_name:
      # cross reference the sku with the products master list
      if not sku.replace("+egg", "") in products:
        # if this sku was not found in the master list report it as
        # a sku not found
        sku_product_not_found.append(sku)
      else:
        # MiniMicro is defined in the reptile.py file 
        reptile.MiniMicro(qty, desc, labels)

  except StopIteration:
    break

# 
#  END loop here so we close the csv file  
f.close()



############################################
# Pick list to pdf file here 
############################################
now = datetime.datetime.now()
# title is generated with today's date time
picks_file = "reptilinks-picks-" + now.strftime("%Y-%m-%d %H%M%S") + ".pdf"
title = "Orders: " + str(order_num_min) + " - " + str(order_num_max)

# refer to https://pyfpdf.readthedocs.io/en/latest docs  
# for more information on how to use their libary to format a pdf
pdf = FPDF(format = "Letter")
pdf.add_page()
pdf.set_font('Times', '', 8)
pdf.cell(70, 5, title, 0, 1)

############################################
# regular 
############################################
x = pdf.get_x()
y = pdf.get_y()

# refer to layout.py file for PrintCells function def 
(xr, yr) = layout.PrintCells(pdf, "Regular", regular_products, x, y, y)

############################################
# Mini
############################################
(xm, ym) = layout.PrintCells(pdf, "Mini", mini_products, xr, yr, y)

############################################
# Non link
############################################
(xn, yn) = layout.PrintCells(pdf, "Non-link", non_sausage, xm, ym, y)

############################################
# Summary
############################################
# if not 3rd column set summary to 3rd column
if xn < 150:
  xn += 70
  yn = y

pdf.set_xy(xn, y-5)
timestamp = "Date: " + now.strftime("%Y-%m-%d %H:%M:%S")
pdf.cell(70, 5, timestamp, 0, 1) 

pdf.set_xy(xn, yn)
pdf.cell(50, 5, "One day orders", 1, 0)
pdf.cell(10, 5, str(len(one_day_addresses)), 1, 0, 'R')

pdf.set_xy(xn, yn+5)
pdf.cell(50, 5, "Two day orders", 1, 0)
pdf.cell(10, 5, str(len(two_day_addresses)), 1, 0, 'R')

pdf.set_xy(xn, yn+10)
pdf.cell(50, 5, "Three day orders", 1, 0)
pdf.cell(10, 5, str(len(three_day_addresses)), 1, 0, 'R')

pdf.set_xy(xn, yn+15)
pdf.cell(50, 5, "Four day orders", 1, 0)
pdf.cell(10, 5, str(len(four_day_addresses)), 1, 0, 'R')

pdf.set_xy(xn, yn+20)
pdf.cell(50, 5, "Ice total lbs", 1, 0)
pdf.cell(10, 5, str(ice_total), 1, 0, 'R')

ye = yn+5
pdf.set_xy(xn, yn+25)
pdf.cell(50, 5, "Skus not found:", 0, 1)
ye += 25 
for sku in sku_product_not_found:
  pdf.set_xy(xn+5, ye)
  pdf.cell(10, 5, sku, 0, 0)
  ye += 5

# if running via app
if len(sys.argv) > 2:
  # if running file manually via command line
  pdf.output(picks_file, 'F')
else:
  # if running via app
  pdf.output("../../../"+picks_file, 'F')

############################################
# Labels here 
############################################
label_file = "reptilinks-labels-" + now.strftime("%Y-%m-%d %H%M%S") + ".pdf"
#pdf = FPDF(format = "Letter")
pdf = FPDF('P', 'in', (4, 0.5))
pdf.set_font('Helvetica', '', 10)
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

if len(sys.argv) > 2:
  # if running via cli
  pdf.output(label_file, 'F')
else:
  pdf.output("../../../"+label_file, 'F')