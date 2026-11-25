from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="This is a test scientific document.", ln=True)
pdf.cell(200, 10, txt="The main claim is that AI can parse PDFs and summarize them.", ln=True)
pdf.output("test.pdf")
print("test.pdf created")
