from __future__ import annotations
from typing import Optional
import streamlit as st
from models.pet import Pet


class PetRepository:
    def __init__(self):
        st.session_state.setdefault("pets", {})
        st.session_state.setdefault("next_pet_id", 1)

    @property
    def _store(self) -> dict[int, Pet]:
        return st.session_state["pets"]

    @property
    def _next_id(self) -> int:
        return st.session_state["next_pet_id"]

    @_next_id.setter
    def _next_id(self, value: int) -> None:
        st.session_state["next_pet_id"] = value

    def create(self, owner_id: int, name: str,
               animal_type: Optional[str] = None, breed: Optional[str] = None) -> Pet:
        pet = Pet(name=name, owner_id=owner_id, animal_type=animal_type, breed=breed)
        pet.id = self._next_id
        self._next_id += 1
        self._store[pet.id] = pet
        return pet

    def get(self, pet_id: int) -> Optional[Pet]:
        return self._store.get(pet_id)

    def get_by_owner(self, owner_id: int) -> list[Pet]:
        return [p for p in self._store.values() if p.owner_id == owner_id]

    def update(self, pet_id: int, name: str,
               animal_type: Optional[str], breed: Optional[str]) -> Optional[Pet]:
        pet = self.get(pet_id)
        if pet is None:
            return None
        pet.name = name
        pet.animal_type = animal_type
        pet.breed = breed
        return pet

    def delete(self, pet_id: int) -> bool:
        return self._store.pop(pet_id, None) is not None
