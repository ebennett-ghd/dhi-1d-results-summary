DHI 1D POINTS READ tool - User Documentation 04/04/2022

INTRODUCTION AND PURPOSE
========================
This readme.txt provides a longer version of user documentation for the "DHI 1D POINTS READ" extraction tool.

The purpose of the tool is to extract x,y location and 'max of timeseries' water level points data from various DHI 1D water gravity network result files, such as PRF and RES11 formats. The tool is developed to automate the extraction from a potentially large list of such input files and generates a single csv output file, with point name x,y in the initial columns and the water level data for each input file in a series of subsequent columns.

It is intended for use across groups of similar files with matching point names and locations so that the output data is matched and neatly collated. Where points do not match then gaps will result in the corresponding output water levels. PRF and RES11 file types are intrinsically not similar, however the tool is flexible enough to process both in a single output file with the types of input identified therein.

At the end of this extraction and collation process, max of max water level is calculated. Invert levels are also extracted enabling the simple derivation of max of max depth thereof. If the user defines rainfall duration in association with each input file, then the tool will identify while input file generates the 'max of max' and then outputs that files rainfall duration. This identifies 'critical duration' which is a common concept in stormwater and flood modelling when using a batch of runs with varied design rainfall duration to determine the worst (critical) rainfall duration event at any location.

The csv output is designed so as to be ready with a simple process to load into Excel for tabular inspection or various GIS products using the x, y data for spatial inspection.

The log output file records key information from the tool runtime, such as when the tool was used, input and output files. If the CSV file is converted to spatial format (eg: SHP, KMZ, GEOJSON) then it would be advisable to copy this log file record into the spatial metadata. If the CSV file is converted to spreadsheet format then it would be advisable to copy this log file record into a separate 'readme' tab or similar in the spreadsheet.


USAGE MODES
===========
The tool DHI_1D_POINTS_READ.EXE is designed to run either directly from the Windows command line interface or to be called through a Windows BAT file (bat files help in running the tool perhaps multiple times). In either method, the way the tool works is controlled by command line switches and inputs. A variety of intermediate Excel, visual basic or other text generation processes may be used to intelligently generate batch files which activate the tool innumerable times generating as many output files as required.

The simplest usage is to user specify the input and output files (path and file). The input file should consist of a plain text formatted list of DHI input files for processing, with an optional space separated second parameter which is the associated rainfall duration. If the input path\file list includes space characters then the path\file text should be enclosed in "quotes". The user may generate such input list(s) through conventional inspection and manual compilation or through some secondary database if the input files are already catalogued or follow a known organisational system.

As an alternative usage the tool can generate it's own input file list(s). The user directs the tool to a directory and the tool will find any files of the PRF or RES11 type therein and generate a text input file list of those files. The user has a command line switch option whether or not to include subdirectories. Once the list is generated the user can then intervene to adjust the sequencing of the files, remove or add files and if desired add the secondary 'duration' parameter for some or all files. In this usage the output file becomes a single .TXT file type rather than the dual .CSV and .LOG files generated otherwise. Once this list is generated the tool is run (again) in the above simplest usage mode.

A third usage is to direct the tool to a directory (which again may include subdirectories or not) and then automatically process all files of the right type found therein, without generating an intermediate list and then the user has no ability to intervene or to apply and duration parameter to the files. Some users may find it convenient to apply duration after the tool is complete using Excel, and with intermediate skills Excel readily enough be used to generate the critical duration output.

The tool is designed to read groups of files, and doesn't have a convenient 'single file only' mode. The list of files can contain only one file and the process will work fine, but you still need the list which is a bit overkill when reading a single input file.

Usage switch syntax
-------------------

Running the tool with a -h switch will print out the following list of all the available switches.

DHI_1D_POINTS_READ.EXE - Compiled 19/05/2022

