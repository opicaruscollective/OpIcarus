
#!/usr/bin/env python

import sys, argparse, telnetlib, time, datetime, traceback, re, os, getpass

def showBanner():
    print('''
[*] +-------------------------------+
[*] | Tor Switcher                  |
[*] |              v0.1             |
[*] | nwmonster[at]insight-labs.org |
[*] +-------------------------------+
        ''')

def cleanScreen():
    os.system(['clear', 'cls'][os.name == 'nt'])

def main():
    try:
        ap = argparse.ArgumentParser(description='Tor Switcher v0.1')
        ap.add_argument('--passwd', help='tor control authenticate password', default=None, required=False)
        ap.add_argument('--host', help='tor control host ip', default='127.0.0.1', required=False)
        ap.add_argument('--port', help='tor control host port', default='9051', required=False)
        ap.add_argument('--timer', help='switch timer', default=60, type=int, required=False)
        args = ap.parse_args()
        if args.passwd == None:
            showBanner()
            print('[!] Tor Control Authenticate')
            passwd = getpass.getpass(prompt='[?] Password:')
        else:
            passwd = args.passwd
        clock = args.timer
        host = args.host
        port = args.port   
        tn = telnetlib.Telnet(host, port)
        if passwd == '':
            tn.write('AUTHENTICATE\r\n')
        else:
            tn.write('AUTHENTICATE \"%s\"\r\n' % (passwd))
        res = tn.read_until('250 OK', 5)

        if res.find('250 OK') > -1:
            print('[!] AUTHENTICATE SUCCEED\n')
        else:
            print('[!] AUTHENTICATE ERROR\n')
            print('[!] EXIT')
            return
    except Exception, ex:
        print('[!] ERROR: %s.' % (ex))
        print('[!] EXIT')
    cleanScreen()
    showBanner()
    while True:
        try:    
            tn.write('SIGNAL NEWNYM\r\n')
            tn.read_until('250 OK', 5)
            for x in range(clock):
                tn.write('GETINFO circuit-status\r\n')
                res = tn.read_until('250 OK',5)
                print '             HOST\n              |\n              V'
                regex = re.compile('\$')
                s = re.finditer(regex, res)
                i = 0
                for match in s:
                    id = res[match.end():match.end()+40]
                    tn.write('GETINFO ns/id/%s\r\n' % id)
                    txt = tn.read_until('250 OK', 5)
                    list = re.split('\s+', txt)
                    tn.write('GETINFO ip-to-country/%s\r\n' % list[8])
                    country = tn.read_until('250 OK', 5)
                    country = country[-10:-8]
                    print('   IP:%s[%s] NAME:%s' % (list[8], country.upper(), list[3]))
                    if i<2:
                        i = i+1
                        print('              |')
                        print('              V')
                    else:
                        print('\n')
                        break
                now = datetime.datetime.now()
                print('[!] [%02d:%02d:%02d] [%d/%d]' % (now.hour, now.minute, now.second, x, clock))
                time.sleep(1)
                cleanScreen()
                showBanner()
        except (KeyboardInterrupt, SystemExit):
            try:
                tn.write("[!] QUIT\r\n")
                tn.close()
            except:
                pass

if __name__ == '__main__':
    main()