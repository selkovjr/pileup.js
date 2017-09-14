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
# This should be an option
%arg<coords> ~~ s/chr//;
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

my ($stderr, $stderr-fh) = tempfile(:prefix('samtools-view-stderr-'), :unlink);

my $downsample = '';
if (%arg<downssample>) {
  $downsample = " -s %arg<downssample>";
}

my $subcommand_alt = '';
if (%arg<alt>) {
  $subcommand_alt = '| ./select-mismatches';
}

my $command;
if (%arg<filter>) {
  $command = qq{/home/selkov/bin/samtools view $downsample '$data' %arg<coords> $subcommand_alt 2> $stderr | egrep -i '%arg<filter>'};
}
else {
  $command = qq{/home/selkov/bin/samtools view $downsample $data %arg<coords> $subcommand_alt 2> $stderr};
}

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

my $result = chomp qq:x{$command};

my $err = False;
my $message = '';
for $stderr-fh.lines -> $line {
  $err = True;
  $message ~= "\n" ~ $line;
}

if ($err) {
  say "Status: 201 Backend Error\n";
  say 'Error in samtools';
  print $message;

  print $*ERR: color('yellow');
  print $*ERR: $message;
  print $*ERR: color('reset');
  print $*ERR: "\n";
}
else {
  say ''; # finish the HTTP header
  print $result;
  if ($message) {
    print $*ERR: color('yellow');
    print $*ERR: $message;
    print $*ERR: color('reset');
    print $*ERR: "\n";
  }
}

unlink $stderr;
