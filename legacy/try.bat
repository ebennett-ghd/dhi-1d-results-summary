REM Obtain PRF node list
"C:\ProgramData\Anaconda3\Scripts\ipython.exe" ResultDataExtract.py V05_20Te09h.PRF PRF_output.csv node

REM Obtain res11 reach list
"C:\ProgramData\Anaconda3\Scripts\ipython.exe" ResultDataExtract.py V109_Avon_2020_0SLR_200ARI_01hr_down.res11 Res11_output.csv reach



REM Obtain PRF Quantities item 
"C:\ProgramData\Anaconda3\Scripts\ipython.exe" ResultDataExtract.py V05_20Te09h.PRF PRF_output.csv

REM Obtain res11 Quantities item
"C:\ProgramData\Anaconda3\Scripts\ipython.exe" ResultDataExtract.py V109_Avon_2020_0SLR_200ARI_01hr_down.res11 Res11_output.csv



REM Extract PRF water level at a particular node
"C:\ProgramData\Anaconda3\Scripts\ipython.exe" ResultDataExtract.py V05_20Te09h.PRF PRF_output.csv node:WaterLevel:SUMN.Junction.CCCGIS.2806

REM Extract res11 water level at a particular reach
"C:\ProgramData\Anaconda3\Scripts\ipython.exe" ResultDataExtract.py V109_Avon_2020_0SLR_200ARI_01hr_down.res11 Res11_output.csv reach:"Water Level":AVON.PORRIT

pause