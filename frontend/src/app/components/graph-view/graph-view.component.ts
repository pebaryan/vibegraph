import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import * as d3 from 'd3';
import { GraphService } from '@app/services/graph.service';

@Component({
  selector: 'app-graph-view',
  templateUrl: './graph-view.component.html',
  styleUrls: ['./graph-view.component.scss']
})
export class GraphViewComponent implements OnInit {
  triples: any[] = [];
  nodes: any[] = [];
  links: any[] = [];
  newSubject = '';
  newPredicate = '';
  newObject = '';

  constructor(private graphService: GraphService, private route: ActivatedRoute) {}

  ngOnInit() {
    this.fetchTriples();
  }

  fetchTriples() {
    // For simplicity, use the first graph id; in real app, pass id from route
    const graphId = 'default';
    this.graphService.getTriples(graphId).subscribe((data) => {
      this.triples = data;
      this.processTriples();
      this.renderGraph();
    });
  }

  processTriples() {
    const nodeMap: Record<string, any> = {};
    this.links = [];
    this.triples.forEach((t) => {
      const s = t.subject;
      const p = t.predicate;
      const o = t.object;
      if (!nodeMap[s]) nodeMap[s] = { id: s };
      if (!nodeMap[o]) nodeMap[o] = { id: o };
      this.links.push({ source: s, target: o, label: p });
    });
    this.nodes = Object.values(nodeMap);
  }

  renderGraph() {
    const svg = d3.select('#graphSvg');
    svg.selectAll('*').remove();
    const width = 800;
    const height = 600;
    const simulation = d3.forceSimulation(this.nodes)
      .force('link', d3.forceLink(this.links).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(this.links)
      .enter()
      .append('line')
      .attr('stroke-width', 1);

    const node = svg
      .append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(this.nodes)
      .enter()
      .append('circle')
      .attr('r', 10)
      .attr('fill', '#69b3a2')
      .call(
        d3
          .drag<SVGCircleElement, any>()
          .on('start', (event: any, d: any) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event: any, d: any) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event: any, d: any) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      )
      .on('click', (event: any, d: any) => this.onNodeClick(d));

    const label = svg
      .append('g')
      .selectAll('text')
      .data(this.nodes)
      .enter()
      .append('text')
      .text((d) => d.id)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', '0.35em');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y);
      label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y);
    });
  }

  onNodeClick(node: any) {
    console.log('Node clicked:', node.id);
    // Placeholder for expansion logic
  }

  addTriple() {
    const graphId = 'default';
    const triple = {
      subject: this.newSubject,
      predicate: this.newPredicate,
      object: this.newObject,
    };
    this.graphService.createTriple(graphId, triple).subscribe(() => {
      this.fetchTriples();
      this.newSubject = '';
      this.newPredicate = '';
      this.newObject = '';
    });
  }
}
