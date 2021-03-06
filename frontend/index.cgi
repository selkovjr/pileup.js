#!/opt/rakudo-pkg/bin/perl6
# header {{{1
v6;

use URI::Encode;
use Template::Mustache;
use Terminal::ANSIColor;
use Data::Dump;

my $basename = IO::Path.new($*PROGRAM-NAME).basename;
my $path = $*PROGRAM-NAME.substr(0, $*PROGRAM-NAME.index($basename));

sub log_message ($message) {
  note color('blue'), $path, color('bold blue'), $basename, color('reset'),
    ': ',
    color('green'), $message, color('reset');
}

log_message('start');

say "Content-type: text/html";
say "Access-Control-Allow-Origin: *";
say '';
#}}}

my $template_engine = Template::Mustache.new(:from<.>, :extension<.mustache>);

# query args {{{1
my %arg;

sub usage {
  my $path = %*ENV<_> ?? %*ENV<_> !! '<pileup-script-uri>';
  if (%*ENV<SCRIPT_NAME>) {
    $path = "%*ENV<HTTP_HOST>%*ENV<SCRIPT_NAME>";
    $path ~~ s% '/index.cgi' $ %%;
  }
  say $template_engine.render('usage.html', {
    base_url => $path,
    server => %*ENV<HTTP_HOST>
  });

  if (%arg) {
    say "query parameters: {%arg.perl}";
  }
  log_message('rendered usage page');
  exit;
}

if %*ENV<QUERY_STRING> {
  my $q = uri_decode(%*ENV<QUERY_STRING>);
  for $q.split(/<[&;]>/) -> $p {
    if $p.match: /'='/ {
      my ($k, $v) = $p.split('=');
      if $v {
        %arg{$k} = $v;
      }
      else {
        %arg{$k} = Any;
      }
    }
    else {
      %arg{$p} = True;
    }
  }

  if not (%arg<coords> or %arg<bam>) { # this test needs to be more intelligent
    usage();
  }
}
else {
  usage();
}

#}}}

my $coords = %arg<coords>;
if (not $coords) {
  say 'missing coordinates';
  exit;
}

my $mark = %arg<mark>;

if ($coords ~~ /^ <-[:]>+ ':' (<-[-]>+) $/ and not $mark) {
  $mark = $0;
}

my $downsample = '';
if (%arg<downsample>) {
  $downsample = "downssample=%arg<downsample>;";
}

my $ref = 'hg19';
if (%arg<ref>) {
  $ref = %arg<ref>
}

my $filter = '';
if (%arg<filter>) {
  $filter = "filter=%arg<filter>;";
}

my $chr = '';
if %arg<chr> {
  $chr = 'chr;'
}

my $pairs = '';
if (%arg<pair> or %arg<pairs> or %arg<paired>) {
  $pairs = True;
}

my $qual = '';
if (%arg<qual> or %arg<quality>) {
  $qual = True;
}

my $collapse = '';
if (%arg<collapse> or %arg<collapse>) {
  $collapse = True;
}

my $select = '';
if (%arg<select>) {
  $select = %arg<select>;
}

my ($contig, $range) = $coords.split(':');
$range ~~ s:g/','//;
my ($start, $stop);
if ($range ~~ /'-'/) {
  ($start, $stop) = $range.split('-');
}
else {
  ($start, $stop) = ($range - 40, $range + 40);
}
$contig ~~ s/^ (\d\d? | X | Y | MT?) $/chr$0/;

sub get_url {
  my $url = 'http';
  if (%*ENV<HTTPS> and %*ENV<HTTPS> eq 'on') {
    $url ~= "s";
  }
  $url ~= '://';
  $url ~= %*ENV<HTTP_HOST> ~ %*ENV<REQUEST_URI>;
  return $url;
}

my %template_data =
  url => get_url(),
  ref => $ref,
  downsample => $downsample,
  filter => $filter,
  pairs => $pairs,
  chr => $chr,
  qual => $qual,
  collapse => $collapse,
  select => $select,
  coords => $coords,
  contig => $contig,
  start => $start,
  stop => $stop
  ;

if ($mark) {
  $mark ~~ s:g/','//;
  %template_data<mark> = $mark;
}
else {
  %template_data<mark> = False;
}

my $blacklist = %arg<blacklist>;
if ($blacklist) {
  %template_data<blacklist> = {
    url => $blacklist;
  };
}

if %arg<message> {
  %template_data<message> = %arg<message>;
}
if %arg<bam> {
  %template_data<bam> = %arg<bam>;
}
else {
  say "Status: 201 Backend Error\n";
  say 'Missing BAM parameter';
  print Dump(%arg);
  note color('yellow'), Dump(%arg), color('reset');
  exit;
}

log_message('rendering');
say $template_engine.render('index.html', %template_data);
log_message('done');
