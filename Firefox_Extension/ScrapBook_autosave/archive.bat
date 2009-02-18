cd chrome
"C:\Program Files\7-Zip\7z.exe" a -r -tzip sbautosave.jar .\ -x!*.jar -x!*.bat -x!*.svn*
cd ..
"C:\Program Files\7-Zip\7z.exe" a -r -tzip ScrapBook_autosave.xpi .\ -x!*.xpi -x!*.bat -x!*.svn* -x!locale -x!content