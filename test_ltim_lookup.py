from bse import BSE

with BSE(download_folder="./") as bse_client:
    for term in ["LTI", "MINDTREE", "L&T", "LTIMINDTREE LIMITED"]:
        try:
            result = bse_client.lookup(term)
            print(f"'{term}' ->", result)
        except Exception as exc:
            print(f"'{term}' -> FAILED ({exc})")