usage: DHI_1D_POINTS_READ.EXE [-h] [-i INPUT_DIRECTORY] [-o OUTPUT_PATH_AND_FILENAME]
                [-f PATH_TO_LISTFILE.xxx] [-p FROM_CRS] [-s] [-l] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIRECTORY,
                        directory containing the input files to be processed or 
                        from which to generate file list for processing
  -o OUTPUT_PATH_AND_FILENAME,
                        path\filename for outputs (do not include file extension)
                        this applies to either normal or "-l" tool usage
  -f PATH_TO_LISTFILE.xxx,
                        path of text file, including file extension, containing 
                        a list of input files to process, typically TXT format
  -p FROM_CRS,
                        epsg number for the projection/coordinate reference system
                        of the model input data eg. 27200 (refer https://epsg.io/)
                        (this is not currently used but is provided in anticipation
                        of possible future automated SHP or GEOJSON file generation)
  -s, --subdir          include subdirectories when searching for input data
                        (default tool operation otherwise excludes subdirectories)
  -l, --create-file-list
                        creates a .TXT file listing the inputfiles to be processed
                        (default tool operation otherwise generates the main CSV output)
  -r, --no-round-outputs
                        do not round decimal outputs to three decimal places
                        (default tool operation otherwise rounds all data to 3DP 
                        except M11 chainages which are always rounded to 1DP)

  -t, --include-timings
                        generates second separate timing output file (*_timing.csv) 
                        showing the timestep (count) when maximum water levels occur

Notes:
the "--XXX_XXX" type arguments are simply more verbose versions with the same function as their one character version
items in CAPITALS indicate parameters to be defined by the user
any path including filename that contains a space character will need to be delimited with "" (avoidance of space characters is preferred)
for INPUT_DIRECTORY do not include a trailing "\" character
output files will overwrite any existing files
if the output path or file is not specified then the output will default to the current directory with filenames formatted_node_data.CSV, formatted_node_data.LOG and input_files.TXT.
The tool is programmed to recognise and ignore any *.RES11 files of the special additional type ie: "*HDAdd.res11" as these do not contain water level information.

Sample code 1 - generating output using a LISTFILE
C:\Filepath\DHI_1D_POINTS_READ.EXE -f "C:\Filepath\Output\ListofResultFiles.txt" -o "C:\Filepath\Output\ExtractedWaterLevels"

Sample code 2 - generating a LISTFILE
C:\Filepath\DHI_1D_POINTS_READ.EXE -i "C:\Filepath\Results" -o "C:\Filepath\Output\ListofResultFiles" -s -l

Sample code 3 - generating output using a FOLDER containing the inputs
C:\Filepath\DHI_1D_POINTS_READ.EXE -i "C:\Filepath\Results" -o "C:\Filepath\Output\\ExtractedWaterLevels" -s

TECHNICAL DETAILS
=================

Setting up
------------
The program does not need to be "installed".
The EXE file requires a package of library files to be present adjacent to the saved location for the .EXE file in order to operate. These files are typically supplied with the .EXE file in a zipped folder.

System requirements
-------------------
The tool is expected to run well on current common Windows environment PCs. The CSV is formatted to open ready into suit Excel for Microsoft 365, 2021. And equally is readily imported into current versions of ArcMap.

Known issues and limitations
----------------------------
While the CSV file has x,y data, it generally lacks knowledge of which spatial coordinate system is used in the model (if any). Typically model build reports or other user knowledge will identify the spatial coordinate system if this is important to overlay results in a generalised spatial environment. In some cases input files might contain defined projections which will be reported into the projection column in the tool output csv file. The authors are yet to find any example input file with an internally defined projection.

The extraction of x,y and water level data from RES11 format uses two separate data tables in each RES11 data file. The branch and chainage referencing in the two table are often inconsistent with respect to decimal place details of the chainage part. This disrupts the tools data matching function. The tool list is generated from the x,y,invert tabular data and if matching fails then no water level data will be reported. To improve matching both chainages are rounded to 1DP format and testing shows this is circa 99% effective (i.e. there maybe gaps in the data). However, if input files have multiple points at close proximity within the 1DP distance then the tool will not be effective. Also we still notice occasional matching failures the particular cause(s) of which remain unclear.

Any existing output files will be overwritten by the tool. A future improvement might include prevention of overwriting (tool stops and error reports) and/or a new switch option to enable overwriting.

If processing large job lists, it is advisable to monitor RAM usage (i.e. using Task Manager on a Windows device). If 
RAM limits are an issue then consider reducing the job list, or finding a computer with more RAM.

RES11READ alternative
---------------------
For RES11 file types, DHI have an existing RES11READ.EXE tool which is able to extract the max of timeseries water level from RES11 files. This tool, however, does not provide the ability to generate simple file list, max of max level, critical duration or any PRF based functionality. Authors of DHI_1D_POINTS_READ anticipate that once users become familiar with this new tool that the RES11READ tool may no longer be useful.

Readme.txt
----------
This readme.txt user documentation is developed using simple Markdown syntax [daringfireball.net/projects/markdown](https://daringfireball.net/projects/markdown/syntax)
which means that it can be readily converted from plaintext to HTML (and other rich text formats) if desired for readability or other future purpose using software tools like "Markdown" [Wiki/Markdown](https://en.wikipedia.org/wiki/Markdown)

Open source code and licencing
-------------------------------------
The open source code is generally supplied with the ZIP file package and has also been published on Github at https://github.com/ebennett-ghd/dhi-1d-results-summary
The license is indicated seperately within this repository. This licensing prevents modification and distribution of derivative products (like exe files) without also distributing the source code, which ensures improved or derived tools continue to be open source software. 

Coding Language and Compilation
===============================
This tool has been developed using Python v3.8, Anaconda code editing interface and the DHI suite of Mike I/O 1D 
library of tools. [mikeio1d](https://github.com/DHI/mikeio1d). In order to compile a new EXE file after coding improvements are made, we used Anaconda with a list of extensions (most notably PyInstaller and mikeio1d).

EXAMPLE STORY
-----
1. Install Python v3.8 (freeware)
2. Install Anaconda (this step is optional)
3. Ensure Anaconda is activated in the computer (activate.bat) if using Anaconda
4. Use PIP to install the list of required modules (requirements.txt) PIP installs from known online resources - this needs an internet connection.
5. Submit the main code (main.py) into PyInstaller to generate the main.EXE file into the current directory (if using a bat file this is the directory where the bat file is saved)
6. Copy (or move) MAIN.EXE to the desired folder (if required) and rename to DHI_1D_POINTS_READ.EXE
7. Copy the mikeio1d library package from ProgramData\Anaconda3\Lib\site-packages\mikeio1d into the same folder as the 
   DHI_1D_POINTS_READ.EXE file 

Requirements (to run code + generate EXE)
-----------------------------------------
Requirements are indicated separately within requirements.txt, according to standard Python programming practice.

Example BAT file (to generate EXE)
----------------------------------
The process to achieve steps 3-6 above is as follows. Call:
`C:\ProgramData\Anaconda3\Scripts\activate.bat`
`pip install -r requirements.txt`
`create_exe.bat`


VERSION HISTORY AND AUTHORS
===========================
The tool was developed as open source code by GHD, through work funded by Christchurch City Council. Contributions to the tool design, coding and beta testing were also made by Tim Preston, Yanni Hooi and Rowan De Costa (GHD). Authorisation to release the code under this licencing was given by Kevin McDonnell (CCC) on 16/3/2022 (GHD email repository 12555628). The first publication to Github (https://github.com/ebennett-ghd/dhi-1d-results-summary) was done on 25/3/2022.


OPPORTUNITIES FOR IMPROVEMENT
====================================
1. Addition of support for the RES1D file format
2. Improving and hopefully fully resolving the RES11 data table matching issue. A feasible intermediate step would be to at least ensure that all data in the water level table is extracted, even if matching x,y,invert data cannot be found. Retain additional decimal places to support model instances where computational points might be more closely spaced. The DHI res11 file does not have this issue, learning from this tool is required to update this tool
3. Option to directly output file(s) in spatial formats, with or without somehow user defined projection systems. Suggested spatial formats would include SHP, KMZ and GEOJSON.
4. The code could be made into an installable Python package to facilitate distribution of the tool.
5. Impliment a logical vertical sorted order into the points data such as PRF first alphabetically and RES11 second by branch alphabetically and then chainage in numeric sequence
6. Distinguishing different types of computation points - for example PRF nodes can be type 1,2,3 (2 being open channel nodes), and RES11 files can include open channels, closed cross sections and structures
7. Improve the file overwriting behaviour, to either request confirmation to overwrite, or fail with suitable error messaging
8. Improved clarity on error messaging (eg: "LISTFILE input not found")
9. When one file (*.res11 or a *.prf file) is to be processed, then to change the code to refer to the file rather than the folder the file is saved in or a list of files.
10. Output the last saved timestep. This will help in understanding either the crash time or confirm the completed run duration.
