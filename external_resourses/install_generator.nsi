# Nombre del instalador
OutFile "Ontology Viewer Installer.exe"

# Carpeta de instalación por defecto
InstallDir "$PROGRAMFILES\Ontology Viewer"

# Sección de instalación
Section "Principal"
    # Crear carpeta de destino
    SetOutPath "$INSTDIR"

    # Archivos a copiar
    File /r "../dist/ontology_viewer_v6\*"


    # Crear accesos directos
    CreateShortcut "$DESKTOP\Ontology Viewer.lnk" "$INSTDIR\ontology_viewer_v6" "" "$INSTDIR\icon.ico"
    CreateShortcut "$SMPROGRAMS\Ontology Viewer\Ontology Viewer.lnk" "$INSTDIR\ontology_viewer_v6" "" "$INSTDIR\icon.ico"

    # Escribir el desinstalador
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    # Borrar los accesos directos
    Delete "$DESKTOP\Ontology Viewer.lnk"
    Delete "$SMPROGRAMS\Ontology Viewer\Ontology Viewer.lnk"

    # Borrar la carpeta de instalación junto con sus archivos y subcarpetas
    RMDir /r "$INSTDIR"

    # Borrar la carpeta del menú Inicio
    RMDir "$SMPROGRAMS\Ontology Viewer"
SectionEnd

