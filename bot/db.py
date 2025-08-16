import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from loguru import logger

try:
	from pymongo import MongoClient, ASCENDING
	from pymongo.collection import Collection
	has_pymongo = True
except Exception:
	has_pymongo = False


class InMemoryStore:
	def __init__(self):
		self.users: Dict[str, Dict[str, Any]] = {}
		self.otps: Dict[str, Dict[str, Any]] = {}

	def get_user(self, email: str) -> Optional[Dict[str, Any]]:
		return self.users.get(email.lower())

	def upsert_user(self, email: str, update: Dict[str, Any]) -> Dict[str, Any]:
		em = email.lower()
		user = self.users.get(em) or {"email": em, "created_at": datetime.utcnow()}
		user.update(update)
		self.users[em] = user
		return user

	def save_otp(self, email: str, code: str, expires_at: datetime):
		self.otps[email.lower()] = {"code": code, "expires_at": expires_at}

	def consume_otp(self, email: str, code: str) -> bool:
		rec = self.otps.get(email.lower())
		if not rec:
			return False
		if rec["code"] != code:
			return False
		if datetime.utcnow() > rec["expires_at"]:
			return False
		# one-time use
		del self.otps[email.lower()]
		return True


class MongoStore:
	def __init__(self, uri: str, db_name: str = "winnerbot"):
		client = MongoClient(uri)
		db = client[db_name]
		self.users: Collection = db["users"]
		self.otps: Collection = db["otps"]
		try:
			self.otps.create_index([("email", ASCENDING)], unique=True)
			self.otps.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
		except Exception as e:
			logger.warning(f"Mongo index creation issue: {e}")

	def get_user(self, email: str) -> Optional[Dict[str, Any]]:
		return self.users.find_one({"email": email.lower()})

	def upsert_user(self, email: str, update: Dict[str, Any]) -> Dict[str, Any]:
		em = email.lower()
		res = self.users.find_one_and_update(
			{"email": em},
			{"$set": update, "$setOnInsert": {"email": em, "created_at": datetime.utcnow()}},
			upsert=True,
			return_document=True,
		)
		if res is None:
			res = self.users.find_one({"email": em})
		return res or {"email": em}

	def save_otp(self, email: str, code: str, expires_at: datetime):
		self.otps.update_one(
			{"email": email.lower()},
			{"$set": {"email": email.lower(), "code": code, "expires_at": expires_at}},
			upsert=True,
		)

	def consume_otp(self, email: str, code: str) -> bool:
		rec = self.otps.find_one({"email": email.lower()})
		if not rec:
			return False
		if rec.get("code") != code:
			return False
		if datetime.utcnow() > rec.get("expires_at", datetime.utcnow()):
			return False
		self.otps.delete_one({"email": email.lower()})
		return True


def get_store():
	uri = os.getenv("MONGODB_URI", "").strip()
	if uri and has_pymongo:
		return MongoStore(uri)
	return InMemoryStore()