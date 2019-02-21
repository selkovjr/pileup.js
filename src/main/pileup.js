/**
 * This exposes the main entry point into pileup.js.
 * @flow
 */
'use strict';

import type {Track, VisualizedTrack, VizWithOptions} from './types';
import {AlleleFrequencyStrategy} from './types';
import type {State} from './types';

import type {VizProps} from './VisualizationWrapper';
import _ from 'underscore';
import React from 'react';
import ReactDOM from 'react-dom';

// Data sources
import TwoBitDataSource from './sources/TwoBitDataSource';
import BigBedDataSource from './sources/BigBedDataSource';
import BigBedRegionDataSource from './sources/BigBedRegionDataSource';
import VcfDataSource from './sources/VcfDataSource';
import BamDataSource from './sources/BamDataSource';
import SamViewDataSource from './sources/SamViewDataSource';
import EmptySource from './sources/EmptySource';

// Data sources from json
import GA4GHAlignmentJson from './json/GA4GHAlignmentJson';
import GA4GHVariantJson from './json/GA4GHVariantJson';
import GA4GHFeatureJson from './json/GA4GHFeatureJson';

// GA4GH sources
import GA4GHAlignmentSource from './sources/GA4GHAlignmentSource';
import GA4GHVariantSource from './sources/GA4GHVariantSource';
import GA4GHFeatureSource from './sources/GA4GHFeatureSource';

// Visualizations
import CoverageTrack from './viz/CoverageTrack';
import GenomeTrack from './viz/GenomeTrack';
import GeneTrack from './viz/GeneTrack';
import FeatureTrack from './viz/FeatureTrack';
import RegionTrack from './viz/RegionTrack';
import LocationTrack from './viz/LocationTrack';
import PileupTrack from './viz/PileupTrack';
import ScaleTrack from './viz/ScaleTrack';
import VariantTrack from './viz/VariantTrack';
import GenotypeTrack from './viz/GenotypeTrack';
import BlacklistTrack from './viz/VariantTrack';
import Root from './Root';

type GenomeRange = {
  contig: string;
  start: number;
  stop: number;
}

type Pileup = {
  setRange(range: GenomeRange): void;
  getRange(): GenomeRange;
  destroy(): void;
}

type PileupParams = {
  range: {
    contig: string,
    start: number,
    stop: number
  };
  tracks: Track[];
}

function findReference(tracks: VisualizedTrack[]): ?VisualizedTrack {
  return _.find(tracks, t => !!t.track.isReference);
}

function create(elOrId: string|Element, params: PileupParams): Pileup {
  var el = typeof(elOrId) == 'string' ? document.getElementById(elOrId) : elOrId;
  if (!el) {
    throw new Error(`Attempted to create pileup with non-existent element ${elOrId.toString()}`);
  }

  var vizTracks = params.tracks.map(function(track: Track): VisualizedTrack {
    var source = track.data ? track.data : track.viz.component.defaultSource;
    if(!source) {
      var displayName = track.viz.component.displayName != null ? track.viz.component.displayName : 'track';
      throw new Error(
        `Track '${displayName}' doesn't have a default ` +
        `data source; you must specify one when initializing it.`
      );
    }

    return {visualization: track.viz, source, track};
  });

  var referenceTrack = findReference(vizTracks);
  if (!referenceTrack) {
    throw new Error('You must include at least one track with type=reference');
  }

  var reactElement =
      ReactDOM.render(<Root referenceSource={referenceTrack.source}
                            tracks={vizTracks}
                            initialRange={params.range} />, el);

  //if the element doesn't belong to document DOM observe DOM to detect
  //when it's attached
  var observer = null;
  var body = document.body;
  if (!body) throw new Error("Failed to match: document.body");

  if (!body.contains(el)) {
    observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList') {
          var added= false;
          for (var i=0; i<mutation.addedNodes.length;i++) {
            //when added element is element where we visualize pileup
            //or it contains element where we visualize pileup
            //then we will have to update component
            if (mutation.addedNodes[i]===el || mutation.addedNodes[i].contains(el)) {
              added = true;
            }
          }
          if (added) {
            if (reactElement) {
              reactElement.setState({updateSize:true});
            } else {
              throw 'ReactElement was not initialized properly';
            }
          }
        }
      });
    });
    // configuration of the observer:
    var config = {attributes: true, childList: true, characterData: true, subtree: true};

    // start observing document
    observer.observe(document, config);
  }

  return {
    setRange(range: GenomeRange) {
      if (reactElement === null) {
        throw 'Cannot call setRange on a destroyed pileup';
      }
      reactElement.handleRangeChange(range);
    },
    getRange(): GenomeRange {
      if (reactElement === null) {
        throw 'Cannot call getRange on a destroyed pileup';
      }
      if (reactElement.state.range != null) {
        return _.clone(reactElement.state.range);
      } else {
        throw 'Cannot call setRange on non-existent range';
      }

    },
    destroy(): void {
      if (!vizTracks) {
        throw 'Cannot call destroy() twice on the same pileup';
      }
      vizTracks.forEach(({source}) => {
        source.off();
      });
      ReactDOM.unmountComponentAtNode(el);
      reactElement = null;
      referenceTrack = null;
      vizTracks = null;

      // disconnect observer if it was created
      if (observer !== null && observer !== undefined) {
        observer.disconnect();
      }
    }
  };
}

type VizObject = ((options: ?Object) => VizWithOptions);

function makeVizObject(component: Class<React.Component<VizProps<any>, State>>): VizObject {
  return options => {
    // $FlowIgnore: TODO remove flow suppression
    options = _.extend({}, component.defaultOptions, options);
    return {component, options};
  };
}

var pileup = {
  create: create,
  formats: {
    bam: BamDataSource.create,
    alignmentJson: GA4GHAlignmentJson.create,
    variantJson: GA4GHVariantJson.create,
    featureJson: GA4GHFeatureJson.create,
    reads: SamViewDataSource.create,
    vcf: VcfDataSource.create,
    twoBit: TwoBitDataSource.create,
    bigBed: BigBedDataSource.create,
    bigBedRegion: BigBedRegionDataSource.create,
    GAReadAlignment: GA4GHAlignmentSource.create,
    GAVariant: GA4GHVariantSource.create,
    GAFeature: GA4GHFeatureSource.create,
    empty: EmptySource.create
  },
  viz: {
    coverage:  makeVizObject(CoverageTrack),
    genome:    makeVizObject(GenomeTrack),
    genes:     makeVizObject(GeneTrack),
    features:  makeVizObject(FeatureTrack),
    regions:   makeVizObject(RegionTrack),
    location:  makeVizObject(LocationTrack),
    scale:     makeVizObject(ScaleTrack),
    variants:  makeVizObject(VariantTrack),
    genotypes: makeVizObject(GenotypeTrack),
    blacklist: makeVizObject(BlacklistTrack),
    pileup:    makeVizObject(PileupTrack)
  },
  enum: {
    variants: {
      alleleFrequencyStrategy: AlleleFrequencyStrategy,
    },
  },
  version: '0.6.10.tempus'
};

module.exports = pileup;

// Export a global until the distributed package works with CommonJS
// See https://github.com/hammerlab/pileup.js/issues/136
if (typeof window !== 'undefined') {
  window.pileup = pileup;
}
