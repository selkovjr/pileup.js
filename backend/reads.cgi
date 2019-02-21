#!/usr/bin/env perl6

# header {{{1
v6;

use URI::Encode;
use File::Temp;
use Terminal::ANSIColor;
use Data::Dump;

say 'Content-type: text/plain';
say 'Access-Control-Allow-Origin: *';
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

# This is now an option, but there must be an intelligent way of doing this
unless %arg<chr> {
  %arg<coords> ~~ s/chr//;
}
#}}}


my $data;
if %arg<bam> {
  $data = %arg<bam>
}
else {
  say "Status: 201 Backend Error\n";
  say 'Missing BAM parameter';
  say Dump(%arg, :color(False));

  note Dump(%arg);
  exit;
}

my ($stderr, $stderr-fh) = tempfile(:prefix('samtools-view-stderr-'), :unlink);

my $downsample-arg = '';
if (%arg<downssample>) {
  $downsample-arg = "-s %arg<downssample> ";
}

my $subcommand_alt = '';
if (%arg<alt>) {
  $subcommand_alt = '| ./select-mismatches';
}

my $filter-subcommand = '';
if (%arg<filter>) {
  $filter-subcommand = qq{ | egrep '^@|%arg<filter>'};
  $downsample-arg = '';
}

my $fill-in-md = True;
my $md-subcommand = '';
if $fill-in-md {
 if %arg<ref> eq 'hg38' {
    $md-subcommand = qq{ | samtools calmd -S - /data3/selkov_workdir/data/reference/GRCh38.analysis_set.fa 2>> $stderr | grep -v '^@' $subcommand_alt 2>> $stderr};
  }
  else {
    $md-subcommand = qq{ | samtools calmd -S - /data3/selkov_workdir/data/reference/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa 2>> $stderr | grep -v '^@' $subcommand_alt 2>> $stderr};
  }
}

my $command = qq{samtools view -h $downsample-arg'$data' %arg<coords> 2> $stderr$filter-subcommand$md-subcommand};

my $basename = IO::Path.new($*PROGRAM-NAME).basename;
my $path = $*PROGRAM-NAME.substr(0, $*PROGRAM-NAME.index($basename));
note color('blue'), $path, color('bold blue'), $basename, color('reset'),
  ": ",
  color('green'), $command, color('reset');


my $result;
indir tempdir(:prefix('samtools-view-'), '*******'), {
  $result = chomp qq:x{$command};
};


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
