Unicode true
Name "GePeGe 0.2b"
OutFile "${ROOT}\GePeGe-0.2b-Windows-x86_64-Setup.exe"
InstallDir "$PROGRAMFILES64\GePeGe"
RequestExecutionLevel admin
ShowInstDetails show

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "GePeGe" SEC_MAIN
  SetOutPath "$INSTDIR"
  File /r "${ROOT}\dist\GePeGe\*"
  CreateDirectory "$SMPROGRAMS\GePeGe"
  CreateShortcut "$SMPROGRAMS\GePeGe\GePeGe.lnk" "$INSTDIR\GePeGe.exe"
  WriteUninstaller "$INSTDIR\Desinstalar.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GePeGe" "DisplayName" "GePeGe 0.2b"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GePeGe" "UninstallString" '"$INSTDIR\Desinstalar.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GePeGe" "DisplayVersion" "0.2b"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GePeGe" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GePeGe" "NoRepair" 1
  IfFileExists "$PROGRAMFILES32\GnuPG\bin\gpg.exe" done
  IfFileExists "$PROGRAMFILES64\GnuPG\bin\gpg.exe" done
  IfFileExists "$PROGRAMFILES32\Gpg4win\bin\gpg.exe" done
  IfFileExists "$PROGRAMFILES64\Gpg4win\bin\gpg.exe" done
  MessageBox MB_OK|MB_ICONINFORMATION "GePeGe necesita GnuPG. A continuación se abrirá su instalador oficial incluido. Sigue sus instrucciones para completar la instalación."
  InitPluginsDir
  SetOutPath "$PLUGINSDIR"
  File /oname=gnupg-installer.exe "${ROOT}\gnupg-installer.exe"
  ExecWait '"$PLUGINSDIR\gnupg-installer.exe"' $0
  IfFileExists "$PROGRAMFILES32\GnuPG\bin\gpg.exe" done
  IfFileExists "$PROGRAMFILES64\GnuPG\bin\gpg.exe" done
  IfFileExists "$PROGRAMFILES32\Gpg4win\bin\gpg.exe" done
  IfFileExists "$PROGRAMFILES64\Gpg4win\bin\gpg.exe" done
  MessageBox MB_OK|MB_ICONEXCLAMATION "No se ha detectado GnuPG. GePeGe está instalado, pero necesita GnuPG para funcionar. Instálalo desde gnupg.org y vuelve a abrir GePeGe."
  done:
SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS\GePeGe\GePeGe.lnk"
  RMDir "$SMPROGRAMS\GePeGe"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GePeGe"
  RMDir /r "$INSTDIR"
SectionEnd
