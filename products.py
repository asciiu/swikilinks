import csv

#file = "products_export.csv"
#f = open(file)
#csv_file = csv.reader(f)
#
#sku_index = 0
#desc_index = 0
#title_index = 0
#
#title = ""
#
#for i, val in enumerate(csv_file):
#
#  # first row should be headers
#  if i == 0:
#    # assign indices of columns based upon headers
#    for j, header in enumerate(val):
#      if header == "Variant SKU":
#        sku_index = j
#      if header == "Option1 Value":
#        desc_index = j
#      if header == "Title":
#        title_index = j
#     # skip outer loop once since the first row are headers
#  else:
#    # if the title is empty in title cell then use the last title
#    title = title if val[title_index] == "" else val[title_index]
#
#    sku = val[sku_index]
#    desc = val[desc_index]
#
#    print title + " (" + val[sku_index] + "): " + val[desc_index] 
#
#f.close()

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

          product = title + " (" + sku + "): " + desc
          products[sku] = product

    f.close()
    return products
