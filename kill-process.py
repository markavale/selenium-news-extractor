import subprocess, os

from datetime import datetime

subprocess = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)

output, error = subprocess.communicate()



# print(output.splitlines(), len(output.splitlines()))



for i in output.splitlines():

    if 'python scraper.py' in str(i):

        p = list(filter(lambda x:x, str(i).split(' ')))

        if p[8].find(":") != -1:

            #os.kill(int(p[1]), 9)

            t_now = datetime.now().strftime('%H')

            p_time = datetime.strptime(p[8].split(':')[0], "%H")

            t_final = datetime.strptime(t_now, '%H')

            t_result = t_final - p_time

            t_hour = int(t_result.seconds / 3600)

            if t_hour >= 1:

                os.kill(int(p[1]), 9)

                print('killing',p[1], p[8], t_hour)

        elif p[8].find(":") == -1:

            os.kill(int(p[1]), 9)

            print('Killing process', p[1])