** Requirements:
	- Python 2.7 (minimum)
	- wxPython (wxWidgets Cross-platform C++ GUI toolkit (wxPython binding))
	- libxml2 and libxslt (Used by the tool to handle the input/output XML files) 

** Installation of the requirements on Debian System:

- Installation of Python 2.7 and it's standard libraries:
	apt-get install python2.7 libpython2.7-minimal libpython2.7-stdlib libpython2.7 

- Installation of wxPython:
	apt-get install python-wxgtk2.8

- Installation of libxml2 and libxslt
	apt-get install python-lxml


** Utilization:
The RORI evaluation tool can be used in 2 ways:
   - By calling the python script "RORI.py" from the shell as a regular bash/python script or,
   - by calling the python script "main.py" wich contains a more friendly GUI of the tool.

- Calling the python script "RORI.py":
   
   The "RORI.py" script will receive 2 parameters: the system path to the input XML file with all the information required to perform the RORI evaluation (there are some examples in the input examples directory) and the second (optional) parameter is the path and the desired name of XML file with the results of the evaluation. 

An example of the usage of RORI.py can be:

	python RORI.py -i ./input_examples/RORI_input.xml -o /home/user/RORI_eval_results.xml

in this example the input XML file is "RORI_input.xml" and is given with the option -i. The desired name for the output XML file is "RORI_eval_results.xml" and it will be saved in the /home/user location.

If the output (-o) option is omitted, the output will be generated in an XML file called "RORI_output.xml" located in the current working directory.

- Calling the python script "main.py":

   The "main.py" is the more friendly way to use the RORI evaluation tool. By calling it a GUI will be displayed. The GUI is intuitive enough to be easily used; in it the input/output XML files can be given/set using file explorer windows and the results of the RORI evaluation will be displayed in a more detailed form than with the "RORI.py" script. If all the dependancies given earlier has been installed correctly the GUI can be called as follows:

	python main.py

