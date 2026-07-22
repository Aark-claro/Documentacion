from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import json
import time
import os

# Instalar: pip install selenium

# ─────────────────────────────────────────────
#  CONFIGURACIÓN  
# ─────────────────────────────────────────────
EMAIL    = "38101491@claro.com.co"   # ← Correo a usar
PASSWORD = "Septem23()"                # ← pon aquí la contraseña

SHAREPOINT_URL  = "https://claromovilco.sharepoint.com/_layouts/15/sharepoint.aspx"
LOGIN_URL       = "https://login.microsoftonline.com"
COOKIES_FILE    = "cookies.json"
# ─────────────────────────────────────────────


def load_existing_cookies() -> dict:
    """Carga las cookies guardadas anteriormente (si existen)."""
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def extract_auth_cookies(driver) -> dict:
    """Extrae FedAuth y rtFa del navegador actual."""
    cookies = driver.get_cookies()
    result = {}
    for c in cookies:
        if c["name"] in ("FedAuth", "rtFa"):
            result[c["name"]] = c["value"]
    return result


def compare_cookies(old: dict, new: dict):
    """Muestra si las cookies cambiaron respecto a la sesión anterior."""
    print("\n📊 Comparación de cookies (pre vs post login):")
    for name in ("FedAuth", "rtFa"):
        old_val = old.get(name, "")
        new_val = new.get(name, "")
        if not old_val:
            print(f"  • {name}: sin cookie previa  →  {'✅ obtenida' if new_val else '❌ no obtenida'}")
        elif old_val == new_val:
            print(f"  • {name}: ⚠️  sin cambios (misma cookie que antes)")
        else:
            print(f"  • {name}: ✅ actualizada correctamente")


def do_login(driver, wait: WebDriverWait):
    """
    Ejecuta el flujo de login de Microsoft 365.
    Ajusta los selectores si tu tenant usa ADFS u otro IdP.
    """
    print("🔑 Iniciando flujo de login automático...")

    # ── Paso 1: ingresar el email ──────────────────────────────────────────
    try:
        email_field = wait.until(
            EC.presence_of_element_located((By.NAME, "loginfmt"))
        )
        email_field.clear()
        email_field.send_keys(EMAIL)

        next_btn = driver.find_element(By.ID, "idSIButton9")
        next_btn.click()
        print("  → Email enviado")
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  No se encontró el campo de email: {e}")
        print("     Si tu organización usa SSO/ADFS, completa el login manualmente.")
        return False

    # ── Paso 2: ingresar la contraseña ────────────────────────────────────
    try:
        # Algunos tenants redirigen a ADFS; espera el campo de password
        password_field = wait.until(
            EC.presence_of_element_located((By.NAME, "passwd"))
        )
        password_field.clear()
        password_field.send_keys(PASSWORD)

        sign_in_btn = driver.find_element(By.ID, "idSIButton9")
        sign_in_btn.click()
        print("  → Contraseña enviada")
        time.sleep(3)
    except Exception as e:
        print(f"  ⚠️  No se encontró el campo de contraseña: {e}")
        print("     Completa el paso de contraseña manualmente.")

    # ── Paso 3: "¿Mantener sesión iniciada?" ──────────────────────────────
    try:
        stay_signed = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        stay_signed.click()
        print("  → 'Mantener sesión' aceptado")
        time.sleep(2)
    except Exception:
        pass  # El diálogo no siempre aparece

    return True


def get_sharepoint_cookies():
    """Flujo principal: login → cookies antes → cookies después → comparación."""

    # ── Cookies previas (pre-login) ────────────────────────────────────────
    pre_cookies = load_existing_cookies()
    if pre_cookies:
        print(f"📂 Cookies previas cargadas desde '{COOKIES_FILE}'")
    else:
        print("📂 No hay cookies previas guardadas")

    # ── Configurar Edge en modo limpio (sin perfil guardado) ───────────────
    print("\n🌐 Abriendo navegador (perfil limpio para forzar login)...")
    options = Options()
    options.add_argument("--inprivate")          # ventana InPrivate = sin sesión cacheada
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")

    driver = webdriver.Edge(options=options)
    wait   = WebDriverWait(driver, 120)

    try:
        # ── Navegar a SharePoint (redirige a login de Microsoft) ───────────
        print(f"📍 Navegando a: {SHAREPOINT_URL}")
        driver.get(SHAREPOINT_URL)
        time.sleep(3)

        current_url = driver.current_url
        print(f"🔗 URL actual: {current_url}")

        # ── Intentar login automático si estamos en Microsoft login ────────
        if "login.microsoftonline.com" in current_url or "login.microsoft.com" in current_url:
            auto_ok = do_login(driver, wait)
            if not auto_ok:
                print("\n👤 Completa el login manualmente en la ventana del navegador...")
        else:
            print("⚠️  No se detectó la página de login de Microsoft.")
            print("    Si SharePoint se abrió directamente con otra cuenta,")
            print("    cierra sesión en el navegador manualmente y vuelve a ejecutar.")

        # ── Esperar a que SharePoint cargue completamente ──────────────────
        print("\n⏳ Esperando que SharePoint cargue (máx. 2 minutos)...")
        try:
            wait.until(EC.url_contains("sharepoint.com"))
            print("✅ SharePoint cargado")
        except Exception:
            print("⚠️  Tiempo agotado esperando SharePoint; intentando capturar cookies de todas formas...")

        time.sleep(3)  # pausa extra para cookies de sesión

        # ── Extraer cookies post-login ─────────────────────────────────────
        post_cookies = extract_auth_cookies(driver)

        # ── Comparar pre vs post ───────────────────────────────────────────
        compare_cookies(pre_cookies, post_cookies)

        # ── Guardar si son válidas ─────────────────────────────────────────
        if post_cookies.get("FedAuth") and post_cookies.get("rtFa"):
            with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                json.dump(post_cookies, f, indent=2)
            print(f"\n✅ Cookies guardadas en '{COOKIES_FILE}'")
            print(f"   FedAuth : {post_cookies['FedAuth'][:60]}...")
            print(f"   rtFa    : {post_cookies['rtFa'][:60]}...")
            return True
        else:
            print("\n❌ No se obtuvieron FedAuth/rtFa.")
            if not post_cookies.get("FedAuth"):
                print("   - FedAuth no encontrada")
            if not post_cookies.get("rtFa"):
                print("   - rtFa no encontrada")
            return False

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False
    finally:
        driver.quit()
        print("\n🔒 Navegador cerrado")


if __name__ == "__main__":
    get_sharepoint_cookies()