'*****************************************************************************
'Automatic Script to set Internet Explorer proxy server setting
'Date:23/06/2008'Site : http://www.nhowetech.com/
'Email :nhowelson@nhowetech.com
'*****************************************************************************
On Error Resume Next
Dim WSH_Shell
Dim Proxy_URL
Dim Proxy_Port

'****You need to define this parameters based on your needs************************
Proxy_URL = "web-proxy.hpl.hp.com"
Proxy_Port = "8088"
'*****************************************************************************
'Load a shellSet
Set WSH_Shell = WScript.CreateObject("WScript.Shell")
'Execute Registry write to change value in registry
WSH_Shell.RegWrite "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyServer", Proxy_URL & ":" & Proxy_Port, "REG_SZ"
WSH_Shell.RegWrite "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyEnable", 1, "REG_DWORD"

'WScript.Echo WSH_Shell.RegRead("HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyServer")

Set WSH_Shell = Nothing

'******************************************************************************