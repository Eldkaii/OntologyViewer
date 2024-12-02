# Nombre del instalador
OutFile "Ontology Viewer Installer.exe"

# Carpeta de instalación por defecto
InstallDir "$PROGRAMFILES\Ontology Viewer"

# Solicitar permisos de administrador
RequestExecutionLevel admin

# Ruta al instalador de Java
!define JAVA_INSTALLER_PATH "$EXEDIR\javaSetup.exe"

# Sección de instalación
Section "Principal"
    # Configuración para detalles de depuración
    SetDetailsPrint both

    # Instalar Java siempre
    MessageBox MB_OK "Iniciando instalación de Java desde: ${JAVA_INSTALLER_PATH}"
    ExecShell "runas" "${JAVA_INSTALLER_PATH}" ; Ejecutar como administrador
    IfErrors JavaError JavaSuccess

    JavaError:
        MessageBox MB_OK "No se pudo iniciar el instalador de Java. Verifique si tiene permisos suficientes."
        Abort "La instalación se detuvo porque Java no pudo instalarse."
    
    JavaSuccess:
        MessageBox MB_OK "El instalador de Java fue iniciado. Por favor, complete la instalación."

    # Continuar con la instalación de Ontology Viewer
    SetOutPath "$INSTDIR"

    # Archivos a copiar
    File /r "../dist/ontology_viewer_v6\*"

    # Crear accesos directos
    CreateShortcut "$DESKTOP\Ontology Viewer.lnk" "$INSTDIR\ontology_viewer_v6" "" "$INSTDIR\icon.ico"
    CreateShortcut "$SMPROGRAMS\Ontology Viewer\Ontology Viewer.lnk" "$INSTDIR\ontology_viewer_v6" "" "$INSTDIR\icon.ico"

    # Escribir el desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

# Sección de desinstalación
Section "Uninstall"
    # Configuración para detalles de depuración
    SetDetailsPrint both

    # Borrar los accesos directos
    Delete "$DESKTOP\Ontology Viewer.lnk"
    Delete "$SMPROGRAMS\Ontology Viewer\Ontology Viewer.lnk"

    # Borrar la carpeta de instalación junto con sus archivos y subcarpetas
    RMDir /r "$INSTDIR"

    # Borrar la carpeta del menú Inicio
    RMDir "$SMPROGRAMS\Ontology Viewer"
SectionEnd
