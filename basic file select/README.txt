HOW TO USE

1. Open a command prompt and navigate to this folder

2. Run the following commands:
	'set FLASK_APP=upload.py'
	'set FLASK_DEBUG=1' <- (Optional, instant updates when changing any template HTMLs and/or the Python script)
	'flask run'
	
3. Open the browser to localhost:5000

You will be met with an an upload interface.
Once you have uploaded a file, you are redirected to localhost:5000/uploads/<filename>. 
On this page you can navigate back to the upload page, 
	which will display the filename of the file you just uploaded in the section 'Uploaded Files'.