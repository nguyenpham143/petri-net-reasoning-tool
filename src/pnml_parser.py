import xml.etree.ElementTree as ET
import numpy as np
import os
from src.petri_model import SafePetriNetSystem

class PNMLReader:
    """
    Bo doc file chuan PNML (Petri Net Markup Language).
    Nhiem vu: Parse XML -> Trich xuat P, T, Arc -> Tao doi tuong SafePetriNetSystem.
    """
    
    @staticmethod
    def read_file(file_path: str) -> SafePetriNetSystem:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            raise ValueError(f"XML Parsing Error: {e}")

        # --- Xu ly Namespace XML ---
        # File PNML thuong co namespace dang {http://pnml.org...}
        ns_map = {}
        if '}' in root.tag:
            url = root.tag.split('}')[0].strip('{')
            ns_map = {'p': url}
            def _tag(t): return f"p:{t}"
        else:
            def _tag(t): return t

        # 1. Doc Places (Giu nguyen thu tu trong file)
        raw_places = []
        for p in root.findall(f".//{_tag('place')}", ns_map):
            pid = p.get('id')

            # Lay ten hien thi
            name_node = p.find(f"{_tag('name')}/{_tag('text')}", ns_map)
            pname = name_node.text if name_node is not None else pid
            
            # Lay so token ban dau
            m0 = 0
            mark_node = p.find(f"{_tag('initialMarking')}/{_tag('text')}", ns_map)
            if mark_node is not None:
                try: m0 = int(mark_node.text)
                except: m0 = 0
            
            raw_places.append({'id': pid, 'name': pname, 'm0': m0})

        # 2. Doc Transitions
        raw_trans = []
        for t in root.findall(f".//{_tag('transition')}", ns_map):
            tid = t.get('id')
            name_node = t.find(f"{_tag('name')}/{_tag('text')}", ns_map)
            tname = name_node.text if name_node is not None else tid
            raw_trans.append({'id': tid, 'name': tname})

        # 3. Xay dung Ma tran
        place_ids = [item['id'] for item in raw_places]
        trans_ids = [item['id'] for item in raw_trans]
        
        # Map ID -> index de dien ma tran nhanh
        p_idx = {pid: i for i, pid in enumerate(place_ids)}
        t_idx = {tid: i for i, tid in enumerate(trans_ids)}
        
        num_p = len(place_ids)
        num_t = len(trans_ids)
        
        pre_mat = np.zeros((num_t, num_p), dtype=int)
        post_mat = np.zeros((num_t, num_p), dtype=int)

        # Duyet qua cac cung (Arcs)
        for arc in root.findall(f".//{_tag('arc')}", ns_map):
            src = arc.get('source')
            tgt = arc.get('target')
            
            w = 1
            insc = arc.find(f"{_tag('inscription')}/{_tag('text')}", ns_map)
            if insc is not None:
                try: w = int(insc.text)
                except: pass

            if src in p_idx and tgt in t_idx:
                # Place -> Transition (Pre Matrix)
                pre_mat[t_idx[tgt], p_idx[src]] = w
            elif src in t_idx and tgt in p_idx:
                # Transition -> Place (Post Matrix)
                post_mat[t_idx[src], p_idx[tgt]] = w

        # Tao vector M0
        m0_vec = np.array([item['m0'] for item in raw_places], dtype=int) if raw_places else np.array([], dtype=int)

        return SafePetriNetSystem(
            places=place_ids,
            transitions=trans_ids,
            pre_matrix=pre_mat,
            post_matrix=post_mat,
            initial_marking=m0_vec,
            place_labels=[item['name'] for item in raw_places],
            transition_labels=[item['name'] for item in raw_trans]
        )