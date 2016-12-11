# You can use reactor.spawnProcess to set up arbitrary file descriptor mappings
#  between a parent process and a child process it spawns. For example, to run a
#  program and give it two extra output descriptors (in addition to stdin, stdout,
#  and stderr) with which it can send bytes back to the parent process, you would
#  do something like this:

reactor.spawnProcess(protocol, executable, args,
                     childFDs={0: 'w', 1: 'r', 2: 'r', 3: 'r', 4: 'r'})
# The reactor will take care of creating the pipes for you, and will call
#  childDataReceived on the ProcessProtocol you pass in when data is read
#  from them. See the spawnProcess API docs for details.

