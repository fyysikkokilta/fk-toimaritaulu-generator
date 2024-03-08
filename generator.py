import os
import json
import sys
from fpdf import FPDF
from xhtml2pdf import pisa

def create_toimari_object(jaokset, toimarit, kuvat):
    toimaritJaoksittain = {}
    for jaos_nimi, jaos_virat in jaokset.items():
        toimaritJaoksittain[jaos_nimi] = []
        for toimari_nimi, toimari_virat in toimarit.items():
            toimari_virat_jaoksessa = []
            for virka in toimari_virat:
                if virka in jaos_virat:
                    toimari_virat_jaoksessa.append(virka)
            if len(toimari_virat_jaoksessa) > 0:
                toimaritJaoksittain[jaos_nimi].append({
                    "nimi": toimari_nimi,
                    "virat": toimari_virat_jaoksessa,
                    "kuva": kuvat[toimari_nimi]
                })
    return toimaritJaoksittain

def create_html(data, default_image, cells_per_row, jaos_colors_and_order):
    html_content = f'<div style="font-family: Source Sans Pro,Calibri,sans-serif,Apple Color Emoji,Segoe UI Emoji,Segoe UI Symbol,Noto Color Emoji; padding: 0; width: fit-content;">'
    html_content += f'<div style="display: flex; flex-direction: row">'

    counter = 0

    for jaos in jaos_colors_and_order.keys():
        toimihenkilot = sorted(data[jaos], key=lambda x: (x["virat"][0], x["nimi"]))
        background_color = jaos_colors_and_order.get(jaos, "lightgray")
        text_color = "black" if background_color == "#fbdb1d" else "white"
        html_content += f'<div style="display: flex; text-align: left; justify-content: center; align-items: center; padding: 2% 1%; color: {text_color}; background-color: {background_color}; font-family: Lora,Helvetica,serif; font-style: italic"><div style="width: 160px;"><h3>{jaos}</h3></div></div>'

        if counter % cells_per_row == cells_per_row - 1:
                html_content += '</div><div style="display: flex; flex-direction: row">'

        counter += 1

        for i, toimihenkilo in enumerate(toimihenkilot, start=1):
            image_path = f"kuvat/{toimihenkilo['kuva']}"
            
            # Check if the image file exists before adding the image tag
            if os.path.exists(image_path):
                img_tag = f'<div style="min-height: 250px"><img src="{image_path}" width="160px" style="margin-bottom: 10px;"></div>'
            else:
                img_tag = f'<div style="min-height: 250px"><img src="{default_image}" width="160px" style="margin-bottom: 10px;"></div>'

            cell_html = f'<div style="display: inline-block; width: 160px; text-align: center; padding: 3.5% 1%; color: {text_color}; background-color: {background_color};">{img_tag}<br><b>{toimihenkilo["nimi"]}</b><br>{", ".join(toimihenkilo["virat"])}</div>'
            
            html_content += cell_html

            if counter % cells_per_row == cells_per_row - 1:
                html_content += '</div><div style="display: flex; flex-direction: row">'

            counter += 1

    html_content += '</div>'
    html_content += '</div>'

    return html_content

# Read JSON files
with open('jaokset.json', encoding='utf-8') as f:
    jaokset = json.load(f)

with open('toimarit.json', encoding='utf-8') as f:
    toimarit = json.load(f)

with open('kuvat.json', encoding='utf-8') as f:
    kuvat = json.load(f)

# Define background colors for each jaos
jaos_colors_and_order = {
    "Fuksijaos": "#fbdb1d",
    "Hyvinvointijaos": "#ff8a04",
    "Infojaos": "#007bff",
    "Opintojaos": "#28a745",
    "Tapahtumajaos": "#911f2f",
    "Ulkojaos": "#fbdb1d",
    "Yrityssuhdejaos": "#ff8a04",
    "Muut toimihenkilöt": "#007bff"
}

default_image = "kuvat/fii_pelle2-valk-1024x1024.png"

if __name__ == "__main__":
    data = create_toimari_object(jaokset, toimarit, kuvat)
    if len(sys.argv) != 2:
        raise ValueError("Invalid number of arguments, expected 1 argument (cells per row)")
    cells_per_row = sys.argv[1]
    if not cells_per_row.isnumeric() or int(cells_per_row) < 1:
        raise ValueError("Invalid number of cells per row")
    
    html_content = create_html(data, default_image, int(cells_per_row), jaos_colors_and_order)

    pdf_content = f'<html><head><style>img {{border-radius: 50%;}}@page {{size: a4 portrait}}</style></head><body style="margin: 0;">{html_content}</body></html>'

    with open('toimihenkilot.html', 'w', encoding='utf-8') as html_file:
        html_file.write(pdf_content)

    #result_file = open("toimihenkilot.pdf", "w+b")

    # convert HTML to PDF
    #pisa_status = pisa.CreatePDF(
    #        pdf_content,                # the HTML to convert
    #        dest=result_file)           # file handle to recieve result

    # close output file
    #result_file.close()                 # close output file

    # return False on success and True on errors
    #print(pisa_status.err)
