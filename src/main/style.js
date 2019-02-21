'use strict';

/**
 * Central collection of styling settings.
 * Until we figure out a better story around canvas & CSS, they live here.
 *
 * @flow
 */

module.exports = {
  // Colors for individual base pairs
  BASE_COLORS: {
    'A': '#188712',
    'G': '#a14b12',
    'C': '#0600F9',
    'T': '#ff0015',
    'U': '#F70016',
    'N': '#a0o0o0'
  },

  // Styles for base pairs which are rendered as letters
  LOOSE_TEXT_STYLE: `24px 'Helvetica Neue', Helvetica, Arial, sans-serif`,
  TIGHT_TEXT_STYLE: `bold 10px 'Helvetica Neue', Helvetica, Arial, sans-serif`,

  // Gene track
  GENE_ARROW_SIZE: 4,
  GENE_COLOR: 'blue',  // color of the gene line, exons, text, etc.
  GENE_COMPLEMENT_COLOR: 'white',  // a color visible on top of GENE_COLOR
  GENE_FONT: `'Helvetica Neue', Helvetica, Arial, sans-serif`,
  GENE_FONT_SIZE: 12,
  GENE_TEXT_PADDING: 5,  // space between bottom of coding exon & top of gene name

  // Pileup track
  ALIGNMENT_COLOR: '#c8c8c8',
  ALIGNMENT_PLUS_STRAND_COLOR: '#DD989B',
  ALIGNMENT_MINUS_STRAND_COLOR: '#b0b0ec',
  READ_COLOR: {
    F1F2: '#911C22',
    F1R2: {
      R1: '#DD989B',
      R2: '#b0b0ec',
    },
    R1F2: {
      R1: '#e4c490',
      R2: '#79B2A4',
    },
  },
  DELETE_COLOR: 'black',
  INSERT_COLOR: '#6100d8',
  READ_SPACING: 1, // vertical spacing between reads
  READ_HEIGHT: 11, // Height of read


  // Coverage track
  COVERAGE_FONT_STYLE: `bold 9px 'Helvetica Neue', Helvetica, Arial, sans-serif`,
  COVERAGE_FONT_COLOR: 'black',
  COVERAGE_TICK_LENGTH: 5,
  COVERAGE_TEXT_PADDING: 3,  // space between axis ticks and text
  COVERAGE_TEXT_Y_OFFSET: 3,  // so that ticks and texts align better
  COVERAGE_BIN_COLOR: '#a0a0a0',
  COVERAGE_MIN_BAR_WIDTH_FOR_GAP: 8,  // show a 1px gap between bars at this resolution

  // Scale Track
  SCALE_LINE_PADDING: 40,  // space between mid point and left/right lines
  SCALE_FONT_STYLE: `bold 12px 'Helvetica Neue', Helvetica, Arial, sans-serif`,
  SCALE_TEXT_Y_OFFSET: 5,  // so that lines and the text align better
  SCALE_FONT_COLOR: 'black',
  SCALE_ARROW_SIZE: 4,

  // Location track
  LOC_TEXT_PADDING: 5,  // space between mid-point label and tick
  LOC_TICK_LENGTH: 10,
  LOC_TEXT_Y_OFFSET: 5,  // so that the line and the text align better
  LOC_FONT_STYLE: `13px 'Helvetica Neue', Helvetica, Arial, sans-serif`,
  LOC_FONT_COLOR: 'black',

  // Variant Track
  VARIANT_STROKE: '#666',
  VARIANT_FILL: '#ddd',
  VARIANT_HEIGHT: 14,

 // Genotype Track
  GENOTYPE_SPACING: 1,
  GENOTYPE_HEIGHT: 10,
  GENOTYPE_FILL: '#999999',
  BACKGROUND_FILL: '#f2f2f2',

  // Blacklist Track
  BLACKLIST_TEXT_COLOR: 'black'
};
