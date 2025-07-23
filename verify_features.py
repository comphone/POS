import os
import ast

# --- Configuration: Define what we expect to find ---

EXPECTED_BLUEPRINTS = {
    'auth', 'core', 'customer', 'inventory', 'service', 'pos', 'accounting', 'linebot', 'ai_tools'
}

EXPECTED_MODELS = {
    'User', 'Customer', 'Product', 'ServiceJob', 'Task', 'Sale', 'SaleItem',
    'JobUpdate', 'ServiceJobPart', 'SystemSettings'
}

# Check for specific routes (endpoint functions) within each blueprint's routes.py
EXPECTED_ROUTES = {
    'auth': {'login', 'logout'},
    'customer': {'list_customers', 'add_customer', 'edit_customer'},
    'inventory': {'list_products', 'add_product', 'edit_product', 'search_products'},
    'service': {
        'list_jobs', 'add_job', 'job_detail', 'edit_job', 
        'toggle_task', 'delete_task', 'delete_part',
        'generate_customer_onboarding_qr'
    },
    'pos': {'index'},
    'accounting': {'sale_history', 'receipt_pdf'},
    'linebot': {'callback'},
    'ai_tools': {'get_job_history'}
}

# --- Verification Functions ---

def get_defined_functions(filepath):
    """Parses a Python file and returns the names of defined functions."""
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
            return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        except Exception as e:
            print(f"    [Warning] Could not parse {filepath}: {e}")
            return set()

def get_defined_classes(filepath):
    """Parses a Python file and returns the names of defined classes."""
    if not os.path.exists(filepath):
        return set()
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
            return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        except Exception as e:
            print(f"    [Warning] Could not parse {filepath}: {e}")
            return set()

def check_feature(title, condition, success_msg="ครบถ้วน", failure_msg="ไม่ครบถ้วน"):
    """Prints a formatted check result."""
    status_icon = "✅" if condition else "❌"
    status_text = success_msg if condition else failure_msg
    print(f"{status_icon} {title:<35} | สถานะ: {status_text}")
    if not condition:
        global all_checks_passed
        all_checks_passed = False

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

# --- Main Verification Logic ---

all_checks_passed = True

def run_verification():
    """Runs all checks and prints the report."""
    
    print_header("เริ่มต้นการตรวจสอบโปรเจกต์ Comphone Integrated System")

    # 1. Check Project Structure
    print_header("1. ตรวจสอบสถาปัตยกรรมและโครงสร้างไฟล์")
    base_path = 'app/blueprints'
    found_blueprints = {d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and not d.startswith('__')}
    check_feature("โครงสร้าง Blueprints", EXPECTED_BLUEPRINTS.issubset(found_blueprints),
                  success_msg=f"พบ {len(found_blueprints)}/{len(EXPECTED_BLUEPRINTS)} Blueprints",
                  failure_msg=f"พบ {len(found_blueprints)}/{len(EXPECTED_BLUEPRINTS)}. ขาด: {EXPECTED_BLUEPRINTS - found_blueprints}")
    
    check_feature("ไฟล์ app/__init__.py (Application Factory)", os.path.exists('app/__init__.py'))
    check_feature("ไฟล์ app/models.py", os.path.exists('app/models.py'))
    check_feature("ไฟล์ scripts/migrate_from_google_tasks.py", os.path.exists('scripts/migrate_from_google_tasks.py'))

    # 2. Check Database Models
    print_header("2. ตรวจสอบฐานข้อมูล (Database Models)")
    models_path = 'app/models.py'
    found_models = get_defined_classes(models_path)
    check_feature("Models หลักในระบบ", EXPECTED_MODELS.issubset(found_models),
                  success_msg=f"พบ {len(found_models)} Models ที่ต้องการ",
                  failure_msg=f"ขาด: {EXPECTED_MODELS - found_models}")

    # 3. Check Core Features (Routes)
    print_header("3. ตรวจสอบฟีเจอร์หลัก (Core Features via Routes)")
    for bp_name, expected_funcs in EXPECTED_ROUTES.items():
        routes_path = os.path.join(base_path, bp_name, 'routes.py')
        found_funcs = get_defined_functions(routes_path)
        check_feature(f"ฟีเจอร์ใน '{bp_name}' blueprint", expected_funcs.issubset(found_funcs),
                      success_msg=f"พบ {len(expected_funcs)}/{len(expected_funcs)} ฟังก์ชัน",
                      failure_msg=f"ขาด: {expected_funcs - found_funcs}")

    # Final Summary
    print_header("สรุปผลการตรวจสอบ")
    if all_checks_passed:
        print("🎉 ยอดเยี่ยม! โครงสร้างของโปรเจกต์มีความสมบูรณ์ครบถ้วนตามที่ออกแบบไว้ทั้งหมด")
        print("ขั้นตอนต่อไปที่แนะนำคือการทดสอบการทำงานจริงตาม 'แผนการทดสอบระบบ (UAT Checklist)'")
    else:
        print("⚠️ พบว่าโครงสร้างบางส่วนยังไม่ครบถ้วน กรุณาตรวจสอบรายการที่มีเครื่องหมาย ❌ ด้านบน")


if __name__ == "__main__":
    run_verification()
