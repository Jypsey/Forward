import pymongo
from pymongo import MongoClient
import os

class Database:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
        self.db = self.client["telegram_forwarder"]
        self.media_queue = self.db["media_queue"]

    def add_media(self, file_path, caption, is_video):
        media = {
            "file_path": file_path,
            "caption": caption,
            "is_video": is_video,
            "status": "pending",
            "created_at": pymongo.utils.datetime.datetime.utcnow()
        }
        result = self.media_queue.insert_one(media)
        return result.inserted_id

    def get_pending_media(self, limit=5):
        return list(self.media_queue.find({"status": "pending"}).sort("created_at", pymongo.ASCENDING).limit(limit))

    def mark_completed(self, media_id):
        self.media_queue.update_one(
            {"_id": media_id},
            {"$set": {"status": "completed"}}
        )

    def cleanup_old(self):
        self.media_queue.delete_many({
            "status": "completed",
            "created_at": {"$lt": pymongo.utils.datetime.datetime.utcnow() - pymongo.timedelta(hours=1)}
        })
