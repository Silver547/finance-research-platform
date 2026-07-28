from bse import BSE

with BSE(download_folder='./') as bse:
    code = bse.getScripCode('RELIANCE')
    print("Scrip code:", code)
    snapshot = bse.resultsSnapshot(code)
    print(snapshot)
    