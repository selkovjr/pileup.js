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
  print $*ERR: color('blue');
  print $*ERR: $path;
  print $*ERR: color('bold blue');
  print $*ERR: $basename;
  print $*ERR: color('reset');
  print $*ERR: ": ";
  print $*ERR: color('green');
  print $*ERR: $message;
  print $*ERR: color('reset');
  print $*ERR: "\n";
}

log_message('start');

print "Content-type: text/html\n";
print "Access-Control-Allow-Origin: *\n\n";
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
        say $*ERR: "$k -> %arg{$k}";
      }
      else {
        %arg{$k} = Any;
        say $*ERR: "$k -> %arg{$k}";
      }
    }
    else {
      %arg{$p} = True;
      say $*ERR: "$p -> %arg{$p}";
    }
  }

  if not (%arg<coords> or %arg<bam> or %arg<aws> or %arg<order>) { # elaborate!
    usage();
  }
}
else {
  usage();
}

#}}}

# order/run attributes {{{1
my $bucket = %*ENV<DEFAULT_AWS_BUCKET>;
if %arg<bucket> {
  $bucket = %arg<bucket>;
}

my $panel = 'xO';
if %arg<panel> {
  $panel = %arg<panel>;
}

my $type = 'TN';
if %arg<type> {
  $type = %arg<type>;
}

my $rel = 'M';
if %arg<rel> {
  $rel = %arg<rel>;
}

my $product = 'R';
if %arg<product> {
  $product = %arg<product>;
}

my $sample = 'T';
if %arg<sample> {
  $sample = %arg<sample>;
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
  panel => $panel,
  ref => $ref,
  downsample => $downsample,
  filter => $filter,
  pairs => $pairs,
  chr => $chr,
  qual => $qual,
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
  %template_data<local> = True;
  %template_data<bam> = %arg<bam>;
}
elsif %arg<aws> {
  %template_data<aws_path> = True;
  %template_data<bucket> = $bucket;
  %template_data<aws> = %arg<aws>;
}
elsif %arg<order> {
  %template_data<aws_detail> = True;
  %template_data<bucket> = $bucket;
  %template_data<order> = %arg<order>;
  %template_data<run> = %arg<run>;
  %template_data<type> = $type;
  %template_data<rel> = $rel;
  %template_data<product> = $product;
  %template_data<sample> = $sample;
}
else {
  say "Status: 201 Backend Error\n";
  say 'incorrect URL arguments';
  print Dump(%arg);

  print $*ERR: color('yellow');
  print Dump(%arg);
  print $*ERR: color('reset');
  print $*ERR: "\n";
  exit;
}

log_message('rendering');
say $template_engine.render('index.html', %template_data);
log_message('done');

