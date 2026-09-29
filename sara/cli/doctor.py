import sys
import os

class SaraDoctor:
    @staticmethod
    def run_diagnostics():
        print("SARA System Diagnostic")
        print("----------------------")
        
        # 1. Environment variables
        print("[1] Environment Variables:")
        keys = ['TELEGRAM_TOKEN', 'GITHUB_TOKEN']
        for k in keys:
            val = os.environ.get(k)
            if val:
                print(f"  ✅ {k} is set (length: {len(val)})")
            else:
                print(f"  ❌ {k} is missing")

        # 2. Database connectivity
        print("\n[2] Database Connectivity:")
        db_path = os.environ.get('SARA_DB_PATH', 'queue.db')
        if os.path.exists(db_path):
            print(f"  ✅ Database exists at {db_path}")
        else:
            print(f"  ❌ Database missing at {db_path}. Run migrations.")
            
        print("\nDiagnostic complete.")
