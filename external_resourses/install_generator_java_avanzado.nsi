# Nombre del instalador
OutFile "Ontology Viewer Installer.exe"

# Carpeta de instalación por defecto
InstallDir "$PROGRAMFILES\Ontology Viewer"

# Solicitar permisos de administrador
RequestExecutionLevel admin

Section "Principal"
    SetDetailsPrint both

    # Crear directorio de instalación si no existe
    CreateDirectory "$INSTDIR"

    SetOutPath "$INSTDIR"

    # Archivos a copiar
    File /r "..\dist\ontology_viewer_v6\*"
    File "..\dist\ontology_viewer_v6\javaSetup.msi" # Incluir el instalador de Java en el paquete

    # Verificar si Java está instalado buscando en el registro
    ReadRegStr $0 HKLM "SOFTWARE\JavaSoft\Java Runtime Environment" "CurrentVersion"
    StrCmp $0 "" JavaNotFound JavaFound

    JavaNotFound:
        MessageBox MB_OK "No se detectó Java en el sistema. Se procederá a instalarlo."

        # Ejecutar el instalador de Java desde el directorio de instalación
        ExecWait 'msiexec /i "$INSTDIR\javaSetup.msi"' $1

        # Capturar el código de salida y manejar casos específicos
        IntCmp $1 0 JavaSuccess JavaRestart JavaError

        JavaSuccess:
            MessageBox MB_OK "Java se instaló correctamente."
            Goto ContinueInstallation

        JavaRestart:
            MessageBox MB_OK "Java se instaló correctamente, pero es necesario reiniciar el sistema para completar la instalación."
            Goto ContinueInstallation

        JavaError:
            MessageBox MB_OK "La instalación de Java falló. Código de error: $1"
            Abort

    JavaFound:
        MessageBox MB_OK "Java ya está instalado en el sistema. No es necesario instalarlo."

    ContinueInstallation:
        # Crear accesos directos
        CreateShortcut "$DESKTOP\Ontology Viewer.lnk" "$INSTDIR\ontology_viewer_v6.exe" "" "$INSTDIR\icon.ico"
        CreateShortcut "$SMPROGRAMS\Ontology Viewer\Ontology Viewer.lnk" "$INSTDIR\ontology_viewer_v6.exe" "" "$INSTDIR\icon.ico"

        # Escribir el desinstalador
        WriteUninstaller "$INSTDIR\uninstall.exe"

        # Eliminar instalador de Java
        DetailPrint "Eliminando instalador de Java..."
        Delete "$INSTDIR\javaSetup.msi"
SectionEnd

Section "Uninstall"
    SetDetailsPrint both

    # Borrar los accesos directos
    Delete "$DESKTOP\Ontology Viewer.lnk"
    Delete "$SMPROGRAMS\Ontology Viewer\Ontology Viewer.lnk"

    # Borrar los archivos y la carpeta de instalación
    RMDir /r "$INSTDIR"

    # Borrar la carpeta del menú Inicio
    RMDir "$SMPROGRAMS\Ontology Viewer"
SectionEnd
