def PrintCells(fpdf, title, prds, x, y, yo):
  endpage = 260 
  line_height = 5

  # Sort the dictionary of skus in order_qty
  sorted_skus = sorted(prds)

  # column coords
  cx = x
  cy = y

  # create header cell 
  fpdf.set_xy(cx, cy)
  fpdf.set_fill_color(200)
  fpdf.cell(70, line_height, title, 1, 1, 'C', True)
  fpdf.set_fill_color(0)
  cy += line_height 

  # for each sku in the sorted list of skus
  for sku in sorted_skus:
    rl = prds[sku]
    sub_products = rl.subProducts()
    parent_height =  line_height * len(sub_products) 
  
    # begin new column
    if cy + parent_height >= endpage:
      cy = yo 
      cx += 70

    # print the parent sku
    fpdf.set_xy(cx, cy)
    fpdf.cell(20, parent_height, rl.parent_sku, 1, 1)

    xm = cx + 20  
    fpdf.set_xy(xm, cy)
    for v in rl.subProducts():
      fpdf.cell(35, line_height, v, 1, 0)
      fpdf.cell(10, line_height, str(rl.product_qty[v]), 1, 0, 'R')

      # this empty box is reserved for check box
      fpdf.cell(line_height, line_height, "", 1, 0)

      cy += line_height 
      fpdf.set_xy(xm, cy)

  # the column should not be allowed to end with a single empty line
  # otherwise the title section header could appear as the last line
  # of the column - we do not want this.
  if cy > endpage - line_height * 2:
    cy = yo
    cx += 70

  return (cx, cy)