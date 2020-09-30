import PyPDF2 #pip install PyPDF2

# url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo2019.pdf'
# url = 'https://www.eia.gov/outlooks/aeo/pdf/aeo2018.pdf'

path = r'c:\users\jeff levy\downloads\aeo2019.pdf'

with open(path, 'rb') as ifile:
    pdf = PyPDF2.PdfFileReader(ifile)

    print('Number of pages:', pdf.numPages)

    pages = []
    for p in range(pdf.numPages):
        page = pdf.getPage(p)
        text = page.extractText()
        pages.append(text)
