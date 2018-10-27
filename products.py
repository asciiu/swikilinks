import csv
import re

# parses the products export csv from shopify
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