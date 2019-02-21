/**
 * Common types used in many modules.
 *
 * Flow makes it difficult for a module to export both symbols and types. This
 * module serves as a dumping ground for types which we'd really like to export
 * from other modules.
 *
 * @flow
 */
'use strict';

// Public API

import React from 'react';

export const AlleleFrequencyStrategy = {
  Minor : {name: "Minor"},
  Major : {name: "Major"},
};


export type NetworkStatus = {numRequests?: number, status?: string};

export type State = {
  networkStatus: ?NetworkStatus;
};

export type VizWithOptions = {
  component: Class<React.Component<any, any>>;
  options: ?Object;
}

export type Track = {
  viz: VizWithOptions;
  data: Object;  // This is a DataSource object
  name?: string;
  cssClass?: string;
  isReference?: boolean;
  options?: Object
}

export type VisualizedTrack = {
  visualization: VizWithOptions;
  source: Object;  // data source
  track: Track;  // for css class and options
}

export type GenomeRange = {
  contig: string;
  start: number;  // inclusive
  stop: number;  // inclusive
}

export type PartialGenomeRange = {
  contig?: string;
  start?: number;
  stop?: number;
}

// BAM/BAI parsing

import type VirtualOffset from './data/VirtualOffset';

export type Chunk = {
  chunk_beg: VirtualOffset;
  chunk_end: VirtualOffset;
}

// src/utils.js
export type InflatedBlock = {
  offset: number;
  compressedLength: number;
  buffer: ArrayBuffer;
}
