from fpdf import FPDF
 
pdf = FPDF()
# define one column and one row margins
pdf.set_margins(297.0/14.0,210.0/20.0)
pdf.set_font('Arial','B',7)
 
pdf.add_page()
#define total rows containing labels
rows=28-2-1-1
# define total columns containing labels
cols=8
#define column size and tweak it empirically <img draggable="false" class="emoji" alt="" src="https://s0.wp.com/wp-content/mu-plugins/wpcom-smileys/twemoji/2/svg/1f642.svg">
columnsize=(297.0/14.0)+5.0/12.0
 
print columnsize
print columnsize*14
 
# define serial number start
serial=0
 
for i in range(rows):
 
    for j in range(cols):
        text="SN: 00-%03i" % serial
        serial+=1
        pdf.set_font('Arial','B',8)
        pdf.cell(columnsize,0,text, align="C")
    pdf.ln()
    for j in range(cols):
        pdf.set_font('Arial','B',6)
        pdf.cell(columnsize,7,"|B|F|D|O|C|L|V|", align="C")
    pdf.ln()
    for j in range(cols):
        pdf.cell(columnsize,(210/20)-6,"")
    pdf.ln()
 
pdf.output('labels.pdf','F')