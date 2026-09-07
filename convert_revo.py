import os
import xml.etree.ElementTree as ET
import csv

# Vojo al la XML-dosieroj en la submodulo
revo_path = "revo-fonto/revo"
output_file = "vortaro.csv"

print(f"🔍 Skanante dosierojn en {revo_path}...")

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    count = 0
    for filename in os.listdir(revo_path):
        if filename.endswith(".xml"):
            try:
                tree = ET.parse(os.path.join(revo_path, filename))
                root = tree.getroot()
                for drv in root.findall('.//drv'):
                    kap_elem = drv.find('kap')
                    dif_elem = drv.find('.//dif')
                    
                    if kap_elem is not None and dif_elem is not None:
                        # Simpla teksta eltiro
                        kap = "".join(kap_elem.itertext()).replace('*', '').strip()
                        dif = "".join(dif_elem.itertext()).strip()
                        
                        if kap and dif:
                            writer.writerow([kap, dif])
                            count += 1
            except Exception:
                continue
    print(f"✅ Finita! {count} artikoloj skribitaj en {output_file}")
