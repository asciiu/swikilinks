import csv
import re

# parses the products export csv from shopify
# returns a dictionary of sku: label description.
#
# example:
#{'': 'sku: \nLarge Keeper Multi-Pack / Pet Store Sampler: ', 
# 'RLWM6': 'sku: RLWM6\nWhite Mice: Hoppers (6-13g each, 50 per bag)', 
# 'RLIG8': 'sku: RLIG8\nIguana Meat: 8-12 g (40 links)', 
# 'RLWM3': 'sku: RLWM3\nWhite Mice: Fuzzies (3-5g each, 50 per bag)', 
# 'RLNR175': 'sku: RLNR175\nNorway Hooded Rats: Large (175-274g each, 7 per bag)'} 
def ParseProductsFile(file):
    f = open(file)
    csv_file = csv.reader(f)

    sku_index = 0
    desc_index = 0
    title_index = 0
    title = ""
    products = {}

    for i, val in enumerate(csv_file):
        # first row should be headers
        if i == 0:
            # assign indices of columns based upon headers
            for j, header in enumerate(val):
              if header == "Variant SKU":
                sku_index = j
              if header == "Option1 Value":
                desc_index = j
              if header == "Title":
                title_index = j
             # skip outer loop once since the first row are headers
        else:
          # if the title is empty in title cell then use the last title
          title = title if val[title_index] == "" else val[title_index]

          sku = val[sku_index]
          desc = val[desc_index]

          product = "sku: " + sku + "\n" + title + ": " + desc
          products[sku] = product

    f.close()
    return products

# extracts the product from the sku
# e.g. RLMBFV extracted from RLMBFV8
def ExtractParentSku(sku):
  # if RLTEGU just return the sku
  if "RLTEGU" in sku:
    return "RLTEGU"

  # if RL5050 return RL5050
  if sku.startswith("RL5050"):
    return "RL5050" 

  # if sku ends with MICRO return the first part only
  if sku.endswith("MICRO"):
    return sku[:-len("MICRO")]

  # if the sku ends with MINI return the first part only
  if sku.endswith("MINI"):
    return sku[:-len("MINI")]
    
  # extract the parent code before the first digit
  parts = re.match(r"([a-z]+)", sku, re.I) 
  # if there are parts 
  if parts:
    # return the first part before the number
    return parts.group(1)
  else: 
    # no match just returns the entire sku
    return sku


# Contains sku and counts 
# all child skus under this object will be of he 
# same parent sku
class ReptilProductQty:
   def __init__(self, sku, qty):
     self.product_qty = {}
     self.parent_sku = ExtractParentSku(sku) 
     self.product_qty[sku] = qty
   
   def addProductQty(self, sku, qty):
     if self.parent_sku != ExtractParentSku(sku):
       return

     total = qty
     if self.product_qty.has_key(sku):
       total = self.product_qty[sku] + qty

     self.product_qty[sku] = total
     return
  
   def subProducts(self):
     return self.product_qty.keys()


def TeguBundle(qty, plus_egg, regular_products, labels):
  # this bundle also contains 1 order of RLMBFV8
  parent = "RLMBFV"
  asku = "RLMBFV8"
  desc = "sku: RLMBFV8\nMEGA-BLEND + F & V: 8-12 g (20/40 links)"
  if plus_egg:
    asku = asku + "+egg"
    desc = desc + " +egg"

  if regular_products.has_key(parent):
    p = regular_products[parent]
    p.addProductQty(asku, qty)
    regular_products[parent] = p 
  else: 
    regular_products[parent] = ReptilProductQty(asku, qty) 

  # print 2 labels for RLMBFV8 - 40 links total 
  # therefore, 2 labels with 20/40 each
  for h in range(0, qty): 
    labels.append(desc)
    labels.append(desc)

  # add 10 labels for tegu bundle
  for i in range(0, 10*qty):
    desc = "sku: RLTEGU\nMegaBlend, Fruits & Veggies (100 uncased)" 
    labels.append(desc)


def MiniMicro(qty, plus_egg, desc, regular_products, labels):
  for _ in range(qty):
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