from datetime import datetime, timezone
from bson import ObjectId
from db import get_db


def get_all_categories():
    db = get_db()
    return list(db.categories.find().sort("name", 1))


def get_subcategories(category_id=None):
    db = get_db()
    query = {}
    if category_id:
        query["category_id"] = ObjectId(category_id) if isinstance(category_id, str) else category_id
    return list(db.subcategories.find(query).sort("name", 1))


def get_subcategory(subcat_id):
    db = get_db()
    return db.subcategories.find_one({"_id": ObjectId(subcat_id) if isinstance(subcat_id, str) else subcat_id})


def add_category(name: str):
    db = get_db()
    result = db.categories.insert_one({
        "name": name.strip(),
        "created_at": datetime.now(timezone.utc),
    })
    return result.inserted_id


def update_category(category_id, name: str):
    db = get_db()
    db.categories.update_one(
        {"_id": ObjectId(category_id) if isinstance(category_id, str) else category_id},
        {"$set": {"name": name.strip()}},
    )


def delete_category(category_id):
    """Deletes the category and all its subcategories."""
    db = get_db()
    oid = ObjectId(category_id) if isinstance(category_id, str) else category_id
    db.subcategories.delete_many({"category_id": oid})
    db.categories.delete_one({"_id": oid})


def add_subcategory(name: str, category_id, assignee):
    db = get_db()
    result = db.subcategories.insert_one({
        "name": name.strip(),
        "category_id": ObjectId(category_id) if isinstance(category_id, str) else category_id,
        "assignee": assignee,  # "Yash" | "Daksha" | None
        "created_at": datetime.now(timezone.utc),
    })
    return result.inserted_id


def update_subcategory(subcat_id, name: str = None, assignee=...):
    """
    Pass name to rename. Pass assignee to change it ("Yash" | "Daksha" | None).
    Use the sentinel default to leave assignee unchanged.
    """
    db = get_db()
    updates = {}
    if name is not None:
        updates["name"] = name.strip()
    if assignee is not ...:
        updates["assignee"] = assignee
    if updates:
        db.subcategories.update_one(
            {"_id": ObjectId(subcat_id) if isinstance(subcat_id, str) else subcat_id},
            {"$set": updates},
        )


def delete_subcategory(subcat_id):
    db = get_db()
    db.subcategories.delete_one({"_id": ObjectId(subcat_id) if isinstance(subcat_id, str) else subcat_id})
