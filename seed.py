from datetime import datetime, timezone
from db import get_db
from config import DEFAULT_CATEGORIES


def seed_categories():
    db = get_db()

    if db.categories.count_documents({}) > 0:
        return  # already seeded

    for cat_data in DEFAULT_CATEGORIES:
        cat_result = db.categories.insert_one({
            "name": cat_data["name"],
            "created_at": datetime.now(timezone.utc),
        })
        cat_id = cat_result.inserted_id

        subcats = [
            {
                "name": sub["name"],
                "category_id": cat_id,
                "assignee": sub["assignee"],
                "created_at": datetime.now(timezone.utc),
            }
            for sub in cat_data["subcategories"]
        ]
        if subcats:
            db.subcategories.insert_many(subcats)


def create_indexes():
    db = get_db()
    db.subcategories.create_index("category_id")
    db.transactions.create_index("date")
    db.transactions.create_index("paid_by")
    db.transactions.create_index("category_id")
    db.transactions.create_index("subcategory_id")
    db.budgets.create_index(
        [("month", 1), ("category_id", 1), ("subcategory_id", 1)],
        unique=True,
    )


def run():
    create_indexes()
    seed_categories()
