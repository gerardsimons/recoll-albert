# recoll-albert
A Python plugin for Albert that queries Recoll

## Motivation
Coming from Mac OS I really missed the Spotlight feature that would display files containing certain terms. Albert provides matches based on file names but not yet on file content. This plugin aims to do just that using Recoll and Xapian for the indexing and subsequent retrieval of documents.

## Prerequisites

Recoll and Xapian and the Python API for Recoll is required.

For recent Ubuntu versions you should just be able to do
 
`sudo apt-get install -y recoll python3-recoll`

This installs the binaries and the Python packages. Note that there is no way of pip install the Python packages as far as I know, which
makes it a bit tricky to work within a virtualenv like you usually would.

Make sure you create an index of the files and directories you deem relevant. 
Follow the [indexing instructions](https://www.lesbonscomptes.com/recoll/usermanual/usermanual.html#RCL.INDEXING) 
in the Recoll User manual, though I can offer one recommendation so you don't get spammed with too many non-relevant 
results and improve indexing performance / time, and that is by making sure the hidden folders and files are not indexed.
You can do that from the GUI by going to `Preferences > Index Configuration > Local Parameters` and adding `.*` or simply
by including it in the .recoll/recoll.conf. Here is a oneliner for it : `echo "skippedNames+ = .*" >> .recoll/recoll.conf` 

Then go ahead an run the indexing from the GUI by clicking `File > Create Index` or from commandline by issuing something like 
`recollindex -r ~` if you would like to index everything recursively from your home folder.

If the indexing worked properly you should be able to issue a query either from the GUI search bar or 
from command line: `recoll -t <query>`. It's worth trying this on a known file's contents and observing the results

Note: I had an issue with some of the filters using `cgi.escape` in Python 3.8 as escape was moved to the html module. So for now you should use Python 3.7 or lower for full compatibility.

This plugin was developed and tested with `Recoll 1.26.3 + Xapian 1.4.14` on Ubuntu 20.04

## Installation

Assuming your Recoll is working properly, we can go ahead and install the Python plugin

Run the install script install.sh to copy the plugin folder to Albert. Then make sure the plug-in is enabled in Albert's
settings under Python.

## Documentation

TODO

## Known Issues





