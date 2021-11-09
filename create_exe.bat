RD /S /Q dist\
pyinstaller --noconfirm main_folder.spec
Xcopy /E /I /S .\venv\Lib\site-packages\mikeio1d dist\DHI_1D_Results_Summary\mikeio1d\