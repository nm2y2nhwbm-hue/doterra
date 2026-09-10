# -*- coding: utf-8 -*-
"""
Agent 3 專用：全站自動化測試統一調度器 (tests/run_all_tests.py)
一鍵調度 Python 與 Node.js 雙環境全量測試套件，涵蓋 L1~L6 六大深度檢驗階層。
"""
import os
import subprocess
import sys
import time

# 確保在 Windows 控制台下支援 UTF-8 編碼
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')

PYTHON_SUITES = [
    ('test_api_endpoints.py', 'L3 後端 API 與防偽邊界', 'Agent 1'),
    ('test_experience_handoff.py', 'L3 短效 Token 防刷加密', 'Agent 1'),
    ('test_catalog_integrity.py', 'L2 資料庫與建議零售價', 'Agent 4'),
    ('test_catalog_sync.py', 'L2 目錄同步與冪等校驗', 'Agent 4'),
    ('test_asset_integrity.py', 'L4 日式美學與資產零破圖', 'Agent 2'),
    ('test_live_endpoints.py', 'L5 正式環境活體韌性探測', 'Agent 5 / 營運'),
]

# 若本機工作區已建置金流與資安測試則一併納入
if os.path.isfile(os.path.join(TESTS_DIR, 'test_payment_api.py')):
    PYTHON_SUITES.insert(1, ('test_payment_api.py', 'L3 第三方金流與防偽驗簽', 'Agent 5 / Agent 1'))

if os.path.isfile(os.path.join(TESTS_DIR, 'test_security_audit.py')):
    PYTHON_SUITES.append(('test_security_audit.py', 'L3 資安漏洞與自然醫學法規', 'Agent 3 照妖鏡'))


NODE_SUITES = [
    ('test_js_syntax.js', 'L1 全站 JS AST 語法編譯', 'Agent 2 / Agent 3'),
    ('test_cart_logic.js', 'L4 購物車核心狀態單元測試', 'Agent 2'),
    ('test_cart_integration.js', 'L4 預約結帳資料合約整合', 'Agent 2'),
    ('test_supabase_client.js', 'L3 前端 RPC 客戶端安全', 'Agent 1 / Agent 2'),
]


def find_node_executable():
    """尋找可用的 Node.js 執行檔（支援標準 PATH 與 Playwright 內建驅動）"""
    # 優先測試系統 PATH
    try:
        res = subprocess.run(['node', '-v'], capture_output=True, text=True, check=False)
        if res.returncode == 0:
            return 'node'
    except FileNotFoundError:
        pass

    # 檢測候選路徑：優先檢測當前 Python 虛擬環境（支援 nodeenv 整合，如 SD_forge_Venv）
    candidates = [
        os.path.join(sys.prefix, 'Scripts', 'node.exe'),
        os.path.join(sys.prefix, 'bin', 'node'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python312', 'Lib', 'site-packages', 'playwright', 'driver', 'node.exe'),
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'playwright', 'driver', 'node.exe'),
        r'C:\Program Files\nodejs\node.exe'
    ]

    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def run_suite(cmd, label):
    """執行單一測試套件並記錄耗時"""
    start_time = time.time()
    proc = subprocess.run(
        cmd,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    elapsed = time.time() - start_time
    passed = (proc.returncode == 0)
    return passed, elapsed, proc.stdout, proc.stderr


def main():
    print("=" * 80)
    print("🧪 [Agent 3] 啟動全站深度自動化測試矩陣 (Testing Depth 2.0)")
    print("=" * 80)

    total_start = time.time()
    results = []
    overall_passed = True

    # 1. 執行 Python 測試套件
    print("\n🐍 [Phase 1/2] 執行 Python 測試套件 (unittest)...")
    for file_name, tier_desc, agent_tag in PYTHON_SUITES:
        cmd = [sys.executable, '-m', 'unittest', f'tests/{file_name}']
        passed, elapsed, stdout, stderr = run_suite(cmd, file_name)
        status_icon = "🟢 PASS" if passed else "🔴 FAIL"
        if not passed:
            overall_passed = False
        results.append((file_name, tier_desc, agent_tag, status_icon, f"{elapsed:.2f}s"))
        print(f"  {status_icon} | {file_name:<26} | {tier_desc:<20} | {agent_tag} ({elapsed:.2f}s)")
        if not passed:
            print(f"     [Error Output]:\n{stderr or stdout}\n")

    # 2. 執行 Node.js 測試套件
    print("\n⬢ [Phase 2/2] 執行 Node.js 前端元件與語法套件...")
    node_bin = find_node_executable()
    if not node_bin:
        print("  ⚠️ 未檢測到 Node.js 執行檔，跳過 Node 測試階段！")
        overall_passed = False
    else:
        for file_name, tier_desc, agent_tag in NODE_SUITES:
            test_path = os.path.join('tests', file_name)
            cmd = [node_bin, test_path]
            passed, elapsed, stdout, stderr = run_suite(cmd, file_name)
            status_icon = "🟢 PASS" if passed else "🔴 FAIL"
            if not passed:
                overall_passed = False
            results.append((file_name, tier_desc, agent_tag, status_icon, f"{elapsed:.2f}s"))
            print(f"  {status_icon} | {file_name:<26} | {tier_desc:<20} | {agent_tag} ({elapsed:.2f}s)")
            if not passed:
                print(f"     [Error Output]:\n{stderr or stdout}\n")

    # 3. 輸出彙總報表
    total_elapsed = time.time() - total_start
    print("\n" + "=" * 80)
    print(f"📊 [Agent 3] 全矩陣檢驗報表 (總耗時: {total_elapsed:.2f}s)")
    print("=" * 80)
    print(f"{'狀態':<8} {'測試模組檔案':<28} {'涵蓋層級與檢驗項目':<26} {'邊界歸屬':<16} {'耗時'}")
    print("-" * 80)
    for fn, desc, tag, status, dur in results:
        print(f"{status:<8} {fn:<28} {desc:<26} {tag:<16} {dur}")
    print("=" * 80)

    if overall_passed:
        print(f"🏆 驗收結論：全數 {len(results)} 項深度測試套件 100% 綠燈通過！系統品質卓越穩定。")
        sys.exit(0)
    else:
        print("❌ 驗收結論：部分測試未通過，請檢查上述錯誤日誌。")
        sys.exit(1)


if __name__ == '__main__':
    main()
