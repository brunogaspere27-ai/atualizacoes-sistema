[Setup]
AppName=CW Transportadora
AppVersion=6.0.0
DefaultDirName={autopf}\CW Transportadora
DefaultGroupName=CW Transportadora
OutputDir=instalador
OutputBaseFilename=CW_Transportadora_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Files]
Source: "dist\CW_Transportadora.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "versao.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "configuracoes.json"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CW Transportadora"; Filename: "{app}\CW_Transportadora.exe"
Name: "{autodesktop}\CW Transportadora"; Filename: "{app}\CW_Transportadora.exe"

[Run]
Filename: "{app}\CW_Transportadora.exe"; Description: "Abrir CW Transportadora"; Flags: nowait postinstall skipifsilent
