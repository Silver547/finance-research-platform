from bse import BSE

candidates = {
    "HPCL": ["HPCL", "HINDPETRO"],
    "VEDANTA": ["VEDANTA", "VEDL"],
    "LTIM": ["LTIM", "LTIMINDTREE"],
    "TATAMOTORS": ["TATAMOTORS", "TATAMOTORS-PV", "TMPV"],
}

with BSE(download_folder="./") as bse_client:
    for label, names in candidates.items():
        for name in names:
            try:
                code = bse_client.getScripCode(name)
                print(f"{label}: '{name}' -> scrip code {code}")
            except Exception as exc:
                print(f"{label}: '{name}' -> FAILED ({exc})")