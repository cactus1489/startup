from markdown_pdf import Section, MarkdownPdf
import os

def convert_md_to_pdf(input_path, output_path):
    print(f"Reading {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(md_content, toc=False))
    pdf.save(output_path)
    print(f"Successfully saved to {output_path}")

if __name__ == "__main__":
    input_file = '/Users/garam/Desktop/icb6/team project/a_final/Coffee_Index_Final_Report_260221.md'
    output_file = '/Users/garam/Desktop/icb6/team project/a_final/Coffee_Index_Final_Report_260221.pdf'
    convert_md_to_pdf(input_file, output_file)
