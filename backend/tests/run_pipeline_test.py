import os
import sys
import asyncio

# Add app folder to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
# Add backend folder to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.pipeline import run_compilation_pipeline
from app.services.google_workspace import GoogleWorkspaceService

async def main():
    print("========================================")
    print("RUNNING PIPELINE INTEGRATION TEST")
    print("========================================")
    
    sample_text = """
    Naval Ravikant on Leverage and Compounding:
    To build wealth, you must optimize for leverage. Leverage can come from labor, capital, code, or media. 
    Code and media are permissionless leverage. You don't need anyone's permission to write a program or publish a podcast.
    When you build a product, it scales at zero marginal cost of replication. This creates network effects where the system compounds value automatically.
    However, the blindspot is that founders often focus too much on first-order gains (e.g. shipping quick hacks) instead of thinking about second-order consequences (e.g. system instability or technical debt).
    Incentives drive everything. Show me the incentive, and I will show you the outcome. If you align recruiter incentives with long-term hire retention, you get better talent.
    """
    
    user_profile = {
        "career": "Recruiter learning AI",
        "goals": "Understand systems thinking and leverage",
        "interests": "AI, recruiting, organization design"
    }
    
    print("\n[1/3] Invoking multi-agent structured pipeline...")
    result = await run_compilation_pipeline(sample_text, source_url="https://test-source.com/naval", user_profile=user_profile)
    
    print("[OK] Pipeline executed successfully!")
    print(f"Title: {result.get('title')}")
    print(f"Speaker: {result.get('speaker')}")
    print(f"Core Thesis: {result.get('core_thesis')[:80]}...")
    print(f"Insights Count: {len(result.get('insights', []))}")
    print(f"Mental Models: {', '.join([m['name'] for m in result.get('mental_models', [])])}")
    print(f"Vocabulary Words: {', '.join([v['word'] for v in result.get('vocabulary', [])])}")
    
    print("\n[2/3] Initializing Google Workspace Service (Local Fallback)...")
    workspace_service = GoogleWorkspaceService(creds_data=None)
    
    print("\n[3/3] Saving compilation result and updating index...")
    doc_link = await workspace_service.save_compilation(result, category="YouTube")
    
    print("[OK] File saved successfully!")
    print(f"Generated Analysis Path: {doc_link}")
    
    # Check if local files exist (under root antigravity/local_drive/)
    local_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "local_drive"))
    csv_path = os.path.join(local_root, "master_index.csv")
    
    if os.path.exists(csv_path):
        print(f"[OK] Master Index CSV updated at: {csv_path}")
        print("\n========================================")
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("========================================")
    else:
        print(f"[ERROR] CSV index was not updated at: {csv_path}")

if __name__ == "__main__":
    asyncio.run(main())
