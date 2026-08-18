"""
backend/data_loader.py

Fast in-memory loader and cache for dataset entities:
Reels, Candidates, Users, Creators, Interactions, Sessions, and Relationships.
"""

from typing import Dict, List, Optional
import os
import csv
import json


class DataLoader:
    """Loads all synthetic CSV records into memory for ultra-fast API response times."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.reels: Dict[str, Dict] = {}
        self.reels_list: List[Dict] = []
        self.candidate_reels: List[Dict] = []
        self.candidate_lookup: Dict[str, Dict] = {}
        self.users: Dict[str, Dict] = {}
        self.creators: Dict[str, Dict] = {}
        self.interactions_by_user: Dict[str, List[Dict]] = {}
        self.ground_truth: Dict[str, Dict] = {}
        self.relationships: List[Dict] = []
        self.load_all()

    def _read_csv(self, filename: str) -> List[Dict]:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def load_all(self):
        # 1. Creators
        for c in self._read_csv("creators.csv"):
            self.creators[c["creator_id"]] = c

        # 2. Reels
        self.reels_list = self._read_csv("reels.csv")
        for r in self.reels_list:
            cid = r.get("creator_id")
            if cid in self.creators:
                r["creator"] = self.creators[cid]
            self.reels[r["reel_id"]] = r

        # 3. Candidate Reels
        self.candidate_reels = self._read_csv("candidate_reels.csv")
        for c in self.candidate_reels:
            cid = c.get("creator_id")
            if cid in self.creators:
                c["creator"] = self.creators[cid]
            self.candidate_lookup[c["reel_id"]] = c
            # Ensure candidate reels are also in lookup
            self.reels[c["reel_id"]] = c

        # 4. Users
        for u in self._read_csv("users.csv"):
            self.users[u["user_id"]] = u

        # 5. Ground Truth
        for gt in self._read_csv("ground_truth.csv"):
            self.ground_truth[gt["user_id"]] = gt

        # 6. Interactions
        all_interactions = self._read_csv("interactions.csv")
        for i in all_interactions:
            uid = i["user_id"]
            self.interactions_by_user.setdefault(uid, []).append(i)

        # 7. Relationships
        self.relationships = self._read_csv("technology_relationships.csv")

    def get_user_interactions(self, user_id: str) -> List[Dict]:
        return self.interactions_by_user.get(user_id, [])

    def get_reel(self, reel_id: str) -> Optional[Dict]:
        return self.reels.get(reel_id)

    def get_all_users(self) -> List[Dict]:
        return list(self.users.values())
