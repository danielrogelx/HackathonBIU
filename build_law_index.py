"""
One-time script to build the RAG index from IsraelyLaw.txt.
Run this ONCE before starting the app:

    source venv/bin/activate
    python build_law_index.py

The index is saved to .rag_cache/ and reused across all sessions.
First run downloads the multilingual embedding model (~100MB) and
processes the law file — takes about 2-5 minutes.
"""

import time
from core.rag.law_rag import build_index, is_index_built, LAW_FILE

print("מתמחה בבית המשפט — בונה אינדקס חוקים ישראליים")
print("=" * 50)

if is_index_built():
    print("האינדקס כבר קיים. משתמש בגרסה הקיימת.")
    print("להרצה מחדש כפויה: python build_law_index.py --force")
    import sys
    if "--force" not in sys.argv:
        exit(0)

print(f"קורא את: {LAW_FILE}")
print("בונה אינדקס... (עשוי לקחת 2-5 דקות בהרצה ראשונה)")

start = time.time()
n_chunks = build_index(force_rebuild="--force" in __import__("sys").argv)
elapsed = time.time() - start

print(f"\n✅ האינדקס נבנה בהצלחה!")
print(f"   קטעים שנוספו: {n_chunks}")
print(f"   זמן: {elapsed:.1f} שניות")
print(f"   שמור ב: .rag_cache/")
print("\nהאפליקציה מוכנה להרצה: streamlit run app.py")
