[Setup]
AppName=CW Transportadora
AppVersion=6.0.7
AppPublisher=CW Transportadora
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={commonpf}\CW Transportadora
DefaultGroupName=CW Transportadora
OutputDir=C:\Users\bruno\OneDrive\Desktop\atualizaçao sistema\CW_TRANSPORTADORA atualizado\release
OutputBaseFilename=CW_Transportadora_v6.0.7_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\CW_Transportadora.exe
InternalCompressLevel=max

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar ícone na área de trabalho"; GroupDescription: "Ícones adicionais:"

[Files]
Source: "C:\Users\bruno\OneDrive\Desktop\atualizaçao sistema\CW_TRANSPORTADORA atualizado\dist\CW_Transportadora.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\telas\*"; DestDir: "{app}\telas"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\services\*"; DestDir: "{app}\services"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\migrations\*"; DestDir: "{app}\migrations"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:/Users/bruno/OneDrive/Desktop/atualizaçao sistema/CW_TRANSPORTADORA atualizado\versao.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CW Transportadora"; Filename: "{app}\CW_Transportadora.exe"
Name: "{commondesktop}\CW Transportadora"; Filename: "{app}\CW_Transportadora.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CW_Transportadora.exe"; Description: "Iniciar CW Transportadora"; Flags: nowait postinstall skipifsilent
