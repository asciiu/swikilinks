def PrintCells(fpdf, title, prds, x, y):
  # Sort the dictionary of skus in order_qty
  sorted_skus = sorted(prds)

  # column coords
  cx = x
  cy = y

  # create header cell 
  fpdf.set_xy(cx, cy)
  fpdf.set_fill_color(200)
  fpdf.cell(70, 5, title, 1, 1, 'C', True)
  fpdf.set_fill_color(0)
  cy += 5

  # for each sku in the sorted list of skus
  for sku in sorted_skus:
    rl = prds[sku]
    sub_products = rl.subProducts()
  
    # begin new column
    if cy > 250:
      cy = y 
      cx += 70

    # print the parent sku
    fpdf.set_xy(cx, cy)
    fpdf.cell(20, 5*len(sub_products), rl.parent_sku, 1, 1)

    xm = cx + 20  
    fpdf.set_xy(xm, cy)
    for v in rl.subProducts():
      fpdf.cell(35, 5, v, 1, 0)
      fpdf.cell(10, 5, str(rl.product_qty[v]), 1, 0, 'R')

      # this empty box is reserved for check box
      fpdf.cell(5, 5, "", 1, 0)

      cy += 5
      fpdf.set_xy(xm, cy)

  return (cx, cy)