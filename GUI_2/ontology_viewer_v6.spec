# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ontology_viewer_v6.py'],
    pathex=[],
    binaries=[],
    datas = [
    ('consultas_personalizadas.json', '.'),  # Agrega el archivo JSON en el directorio raíz
    ('preguntas_competencia.json', '.'),     # Otro archivo JSON en el directorio raíz
    ('style.qss', '.'),                      # Archivo de estilo en el directorio raíz
    ('icons', 'icons'),                      # Carpeta completa de icons en una carpeta `icons` en el ejecutable
    ('base_documents', 'base_documents'),    # Carpeta completa de documentos base en el ejecutable
    ('razonador', 'razonador'),              # Carpeta completa `razonador` en el ejecutable
    ('inference_log.txt', '.')               # Archivo de log (opcional, dependiendo del uso)
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ontology_viewer_v6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
