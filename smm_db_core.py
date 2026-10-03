import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import FieldFilter # added due to firebase warning due to firebase warning to use filter instead
import datetime
import os

def get_db_client():
    """Initializes firebase connection using JSON key and returns Firestore client."""
    if not os.path.exists("serviceAccountKey.json"):
        raise FileNotFoundError("Missing 'serviceAccountKey.json' credential file.")
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

# ==========================================
# C - CREATE (Insert)
# ==========================================
def add_cookbook_record(db, cookbook_id: str, title: str, file_path: str):
    """Inserts a new cookbook document into the parent collection."""
    cb_ref = db.collection("cookbooks").document(cookbook_id)
    cb_ref.set({
        "title": title,
        "file_path": file_path,
        "added_at": datetime.datetime.utcnow().isoformat()
    })

def add_recipe_chunk(db, cookbook_id: str, page_num: int, text_content: str):
    """Inserts a text chunk linked to a parent cookbook document using the parent cookbook ID."""
    chunk_ref = db.collection("recipe_chunks").document() # Auto-generates unique ID
    chunk_ref.set({
        "cookbook_id": cookbook_id, # 🔗 Relational bridge reference link
        "page_number": page_num,
        "text_content": text_content,
        "added_at": datetime.datetime.utcnow().isoformat()
    })

# ==========================================
# R - READ (Query)
# ==========================================
def search_chunks_by_keyword(db, keyword: str) -> list:
    """Loops through all text chunks matching the given keyword."""
    chunks_ref = db.collection("recipe_chunks")
    docs = chunks_ref.stream()
    results = []
    
    for doc in docs:
        data = doc.to_dict()
        if keyword.lower() in data.get("text_content", "").lower():
            # Include the database generated ID for tracking
            data["document_id"] = doc.id
            results.append(data)
    return results

# ==========================================
# U - UPDATE (Modify)
# ==========================================
def update_cookbook_title(db, cookbook_id: str, new_title: str) -> bool:
    """Finds a cookbook by its ID and if it exists it changes the title field."""
    cb_ref = db.collection("cookbooks").document(cookbook_id)
    if not cb_ref.get().exists:
        return False
    cb_ref.update({"title": new_title})
    return True

# ==========================================
# D - DELETE (Remove)
# ==========================================
def delete_cookbook_cascade(db, cookbook_id: str) -> int:
    """Deletes all matching child chunks first, then removes the parent cookbook."""
    cb_ref = db.collection("cookbooks").document(cookbook_id)
    
    # Verify the book exists before doing anything
    if not cb_ref.get().exists:
        return -1  # Return -1 as an error code indicating the book wasn't found

    # 1. Clean up child chunks containing the parent reference link
    chunks_ref = db.collection("recipe_chunks")
    # chunks = chunks_ref.where("cookbook_id", "==", cookbook_id).stream()
    # replaced the line above with line below due to firebase warning to use filter instead
    chunks = chunks_ref.where(filter=FieldFilter("cookbook_id", "==", cookbook_id)).stream()

    deleted_chunks = 0
    for chunk in chunks:
        db.collection("recipe_chunks").document(chunk.id).delete()
        deleted_chunks += 1
        
    # 2. Purge primary parent cookbook record
    db.collection("cookbooks").document(cookbook_id).delete()
    return deleted_chunks
