import os, sys, random


def deviser(max):
    fh = open("deviser.log","w")
    to_be_guessed = int(max * random.random()) + 1

    guess = 0
    while guess != to_be_guessed:
        guess = int(raw_input())
        fh.write(str(guess) + " ")
        if guess > 0:
            if guess > to_be_guessed:
                print 1
            elif guess < to_be_guessed:
                print -1
            else:
                print 0
            sys.stdout.flush()
        else:
            break
    fh.close()

def guesser(max):
    fh = open("guesser.log","w")
    bottom = 0
    top = max
    fuzzy = 10
    res = 1
    while res != 0:
        guess = (bottom + top) / 2
        print guess
        sys.stdout.flush()
        fh.write(str(guess) + " ")
        res = int(raw_input())
        if res == -1: # number is higher
            bottom = guess
        elif res == 1:
            top = guess
        elif res == 0:
            message = "Wanted number is %d" % guess
            fh.write(message)
        else: # this case shouldn't occur
            print "input not correct"
            fh.write("Something's wrong")


n = 100
stdin  = sys.stdin.fileno() # usually 0
stdout = sys.stdout.fileno() # usually 1

parentStdin, childStdout  = os.pipe()
childStdin,  parentStdout = os.pipe()
pid = os.fork()
if pid:
    # parent process
    os.close(childStdout)
    os.close(childStdin)
    os.dup2(parentStdin,  stdin)
    os.dup2(parentStdout, stdout)
    deviser(n)
else:
    # child process
    os.close(parentStdin)
    os.close(parentStdout)
    os.dup2(childStdin,  stdin)
    os.dup2(childStdout, stdout)
    guesser(n)