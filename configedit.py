import sys, json, readline

try: config = json.load(open(sys.argv[1]))
except: config = {}

def decode_time(x):
    x = list(map(int, x.split(':')))
    x[-1] *= 2
    i = 0
    for j in x:
        i = 60 * i + j
    return i // 2

def encode_time(x):
    x *= 2
    ans = []
    for i in range(3):
        ans.append(x % 60)
        x //= 60
    ans.append(x)
    ans.reverse()
    ans[-1] //= 2
    return '%02d:%02d:%02d:%02d'%tuple(ans)

def execute(cmd, kind):
    if cmd.startswith('sink '):
        config[kind+'_sink'] = cmd[5:]
    elif cmd.startswith('push '):
        video, start, length = cmd[5:].rsplit(' ', 2)
        start = decode_time(start)
        length = decode_time(length)
        if kind+'_stack' not in config:
            config[kind+'_stack'] = []
        config[kind+'_stack'].append([video, start, length])
    elif cmd == 'pop':
        if config.get(kind+'_stack'):
            config[kind+'_stack'].pop()
        else:
            print('stack is empty')
    elif cmd == 'stat':
        print('*', kind, 'is at', encode_time(sum(i[2] for i in config.get(kind+'_stack', ()))))
    else:
        print('unknown cmd')

mode = ('video', 'audio')

while True:
    try: cmd = input('> ')
    except (KeyboardInterrupt, EOFError): break
    if cmd.startswith('mode '):
        mode = (cmd[5:],)
        if mode == ('both',): mode = ('video', 'audio')
    elif cmd.startswith('size '):
        width, height = map(int, cmd[5:].split())
        config['width'] = width
        config['height'] = height
    else:
        for kind in mode:
            execute(cmd, kind)

with open(sys.argv[1], 'w') as file:
    json.dump(config, file)
