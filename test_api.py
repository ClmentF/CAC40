#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement de l'API
"""

import requests
import time
from colorama import init, Fore, Style

init(autoreset=True)

API_URL = "http://localhost:8000"

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

def test_endpoint(name, endpoint, expected_keys=None):
    """Teste un endpoint de l'API"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if expected_keys:
            for key in expected_keys:
                if key not in str(data):
                    print_error(f"{name}: clé '{key}' manquante")
                    return False
        
        print_success(f"{name}: OK")
        return True
    except requests.exceptions.ConnectionError:
        print_error(f"{name}: Impossible de se connecter à l'API")
        return False
    except requests.exceptions.Timeout:
        print_error(f"{name}: Timeout")
        return False
    except Exception as e:
        print_error(f"{name}: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("🧪 TEST DE L'API CAC 40")
    print("="*60 + "\n")
    
    tests = [
        ("Root endpoint", "/", ["message", "version"]),
        ("Health check", "/health", ["status", "companies"]),
        ("Companies list", "/companies", ["ticker", "name"]),
        ("Sectors list", "/sectors", ["sectors"]),
        ("Stock prices (LVMH)", "/prices/MC.PA?limit=10", ["ticker", "date"]),
        ("Latest price (Total)", "/latest/FP.PA", ["ticker", "close"]),
        ("Statistics (Airbus)", "/statistics/AIR.PA?days=30", ["ticker", "avg_close"]),
        ("Top performers", "/top-performers?days=30&limit=5", ["top_performers"]),
    ]
    
    results = []
    for test in tests:
        result = test_endpoint(*test)
        results.append(result)
        time.sleep(0.2)  # Petite pause entre les tests
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print_success(f"TOUS LES TESTS RÉUSSIS ({passed}/{total})")
    else:
        print_error(f"CERTAINS TESTS ONT ÉCHOUÉ ({passed}/{total})")
    
    print("="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
