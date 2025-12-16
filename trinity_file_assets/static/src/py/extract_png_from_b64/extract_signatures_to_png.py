import csv
import base64
from pathlib import Path

# Input CSV path
INPUT_CSV = Path("/opt/odoo18/custom/signatures/input.csv")

OUTPUT_DIR = INPUT_CSV.parent

with open(INPUT_CSV, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Get fields
        e_examination_lrn = row["e_examination_lrn"]
        b64_data = row["Signature_0_b64"]

        # Decode Base64 to binary PNG data
        img_data = base64.b64decode(b64_data)

        # Save as PNG
        filename = f"signature_{e_examination_lrn}.png"
        filepath = OUTPUT_DIR / filename

        with open(filepath, "wb") as f:
            f.write(img_data)

        print(f"✅ Saved {filepath}")

# sudo mkdir -p /opt/odoo18/custom/signatures && sudo chown -R odoo18:odoo18 /opt/odoo18/custom/signatures && sudo chmod -R 755 /opt/odoo18/custom/signatures
# sudo rm -r /opt/odoo18/custom/signatures
# python3 /opt/odoo18/custom/signatures/extract_signatures_to_png.py