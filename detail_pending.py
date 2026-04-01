from database_manager import DatabaseManager
import json

def detail_pending():
    db = DatabaseManager()
    if not db.connect():
        return
    
    try:
        db.cursor.execute("SELECT * FROM sync_queue WHERE status = 'pending'")
        records = db.cursor.fetchall()
        
        if not records:
            print("No pending records found.")
            return

        print(f"Total pending: {len(records)}")
        for rec in records:
            print(f"\n--- ID: {rec['id']} ---")
            print(f"Table: {rec['table_name']}")
            print(f"Action: {rec['action_type']}")
            print(f"Created At: {rec['created_at']}")
            try:
                data = json.loads(rec['data_json'])
                # Summarize data
                if 'invoice_id' in data:
                    print(f"Invoice ID: {data['invoice_id']}")
                elif 'id' in data:
                    print(f"Record ID: {data['id']}")
                
                # If it's a finalizing invoice, show some details
                if rec['table_name'] == 'invoices_finalize':
                    print(f"Details: {data.get('total_amount', 'N/A')} {data.get('currency', '')}")
            except:
                print("Data: [Invalid JSON or too complex]")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    detail_pending()
