"""
Script para automatizar la descarga de bases de datos desde Oracle Cloud
Autor: Script generado por Kiro
Fecha: 2026-06-04
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

class OracleCloudDownloader:
    def __init__(self):
        self.url = "https://amx-res-co.fs.ocs.oraclecloud.com/"
        self.email = "38101491@claro.com.co"
        self.password = "Jmmich15()"
        
        # Configuración de carpetas
        self.base_folder = os.path.join(_PROJECT_ROOT, "BDS_work")
        self.folders = {
            "RECURSOS OCCIDENTE (INTEGRAL) SEG FIJA": "Recursos_Occidente",
            "PYMES OCCIDENTE": "Pymes_Occidente",
            "REGION OCCIDENTE": "Region_Occidente",
            "DTH OCCIDENTE (O)": "DTH_Occidente"
        }
        
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura el driver de Microsoft Edge en modo incógnito"""
        edge_options = Options()
        
        # Activar modo incógnito (InPrivate en Edge)
        edge_options.add_argument("--inprivate")
        
        # Configurar carpeta de descargas
        download_path = os.path.abspath(self.base_folder)
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
        
    def create_folders(self):
        """Crea la estructura de carpetas necesaria"""
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
            
        for folder_name in self.folders.values():
            folder_path = os.path.join(self.base_folder, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                
        print("✓ Carpetas creadas correctamente")
        
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
                # Intentar múltiples selectores para el botón SSO
                sso_button = None
                selectors = [
                    "//button[contains(text(), 'Conectarse con SSO')]",
                    "//button[contains(text(), 'SSO')]",
                    "//button[contains(@class, 'sso')]",
                    "//*[contains(text(), 'Conectarse con SSO')]",
                    "//button[contains(., 'SSO')]"
                ]
                
                for selector in selectors:
                    try:
                        sso_button = self.driver.find_element(By.XPATH, selector)
                        if sso_button:
                            break
                    except:
                        continue
                
                if not sso_button:
                    # Buscar todos los botones y listar
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    print(f"  ⚠️ Botones encontrados en la página:")
                    for btn in all_buttons:
                        print(f"    - Texto: '{btn.text}' | Clase: '{btn.get_attribute('class')}'")
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
            
    def configure_export_format(self):
        """Configura el formato de exportación a Excel 2007"""
        print("\n=== CONFIGURANDO FORMATO DE EXPORTACIÓN ===")
        
        try:
            # Click en icono de usuario (arriba a la derecha)
            user_icon = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='CD'], a[title='CD'], .user-icon, [class*='user']"))
            )
            user_icon.click()
            time.sleep(1)
            
            # Click en Preferencias
            preferences_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Preferencias')] | //button[contains(text(), 'Preferencias')]"))
            )
            preferences_link.click()
            time.sleep(2)
            
            # Buscar y seleccionar el formato de exportación
            export_format_select = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//select[contains(@id, 'export') or contains(@name, 'export')] | //label[contains(text(), 'Formato de exportación')]/following-sibling::select"))
            )
            
            # Seleccionar Excel 2007 (xlsx)
            from selenium.webdriver.support.ui import Select
            select = Select(export_format_select)
            select.select_by_visible_text("Excel 2007 (xlsx)")
            time.sleep(1)
            
            # Guardar cambios
            save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Guardar')] | //button[contains(text(), 'Aceptar')] | //input[@type='submit']")
            save_button.click()
            time.sleep(2)
            
            print("✓ Formato de exportación configurado a Excel 2007 (xlsx)")
            
        except Exception as e:
            print(f"✗ Error configurando formato: {str(e)}")
            print("⚠️  Intenta configurarlo manualmente y presiona ENTER para continuar")
            input()
            
    def navigate_to_database(self, db_name):
        """Navega a una base de datos específica"""
        print(f"\n→ Navegando a: {db_name}")
        
        try:
            # Cerrar cualquier overlay que pueda estar bloqueando
            try:
                overlay = self.driver.find_element(By.CSS_SELECTOR, ".app-menu-overlay")
                if overlay.is_displayed():
                    # Click en el overlay para cerrarlo
                    self.driver.execute_script("arguments[0].click();", overlay)
                    time.sleep(1)
            except:
                pass
            
            # Esperar un momento para asegurar que la página está lista
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
            successful_selector = None
            
            for selector in db_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        # Si hay múltiples elementos, buscar el visible
                        for elem in elements:
                            if elem.is_displayed():
                                db_link = elem
                                successful_selector = selector
                                break
                        if db_link:
                            break
                except Exception as e:
                    continue
            
            if not db_link:
                print(f"    ✗ No se encontró '{db_name}' con ningún selector")
                print(f"    ℹ️  Buscando elementos similares en el panel...")
                
                # Intentar encontrar todos los elementos del menú para debug
                try:
                    all_menu_items = self.driver.find_elements(By.XPATH, "//span[contains(@class, 'tree-item-text')] | //a[contains(@class, 'menu-item')]")
                    print(f"    ℹ️  Elementos encontrados en el menú lateral:")
                    for item in all_menu_items[:20]:  # Mostrar solo los primeros 20
                        try:
                            if item.is_displayed():
                                text = item.text.strip()
                                if text and "OCCIDENTE" in text:
                                    print(f"        - '{text}'")
                        except:
                            pass
                except:
                    pass
                
                raise Exception(f"No se encontró la base de datos '{db_name}' en el panel izquierdo")
            
            print(f"    ℹ️  Elemento encontrado con selector: {successful_selector}")
            
            # Scroll al elemento
            self.driver.execute_script("arguments[0].scrollIntoView(true);", db_link)
            time.sleep(1)
            
            # Click con JavaScript para evitar problemas de overlay
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
            # Formatear la fecha para buscarla en el calendario
            day = target_date.day
            month_names = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            target_month = month_names[target_date.month]
            target_year = target_date.year
            
            # Abrir el date picker haciendo clic en el botón de fecha
            try:
                date_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-ofsc-id='toolbar-date-button-value']"))
                )
                self.driver.execute_script("arguments[0].click();", date_button)
                time.sleep(1.5)
            except Exception as e:
                print(f"    ⚠️  No se pudo abrir el calendario: {str(e)}")
            
            # Navegar al mes correcto usando las flechas del calendario si es necesario
            current_date = datetime.now()
            months_diff = (target_date.year - current_date.year) * 12 + (target_date.month - current_date.month)
            
            if months_diff != 0:
                # Navegar entre meses
                for i in range(abs(months_diff)):
                    if months_diff > 0:
                        # Mes siguiente
                        next_month_selectors = [
                            "//button[@data-ofsc-id='dc__top_panel__date_picker__popup--button-next']",
                            "//button[@aria-label='Siguiente']"
                        ]
                    else:
                        # Mes anterior
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
            
            # Hacer clic en el día específico del calendario
            # El HTML muestra: <a role="checkbox" aria-label="4 Junio Jueves" ... href="#">4</a>
            day_selectors = [
                f"//a[@role='checkbox'][contains(@aria-label, '{day} {target_month}')]",
                f"//a[@role='checkbox'][text()='{day}']",
                f"//a[contains(@class, 'ui-state-default')][text()='{day}']"
            ]
            
            clicked = False
            for selector in day_selectors:
                try:
                    # Buscar el día en el calendario visible
                    day_element = self.driver.find_element(By.XPATH, selector)
                    self.driver.execute_script("arguments[0].click();", day_element)
                    time.sleep(1)
                    clicked = True
                    print(f"    ✓ Fecha seleccionada en calendario: {target_date.strftime('%d/%m/%Y')}")
                    break
                except:
                    continue
            
            if not clicked:
                print(f"    ⚠️  No se pudo hacer clic en el día {day} del calendario")
                return
            
            time.sleep(1)
            
            # Click en dropdown "Acciones"
            try:
                # Esperar y hacer clic en el botón Acciones usando selectores específicos de Oracle
                actions_selectors = [
                    "//button[@aria-label='Acciones']",
                    "//button[@title='Acciones']",
                    "//button[.//span[text()='Acciones']]",
                    "//controls:app-menu-button//button[contains(@class, 'app-button')]",
                    "//button[@class='app-button app-button--borderless app-button--sm app-button--transparent active']"
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
                
                # Scroll al elemento si es necesario
                self.driver.execute_script("arguments[0].scrollIntoView(true);", actions_dropdown)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", actions_dropdown)
                time.sleep(1.5)
            except Exception as e:
                print(f"    ⚠️  Error abriendo menú Acciones: {str(e)}")
                raise
            
            # Click en "Exportar" dentro del dropdown
            try:
                # Usar selectores específicos para el botón de exportar
                export_selectors = [
                    "//button[@data-bar-id='dc__top_panel__configured_action_action_link__export_queue']",
                    "//button[@aria-label='Exportar']",
                    "//button[@title='Exportar']",
                    "//button[@class='toolbar-menu-button menu-item'][.//span[text()='Exportar']]",
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
            except Exception as e:
                print(f"    ⚠️  Error haciendo clic en Exportar: {str(e)}")
                raise
            
            print(f"    ✓ Exportado: {target_date.strftime('%d/%m/%Y')}")
            
        except Exception as e:
            print(f"    ✗ Error exportando {target_date.strftime('%d/%m/%Y')}: {str(e)}")
            
    def download_database(self, db_name, dates):
        """Descarga todos los archivos de una base de datos para las fechas especificadas"""
        print(f"\n{'='*60}")
        print(f"DESCARGANDO: {db_name}")
        print(f"Total de fechas: {len(dates)}")
        print(f"{'='*60}")
        
        # Mostrar las fechas que se van a descargar
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
            time.sleep(2)  # Pausa entre descargas
            
        print(f"✓ Completado: {db_name}\n")
        
    def get_date_ranges(self):
        """Define los rangos de fechas para cada base de datos"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        print(f"\n📅 Fecha actual del sistema: {today.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📅 Fecha de ayer: {yesterday.strftime('%d/%m/%Y')}\n")
        
        date_ranges = {
            # Recursos Occidente: día anterior y día actual
            "RECURSOS OCCIDENTE (INTEGRAL) SEG FIJA": [
                yesterday,
                today
            ],
            
            # Pymes: día actual y próximos 20 días
            "PYMES OCCIDENTE": [
                today + timedelta(days=i) for i in range(21)
            ],
            
            # Regional Occidente: día actual y próximos 20 días
            "REGION OCCIDENTE": [
                today + timedelta(days=i) for i in range(21)
            ],
            
            # DTH: día actual hasta dentro de 2 meses (60 días)
            "DTH OCCIDENTE (O)": [
                today + timedelta(days=i) for i in range(61)
            ]
        }
        
        return date_ranges
        
    def move_downloaded_files(self, db_name):
        """Mueve los archivos descargados a la carpeta correspondiente"""
        try:
            source_folder = self.base_folder
            target_folder = os.path.join(self.base_folder, self.folders[db_name])
            
            # Esperar a que los archivos terminen de descargarse
            time.sleep(5)
            
            # Mover archivos xlsx recientes
            for filename in os.listdir(source_folder):
                if filename.endswith('.xlsx'):
                    source_path = os.path.join(source_folder, filename)
                    target_path = os.path.join(target_folder, filename)
                    
                    if os.path.isfile(source_path):
                        os.rename(source_path, target_path)
                        
            print(f"✓ Archivos movidos a: {self.folders[db_name]}")
            
        except Exception as e:
            print(f"⚠️  Error moviendo archivos: {str(e)}")
            
    def run(self):
        """Ejecuta el proceso completo de descarga"""
        try:
            print("\n" + "="*60)
            print("AUTOMATIZACIÓN DE DESCARGA - ORACLE CLOUD")
            print("Modo: LOOP cada 15 minutos")
            print("="*60)
            
            # Preparación
            self.create_folders()
            self.setup_driver()
            
            # Login (solo una vez)
            self.login()
            
            # Configurar formato de exportación (OPCIONAL - MANUAL)
            print("\n" + "="*60)
            print("⚠️  CONFIGURACIÓN DE FORMATO DE EXPORTACIÓN")
            print("="*60)
            print("Por favor, configura manualmente el formato de exportación:")
            print("1. Click en tu icono de usuario (arriba a la derecha)")
            print("2. Click en 'Preferencias'")
            print("3. Selecciona 'Excel 2007 (xlsx)' en formato de exportación")
            print("4. Guarda los cambios")
            input("\nPresiona ENTER cuando hayas configurado el formato...")
            
            # Loop infinito cada 15 minutos
            ciclo = 1
            while True:
                print("\n" + "="*70)
                print(f"🔄 CICLO #{ciclo} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                print("="*70)
                
                try:
                    # Obtener rangos de fechas
                    date_ranges = self.get_date_ranges()
                    
                    # Descargar cada base de datos
                    for db_name in self.folders.keys():
                        try:
                            dates = date_ranges[db_name]
                            self.download_database(db_name, dates)
                            self.move_downloaded_files(db_name)
                        except Exception as e:
                            print(f"\n⚠️  Error en {db_name}: {str(e)}")
                            print(f"⚠️  Continuando con la siguiente base de datos...")
                            continue
                    
                    print("\n" + "="*70)
                    print(f"✓ CICLO #{ciclo} COMPLETADO EXITOSAMENTE")
                    print("="*70)
                    
                except Exception as e:
                    print(f"\n✗ ERROR EN CICLO #{ciclo}: {str(e)}")
                    print("⚠️  Intentando continuar con el siguiente ciclo...")
                
                # Esperar 15 minutos antes del próximo ciclo
                ciclo += 1
                next_run = datetime.now() + timedelta(minutes=15)
                print(f"\n⏳ Esperando 15 minutos...")
                print(f"⏰ Próximo ciclo: {next_run.strftime('%d/%m/%Y %H:%M:%S')}")
                print("💡 Presiona Ctrl+C para detener el script")
                
                # Esperar 15 minutos con keep-alive cada 4 minutos
                for i in range(4):  # 4 intervalos de ~3.75 minutos
                    time.sleep(225)  # 3 minutos 45 segundos
                    
                    # Keep-alive: hacer una acción simple para mantener la sesión activa
                    try:
                        # Hacer clic en el logo o actualizar la página de forma suave
                        self.driver.execute_script("console.log('Keep-alive');")
                        # Mover el mouse virtualmente
                        self.driver.execute_script("document.body.style.cursor = 'pointer';")
                        time.sleep(0.5)
                        self.driver.execute_script("document.body.style.cursor = 'default';")
                        print(f"  ✓ Keep-alive {i+1}/4 - Sesión activa")
                    except:
                        print(f"  ⚠️  Error en keep-alive, pero continuando...")
                
                print("\n🔄 Iniciando nuevo ciclo...")
            
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("⚠️  SCRIPT DETENIDO POR EL USUARIO")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ ERROR GENERAL: {str(e)}")
            
        finally:
            # Mantener navegador abierto para verificar
            print("\n⚠️  El navegador permanecerá abierto.")
            print("Presiona ENTER para cerrar el navegador...")
            input()
            
            if self.driver:
                self.driver.quit()
                

if __name__ == "__main__":
    downloader = OracleCloudDownloader()
    downloader.run()
