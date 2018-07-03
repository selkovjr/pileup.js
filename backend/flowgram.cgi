#!/usr/bin/env perl6

# header {{{1
v6;
#}}}

%*ENV<LD_LIBRARY_PATH> = '/home/user/lib/torrentPy';
shell "$*CWD/flowgram.py"
