Known sequence experiment for master's thesis 'Measuring Loss and Reordering with Few Bits'.

## Installation

Python 3.6 is required.

1. (Optional) [Installing python-libtrace](https://www.cs.auckland.ac.nz/~nevil/python-libtrace/) is required for running the `router` node.
2. Install the required modules with `pip install -r requirements.txt`.
3. Add the src folder to the `PYTHONPATH` using `export PYTHONPATH=$PYTHONPATH:~/path/to/sequence/src`

### How to run?

The files for running the client, router and server nodes are `nodes/NODENAME/main.py`. The command line arguments of the nodes are documented in the respective files. 

### Example: Running client & server locally

Executing the following commands in two terminals runs a client with source port `5634`, destination port `3996` at a sending rate of `1000`. The server, accordingly, listens on destination port `3996`.

```
src/nodes/client/main.py 5634 3996 -r 1000
src/nodes/server/main.py 3996
```

## Example: Running client & server on separate machines

In order to run the nodes on separate machines, the sending interface of the client has to be set as an environment variable:

```
export CLIENT_DOMAIN_CLIENT_ADDR=X.X.X.X
```

Likewise, the receiving interface of the server has to be set as an environment variable: 

```
export SERVER_DOMAIN_SERVER_ADDR=Y.Y.Y.Y
```

Then, the server and the client can be started on the respective machines:

```
src/nodes/client/main.py 5634 Y.Y.Y.Y:3996
src/nodes/server/main.py 3996
```
