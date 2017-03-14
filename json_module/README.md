This module simplifies the development of modules that would like to define and check a particular set of input parameters, but be able to flexibly define those inputs in different ways in different contexts. 

It will allow you to 
Passing a command line argument to a location of a json_file which contains the input parameters
OR passing a json_dictionary directly into the module with the parameters defined
AND passing parameters via the command line, in a way that will override the examples given.

##Why
You should consider using this module if this pattern seems familar to you.

You start building some code in an ipython notebook where you define some variables as you go that make your code work, you fiddle with things for awhile and eventually you get it to a point that works.  You then immediately want to use it over and over again, and are scrolling through your ipython notebook, changing variables, making copies of your notebook for different runs.  Several times you make mistakes typing in the exact filepath of some input file, and your notebook breaks on cell 53, but no big deal, you just fix the filename variable and rerun it. 

It's a mess, and you know you should migrate your code over to a module that you can call from other notebooks, or from the command line.  You start collecting your input variables to the top of the notebook and make yourself a wrapper function that you can call.  However, now your mistake in filename typing is a disaster because the file doesn't exist, and your code doesn't check for the existence of the file until quite late. You start implementing some input validation checks to avoid this problem.

Now you start integrating this code into a pipeline of code that isn't all in pipeline, and so you want to have a command line module that executes the code, so you can use some other tool to stitch together a process that includes this code, like some shell scripts.  You implement an argparse set of inputs and default values that make your python program a self-contained program, with some help documentation.  Along the way, you have to refactor the parsed argparse variables into your function

Now this module starts becoming useful enough that you want to integrate it into more complex modules.  You end up copying and pasting the argparse code over to the other module, and then 5 other modules.  Later you decide to change your original module a little bit, and you have a nightmare of code replace to fix up the other modules.. you kick yourself for not having thought this through more clearly.

Your code is now pretty useful, but its so useful you start running it on larger and larger jobs, and you want to deploy it on a cluster in a pipeline.  The pipeline would like to simply write all the inputs to a file, and pass your program that file, rather than having to parse out the inputs into python's argparse format.  Now you have to refactor your inputs again to deal with this new pattern, so you have to make a new version that works in this way. Now you have to redo validation to work in a different way, since you were using argparse to do it before. 

If you had only designed things from the ground up to make all these use cases easy.  This is what json_module is designed to help with.

