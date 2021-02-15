from pyzolocal.apis.fastapi import get_fastapis

app = get_fastapis()

"""
then run in shell:
    uvicorn examples.fastapi_demo:app --reload
    
then visit http://127.0.0.1:8000/docs to view api list
"""
