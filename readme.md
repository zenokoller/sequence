Known sequence experiment for master's thesis 'Measuring Loss and Reordering with Few Bits'.

## Installation

To run, first [install python-libtrace](https://www.cs.auckland.ac.nz/~nevil/python-libtrace/) (only required for the observer node, but not for running the experiments). Then, install the required modules:

```
pip install -r requirements.txt
```

## How to run

The files for running the client, observer and server nodes are `nodes/NODENAME/main.py`. The command line arguments of the nodes are documented in the respective files. For example, executing the following commands in two terminals runs a client with source port `5634`, destination port `3996` at a sending rate of `1000`. The server, accordingly, listens on destination port `3996`.

```
src/nodes/client/main.py 5634 3996 -r 1000
src/nodes/server/main.py 3996
```
