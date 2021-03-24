import subprocess, os

subprocess = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)

output, error = subprocess.communicate()

for i in output.splitlines():

    if 'python scraper.py' in str(i):

        p = list(filter(lambda x:x, str(i).split(' ')))

        if p[8].find(":") == -1:

            os.kill(int(p[1]), 9)



            print('killing',p[1])