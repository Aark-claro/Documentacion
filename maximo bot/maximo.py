import os
import time
import logging
import win32com.client as win32
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# =========================
# CONFIGURACIÓN
# =========================

URL_LOGIN = "https://controldesk.claro.net.co/maximo/webclient/login/login.jsp"
USUARIO = "38101584"
PASSWORD = "Saludo29,,"

TIPOS_TRABAJO = (
    "=CCOAX,=CFIBRA"
)

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descargas")
# =========================
# CORREO
# =========================
DESTINATARIOS = (
    "diana.aristizabalg@claro.com.co;"
    "juan.perez@grupoconectar.co;"
    "ana.mojana@grupoconectar.co;"
    "t.ibarra@ccicsa.com.mx;"
    "yenci.campo@grupoconectar.co;"
    "leidy.ruiz@grupoconectar.co;"
    "l.solano@tabascooc.com;"
    "laura.ospina@grupoconectar.co;"
    "j.aparicio1@tabascooc.com;"
    "jose.camargo@claro.com.co;"
    "luz.sanchez@claro.com.co;"
    "k.paez@tabascooc.com;"
    "e.rengifos@tabascooc.com;"
    "a.gomezre@tabascooc.com"
)
ASUNTO = "Archivo Máximo actualizado"
CUERPO = "Buen Día,\n\nSe adjunta archivo Máximo actualizado.\n\nCordialmente."

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# FUNCIONES
# =========================
def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    prefs = {"download.default_directory": DOWNLOAD_DIR}
    chrome_options.add_experimental_option("prefs", prefs)

    service = ChromeService()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def login_maximo(driver):
    driver.get(URL_LOGIN)
    logging.info("🌐 Página de login abierta")

    user_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='j_username']"))
    )
    user_input.clear()
    user_input.send_keys(USUARIO)
    time.sleep(3)

    pass_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//input[@id='j_password']"))
    )
    pass_input.clear()
    pass_input.send_keys(PASSWORD)
    time.sleep(2)

    pass_input.send_keys(Keys.RETURN)
    logging.info("🔑 Login enviado")

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='titlebar_hyperlink_8-lbsignout']"))
        )
        logging.info("✅ Login exitoso")
    except:
        pass


def ir_a_seguimiento_ot(driver):
    try:
        xpath_seguimiento = "//a[@id='FavoriteApp_WOTRACK']"
        boton_seguimiento = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, xpath_seguimiento))
        )
        boton_seguimiento.click()
        logging.info("➡️ Seguimiento OT abierto")
        time.sleep(3)
    except Exception as e:
        logging.error(f"❌ Error Seguimiento OT: {e}")


def llenar_campos_filtros(driver):
    try:
        xpath_regional = "//input[@id='m6a7dfd2f_tfrow_[C:6]_txt-tb']"
        elemento_regional = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath_regional))
        )
        elemento_regional.clear()
        elemento_regional.send_keys("=OCCIDENTE")
        time.sleep(2)

        xpath_tipo_trabajo = "//input[@id='m6a7dfd2f_tfrow_[C:11]_txt-tb']"
        elemento_tipo_trabajo = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath_tipo_trabajo))
        )
        elemento_tipo_trabajo.clear()
        elemento_tipo_trabajo.send_keys(TIPOS_TRABAJO)
        time.sleep(2)

        elemento_tipo_trabajo.send_keys(Keys.RETURN)
        logging.info("🔎 Búsqueda lanzada")
        time.sleep(3)

    except Exception as e:
        logging.error(f"❌ Error filtros: {e}")


def descargar_excel(driver):
    try:
        WebDriverWait(driver, 60).until_not(
            EC.presence_of_element_located((By.XPATH, "//div[@id='wait' and contains(@style, 'display: block')]"))
        )

        xpath_descarga = "//img[@id='m6a7dfd2f-lb4_image' and contains(@src,'tablebtn_download.gif')]"
        boton_descarga = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, xpath_descarga))
        )

        boton_descarga.click()
        logging.info("⬇️ Descargando archivo")

        # 🔥 NO se modifica tu espera
        time.sleep(120)

    except Exception as e:
        logging.error(f"❌ Error descarga: {e}")


def renombrar_archivo_maximo():
    try:
        archivos = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)]
        archivos = [f for f in archivos if os.path.isfile(f)]

        ultimo_archivo = max(archivos, key=os.path.getctime)
        ruta_final = os.path.join(DOWNLOAD_DIR, "maximo.xlsx")

        if os.path.exists(ruta_final):
            os.remove(ruta_final)

        os.rename(ultimo_archivo, ruta_final)
        logging.info("📁 Archivo renombrado a maximo.xlsx")

        return ruta_final

    except Exception as e:
        logging.error(f"❌ Error renombrando: {e}")
        return None


def enviar_correo(ruta_archivo):
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)

        mail.To = DESTINATARIOS
        mail.Subject = ASUNTO
        mail.Body = CUERPO

        if ruta_archivo and os.path.exists(ruta_archivo):
            mail.Attachments.Add(ruta_archivo)

        mail.Send()
        logging.info("📧 Correo enviado")

    except Exception as e:
        logging.error(f"❌ Error correo: {e}")


# =========================
# MAIN
# =========================
def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    driver = iniciar_driver()
    try:
        login_maximo(driver)
        ir_a_seguimiento_ot(driver)
        llenar_campos_filtros(driver)
        descargar_excel(driver)

        ruta = renombrar_archivo_maximo()
        enviar_correo(ruta)

        logging.info("🎯 Proceso completado")
        time.sleep(5)

    finally:
        driver.quit()


if __name__ == "__main__":
    INTERVALO_MINUTOS = 10
    while True:
        logging.info("🚀 Iniciando ejecución...")
        main()
        logging.info(f"⏳ Esperando {INTERVALO_MINUTOS} minutos para la próxima ejecución...")
        time.sleep(INTERVALO_MINUTOS * 60)