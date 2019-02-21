/**
 * @flow
 */
'use strict';


import type {TwoBitSource} from './sources/TwoBitDataSource';

import React from 'react';
import ReactDOM from 'react-dom';
import d3utils from './viz/d3utils';
import _ from 'underscore';
import d3 from '../lib/minid3';

export type VizProps<T: any> = {
  width: number;
  height: number;
  range: GenomeRange;
  referenceSource: TwoBitSource;
  source: T;
  options: any;
};

type Props = {
  range: ?GenomeRange;
  visualization: VizWithOptions;
  onRangeChange: (newRange: GenomeRange) => void;
  referenceSource: TwoBitSource;
  source: any;
  options: ?Object;
};

type State = {
  width: number;
  height: number;
  updateSize: boolean;
};

class VisualizationWrapper extends React.Component<Props, State> {
  props: Props;
  state: State;
  hasDragBeenInitialized: boolean;
  onResizeListener: Object;  //listener that handles window.onresize event

  constructor(props: Object) {
    super(props);
    this.hasDragBeenInitialized = false;
    this.state = {
      updateSize: false,
      width: 0,
      height: 0
    };
  }

  updateSize(): any {
    var thisNode = ReactDOM.findDOMNode(this)
    if (thisNode && thisNode instanceof Element) { // check for getContext
      var parentDiv = thisNode.parentNode;
      if (parentDiv && parentDiv instanceof HTMLElement) { // check for getContext
        this.setState({
          updateSize: false,
          width: parentDiv.offsetWidth,
          height: parentDiv.offsetHeight
        });
      }
    }
  }

  componentDidMount(): any {
    //local copy of the listener, so we can remove it
    //when pileup is destroyed
    this.onResizeListener = () => this.updateSize();
    window.addEventListener('resize', this.onResizeListener);
    this.updateSize();

    if (this.props.range && !this.hasDragBeenInitialized) this.addDragInterface();
  }

  componentDidUpdate(): any {
    if (this.props.range && !this.hasDragBeenInitialized) this.addDragInterface();
  }

  componentWillUnmount(): any {
    window.removeEventListener('resize', this.onResizeListener);
  }

  getScale(): (num: number)=>number {
    if (!this.props.range) return x => x;
    return d3utils.getTrackScale(this.props.range, this.state.width);
  }

  removeDragInterface(): any {
    var div = ReactDOM.findDOMNode(this);

    var drag = d3.behavior.drag()
        .on('dragstart', null)
        .on('drag', null)
        .on('dragend', null);

    d3.select(div).call(drag);
  }

  addDragInterface(): any {
    this.hasDragBeenInitialized = true;
    var div = ReactDOM.findDOMNode(this);
    var originalRange, originalScale, dx=0;
    var dragstarted = () => {
      d3.event.sourceEvent.stopPropagation();
      dx = 0;
      originalRange = _.clone(this.props.range);
      originalScale = this.getScale();
    };
    var updateRange = () => {
      if (!originalScale) return;  // can never happen, but Flow don't know.
      if (!originalRange) return;  // can never happen, but Flow don't know.
      var newStart = originalScale.invert(-dx),
          intStart = Math.round(newStart),
          offsetPx = originalScale(newStart) - originalScale(intStart);

      var newRange = {
        contig: originalRange.contig,
        start: intStart,
        stop: intStart + (originalRange.stop - originalRange.start),
        offsetPx: offsetPx
      };
      this.props.onRangeChange(newRange);
    };
    var dragmove = () => {
      dx += d3.event.dx;  // these are integers, so no roundoff issues.
      updateRange();
    };
    function dragended() {
      updateRange();
    }

    var drag = d3.behavior.drag()
        .on('dragstart', dragstarted)
        .on('drag', dragmove)
        .on('dragend', dragended);

    d3.select(div).call(drag).on('click', this.handleClick.bind(this));
  }

  handleClick(): any {
    if (d3.event.defaultPrevented) {
      d3.event.stopPropagation();
    }
  }

  componentWillUpdate(nextProps:Props, nextState: Object) {
    if (nextState.updateSize) {
      this.updateSize();
    }
  }

  render(): any {
    const range = this.props.range;
    const component = this.props.visualization.component;
    if (!range) {
      if (component.displayName != null)
        return <EmptyTrack className={component.displayName} />;
      else
        return <EmptyTrack className='EmptyTrack' />;
    }

    var options = _.extend(_.clone(this.props.visualization.options),this.props.options);

    var el = React.createElement(component, ({
      range: range,
      source: this.props.source,
      referenceSource: this.props.referenceSource,
      width: this.state.width,
      height: this.state.height,
      options: options,
      parent: this
    } : VizProps<any>));

    return <div className='drag-wrapper'>{el}</div>;
  }
}
VisualizationWrapper.displayName = 'VisualizationWrapper';


type EmptyTrackProps = {className: string};
class EmptyTrack extends React.Component<EmptyTrackProps> {
  render() {
    var className = this.props.className + ' empty';
    return <div className={className}></div>;
  }
}

module.exports = VisualizationWrapper;
