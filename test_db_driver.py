import smm_db_core
import os

# Sample data to test CRUD
MOCK_CHUNKS = [
    {"page": 12, "text": "Ingredients: 2 lbs chicken breast, 1 cup salsa, cumin. [Page 12] Slow cook on high for 4 hours."},
    {"page": 13, "text": "Instructions: Shred the cooked chicken using two forks. Serve hot inside warm corn tortillas."}
]

# ==========================================
# 🎛️ MAIN MENU
# ==========================================
def run_test_menu():
    try:
        db = smm_db_core.get_db_client()
    except Exception as e:
        print(f"[ERROR] Could not connect to database module: {e}")
        return

    while True:
        print("\n=========================================")
        print(" Python-Firestore CRUD Menu")
        print("=========================================")
        print("1. [CREATE] Add Cookbook & Sample Text Chunks")
        print("2. [READ] Search Cookbook Text Chunks by Keyword")
        print("3. [UPDATE] Update a Cookbook Title")
        print("4. [DELETE] Delete a Cookbook & Linked Text Chunks")
        print("5. Exit Program")
        
        choice = input("\nChoose an option (1-5): ").strip()
        
        if choice == "1":
            cb_id = "test-bible"
            print(f"\nCreating cookbook record for '{cb_id}'...")
            smm_db_core.add_cookbook_record(db, cb_id, "The Master Ingestion Guide", "/vault/mock_book.pdf")
            print("[SUCCESS] Core DB module processed parent creation.")
            
            print(f"Inserting {len(MOCK_CHUNKS)} sample text chunks...")
            for chunk in MOCK_CHUNKS:
                smm_db_core.add_recipe_chunk(db, cb_id, chunk["page"], chunk["text"])
            print("✔️ Successfully inserted cookbook and linked chunks to Firestore!")
            
        elif choice == "2":
            keyword = input("\nEnter keyword to search for (e.g. chicken): ").strip()
            if not keyword: continue
            
            print("Querying Firestore database...")
            matches = smm_db_core.search_chunks_by_keyword(db, keyword)
            
            for idx, match in enumerate(matches, start=1):
                print(f"\n🎯 [MATCH #{idx}] Document ID: {match['document_id']}")
                print(f"🔗 Linked Cookbook: {match['cookbook_id']}")
                print(f"📖 Text Chunk: {match['text_content']}")
                print("-" * 50)
            if not matches:
                print(f"No database records matched the word: '{keyword}'")
                
        elif choice == "3":
            cb_id = input("\nEnter the cookbook ID of the Title you want to update: ").strip()
            new_title = input("Enter the new title: ").strip()
            
            print("Updating Cookbook Title...")
            if smm_db_core.update_cookbook_title(db, cb_id, new_title):
                print(f"✔️ Title successfully changed for cookbook ID '{cb_id}'.")
            else:
                print(f"Cookbook '{cb_id}' not found.")
                
        elif choice == "4":
            cb_id = input("\nEnter cookbook ID to delete: ").strip()
            confirm = input(f"Are you sure you want to delete '{cb_id}'? (yes/no): ")
            if confirm.lower() != 'yes': continue
            
            print("Performing cascading delete...")
            count = smm_db_core.delete_cookbook_cascade(db, cb_id)
            # print(f"✔️ Deleted cookbook and all {count} child text chunks.")
            # 1. Does the cookbook exist at all?
            if count == -1:
                print(f"Cookbook '{cb_id}' not found.")            
            # 2. Book exists but no chunks attached to it
            elif count == 0:
                print(f"✔️ Deleted cookbook '{cb_id}'. There were no child text chunks.")            
            # 3. Standard cascade delete
            else:
                print(f"✔️ Deleted cookbook '{cb_id}' and all {count} child text chunks.")
            
        elif choice == "5":
            print("\nGoodbye!")
            break
        else:
            print("Invalid option number. Please select a number from 1 to 5.")

if __name__ == "__main__":
    run_test_menu()
