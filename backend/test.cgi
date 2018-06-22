#!/usr/bin/env perl6

# header {{{1
v6;

use URI::Encode;
use File::Temp;
use Terminal::ANSIColor;
use Data::Dump;

print "Content-type: text/plain\n";
print "Access-Control-Allow-Origin: *\n\n";
#}}}

say Dump(%*ENV, :color(False));
