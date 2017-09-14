#!/usr/bin/env perl6

# header {{{1
v6;

use URI::Encode;
use File::Temp;
use Terminal::ANSIColor;
use Data::Dump;

print "Content-type: text/plain\n";
print "Access-Control-Allow-Origin: *\n";
#}}}

# query args {{{1
my %arg;
my $q = uri_decode(%*ENV<QUERY_STRING>);
for $q.split(/<[&;]>/) -> $p {
  if $p.match: /'='/ {
    my ($k, $v) = $p.split('=');
    if $v {
      %arg{$k} = $v;
      say $*ERR: "$k -> %arg{$k}";
    }
    else {
      %arg{$k} = '';
      say $*ERR: "$k -> %arg{$k}";
    }
  }
  else {
    %arg{$p} = True;
    say $*ERR: "$p -> %arg{$p}";
  }
}
#}}}

# order/run attributes {{{1
my $bucket = 'clinical-data-processing-complete';
if %arg<bucket> {
  $bucket = %arg<bucket>;
}
say $*ERR: "bucket: $bucket";

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
  $data = "s3://$bucket/{%arg<aws>}";
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
  print Dump(%arg);

  print $*ERR: color('yellow');
  print Dump(%arg);
  print $*ERR: color('reset');
  print $*ERR: "\n";
  exit;
}

my $command = qq{/home/selkov/bin/samtools view -H '$data'};

my $basename = IO::Path.new($*PROGRAM-NAME).basename;
my $path = $*PROGRAM-NAME.substr(0, $*PROGRAM-NAME.index($basename));
print $*ERR: color('blue');
print $*ERR: $path;
print $*ERR: color('bold blue');
print $*ERR: $basename;
print $*ERR: color('reset');
print $*ERR: ": ";
print $*ERR: color('green');
print $*ERR: $command;
print $*ERR: color('reset');
print $*ERR: "\n";

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

  print $*ERR: color('yellow');
  print $*ERR: $message;
  print $*ERR: color('reset');
  print $*ERR: "\n";
}
else {
  say ''; # finish the HTTP header
  print $result;
}

unlink $stderr;
