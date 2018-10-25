
def Avery5160(x, y):
    #left = 4.826    # 0.19" in mm
    #top = 12.7      # 0.5" in mm
    #width = 76.802  # 2.63" in mm
    #height = 25.4   # 1.0" in mm
    #hgap = 3.048    # 0.12" in mm
    #vgap = 0.0      

    left = 4.7625 # 0.1875" in mm
    top = 12.7 # 0.5" in mm
    width = 66.675 # 2.625" in mm
    height = 25.4 # 1.0" in mm
    hgap = 3.175 # 0.125" in mm
    vgap = 0.0

    x = left + ((width + hgap) * x)
    y = top + ((height + vgap) * y)
    return (x, y, width, 5)
    #pdf.SetXY(x, y)
    #pdf->MultiCell(width, 5, text, 1, 'C')