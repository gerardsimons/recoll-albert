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

Then make sure you create an index of the files and directories you deem relevant. Follow the [indexing instructions](https://www.lesbonscomptes.com/recoll/usermanual/usermanual.html#RCL.INDEXING) in the Recoll User manual

If the indexing worked properly you should be able to issue a query either from the GUI search bar or 
from command line: `recoll -t <query>`. It's worth trying this on a known file's contents and observing the results

Note: I had an issue with some of the filters using `cgi.escape` in Python 3.8 as escape was moved to the html module. So for now you should use Python 3.7 or lower for full compatibility.

This plugin was developed and tested with `Recoll 1.26.3 + Xapian 1.4.14` on Ubuntu 20.04

## Installation

If the above is working correctly this Python plugin should be able to connect to the Recoll database and query for 
results. 

Either copy the folder recoll to your 


## Documentation




