import json, ff_io, sys

config = json.load(open(sys.argv[1]))

manager = ff_io.FFIOManager(config['width'], config['height'])

def do_render(kind):
    outfile = config.get(kind+'_sink', None)
    infiles = config.get(kind+'_stack', [])
    sink = getattr(manager, 'open_'+kind+'_sink')(outfile)
    i = iter(infiles)
    left = 0
    cur = None
    while True:
        if left == 0:
            print('picked up the next fragment')
            try: cur = next(i)
            except StopIteration: break
            left = cur[2]
            if left == 0: continue
            cur = getattr(manager, 'open_'+kind+'_source')(cur[0], cur[1])
#       left -= 1
#       sink.write_frame(cur.read_frame())
        cur.forward_frames(left, sink)
        left = 0

print('Rendering video...')
do_render('video')
print('Rendering audio...')
do_render('audio')
