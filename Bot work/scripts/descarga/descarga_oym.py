"""
Script para automatizar la descarga de archivos OYM desde Oracle Cloud
Autor: Script generado por Kiro
Fecha: 2026-06-05
"""

import os
import time
from datetime import datetime, timedelta

# Raíz del proyecto (dos niveles arriba de este script)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class OYMDownloader:
    def __init__(self):
        self.url = "https://amx-res-co.fs.ocs.oraclecloud.com/"
        self.email = "38101491@claro.com.co"
        self.password = "Jmmich15()"
        
        # Configuración de carpeta de destino
        self.output_folder = os.path.join(_PROJECT_ROOT, "Oym panel")
        
        # TODO: Definir los nombres exactos de las bases de datos OYM
        self.oym_databases = [
            "OYM 1",  # Cambiar por el nombre real
            "OYM 2"   # Cambiar por el nombre real
        ]
        
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura el driver de Microsoft Edge en modo incógnito"""
        edge_options = Options()
        
        # Activar modo incógnito (InPrivate en Edge)
        edge_options.add_argument("--inprivate")
        
        # Configurar carpeta de descargas
        download_path = os.path.abspath(self.output_folder)
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        edge_options.add_experimental_option("prefs", prefs)
        
        # Inicializar driver de Edge
        self.driver = webdriver.Edge(options=edge_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)
        
        print("✓ Driver configurado correctamente")
        
    def create_folder(self):
        """Crea la carpeta de destino si no existe"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"✓ Carpeta '{self.output_folder}' creada")
        else:
            print(f"✓ Carpeta '{self.output_folder}' ya existe")
            
    def login(self):
        """Realiza el proceso de login: Oracle SSO → Microsoft SSO → Autenticación 2FA"""
        print("\n=== INICIANDO SESIÓN ===")
        self.driver.get(self.url)
        
        try:
            # ========== PASO 1: Login en Oracle con SSO ==========
            print("Paso 1: Login en Oracle Field Service con SSO...")
            time.sleep(5)
            
            # Ingresar solo el correo en Oracle
            try:
                username_input = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Nombre de usuario']"))
                )
                self.driver.execute_script("arguments[0].value = '';", username_input)
                self.driver.execute_script("arguments[0].value = arguments[1];", username_input, self.email)
                time.sleep(1)
                print("  ✓ Correo ingresado")
            except Exception as e:
                print(f"  ✗ Error ingresando correo: {str(e)}")
                raise
            
            # Click en botón "Conectarse con SSO"
            try:
                sso_button = None
                selectors = [
                    "//button[contains(text(), 'Conectarse con SSO')]",
                    "//button[contains(text(), 'SSO')]",
                    "//button[contains(@class, 'sso')]"
                ]
                
                for selector in selectors:
                    try:
                        sso_button = self.driver.find_element(By.XPATH, selector)
                        if sso_button:
                            break
                    except:
                        continue
                
                if not sso_button:
                    raise Exception("No se encontró el botón SSO")
                
                self.driver.execute_script("arguments[0].click();", sso_button)
                time.sleep(3)
                print("  ✓ Botón 'Conectarse con SSO' presionado")
            except Exception as e:
                print(f"  ✗ Error presionando botón SSO: {str(e)}")
                raise
            
            print("✓ Redirigiendo a Microsoft SSO")
            
            # ========== PASO 2: Login en Microsoft ==========
            print("\nPaso 2: Login en Microsoft...")
            time.sleep(5)
            
            # Ingresar email en Microsoft
            try:
                ms_email_input = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@type='email']"))
                )
                self.driver.execute_script("arguments[0].value = '';", ms_email_input)
                self.driver.execute_script("arguments[0].value = arguments[1];", ms_email_input, self.email)
                time.sleep(1)
                print("  ✓ Email de Microsoft ingresado")
            except Exception as e:
                print(f"  ✗ Error ingresando email Microsoft: {str(e)}")
                raise
            
            # Click en "Siguiente"
            try:
                next_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(4)
                print("  ✓ Botón 'Siguiente' presionado")
            except Exception as e:
                print(f"  ✗ Error presionando Siguiente: {str(e)}")
                raise
            
            print("✓ Email de Microsoft enviado")
            
            # Ingresar contraseña en Microsoft
            try:
                ms_password_input = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))
                )
                self.driver.execute_script("arguments[0].value = '';", ms_password_input)
                self.driver.execute_script("arguments[0].value = arguments[1];", ms_password_input, self.password)
                time.sleep(1)
                print("  ✓ Contraseña de Microsoft ingresada")
            except Exception as e:
                print(f"  ✗ Error ingresando contraseña Microsoft: {str(e)}")
                raise
            
            # Click en "Iniciar sesión"
            try:
                signin_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
                self.driver.execute_script("arguments[0].click();", signin_button)
                time.sleep(2)
                print("  ✓ Botón 'Iniciar sesión' presionado")
            except Exception as e:
                print(f"  ✗ Error presionando Iniciar sesión: {str(e)}")
                raise
            
            print("✓ Contraseña de Microsoft enviada")
            
            # ========== PASO 3: Autenticación de dos pasos ==========
            print("\nPaso 3: Autenticación de dos pasos...")
            time.sleep(3)
            
            print("\n" + "="*60)
            print("⚠️  ATENCIÓN: Completa la autenticación numérica de dos pasos")
            print("="*60)
            input("Presiona ENTER cuando estés dentro del sistema (página principal)...")
            
            print("✓ Login completado exitosamente")
            time.sleep(2)
            
        except Exception as e:
            print(f"\n✗ Error en el proceso de login: {str(e)}")
            print("\n⚠️  Completa el resto del login tu mismo")
            input("Presiona ENTER cuando estés dentro del sistema...")
            time.sleep(2)
            
    def navigate_to_database(self, db_name):
        """Navega a una base de datos específica"""
        print(f"\n→ Navegando a: {db_name}")
        
        try:
            # Cerrar cualquier overlay que pueda estar bloqueando
            try:
                overlay = self.driver.find_element(By.CSS_SELECTOR, ".app-menu-overlay")
                if overlay.is_displayed():
                    self.driver.execute_script("arguments[0].click();", overlay)
                    time.sleep(1)
            except:
                pass
            
            time.sleep(2)
            
            # Intentar múltiples selectores para encontrar la base de datos
            db_selectors = [
                f"//span[text()='{db_name}']",
                f"//a[text()='{db_name}']",
                f"//span[contains(text(), '{db_name}')]",
                f"//a[contains(text(), '{db_name}')]",
                f"//*[normalize-space(text())='{db_name}']",
                f"//*[contains(@title, '{db_name}')]"
            ]
            
            db_link = None
            
            for selector in db_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        for elem in elements:
                            if elem.is_displayed():
                                db_link = elem
                                break
                        if db_link:
                            break
                except Exception as e:
                    continue
            
            if not db_link:
                raise Exception(f"No se encontró la base de datos '{db_name}' en el panel izquierdo")
            
            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", db_link)
            time.sleep(1)
            
            # Click con JavaScript
            self.driver.execute_script("arguments[0].click();", db_link)
            time.sleep(3)
            
            print(f"✓ En base de datos: {db_name}")
            
        except Exception as e:
            print(f"✗ Error navegando a {db_name}: {str(e)}")
            raise
            
    def select_date_and_export(self, target_date):
        """Selecciona una fecha específica y exporta el archivo"""
        print(f"  • Exportando fecha: {target_date.strftime('%d/%m/%Y')}")
        
        try:
            # Formatear la fecha
            day = target_date.day
            month_names = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            
            # Abrir el date picker
            try:
                date_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-ofsc-id='toolbar-date-button-value']"))
                )
                self.driver.execute_script("arguments[0].click();", date_button)
                time.sleep(1.5)
            except Exception as e:
                print(f"    ⚠️  No se pudo abrir el calendario: {str(e)}")
            
            # Navegar al mes correcto si es necesario
            current_date = datetime.now()
            months_diff = (target_date.year - current_date.year) * 12 + (target_date.month - current_date.month)
            
            if months_diff != 0:
                for i in range(abs(months_diff)):
                    if months_diff > 0:
                        next_month_selectors = [
                            "//button[@data-ofsc-id='dc__top_panel__date_picker__popup--button-next']",
                            "//button[@aria-label='Siguiente']"
                        ]
                    else:
                        next_month_selectors = [
                            "//button[@data-ofsc-id='dc__top_panel__date_picker__popup--button-prev']",
                            "//button[@aria-label='Anterior']"
                        ]
                    
                    for selector in next_month_selectors:
                        try:
                            month_button = self.driver.find_element(By.XPATH, selector)
                            if month_button.get_attribute('aria-disabled') == 'false':
                                self.driver.execute_script("arguments[0].click();", month_button)
                                time.sleep(1)
                                break
                        except:
                            continue
            
            # Hacer clic en el día específico
            day_selectors = [
                f"//a[@role='checkbox'][contains(@aria-label, '{day}')]",
                f"//a[@role='checkbox'][text()='{day}']",
                f"//a[contains(@class, 'ui-state-default')][text()='{day}']"
            ]
            
            clicked = False
            for selector in day_selectors:
                try:
                    day_element = self.driver.find_element(By.XPATH, selector)
                    self.driver.execute_script("arguments[0].click();", day_element)
                    time.sleep(1)
                    clicked = True
                    print(f"    ✓ Fecha seleccionada: {target_date.strftime('%d/%m/%Y')}")
                    break
                except:
                    continue
            
            if not clicked:
                print(f"    ⚠️  No se pudo seleccionar el día {day}")
                return
            
            time.sleep(1)
            
            # Click en dropdown "Acciones"
            try:
                actions_selectors = [
                    "//button[@aria-label='Acciones']",
                    "//button[@title='Acciones']",
                    "//button[.//span[text()='Acciones']]"
                ]
                
                actions_dropdown = None
                for selector in actions_selectors:
                    try:
                        actions_dropdown = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if actions_dropdown:
                            break
                    except:
                        continue
                
                if not actions_dropdown:
                    raise Exception("No se encontró el botón Acciones")
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", actions_dropdown)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", actions_dropdown)
                time.sleep(1.5)
            except Exception as e:
                print(f"    ⚠️  Error abriendo menú Acciones: {str(e)}")
                raise
            
            # Click en "Exportar"
            try:
                export_selectors = [
                    "//button[@data-bar-id='dc__top_panel__configured_action_action_link__export_queue']",
                    "//button[@aria-label='Exportar']",
                    "//button[@title='Exportar']",
                    "//button[contains(@class, 'toolbar-menu-button')][.//span[text()='Exportar']]"
                ]
                
                export_button = None
                for selector in export_selectors:
                    try:
                        export_button = self.wait.until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if export_button:
                            break
                    except:
                        continue
                
                if not export_button:
                    raise Exception("No se encontró el botón Exportar")
                
                self.driver.execute_script("arguments[0].click();", export_button)
                time.sleep(4)
                print(f"    ✓ Exportado correctamente")
            except Exception as e:
                print(f"    ⚠️  Error haciendo clic en Exportar: {str(e)}")
                raise
            
        except Exception as e:
            print(f"    ✗ Error exportando {target_date.strftime('%d/%m/%Y')}: {str(e)}")
            
    def download_oym_database(self, db_name, dates):
        """Descarga archivos de una base de datos OYM para las fechas especificadas"""
        print(f"\n{'='*60}")
        print(f"DESCARGANDO: {db_name}")
        print(f"Total de fechas: {len(dates)}")
        print(f"{'='*60}")
        
        # Mostrar las fechas
        print("Fechas a descargar:")
        for idx, date in enumerate(dates, 1):
            print(f"  {idx}. {date.strftime('%d/%m/%Y')}")
        print()
        
        # Navegar a la base de datos
        self.navigate_to_database(db_name)
        
        # Descargar cada fecha
        for idx, date in enumerate(dates, 1):
            print(f"[{idx}/{len(dates)}]", end=" ")
            self.select_date_and_export(date)
            time.sleep(2)
            
        print(f"✓ Completado: {db_name}\n")
        
    def get_dates_to_download(self):
        """Define las fechas a descargar (por defecto: día actual)"""
        today = datetime.now()
        
        print(f"\n📅 Fecha actual: {today.strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        # TODO: Ajustar según necesidad
        # Por ahora solo descarga el día actual
        return [today]
        
    def run(self):
        """Ejecuta el proceso completo de descarga de archivos OYM"""
        try:
            print("\n" + "="*60)
            print("DESCARGA DE ARCHIVOS OYM - ORACLE CLOUD")
            print("="*60)
            
            # Preparación
            self.create_folder()
            self.setup_driver()
            
            # Login
            self.login()
            
            # Configurar formato de exportación (MANUAL)
            print("\n" + "="*60)
            print("⚠️  CONFIGURACIÓN DE FORMATO DE EXPORTACIÓN")
            print("="*60)
            print("Por favor, configura manualmente el formato de exportación:")
            print("1. Click en tu icono de usuario (arriba a la derecha)")
            print("2. Click en 'Preferencias'")
            print("3. Selecciona 'Excel 2007 (xlsx)' en formato de exportación")
            print("4. Guarda los cambios")
            input("\nPresiona ENTER cuando hayas configurado el formato...")
            
            # Obtener fechas a descargar
            dates = self.get_dates_to_download()
            
            # Descargar cada base de datos OYM
            for db_name in self.oym_databases:
                try:
                    self.download_oym_database(db_name, dates)
                except Exception as e:
                    print(f"\n⚠️  Error en {db_name}: {str(e)}")
                    print(f"⚠️  Continuando con la siguiente base de datos...")
                    continue
            
            print("\n" + "="*60)
            print("✓ DESCARGA COMPLETADA")
            print(f"✓ Archivos guardados en: {self.output_folder}")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ ERROR GENERAL: {str(e)}")
            
        finally:
            print("\n⚠️  El navegador permanecerá abierto para verificar.")
            print("Presiona ENTER para cerrar el navegador...")
            input()
            
            if self.driver:
                self.driver.quit()
                

if __name__ == "__main__":
    downloader = OYMDownloader()
    downloader.run()
