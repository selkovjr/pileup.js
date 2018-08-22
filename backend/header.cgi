#!/opt/rakudo-pkg/bin/perl6

# header {{{1
v6;

use URI::Encode;
use File::Temp;
use Terminal::ANSIColor;
use Data::Dump;

say "Content-type: text/plain";
say "Access-Control-Allow-Origin: *";
#}}}

# query args {{{1
my %arg;
my $q = uri_decode(%*ENV<QUERY_STRING>);
for $q.split(/<[&;]>/) -> $p {
  if $p.match: /'='/ {
    my ($k, $v) = $p.split('=');
    if $v {
      %arg{$k} = $v;
    }
    else {
      %arg{$k} = '';
    }
  }
  elsif $p {
    %arg{$p} = True;
  }
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


my $data;
if %arg<bam> {
  $data = %arg<bam>
}
elsif %arg<aws> {
  if %arg<aws> ~~ /^ s3:/ {
    $data = %arg<aws>;
  }
  else {
    $data = "s3://$bucket/{%arg<aws>}";
  }
}
elsif %arg<order> {
  if %arg<run> {
    $data = "s3://$bucket/{%arg<order>}_{$type}_{$rel}_{$product}_{$panel}/{%arg<run>}/{%arg<order>}_{$type}_{$rel}_{$product}_{$panel}_{$sample}.dedup.bam"
  }
  else {
    $data = "s3://$bucket/{%arg<order>}_{$type}_{$rel}_{$product}_{$panel}/{%arg<order>}_{$type}_{$rel}_{$product}_{$panel}_{$sample}.dedup.bam"
  }
}
else {
  say "Status: 201 Backend Error\n";
  say 'incorrect URL arguments';
  say Dump(%arg, :color(False));
  note Dump(%arg);
  exit;
}

my $command = qq{samtools view -H '$data'};

my $basename = IO::Path.new($*PROGRAM-NAME).basename;
my $path = $*PROGRAM-NAME.substr(0, $*PROGRAM-NAME.index($basename));
note color('blue'), $path, color('bold blue'), $basename, color('reset'),
  ": ",
  color('green'), $command, color('reset');

my ($stderr, $stderr-fh) = tempfile(:prefix('samtools-header-stderr'), :unlink);

my $result = chomp qq:x{$command 2> $stderr};

my $err = False;
my $message = '';
for $stderr-fh.lines -> $line {
  $err = True;
  $message ~= "\n" ~ $line;
}

if ($err) {
  say "Status: 201 Backend Error\n";
  say 'Error getting bam header with samtools';
  print $message;

  note color('yellow'), $message, color('reset');
}
else {
  say ''; # finish the HTTP header
  print $result;
}

unlink $stderr;
