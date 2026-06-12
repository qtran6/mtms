; installer.iss — Inno Setup script for MTMS
; Open in Inno Setup Compiler and click Build
; Layout: {app}\BangGia.xlsx (user-editable) + {app}\app\ (exe, _internal, uninstaller)

#define MyAppName       "Toa Hang"
#define VerFile FileOpen("client\version.py")
#define VerLine FileRead(VerFile)
#expr FileClose(VerFile)
#define MyAppVersion Copy(VerLine, Pos('"', VerLine) + 1, RPos('"', VerLine) - Pos('"', VerLine) - 1)
#define MyAppPublisher  "Quan Tran"
#define MyAppExeName    "Toa Hang.exe"

[Setup]
AppId={{CC06E256-E0FE-42B1-98DE-093B0D164E08}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userdesktop}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=no
OutputBaseFilename=MTMS_Setup
SetupIconFile=client\assets\MT.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\app\{#MyAppExeName}
PrivilegesRequired=lowest
UninstallFilesDir={app}\app

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; Migrate old flat layout — remove root-level exe/_internal/uninstaller on upgrade
Type: files;          Name: "{app}\Toa Hang.exe"
Type: filesandordirs; Name: "{app}\_internal"
Type: files;          Name: "{app}\unins000.exe"
Type: files;          Name: "{app}\unins000.dat"

[Files]
; Bundle everything from PyInstaller's output folder into the app subfolder
Source: "dist\MTMS\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs
; Price list stays at the root, never overwritten on update
Source: "data\BangGia.xlsx"; DestDir: "{app}"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\app\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\app\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\app\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent