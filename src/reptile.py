import csv
import os
import re
import sys
import codecs

def ResourcePath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# parses the products export csv from shopify
# returns a dictionary of sku: label description.
#
# example:
#{'': 'sku: \nLarge Keeper Multi-Pack / Pet Store Sampler: ', 
# 'RLWM6': 'sku: RLWM6\nWhite Mice: Hoppers (6-13g each, 50 per bag)', 
# 'RLIG8': 'sku: RLIG8\nIguana Meat: 8-12 g (40 links)', 
# 'RLWM3': 'sku: RLWM3\nWhite Mice: Fuzzies (3-5g each, 50 per bag)', 
# 'RLNR175': 'sku: RLNR175\nNorway Hooded Rats: Large (175-274g each, 7 per bag)'} 
def ParseProductsFile(filename):
    with codecs.open(filename, encoding="utf-8") as csvfile:
    #with open(filename, newline='') as csvfile:
        product_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        sku_index = 0
        desc_index = 0
        title_index = 0
        title = ""
        products = {}

        # read headers from first row
        headers = next(product_reader)
        for j, header in enumerate(headers):
          if header == "Variant SKU":
            sku_index = j
          if header == "Option1 Value":
            desc_index = j
          if header == "Title":
            title_index = j

        for row in product_reader:
            # if the title is empty in title cell then use the last title
            title = title if row[title_index] == "" else row[title_index]
            sku = row[sku_index]
            desc = row[desc_index]
            product = f"sku: {sku}\n{title}: {desc}"
            products[sku] = product

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
  
  # return sku RL25/25/50
  if sku.startswith("RL25/25/50"):
    return "RL25/25/50"

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
     if sku in self.product_qty:
       total = self.product_qty[sku] + qty

     self.product_qty[sku] = total
     return
  
   def subProducts(self):
     return self.product_qty.keys()

# This is a function that adds product quantity. You can think of the 
# products as a collection of regular, mini, or non sausage product gruops. 
# It is how the code represents the regular or mini subsections in the pick list 
# pdf.
#
# params: 
#      category - this is of type dictionary where the key is a string like "RLQR" and the value 
#             is an object of type ReptilProductQty above. 
#      parent - parent sku string e.g. "RLQR"
#      sku - the full product sku e.g. "RLQR25"
#      qty - the qty integer to add
def AddProdQty(products, parent_sku, sku, qty): 
  # if the products dictionary contains an existing ReptilProductQty value with the 
  # parent_sku add the qty to that existing value 
  if sku in products:
    p = products[parent_sku]
    p.addProductQty(sku, qty)
    products[parent_sku] = p 
  else: 
    products[parent_sku] = ReptilProductQty(sku, qty)

  return products


def RabbitBundle(qty, plus_egg, labels):
  multipack = [
    "sku: RLMULTIR-01\nRabbit Multipack: 8-12g (10/10 links)",
    "sku: RLMULTIR-01\nRabbit Multipack: 16-20g (5/5 links)",
    "sku: RLMULTIR-01\nRabbit Multipack: 25g (5/5 links)",
    "sku: RLMULTIR-01\nRabbit Multipack: 50g short (4/4 links)",
    "sku: RLMULTIR-01\nRabbit Multipack: 50g long  (4/4 links)",
    "sku: RLMULTIR-01\nRabbit Multipack: 75g (3/3 links)",
    "sku: RLMULTIR-01\nRabbit Multipack: 100g (2/2 links)"
  ]

  if plus_egg:
    for i, _ in enumerate(multipack):
      multipack[i] = multipack[i] + " +egg"
  
  for _ in range(qty):
    for i, d in enumerate(multipack):
      labels.append(d)


def TeguBundle(qty, plus_egg, regular_products, labels):
  # this bundle also contains 1 order of RLMBFV8
  parent = "RLMBFV"
  asku = "RLMBFV8"
  desc = "sku: RLMBFV8\nMEGA-BLEND + F & V: 8-12 g (20/40 links)"
  if plus_egg:
    asku = asku + "+egg"
    desc = desc + " +egg"

  if parent in regular_products:
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

  # add 10*qty labels for tegu bundle
  for i in range(0, 10*qty):
    desc = "sku: RLTEGU\nMegaBlend, Fruits & Veggies (100 uncased)" 
    labels.append(desc)


def MiniMicro(qty, desc, labels):
  for _ in range(qty):
    # 40 links = 2 labels with 20 links 
    if "(40 links)" in desc:
      d = desc.replace("(40 links)", "(20/40 links)")
      labels.append(d)
      labels.append(d)

    # 24 links = 2 labels with 12 links
    elif "(24 links)" in desc:
      d = desc.replace("(24 links)", "(12/24 links)")
      labels.append(d)
      labels.append(d)

    # 20 links = 2 labels with 10 links
    elif "(20 links)" in desc:
      d = desc.replace("(20 links)", "(10/20 links)")
      labels.append(d)
      labels.append(d)

    # 10 links = 2 labels with 5 links
    elif "(10 links)" in desc:
      d = desc.replace("(10 links)", "(5/10 links)")
      labels.append(d)
      labels.append(d)

    # 7 links = 2 labels with 3 links and 4 links 
    elif "(7 links)" in desc:
      d1 = desc.replace("(7 links)", "(3/7 links)")
      labels.append(d1)
      d2 = desc.replace("(7 links)", "(4/7 links)")
      labels.append(d2)

    # 6 links = 2 labels with 3 links
    elif "(6 links)" in desc:
      d = desc.replace("(6 links)", "(3/6 links)")
      labels.append(d)
      labels.append(d)
    else:
      labels.append(desc)