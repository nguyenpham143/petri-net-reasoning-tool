import re
import collections
import collections.abc

# --- VA LOI TUONG THICH PYTHON 3.10+ ---
# Thu vien pyeda cu goi 'collections.Sequence', nhung tu Python 3.10
# no da bi chuyen sang 'collections.abc.Sequence'.
# Doan code nay tu dong gan lai de tranh loi "AttributeError".
if not hasattr(collections, "Sequence"):
    collections.Sequence = collections.abc.Sequence

def sanitize_variable_name(raw_name: str) -> str:
    """
    Chuan hoa ten bien de su dung an toan trong thu vien BDD (pyeda).
    
    Ly thuyet: Cac thu vien BDD thuong yeu cau ten bien tuan thu quy tac C/Python 
    (chi chua chu cai, so, gach duoi). Cac ky tu nhu '-', ' ' se gay loi cu phap.
    """
    # Thay the tat ca ky tu KHONG phai chu/so bang dau gach duoi
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(raw_name))
    
    # Ten bien khong duoc bat dau bang so (vi du: "1_place" -> "v_1_place")
    if safe_name and safe_name[0].isdigit():
        safe_name = "v_" + safe_name
        
    return safe_name