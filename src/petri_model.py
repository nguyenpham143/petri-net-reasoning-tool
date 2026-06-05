import numpy as np
from typing import List, Optional

class SafePetriNetSystem:
    """
    Lop dai dien cho he thong Mang Petri An Toan (1-safe Petri Net).
    Trong mang nay, moi Place chi chua toi da 1 token tai moi thoi diem.
    """
    def __init__(
        self,
        places: List[str],
        transitions: List[str],
        pre_matrix: np.ndarray,
        post_matrix: np.ndarray,
        initial_marking: np.ndarray,
        place_labels: Optional[List[str]] = None,
        transition_labels: Optional[List[str]] = None
    ):
        self.places = places              # Tap hop P
        self.transitions = transitions    # Tap hop T
        
        # Nhan hien thi (dung de in log cho dep)
        self.place_labels = place_labels if place_labels else places
        self.transition_labels = transition_labels if transition_labels else transitions
        
        # Ma tran cau truc (Structure Matrices)
        # Kich thuoc: [So Transition x So Place]
        self.pre_matrix = pre_matrix      # I (Input): So token t lay khoi p
        self.post_matrix = post_matrix    # O (Output): So token t sinh ra tai p
        
        # Trang thai ban dau (Marking vector M0)
        self.initial_marking = initial_marking

    @property
    def num_places(self) -> int:
        return len(self.places)

    @property
    def num_transitions(self) -> int:
        return len(self.transitions)

    def print_details(self):
        """In thong tin chi tiet ve mang Petri ra man hinh."""
        print("\n" + "="*40)
        print("      PETRI NET MODEL DETAILS      ")
        print("="*40)
        print(f"Total Places:      {self.num_places}")
        print(f"Total Transitions: {self.num_transitions}")
        
        print("\n[Places List]")
        print(f"{self.places}")

        print("\n[Transitions List]")
        print(f"{self.transitions}")
        
        print("\n[Initial Marking M0]")
        print(self.initial_marking)
        
        print("\n[Pre Matrix (Input) - Size: TxP]")
        print(self.pre_matrix)
        
        print("\n[Post Matrix (Output) - Size: TxP]")
        print(self.post_matrix)
        print("="*40 + "\n")

    def get_enabled_transitions(self, current_m: np.ndarray) -> List[int]:
        """
        Xac dinh cac transition co the ban tai trang thai hien tai.
        Dieu kien: M(p) >= Pre(p, t) voi moi place p.
        """
        enabled_indices = []
        for t_idx in range(self.num_transitions):
            # Lay dong t trong ma tran Pre (nhu cau token dau vao)
            required_tokens = self.pre_matrix[t_idx]
            
            # Kiem tra: Trang thai hien tai co du token khong?
            if np.all(current_m >= required_tokens):
                enabled_indices.append(t_idx)
        return enabled_indices

    def fire_transition(self, current_m: np.ndarray, t_idx: int) -> np.ndarray:
        """
        Thuc hien ban transition t, chuyen he thong sang trang thai moi.
        Cong thuc: M' = M - Pre(t) + Post(t)
        """
        new_m = current_m.copy()
        new_m = new_m - self.pre_matrix[t_idx] + self.post_matrix[t_idx]
        return new_m