/* @flow */
'use strict';

import type {GenomeRange} from '../types';
import type {Strand} from '../Alignment';
import {strToStrand} from '../Alignment';

import _ from 'underscore';
import Q from 'q';
import {Events} from 'backbone';

import ContigInterval from '../ContigInterval';
import Interval from '../Interval';
import BigBed from '../data/BigBed';
// requirement for jshint to pass
/* exported Feature */
import Feature from '../data/feature';


export type Gene = {
  position: ContigInterval<string>;
  id: string;  // transcript ID, e.g. "ENST00000269305"
  score: number;
  strand: Strand;
  codingRegion: Interval;  // locus of coding start
  exons: Array<Interval>;
  geneId: string;  // ensembl gene ID
  name: string;  // human-readable name, e.g. "TP53"
}

// Flow type for export.
export type FeatureDataSource = {
  rangeChanged: (newRange: GenomeRange) => void;
  getFeaturesInRange: (range: ContigInterval<string>, resolution: ?number) => Feature[];
  on: (event: string, handler: Function) => void;
  off: (event: string) => void;
  trigger: (event: string, ...args:any) => void;
}

// Flow type for export.
export type BigBedSource = {
  rangeChanged: (newRange: GenomeRange) => void;
  getFeaturesInRange: (range: ContigInterval<string>) => Gene[];
  on: (event: string, handler: Function) => void;
  off: (event: string) => void;
  trigger: (event: string, ...args:any) => void;
}

// The fields are described at http://genome.ucsc.edu/FAQ/FAQformat#format1
// Fields 4-12 are optional
function parseBedFeature(f): Gene {
  var position = new ContigInterval(f.contig, f.start, f.stop),
      x = f.rest.split('\t');

  // if no id, generate randomly for unique storage
  var id = x[0] ? x[0] : position.toString(); // e.g. ENST00000359597
  var score = x[1] ? parseInt(x[1]) : 1000; // number from 0-1000
  var strand =  strToStrand(x[2]); // either +, - or .
  var codingRegion = (x[3] && x[4]) ? new Interval(Number(x[3]), Number(x[4])) :new Interval(f.start, f.stop);
  var geneId =  x[9] ? x[9] : id;
  var name =  x[10] ? x[10] : "";

  // parse exons
  var exons = [];
  if (x[7] && x[8]) {
    // exons arrays sometimes have trailing commas
    var exonLengths = x[7].replace(/,*$/, '').split(',').map(Number),
      exonStarts = x[8].replace(/,*$/, '').split(',').map(Number);

    exons = _.zip(exonStarts, exonLengths)
             .map(function([start, length]) {
               return new Interval(f.start + start, f.start + start + length);
             });
  }

  return {
    position,
    id: id,
    score: score,
    strand: strand,
    codingRegion: codingRegion,
    geneId: geneId,
    name: name,
    exons
  };
}


function createFromBigBedFile(remoteSource: BigBed): BigBedSource {
  // Collection of genes that have already been loaded.
  var genes: {[key:string]: Gene} = {};

  // Ranges for which we have complete information -- no need to hit network.
  var coveredRanges: Array<ContigInterval<string>> = [];

  function addGene(newGene) {
    if (!genes[newGene.id]) {
      genes[newGene.id] = newGene;
    }
  }

  function getFeaturesInRange(range: ContigInterval<string>): Gene[] {
    if (!range) return [];
    var results = [];
    _.each(genes, gene => {
      if (range.intersects(gene.position)) {
        results.push(gene);
      }
    });
    return results;
  }

  function fetch(range: GenomeRange) {
    var interval = new ContigInterval(range.contig, range.start, range.stop);

    // Check if this interval is already in the cache.
    if (interval.isCoveredBy(coveredRanges)) {
      return Q.when();
    }

    coveredRanges.push(interval);
    coveredRanges = ContigInterval.coalesce(coveredRanges);

    return remoteSource.getFeatureBlocksOverlapping(interval).then(featureBlocks => {
      featureBlocks.forEach(fb => {
        coveredRanges.push(fb.range);
        coveredRanges = ContigInterval.coalesce(coveredRanges);
        var genes = fb.rows.map(parseBedFeature);
        genes.forEach(gene => addGene(gene));
      });
      //we have new data from our internal block range
      o.trigger('newdata', interval);
      o.trigger('networkdone');
    });
  }

  var o = {
    rangeChanged: function(newRange: GenomeRange) {
      fetch(newRange).done();
    },
    getFeaturesInRange,

    // These are here to make Flow happy.
    on: () => {},
    off: () => {},
    trigger: (status: string, param: any) => {}
  };
  _.extend(o, Events);  // Make this an event emitter

  return o;
}

function create(data: {url:string}): BigBedSource {
  var url = data.url;
  if (!url) {
    throw new Error(`Missing URL from track: ${JSON.stringify(data)}`);
  }

  return createFromBigBedFile(new BigBed(url));
}

module.exports = {
  create,
  createFromBigBedFile
};
