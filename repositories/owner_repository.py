from __future__ import annotations
from typing import Optional
import streamlit as st
from models.owner import Owner


class OwnerRepository:
	def __init__(self):
		st.session_state.setdefault("owners", {})
		st.session_state.setdefault("next_owner_id", 1)

	@property
	def _store(self) -> dict[int, Owner]:
		return st.session_state["owners"]

	@property
	def _next_id(self) -> int:
		return st.session_state["next_owner_id"]

	@_next_id.setter
	def _next_id(self, value: int) -> None:
		st.session_state["next_owner_id"] = value

	def create(self, first_name: str, last_name: str) -> Owner:
		owner = Owner(
			first_name=first_name,
			last_name=last_name,
		)
		owner.id = self._next_id
		self._next_id += 1
		self._store[owner.id] = owner
		return owner

	def get(self, owner_id: int) -> Optional[Owner]:
		return self._store.get(owner_id)

	def update(
		self,
		owner_id: int,
		first_name: str,
		last_name: str,
	) -> Optional[Owner]:
		owner = self.get(owner_id)
		
		if owner is None:
			return None
		owner.first_name = first_name
		owner.last_name = last_name
		return owner

	def delete(self, owner_id: int) -> bool:
		return self._store.pop(owner_id, None) is not None

	def get_all(self) -> list[Owner]:
		return list(self._store.values())
