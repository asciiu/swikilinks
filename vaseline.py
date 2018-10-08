import csv
import sys

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


# Summary output here 
print "Orders:"
for key, sku in enumerate(order_qty):
  print "\t" + sku + ": " + str(order_qty[sku])

print "Mini orders:"
for key, sku in enumerate(mini_qty):
  print "\t" + sku + ": " + str(mini_qty[sku])

print "Non links:"
for key, sku in enumerate(non_link_qty):
  print "\t" + sku + ": " + str(non_link_qty[sku])

print "West cost orders: " +  str(len(west_coast_addresses))
print "2 day orders: " +  str(len(two_day_addresses))
print "Ice total: " + str(ice_total)
f.close()
