; Inno Setup Script for Intelligent Traffic Light Simulation
; Save as installer/traffic-sim.iss and compile with ISCC.exe

#ifndef MyAppName
#define MyAppName "Intelligent Traffic Light Simulation"
#endif
#ifndef MyAppVersion
#define MyAppVersion "1.0.0"
#endif
#ifndef MyAppPublisher
#define MyAppPublisher "Kawyanethma"
#endif
#ifndef MyAppURL
#define MyAppURL "https://example.com"
#endif
#ifndef MyAppExeName
#define MyAppExeName "main.exe"
#endif

[Setup]
; Use a stable GUID for AppId. Keep the double braces.
AppId={{A2CDF5A0-2E8E-4B0B-9C68-5F4B8BF1C9C7}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=no
; The build script overrides output dir/name, but keep sensible defaults
OutputBaseFilename=Traffic-Sim-Setup-{#MyAppVersion}
OutputDir=.\
Compression=lzma
SolidCompression=yes
; Ensure Control Panel (Apps & Features) shows the app icon
UninstallDisplayIcon={app}\{#MyAppExeName}
; Prefer modern architecture identifiers; see Inno "Architecture Identifiers" docs
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
WizardStyle=modern
; Optional: icon controlled via define (pass /DMyAppIcon=full\\path\\to\\icon.ico)
#ifdef MyAppIcon
SetupIconFile={#MyAppIcon}
#endif
LicenseFile=..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main executable built by PyInstaller
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Resource folder required by the app at runtime
Source: "..\dist\images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; IconIndex: 0

[Run]
; Offer to launch after install
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; WorkingDir: "{app}"; Flags: nowait postinstall skipifsilent