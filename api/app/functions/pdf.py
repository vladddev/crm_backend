from fpdf import FPDF

class PDF(FPDF):
    def footer(self):
        self.set_y(-10)
        self.add_font('DejaVu', '', 'static/fonts/DejaVuSansCondensed.ttf', uni=True)
        # Select Arial italic 8
        self.set_font('DejaVu', size=10)
        # Print centered page number
        self.cell(185)
        self.cell(0, 10, str(self.page_no()))